import logging
from typing import Dict, List, Any

from src.parser.details_parser import extract_job_details
from src.parser.listing_parser import extract_job_listings
from src.core.interfaces import ParserInterface

logger = logging.getLogger(__name__)


class TopCVParser(ParserInterface):
    def extract_job_listings(self, html_content: str) -> List[Dict[str, Any]]:
        return extract_job_listings(html_content)
    
    def extract_job_details(self, html_content: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        return extract_job_details(html_content, job_data)


def create_parser(site_name: str) -> ParserInterface:
    parsers = {
        'topcv': TopCVParser(),
    }
    
    if site_name.lower() in parsers:
        return parsers[site_name.lower()]
    else:
        raise ValueError(f"Unsupported site: {site_name}") 