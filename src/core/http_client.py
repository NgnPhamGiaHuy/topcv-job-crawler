import time
import random
import logging
import requests
import functools

from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, initial_backoff: float = 1.0):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    retries += 1

                    if retries >= max_retries:
                        logger.error(f"Max retries reached: {str(e)}")
                        return None
                        
                    backoff_time = initial_backoff * (2 ** (retries - 1))
                    jitter = backoff_time * (0.8 + 0.4 * random.random())
                    logger.info(f"Retrying in {jitter:.1f} seconds... ({retries}/{max_retries})")
                    time.sleep(jitter)
            return None
        return wrapper
    return decorator


class RateLimitedClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.crawling_config = config['crawling']
        self.timeout = self.crawling_config['timeout']
        self.max_retries = self.crawling_config['max_retries']
        self.user_agent = self.crawling_config['user_agent']

        self.rate_limited = False
        self.last_request_time = 0
        self.min_request_interval = 1.5
        self.rate_limit_backoff = 30
        
        self.session = self._create_session()
        self._setup_proxy()
        
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.topcv.vn/'
        })

        return session

    def _setup_proxy(self) -> None:
        if not self.config.get('proxy', {}).get('enabled', False):
            return
            
        proxies = {}
        proxy_config = self.config['proxy']
        
        if proxy_config.get('http'):
            proxies['http'] = proxy_config['http']
            
        if proxy_config.get('https'):
            proxies['https'] = proxy_config['https']
        
        if proxies:
            self.session.proxies.update(proxies)
            logger.info(f"Using proxies: {proxies}")
        else:
            logger.warning("Proxy is enabled but no proxy URLs are configured")
    
    def _throttle_request(self) -> None:
        now = time.time()
        time_since_last = now - self.last_request_time
        
        delay = self.min_request_interval

        if self.rate_limited:
            delay = delay * 3
        
        delay = delay * (0.8 + 0.4 * random.random())
        
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"Throttling request, sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
    
    def _handle_response(self, response: requests.Response, url: str) -> Optional[str]:
        self.last_request_time = time.time()
        
        if response.status_code == 403:
            logger.error(f"Received 403 Forbidden error from {url}. This may indicate IP blocking.")
            
            if 'proxy' not in self.config or not self.config['proxy']['enabled']:
                logger.warning("Consider enabling proxy in config.yaml to bypass 403 errors")
                
            raise requests.RequestException("403 Forbidden")
        
        if response.status_code == 429:
            self.rate_limited = True
            raise requests.RequestException("429 Too Many Requests")
        
        self.rate_limited = False
        response.raise_for_status()
        
        if 'text/html' not in response.headers.get('Content-Type', ''):
            logger.warning(f"Non-HTML response from {url}: {response.headers.get('Content-Type')}")
            
        return response.text

    @retry_with_backoff()
    def make_request(self, url: str) -> Optional[str]:
        self._throttle_request()
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            return self._handle_response(response, url)
        except requests.RequestException as e:
            logger.warning(f"Request failed: {str(e)}")
            raise 