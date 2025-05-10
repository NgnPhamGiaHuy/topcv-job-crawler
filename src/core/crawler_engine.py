import time
import logging

from datetime import datetime
from typing import Dict, Any, NoReturn

from src.core.storage import JobStorage
from src.core.job_crawler import create_crawler
from src.utils.signal_handler import get_exit_flag


class CrawlerEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.site = config.get('site', 'topcv')
        self.logger = logging.getLogger(__name__)
        self.max_runtime = config['runtime']['max_runtime']
        self.sleep_interval = config['crawling']['sleep_interval']
        
    def crawl_once(self, crawl_all_pages: bool = False) -> int:
        self.logger.info(f"Starting crawl cycle at {datetime.now().isoformat()}")
        
        storage = JobStorage(self.config)
        crawler = create_crawler(self.site, self.config)

        if storage.is_first_run():
            self.logger.info("First run detected - will crawl all available pages")
            crawl_all_pages = True
        
        pages_to_scan = float('inf') if crawl_all_pages else self.config['crawling']['pages_to_scan']
        
        page = 1
        new_jobs_count = 0
        start_time = time.time()
        has_more_pages = True

        while (page <= pages_to_scan and has_more_pages and 
               not self._should_stop_crawling(start_time)):
            
            job_listings, more_pages = crawler.get_job_listings(page)
            has_more_pages = more_pages
            
            if not job_listings:
                self.logger.info(f"No jobs found on page {page}. Ending crawl cycle.")
                break
            
            for job in job_listings:
                if get_exit_flag():
                    break
                    
                detailed_job = crawler.get_job_details(job)
                
                if detailed_job and storage.save_job(detailed_job):
                    new_jobs_count += 1
            
            if has_more_pages:
                page += 1
                self._log_pagination_status(page, pages_to_scan, crawl_all_pages)
            else:
                self.logger.info(f"No more pages available after page {page}. Stopping crawl cycle.")
                break
        
        self.logger.info(f"Completed crawl cycle. Found {new_jobs_count} new jobs.")
        return new_jobs_count
        
    def _log_pagination_status(self, page: int, pages_to_scan: float, crawl_all_pages: bool) -> None:
        if crawl_all_pages:
            self.logger.info(f"Moving to page {page} (crawling all available pages)")
        elif page <= pages_to_scan:
            self.logger.info(f"Moving to page {page} of {int(pages_to_scan)}")
        else:
            self.logger.info(f"Reached configured page limit ({int(pages_to_scan)}). Stopping crawl cycle.")
    
    def _should_stop_crawling(self, start_time: float) -> bool:
        if get_exit_flag():
            self.logger.info("Received exit signal. Stopping crawl cycle.")
            return True
            
        if self.max_runtime > 0 and (time.time() - start_time) > self.max_runtime:
            self.logger.info(f"Maximum runtime of {self.max_runtime} seconds reached. Stopping crawl cycle.")
            return True
            
        return False

    def crawl_continuously(self) -> NoReturn:
        self.logger.info("Starting continuous crawler...")
        
        try:
            cycle_count = 1

            while not get_exit_flag():
                self.logger.info(f"Starting crawl cycle {cycle_count}")
                
                storage = JobStorage(self.config)
                is_first_run = storage.is_first_run()
                
                new_jobs = self.crawl_once(crawl_all_pages=is_first_run)
                
                self.logger.info(f"Crawl cycle {cycle_count} completed. Found {new_jobs} new jobs.")
                
                if is_first_run and new_jobs > 0:
                    self.logger.info("Completed initial full crawl. Future cycles will check for newest jobs only.")
                    
                self._sleep_between_cycles()
                cycle_count += 1
                
        except Exception as e:
            self.logger.error(f"Error in continuous crawling: {str(e)}")
            raise
        finally:
            self.logger.info("Continuous crawler stopped.")
            
    def _sleep_between_cycles(self) -> None:
        self.logger.info(f"Sleeping for {self.sleep_interval} seconds until next cycle...")
        
        sleep_start = time.time()
        
        while time.time() - sleep_start < self.sleep_interval:
            if get_exit_flag():
                break
                
            time.sleep(min(1, self.sleep_interval))


def crawl_once(config: Dict[str, Any], crawl_all_pages: bool = False) -> int:
    engine = CrawlerEngine(config)
    return engine.crawl_once(crawl_all_pages)

def crawl_continuously(config: Dict[str, Any]) -> NoReturn:
    engine = CrawlerEngine(config)
    engine.crawl_continuously() 