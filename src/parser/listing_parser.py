import re
import logging

from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any

from src.parser.html_tools import extract_job_id

logger = logging.getLogger(__name__)


def extract_job_listings(html_content: str) -> List[Dict[str, Any]]:
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        job_items = soup.select('.job-item-search-result')
        
        if not job_items:
            logger.warning("No job items found in the page")
            return []
            
        jobs = []
        for job_item in job_items:
            try:
                title_link = job_item.select_one('.title a')

                if not title_link:
                    continue
                    
                job_title = title_link.get_text(strip=True)
                job_url = title_link.get('href', '')
                
                job_id = extract_job_id(job_url)
                
                company_element = job_item.select_one('.company-name')
                company_name = company_element.get_text(strip=True) if company_element else ''
                
                location_element = job_item.select_one('.address')
                location = location_element.get_text(strip=True) if location_element else ''
                
                salary_element = job_item.select_one('.title-salary')
                salary = salary_element.get_text(strip=True) if salary_element else 'Thỏa thuận'

                salary = re.sub(r'[\r\n\t]', ' ', salary)
                salary = re.sub(r'\s+', ' ', salary).strip()
                salary = re.sub(r'^[^a-zA-Z0-9]+', '', salary).strip()
                
                date_element = job_item.select_one('.label-update')
                posted_date = ""
                last_updated = ""
                
                if date_element:
                    posted_date = date_element.get_text(strip=True)
                    posted_date = re.sub(r'^Đăng', '', posted_date).strip()
                    
                    if date_element.has_attr('data-original-title'):
                        last_updated = date_element['data-original-title'].strip()
                
                exp_element = job_item.select_one('.exp')
                experience = exp_element.get_text(strip=True) if exp_element else ''
                
                job = {
                    'id': job_id,
                    'title': job_title,
                    'company_name': company_name,
                    'location': location,
                    'salary': salary,
                    'experience': experience,
                    'posted_date': posted_date,
                    'crawled_at': datetime.now().isoformat(),
                }
                
                if last_updated:
                    job['last_updated'] = last_updated

                if job_url:
                    job['url'] = job_url

                jobs.append(job)
            except Exception as e:
                logger.error(f"Error parsing job item: {str(e)}")
                continue
                
        return jobs
    except Exception as e:
        logger.error(f"Error extracting job listings: {str(e)}")
        return [] 