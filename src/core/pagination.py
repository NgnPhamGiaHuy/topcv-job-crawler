import re
import logging

from bs4 import BeautifulSoup
from src.core.interfaces import PaginationInterface

logger = logging.getLogger(__name__)


class PaginationParser(PaginationInterface):
    @staticmethod
    def has_more_pages(html_content: str, current_page: int) -> bool:
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            if soup.select_one('a[rel="next"]'):
                logger.debug("Found next page link with rel='next' attribute")
                return True
            
            for link in soup.select('a[data-href*="page="]'):
                href = link.get('data-href', '')

                if 'page=' in href:
                    try:
                        page_param = re.search(r'page=(\d+)', href)

                        if page_param and int(page_param.group(1)) > current_page:
                            logger.debug(f"Found link with page parameter: {page_param.group(1)}")
                            return True
                    except:
                        pass
            
            paginate_text = soup.select_one('#job-listing-paginate-text')

            if paginate_text:
                text = paginate_text.get_text(strip=True)
                match = re.search(r'(\d+)\s*/\s*(\d+)', text)

                if match:
                    current = int(match.group(1))
                    total = int(match.group(2))

                    if current < total:
                        logger.debug(f"Found pagination text: page {current} of {total}")
                        return True
            
            if soup.select_one('.box-pagination'):
                pagination_selectors = [
                    '.pagination a',
                    'ul.pagination li a',
                    'a[aria-label*="Next"]',
                    'a:-soup-contains("›")'
                ]
                
                for selector in pagination_selectors:
                    links = soup.select(selector)

                    for link in links:
                        if link.get('rel') == ['next'] or '›' in link.get_text():
                            logger.debug("Found next page indicator in pagination")
                            return True
            
            job_items = soup.select('.job-item-search-result')

            if len(job_items) >= 20:
                logger.debug(f"Found {len(job_items)} job items, assuming more pages exist")
                return True
            
            logger.info("No more pages detected")
            return False
        except Exception as e:
            logger.error(f"Error checking for more pages: {str(e)}")
            return False


def create_pagination_parser(site_name: str) -> PaginationInterface:
    parsers = {
        'topcv': PaginationParser(),
    }
    
    if site_name.lower() in parsers:
        return parsers[site_name.lower()]
    else:
        raise ValueError(f"Unsupported site for pagination parsing: {site_name}") 