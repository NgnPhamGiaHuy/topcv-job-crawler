import sys
import logging

from src.utils import load_config, configure_logging, setup_signal_handlers, create_required_directories
from src.cli import parse_args
from src.core import CrawlerEngine


def main() -> int:
    args = parse_args()
    
    try:
        config = load_config(args.config)
        configure_logging(config)
        logger = logging.getLogger(__name__)
        
        setup_signal_handlers()
        create_required_directories(config)
        
        engine = CrawlerEngine(config)
        
        if args.once or not config['runtime']['daemon_mode']:
            logger.info("Running in one-time mode")
            engine.crawl_once(crawl_all_pages=args.full)
        else:
            logger.info("Running in continuous mode")
            engine.crawl_continuously()
            
        return 0
    except KeyboardInterrupt:
        print("\nCrawler stopped by user")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 