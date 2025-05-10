import re
import logging
from typing import Dict, Any
from bs4 import Tag

logger = logging.getLogger(__name__)


def process_salary_info(content_element: Tag, salary_details: Dict[str, Any]) -> None:
    salary_list_items = content_element.select('li')

    if salary_list_items:
        salary_info_items = []

        for item in salary_list_items:
            item_text = item.get_text(strip=True)
            salary_info_items.append(item_text)
            
            if 'lương cứng' in item_text.lower() or 'lương cơ bản' in item_text.lower():
                salary_details['base_salary'] = item_text
            elif 'thu nhập' in item_text.lower() and 'kpi' in item_text.lower():
                salary_details['kpi_salary'] = item_text
            elif 'hoa hồng' in item_text.lower() or 'commission' in item_text.lower():
                salary_details['commission'] = item_text
        
        salary_details['items'] = salary_info_items


def process_general_salary(details: Dict[str, Any]) -> None:
    salary_text = details.get('salary', '').lower()
    
    if 'thỏa thuận' in salary_text or 'thoả thuận' in salary_text:
        details['salary_negotiable'] = True
    
    salary_range_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(triệu|tr|trieu|million|usd|vnd|đồng|dong)', salary_text, re.IGNORECASE)

    if salary_range_match:
        details['salary_min'] = float(salary_range_match.group(1).replace('.', ''))
        details['salary_max'] = float(salary_range_match.group(2).replace('.', ''))
        details['salary_currency'] = salary_range_match.group(3).lower()
    else:
        single_salary_match = re.search(r'(\d+(?:\.\d+)?)\s*(triệu|tr|trieu|million|usd|vnd|đồng|dong)', salary_text, re.IGNORECASE)

        if single_salary_match:
            amount = float(single_salary_match.group(1).replace('.', ''))
            details['salary_min'] = amount
            details['salary_max'] = amount
            details['salary_currency'] = single_salary_match.group(2).lower() 