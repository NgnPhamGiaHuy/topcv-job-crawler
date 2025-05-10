import re
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any

from src.parser.html_tools import parse_html_content
from src.parser.salary_parser import process_salary_info
from src.parser.templates.common import finalize_job_details

logger = logging.getLogger(__name__)


def parse_brand_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    try:
        job_sections = soup.select('.brand-job-detail-section')

        if not job_sections:
            job_sections = soup.select('.box-info-job')
        
        salary_details = {}
        
        for section in job_sections:
            try:
                heading = section.select_one('h2, h3, .title')

                if not heading:
                    continue
                
                heading_text = heading.get_text(strip=True).lower()
                content = section.select_one('.content, .desc, .detail')
                
                if not content:
                    continue
                
                content_text = parse_html_content(content)
                
                if 'mô tả' in heading_text:
                    details['description'] = content_text
                elif 'yêu cầu' in heading_text:
                    details['requirements'] = content_text
                elif 'quyền lợi' in heading_text or 'phúc lợi' in heading_text:
                    details['benefits'] = content_text
                elif 'địa điểm' in heading_text:
                    details['work_location'] = content_text
                elif 'lương' in heading_text or 'thu nhập' in heading_text:
                    salary_details['full_text'] = content_text
                    
                    process_salary_info(content, salary_details)
                
            except Exception as e:
                logger.error(f"Error parsing brand job section: {str(e)}")
                continue
        
        deadline_elements = soup.select('.detail-deadline, .deadline-text, .job-deadline')

        for element in deadline_elements:
            deadline_text = element.get_text(strip=True)
            match = re.search(r'(\d{2}/\d{2}/\d{4})', deadline_text)

            if match:
                details['application_deadline'] = match.group(1)
                break
        
        return finalize_job_details(soup, details, salary_details)
    except Exception as e:
        logger.error(f"Error parsing brand template: {str(e)}")
        return details 