import re
import logging

from bs4 import BeautifulSoup
from typing import Dict, Any

from src.parser.html_tools import parse_html_content, find_content_after_heading
from src.parser.salary_parser import process_salary_info
from src.parser.templates.common import finalize_job_details

logger = logging.getLogger(__name__)


def parse_fallback_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    try:
        salary_details = {}
        
        for heading_tag in ['h1', 'h2', 'h3', 'h4']:
            headings = soup.select(f'{heading_tag}')
            
            for heading in headings:
                heading_text = heading.get_text(strip=True).lower()
                
                content = find_content_after_heading(heading)
                
                if content:
                    content_text = parse_html_content(content)
                    
                    if 'mô tả' in heading_text or 'nhiệm vụ' in heading_text:
                        details['description'] = content_text
                    elif 'yêu cầu' in heading_text:
                        details['requirements'] = content_text
                    elif 'quyền lợi' in heading_text or 'phúc lợi' in heading_text or 'chế độ' in heading_text:
                        details['benefits'] = content_text
                    elif 'địa điểm' in heading_text or 'nơi làm việc' in heading_text:
                        details['work_location'] = content_text
                    elif 'lương' in heading_text or 'thu nhập' in heading_text:
                        salary_details['full_text'] = content_text
                        
                        process_salary_info(content, salary_details)
        
        deadline_pattern = re.compile(r'hạn nộp|deadline', re.IGNORECASE)
        deadline_elements = soup.find_all(text=deadline_pattern)
        
        for element in deadline_elements:
            parent = element.parent

            if parent:
                deadline_text = parent.get_text(strip=True)
                match = re.search(r'(\d{2}/\d{2}/\d{4})', deadline_text)

                if match:
                    details['application_deadline'] = match.group(1)
                    break
        
        return finalize_job_details(soup, details, salary_details)
    except Exception as e:
        logger.error(f"Error parsing fallback template: {str(e)}")
        return details 