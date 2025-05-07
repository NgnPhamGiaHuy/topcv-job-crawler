import re
import logging
from typing import Optional
from datetime import datetime
import dateutil.parser

logger = logging.getLogger(__name__)


def parse_vietnamese_date(date_text: str) -> Optional[datetime]:
    """
    Parse Vietnamese date format to datetime object
    
    Args:
        date_text: Date text in Vietnamese format (e.g., "2 ngày trước")
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        date_text = date_text.lower().strip()
        
        # Handle "X ngày trước" (X days ago)
        if 'ngày trước' in date_text:
            days_ago = int(re.search(r'(\d+)', date_text).group(1))
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
        # Handle "X giờ trước" (X hours ago)
        if 'giờ trước' in date_text:
            hours_ago = int(re.search(r'(\d+)', date_text).group(1))
            return datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # Handle specific date format DD/MM/YYYY
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_text):
            return dateutil.parser.parse(date_text, dayfirst=True)
            
        return None
    except Exception as e:
        logger.error(f"Error parsing date '{date_text}': {str(e)}")
        return None 