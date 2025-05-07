import logging
from typing import Dict, List, Any

from src.parser.listing_parser import extract_job_listings
from src.parser.details_parser import extract_job_details
from src.parser.date_parser import parse_vietnamese_date

logger = logging.getLogger(__name__)


class TopCVParser:
    """Parser for TopCV job listings and details"""
    
    @staticmethod
    def extract_job_listings(html_content: str) -> List[Dict[str, Any]]:
        """
        Extract job listings from the search results page
        
        Args:
            html_content: HTML content of the search results page
            
        Returns:
            List of dictionaries containing job data
        """
        return extract_job_listings(html_content)
    
    @staticmethod
    def extract_job_details(html_content: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed job information from job detail page
        
        Args:
            html_content: HTML content of the job detail page
            job_data: Existing job data from the listing page
            
        Returns:
            Dictionary with complete job data
        """
        return extract_job_details(html_content, job_data)
    
    @staticmethod
    def parse_vietnamese_date(date_text: str):
        """
        Parse Vietnamese date format to datetime object
        
        Args:
            date_text: Date text in Vietnamese format (e.g., "2 ngày trước")
            
        Returns:
            Datetime object or None if parsing fails
        """
        return parse_vietnamese_date(date_text) 