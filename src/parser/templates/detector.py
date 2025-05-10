import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def detect_template_type(soup: BeautifulSoup) -> str:
    if soup.select_one('.premium-job-description__box'):
        return "premium"
    
    elif soup.select_one('.job-description__item'):
        return "standard"
        
    elif soup.select_one('.brand-job-detail'):
        return "brand"
        
    return "unknown"