import logging

from bs4 import BeautifulSoup
from typing import Dict, Any

from src.parser.templates import (
    detect_template_type,
    parse_premium_template,
    parse_standard_template, 
    parse_brand_template,
    parse_fallback_template
)
from src.parser.html_tools import clean_list_formatting, clean_location_text

logger = logging.getLogger(__name__)


def extract_job_details(html_content: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        details = job_data.copy()
        
        details['salary_min'] = None
        details['salary_max'] = None
        details['salary_currency'] = None
        details['salary_negotiable'] = False
        
        template_type = detect_template_type(soup)
        logger.info(f"Detected template type: {template_type}")
        
        if template_type == "premium":
            details = parse_premium_template(soup, details)
        elif template_type == "standard":
            details = parse_standard_template(soup, details)
        elif template_type == "brand":
            details = parse_brand_template(soup, details)
        else:
            details = parse_fallback_template(soup, details)
        
        if 'salary_details' in details and not details['salary_details']:
            del details['salary_details']
            
        if 'work_location' in details and details['work_location']:
            details['work_location'] = clean_location_text(details['work_location'])
        
        for field in ['description', 'requirements', 'benefits']:
            if field in details and details[field]:
                details[field] = clean_list_formatting(details[field])
            
        return details
    except Exception as e:
        logger.error(f"Error extracting job details: {str(e)}")
        return job_data 