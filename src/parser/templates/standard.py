import logging

from bs4 import BeautifulSoup
from typing import Dict, Any

from src.parser.html_tools import parse_html_content
from src.parser.salary_parser import process_salary_info
from src.parser.templates.common import finalize_job_details

logger = logging.getLogger(__name__)


def parse_standard_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    try:
        job_description_items = soup.select('.job-description__item')
        
        salary_details = {}
        
        salary_section = None

        for item in job_description_items:
            heading = item.select_one('h3')

            if heading and ('thu nhập' in heading.get_text(strip=True).lower() or 'lương' in heading.get_text(strip=True).lower()):
                salary_section = item
                break
        
        if salary_section:
            content = salary_section.select_one('.job-description__item--content')

            if content:
                salary_text = parse_html_content(content)
                salary_details['full_text'] = salary_text
                
                process_salary_info(content, salary_details)
        
        for item in job_description_items:
            try:
                heading = item.select_one('h3')

                if not heading:
                    continue
                    
                heading_text = heading.get_text(strip=True).lower()
                content = item.select_one('.job-description__item--content')
                
                if not content:
                    continue
                
                content_text = parse_html_content(content)
                    
                if 'mô tả công việc' in heading_text:
                    details['description'] = content_text
                elif 'yêu cầu' in heading_text:
                    details['requirements'] = content_text
                elif 'quyền lợi' in heading_text:
                    details['benefits'] = content_text
                elif 'địa điểm làm việc' in heading_text:
                    details['work_location'] = content_text
                elif 'hạn nộp' in heading_text:
                    details['application_deadline'] = content_text
                    
            except Exception as e:
                logger.error(f"Error parsing standard job description section: {str(e)}")
                continue
        
        return finalize_job_details(soup, details, salary_details)
    except Exception as e:
        logger.error(f"Error parsing standard template: {str(e)}")
        return details 