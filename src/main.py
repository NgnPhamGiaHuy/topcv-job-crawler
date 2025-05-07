#!/usr/bin/env python3

import os
import time
import logging
import argparse
import sys
import signal
from datetime import datetime
from typing import Dict, Any, NoReturn

from src.config import load_config, configure_logging
from src.crawler import TopCVCrawler
from src.storage import JobStorage

# Global variables for handling graceful shutdown
should_exit = False

def signal_handler(signum, frame) -> None:
    """
    Handle signals like SIGTERM and SIGINT to exit gracefully
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global should_exit
    print(f"\nReceived signal {signum}. Exiting gracefully...")
    should_exit = True

def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination

def crawl_once(config: Dict[str, Any], crawl_all_pages: bool = False) -> int:
    """
    Run one complete crawl cycle
    
    Args:
        config: Configuration dictionary
        crawl_all_pages: Whether to crawl all available pages instead of just configured amount
        
    Returns:
        Number of new jobs found
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting crawl cycle at {datetime.now().isoformat()}")
    
    # Initialize crawler and storage
    crawler = TopCVCrawler(config)
    storage = JobStorage(config)
    
    # Check if this is the first run
    if storage.is_first_run():
        logger.info("First run detected - will crawl all available pages")
        crawl_all_pages = True
    
    # Get the number of pages to scan from config
    pages_to_scan = float('inf') if crawl_all_pages else config['crawling']['pages_to_scan']
    
    new_jobs_count = 0
    page = 1
    
    # Track start time for runtime limit
    start_time = time.time()
    max_runtime = config['runtime']['max_runtime']
    
    has_more_pages = True
    while page <= pages_to_scan and has_more_pages:
        # Check if we should exit gracefully
        if should_exit:
            logger.info("Received exit signal. Stopping crawl cycle.")
            break
            
        # Check if we've exceeded the maximum runtime
        if max_runtime > 0 and (time.time() - start_time) > max_runtime:
            logger.info(f"Maximum runtime of {max_runtime} seconds reached. Stopping crawl cycle.")
            break
        
        # Get job listings for the current page
        job_listings, more_pages = crawler.get_job_listings(page)
        has_more_pages = more_pages
        
        # If no jobs on this page, we're done
        if not job_listings:
            logger.info(f"No jobs found on page {page}. Ending crawl cycle.")
            break
        
        for job in job_listings:
            # Exit if we've received a signal to quit
            if should_exit:
                break
                
            # Fetch detailed job information
            detailed_job = crawler.get_job_details(job)
            
            if detailed_job:
                # Save the job (storage handles deduplication)
                if storage.save_job(detailed_job):
                    new_jobs_count += 1
        
        # Move to next page if there are more jobs and we haven't reached the limit
        if has_more_pages:
            page += 1
            # If we're looking for all new job listings (first run), keep going
            if crawl_all_pages:
                logger.info(f"Moving to page {page} (crawling all available pages)")
            elif page <= pages_to_scan:
                logger.info(f"Moving to page {page} of {pages_to_scan}")
            else:
                logger.info(f"Reached configured page limit ({pages_to_scan}). Stopping crawl cycle.")
                break
        else:
            logger.info(f"No more pages available after page {page-1}. Stopping crawl cycle.")
            break
    
    logger.info(f"Completed crawl cycle. Found {new_jobs_count} new jobs.")
    return new_jobs_count

def crawl_continuously(config: Dict[str, Any]) -> NoReturn:
    """
    Run the crawler in an infinite loop with sleep between cycles
    
    Args:
        config: Configuration dictionary
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting continuous crawler...")
    
    sleep_interval = config['crawling']['sleep_interval']
    
    try:
        cycle_count = 1
        while not should_exit:
            logger.info(f"Starting crawl cycle {cycle_count}")
            
            # First check if this is the first run
            storage = JobStorage(config)
            is_first_run = storage.is_first_run()
            
            # Run one crawl cycle - if first run, crawl all pages
            new_jobs = crawl_once(config, crawl_all_pages=is_first_run)
            
            logger.info(f"Crawl cycle {cycle_count} completed. Found {new_jobs} new jobs.")
            
            # Only use shorter sleep interval after initial full crawl is complete
            actual_sleep_interval = sleep_interval
            if is_first_run and new_jobs > 0:
                logger.info("Completed initial full crawl. Future cycles will check for newest jobs only.")
                
            logger.info(f"Sleeping for {actual_sleep_interval} seconds until next cycle...")
            
            # Sleep until next cycle or until interrupted
            sleep_start = time.time()
            while time.time() - sleep_start < actual_sleep_interval:
                if should_exit:
                    break
                time.sleep(min(1, actual_sleep_interval))  # Check for exit signal more frequently
                
            cycle_count += 1
    except Exception as e:
        logger.error(f"Error in continuous crawling: {str(e)}")
        raise
    finally:
        logger.info("Continuous crawler stopped.")

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='TopCV.vn Job Crawler')
    
    parser.add_argument('--config', '-c', 
                      default='config.yaml',
                      help='Path to configuration file')
                      
    parser.add_argument('--once', '-o',
                      action='store_true',
                      help='Run once and exit (for development/testing)')
                      
    parser.add_argument('--full', '-f',
                      action='store_true',
                      help='Crawl all available pages, not just the configured number')
                      
    return parser.parse_args()

def main() -> int:
    """
    Main entry point
    
    Returns:
        Exit code
    """
    # Parse command-line arguments
    args = parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Configure logging
        configure_logging(config)
        logger = logging.getLogger(__name__)
        
        # Set up signal handlers
        setup_signal_handlers()
        
        # Create required directories
        os.makedirs(os.path.dirname(config['output']['jobs_json']), exist_ok=True)
        os.makedirs(os.path.dirname(config['output']['jobs_csv']), exist_ok=True)
        os.makedirs(os.path.dirname(config['logging']['log_file']), exist_ok=True)
        
        # Run in appropriate mode
        if args.once or not config['runtime']['daemon_mode']:
            logger.info("Running in one-time mode")
            crawl_once(config, crawl_all_pages=args.full)
        else:
            logger.info("Running in continuous mode")
            crawl_continuously(config)
            
        return 0
    except KeyboardInterrupt:
        print("\nCrawler stopped by user")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 