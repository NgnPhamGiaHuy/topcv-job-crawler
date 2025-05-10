import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='TopCV.vn Job Crawler')
    
    parser.add_argument('--config', '-c', default='config.yaml', help='Path to configuration file')
    parser.add_argument('--once', '-o', action='store_true', help='Run once and exit (for development/testing)')
    parser.add_argument('--full', '-f', action='store_true', help='Crawl all available pages, not just the configured number')
                      
    return parser.parse_args() 