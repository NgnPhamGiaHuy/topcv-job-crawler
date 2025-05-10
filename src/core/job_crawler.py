import logging

from typing import Dict, List, Optional, Any, Tuple

from src.parser import create_parser
from src.core.interfaces import CrawlerInterface
from src.core.http_client import RateLimitedClient
from src.core.pagination import create_pagination_parser

logger = logging.getLogger(__name__)


class JobCrawlerBase(CrawlerInterface):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = RateLimitedClient(config)


class TopCVCrawler(JobCrawlerBase):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.parser = create_parser('topcv')
        self.crawling_config = config['crawling']
        self.base_url = self.crawling_config['base_url']
        self.pagination_parser = create_pagination_parser('topcv')
        
    def get_job_listings(self, page: int = 1) -> Tuple[List[Dict[str, Any]], bool]:
        url = f"{self.base_url}?page={page}"
        logger.info(f"Fetching job listings from page {page}: {url}")
        
        try:
            html_content = self.client.make_request(url)
            if not html_content:
                return [], False
                
            job_listings = self.parser.extract_job_listings(html_content)
            logger.info(f"Found {len(job_listings)} jobs on page {page}")
            
            has_more_pages = self.pagination_parser.has_more_pages(html_content, page)
            
            return job_listings, has_more_pages
        except Exception as e:
            logger.error(f"Error getting job listings from page {page}: {str(e)}")
            return [], False
            
    def get_job_details(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        job_id = job_data['id']
        job_url = job_data['url']

        logger.info(f"Fetching job details for job {job_id}: {job_url}")
        
        try:
            html_content = self.client.make_request(job_url)
            if not html_content:
                logger.error(f"Failed to get HTML content for job {job_id}")
                return None
                
            detailed_job = self.parser.extract_job_details(html_content, job_data)
            logger.info(f"Successfully fetched details for job {job_id}")
            
            return detailed_job
        except Exception as e:
            logger.error(f"Error getting job details for job {job_id}: {str(e)}")
            return None


def create_crawler(site_name: str, config: Dict[str, Any]) -> CrawlerInterface:
    crawlers = {
        'topcv': TopCVCrawler,
    }
    
    if site_name.lower() in crawlers:
        return crawlers[site_name.lower()](config)
    else:
        raise ValueError(f"Unsupported site: {site_name}") 