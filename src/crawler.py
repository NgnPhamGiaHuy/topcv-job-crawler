import os
import time
import logging
import requests
import random
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple
from bs4 import BeautifulSoup
from datetime import datetime

from src.parser import TopCVParser

logger = logging.getLogger(__name__)

class TopCVCrawler:
    """
    Crawler for TopCV.vn job listings
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize crawler with configuration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.crawling_config = config['crawling']
        self.base_url = self.crawling_config['base_url']
        self.timeout = self.crawling_config['timeout']
        self.max_retries = self.crawling_config['max_retries']
        self.user_agent = self.crawling_config['user_agent']
        
        # Rate limiting state
        self.rate_limited = False
        self.last_request_time = 0
        self.min_request_interval = 1.5  # Base interval between requests in seconds
        self.rate_limit_backoff = 30     # Additional backoff after hitting rate limit
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.topcv.vn/'
        })
        
        # Apply proxy configuration if enabled
        self.setup_proxy()
        
    def setup_proxy(self):
        """
        Configure proxies for the requests session if enabled in config
        """
        if 'proxy' in self.config and self.config['proxy']['enabled']:
            proxies = {}
            
            if self.config['proxy']['http']:
                proxies['http'] = self.config['proxy']['http']
                
            if self.config['proxy']['https']:
                proxies['https'] = self.config['proxy']['https']
            
            if proxies:
                self.session.proxies.update(proxies)
                logger.info(f"Using proxies: {proxies}")
            else:
                logger.warning("Proxy is enabled but no proxy URLs are configured")
        
    def get_job_listings(self, page: int = 1) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Fetch job listings from search results page
        
        Args:
            page: Page number for pagination
            
        Returns:
            Tuple of (job_list, has_more_pages)
        """
        url = f"{self.base_url}?page={page}"
        logger.info(f"Fetching job listings from page {page}: {url}")
        
        try:
            html_content = self._make_request(url)
            if not html_content:
                return [], False
                
            # Parse job listings
            job_listings = TopCVParser.extract_job_listings(html_content)
            logger.info(f"Found {len(job_listings)} jobs on page {page}")
            
            # Check if there are more pages
            has_more_pages = self._has_more_pages(html_content, page)
            
            return job_listings, has_more_pages
        except Exception as e:
            logger.error(f"Error getting job listings from page {page}: {str(e)}")
            return [], False
            
    def get_job_details(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed job information from job detail page
        
        Args:
            job_data: Basic job data from listings page
            
        Returns:
            Complete job data dictionary with details or None if failed
        """
        job_url = job_data['url']
        job_id = job_data['id']
        
        logger.info(f"Fetching job details for job {job_id}: {job_url}")
        
        try:
            html_content = self._make_request(job_url)
            if not html_content:
                logger.error(f"Failed to get HTML content for job {job_id}")
                return None
                
            # Parse job details and merge with existing data
            detailed_job = TopCVParser.extract_job_details(html_content, job_data)
            logger.info(f"Successfully fetched details for job {job_id}")
            
            return detailed_job
        except Exception as e:
            logger.error(f"Error getting job details for job {job_id}: {str(e)}")
            return None
            
    def _make_request(self, url: str) -> Optional[str]:
        """
        Make HTTP request with retries
        
        Args:
            url: URL to request
            
        Returns:
            HTML content as string or None if failed
        """
        retries = 0
        # Initial backoff time in seconds, will increase exponentially
        backoff = 1  
        
        # Respect rate limits with time between requests
        self._throttle_request()
        
        while retries < self.max_retries:
            try:
                response = self.session.get(url, timeout=self.timeout)
                self.last_request_time = time.time()
                
                if response.status_code == 403:
                    logger.error(f"Received 403 Forbidden error from {url}. This may indicate IP blocking.")
                    
                    # Check if proxy is enabled
                    if 'proxy' not in self.config or not self.config['proxy']['enabled']:
                        logger.warning("Consider enabling proxy in config.yaml to bypass 403 errors")
                    
                    retries += 1
                    if retries >= self.max_retries:
                        logger.error(f"Max retries reached for {url}")
                        return None
                        
                    sleep_time = backoff * (2 ** (retries - 1))
                    logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                    continue
                
                if response.status_code == 429:
                    # Rate limited - set flag and use longer backoff
                    self.rate_limited = True
                    retries += 1
                    logger.warning(f"Request failed (attempt {retries}/{self.max_retries}): 429 Client Error: Too Many Requests for url: {url}")
                    
                    if retries >= self.max_retries:
                        logger.error(f"Max retries reached for {url}")
                        return None
                        
                    sleep_time = self.rate_limit_backoff * (2 ** (retries - 1))
                    # Add jitter to avoid synchronized requests
                    sleep_time = sleep_time * (0.8 + 0.4 * random.random())
                    logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                    continue
                
                # Reset rate_limited flag if we get a successful response
                self.rate_limited = False
                response.raise_for_status()
                
                # Check if we got a valid HTML response
                if 'text/html' not in response.headers.get('Content-Type', ''):
                    logger.warning(f"Non-HTML response from {url}: {response.headers.get('Content-Type')}")
                    
                return response.text
            except requests.RequestException as e:
                retries += 1
                logger.warning(f"Request failed (attempt {retries}/{self.max_retries}): {str(e)}")
                
                if retries >= self.max_retries:
                    logger.error(f"Max retries reached for {url}")
                    return None
                    
                # Exponential backoff with jitter
                sleep_time = backoff * (2 ** (retries - 1))
                sleep_time = sleep_time * (0.8 + 0.4 * random.random())  # Add 20% jitter
                logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
                
        return None
    
    def _throttle_request(self) -> None:
        """
        Throttle requests to avoid hitting rate limits
        """
        now = time.time()
        time_since_last_request = now - self.last_request_time
        
        # Adjust delay based on rate limit status
        delay = self.min_request_interval
        if self.rate_limited:
            # Use longer delay if we've been rate limited
            delay = delay * 3
        
        # Add jitter to the delay (±20%)
        delay = delay * (0.8 + 0.4 * random.random())
        
        if time_since_last_request < delay:
            sleep_time = delay - time_since_last_request
            logger.debug(f"Throttling request, sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
    def _has_more_pages(self, html_content: str, current_page: int) -> bool:
        """
        Check if there are more pages of results
        
        Args:
            html_content: HTML content of current page
            current_page: Current page number
            
        Returns:
            True if there are more pages, False otherwise
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Look for pagination elements
            pagination = soup.select('.pagination a')
            if not pagination:
                return False
                
            # Check if there's a "Next" button or higher page numbers
            for page_link in pagination:
                page_text = page_link.get_text(strip=True)
                if page_text.isdigit() and int(page_text) > current_page:
                    return True
                    
                if page_text == '»' or page_text == 'Tiếp':
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"Error checking for more pages: {str(e)}")
            return False 