import re
import logging
from typing import Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup, Tag

from src.parser.utils import clean_list_formatting, clean_location_text
from src.parser.utils import parse_html_content, find_content_after_heading
from src.parser.salary_parser import process_salary_info, process_general_salary

logger = logging.getLogger(__name__)


def extract_job_details(html_content: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract detailed job information from job detail page
    
    Args:
        html_content: HTML content of the job detail page
        job_data: Existing job data from the listing page
        
    Returns:
        Dictionary with complete job data
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Create a copy of the job data to add details
        details = job_data.copy()
        
        # Initialize detailed salary information
        details['salary_min'] = None
        details['salary_max'] = None
        details['salary_currency'] = None
        details['salary_negotiable'] = False
        # We'll add salary_details only if there's actual data
        
        # Detect template type
        template_type = detect_template_type(soup)
        logger.info(f"Detected template type: {template_type}")
        
        # Process the job details based on template type
        if template_type == "premium":
            details = parse_premium_template(soup, details)
        elif template_type == "standard":
            details = parse_standard_template(soup, details)
        elif template_type == "brand":
            details = parse_brand_template(soup, details)
        else:
            # Try a fallback approach for unknown templates
            details = parse_fallback_template(soup, details)
        
        # Remove salary_details if it's empty
        if 'salary_details' in details and not details['salary_details']:
            del details['salary_details']
            
        # Clean work location format if present
        if 'work_location' in details and details['work_location']:
            details['work_location'] = clean_location_text(details['work_location'])
        
        # Clean bullet points and list formatting from text fields
        for field in ['description', 'requirements', 'benefits']:
            if field in details and details[field]:
                details[field] = clean_list_formatting(details[field])
            
        return details
    except Exception as e:
        logger.error(f"Error extracting job details: {str(e)}")
        return job_data


def detect_template_type(soup: BeautifulSoup) -> str:
    """
    Detect the template type used for the job detail page
    
    Args:
        soup: BeautifulSoup object of the job detail page
        
    Returns:
        Template type as string ("premium", "standard", "brand", or "unknown")
    """
    # Check for premium template
    if soup.select_one('.premium-job-description__box'):
        return "premium"
    
    # Check for standard template with job-description__item
    elif soup.select_one('.job-description__item'):
        return "standard"
        
    # Check for brand template
    elif soup.select_one('.brand-job-detail'):
        return "brand"
        
    # Default to unknown
    return "unknown"


def parse_premium_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse job details from premium template
    
    Args:
        soup: BeautifulSoup object of the job detail page
        details: Job details dictionary to update
        
    Returns:
        Updated job details dictionary
    """
    try:
        # Get job description sections
        job_description_boxes = soup.select('.premium-job-description__box')
        
        # Dictionary to collect salary details
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
                
                # Use HTML parsing to better preserve structure
                content_text = parse_html_content(content)
                
                # Extract different sections based on heading
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
                    
                    # Process salary information
                    process_salary_info(content, salary_details)
                    
            except Exception as e:
                logger.error(f"Error parsing premium job description section: {str(e)}")
                continue
        
        # Add salary details to the main details if we collected any
        if salary_details:
            details['salary_details'] = salary_details
        
        # Extract application deadline from the detail page if available
        deadline_element = soup.select_one('.job-detail__information-detail--actions-label')
        if deadline_element:
            deadline_text = deadline_element.get_text(strip=True)
            match = re.search(r'Hạn nộp hồ sơ: (\d{2}/\d{2}/\d{4})', deadline_text)
            if match:
                details['application_deadline'] = match.group(1)
        
        # Process salary text
        process_general_salary(details)
        
        # Update the crawled_at timestamp to the latest
        details['crawled_at'] = datetime.now().isoformat()
        
        return details
    except Exception as e:
        logger.error(f"Error parsing premium template: {str(e)}")
        return details


def parse_standard_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse job details from standard template
    
    Args:
        soup: BeautifulSoup object of the job detail page
        details: Job details dictionary to update
        
    Returns:
        Updated job details dictionary
    """
    try:
        # Get job description sections
        job_description_items = soup.select('.job-description__item')
        
        # Dictionary to collect salary details
        salary_details = {}
        
        # Check for salary in detail page
        # First check for the specific salary section
        salary_section = None
        for item in job_description_items:
            heading = item.select_one('h3')
            if heading and ('thu nhập' in heading.get_text(strip=True).lower() or 'lương' in heading.get_text(strip=True).lower()):
                salary_section = item
                break
        
        if salary_section:
            # Extract salary details from the specific section
            content = salary_section.select_one('.job-description__item--content')
            if content:
                # Use HTML parsing to better preserve structure
                salary_text = parse_html_content(content)
                salary_details['full_text'] = salary_text
                
                # Process salary information
                process_salary_info(content, salary_details)
        
        # Process other job description sections
        for item in job_description_items:
            try:
                heading = item.select_one('h3')
                if not heading:
                    continue
                    
                heading_text = heading.get_text(strip=True).lower()
                content = item.select_one('.job-description__item--content')
                
                if not content:
                    continue
                
                # Use HTML parsing to better preserve structure
                content_text = parse_html_content(content)
                    
                # Extract different sections based on heading
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
        
        # Add salary details to the main details if we collected any
        if salary_details:
            details['salary_details'] = salary_details
        
        # Extract application deadline from the detail page if available
        deadline_element = soup.select_one('.job-detail__information-detail--actions-label')
        if deadline_element:
            deadline_text = deadline_element.get_text(strip=True)
            match = re.search(r'Hạn nộp hồ sơ: (\d{2}/\d{2}/\d{4})', deadline_text)
            if match:
                details['application_deadline'] = match.group(1)
        
        # Process salary text
        process_general_salary(details)
        
        # Update the crawled_at timestamp to the latest
        details['crawled_at'] = datetime.now().isoformat()
        
        return details
    except Exception as e:
        logger.error(f"Error parsing standard template: {str(e)}")
        return details


def parse_brand_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse job details from brand template
    
    Args:
        soup: BeautifulSoup object of the job detail page
        details: Job details dictionary to update
        
    Returns:
        Updated job details dictionary
    """
    try:
        # Look for brand-job-detail sections
        job_sections = soup.select('.brand-job-detail-section')
        if not job_sections:
            job_sections = soup.select('.box-info-job')
        
        # Dictionary to collect salary details
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
                
                # Use HTML parsing to better preserve structure
                content_text = parse_html_content(content)
                
                # Extract different sections based on heading
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
                    
                    # Process salary information
                    process_salary_info(content, salary_details)
                
            except Exception as e:
                logger.error(f"Error parsing brand job section: {str(e)}")
                continue
        
        # Add salary details to the main details if we collected any
        if salary_details:
            details['salary_details'] = salary_details
            
        # Extract deadline if available
        deadline_elements = soup.select('.detail-deadline, .deadline-text, .job-deadline')
        for element in deadline_elements:
            deadline_text = element.get_text(strip=True)
            match = re.search(r'(\d{2}/\d{2}/\d{4})', deadline_text)
            if match:
                details['application_deadline'] = match.group(1)
                break
        
        # Process salary text
        process_general_salary(details)
        
        # Update the crawled_at timestamp to the latest
        details['crawled_at'] = datetime.now().isoformat()
        
        return details
    except Exception as e:
        logger.error(f"Error parsing brand template: {str(e)}")
        return details


def parse_fallback_template(soup: BeautifulSoup, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback parser for unknown templates - tries to extract data using common patterns
    
    Args:
        soup: BeautifulSoup object of the job detail page
        details: Job details dictionary to update
        
    Returns:
        Updated job details dictionary
    """
    try:
        # Look for any heading patterns that might indicate job sections
        for heading_tag in ['h1', 'h2', 'h3', 'h4']:
            headings = soup.select(f'{heading_tag}')
            
            # Dictionary to collect salary details
            salary_details = {}
            
            for heading in headings:
                heading_text = heading.get_text(strip=True).lower()
                
                # Try to find the content that follows this heading
                content = find_content_after_heading(heading)
                
                if content:
                    # Use HTML parsing to better preserve structure
                    content_text = parse_html_content(content)
                    
                    # Extract different sections based on heading text patterns
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
                        
                        # Process salary information
                        process_salary_info(content, salary_details)
        
        # Add salary details to the main details if we collected any
        if salary_details:
            details['salary_details'] = salary_details
            
        # Try to find deadline
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
        
        # Process salary text
        process_general_salary(details)
            
        # Update the crawled_at timestamp to the latest
        details['crawled_at'] = datetime.now().isoformat()
        
        return details
    except Exception as e:
        logger.error(f"Error parsing fallback template: {str(e)}")
        return details 