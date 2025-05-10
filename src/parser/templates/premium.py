import logging

from bs4 import BeautifulSoup
from typing import Dict, Any

from src.parser.html_tools import parse_html_content
from src.parser.salary_parser import process_salary_info
from src.parser.templates.common import finalize_job_details

logger = logging.getLogger(__name__)


def parse_premium_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    try:
        job_description_boxes = soup.select('.premium-job-description__box')
        
        salary_details = {}
        
        for box in job_description_boxes:
            try:
                heading = box.select_one('.premium-job-description__box--title')

                if not heading:
                    continue
                    
                heading_text = heading.get_text(strip=True).lower()
                content = box.select_one('.premium-job-description__box--content')
                
                if not content:
                    continue
                
                content_text = parse_html_content(content)
                
                if 'mô tả công việc' in heading_text:
                    details['description'] = content_text
                elif 'yêu cầu' in heading_text:
                    details['requirements'] = content_text
                elif 'quyền lợi' in heading_text:
                    details['benefits'] = content_text
                elif 'địa điểm' in heading_text:
                    details['work_location'] = content_text
                elif 'thu nhập' in heading_text or 'lương' in heading_text:
                    salary_details['full_text'] = content_text
                    
                    process_salary_info(content, salary_details)
                    
            except Exception as e:
                logger.error(f"Error parsing premium job description section: {str(e)}")
                continue
        
        return finalize_job_details(soup, details, salary_details)
    except Exception as e:
        logger.error(f"Error parsing premium template: {str(e)}")
        return details 