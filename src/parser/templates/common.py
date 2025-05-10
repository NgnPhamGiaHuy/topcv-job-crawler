import re
import logging

from bs4 import BeautifulSoup
from typing import Dict, Any
from datetime import datetime

from src.parser.salary_parser import process_general_salary

logger = logging.getLogger(__name__)


def finalize_job_details(soup: BeautifulSoup, details: Dict[str, Any], salary_details: Dict[str, Any]) -> Dict[str, Any]:
    if salary_details:
        details['salary_details'] = salary_details
    
    deadline_element = soup.select_one('.job-detail__information-detail--actions-label')

    if deadline_element:
        deadline_text = deadline_element.get_text(strip=True)

        match = re.search(r'Hạn nộp hồ sơ: (\d{2}/\d{2}/\d{4})', deadline_text)

        if match:
            details['application_deadline'] = match.group(1)
    
    process_general_salary(details)
    
    details['crawled_at'] = datetime.now().isoformat()
    
    return details 