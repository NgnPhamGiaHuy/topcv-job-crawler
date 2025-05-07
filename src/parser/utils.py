import re
import hashlib
import logging
from typing import Dict, Any, Optional
from bs4 import Tag

logger = logging.getLogger(__name__)


def extract_job_id(url: str) -> str:
    """
    Extract job ID from the URL or create a hash
    
    Args:
        url: Job detail page URL
        
    Returns:
        Job ID string
    """
    # Try to extract numeric ID from URL pattern like /viec-lam/.../123456.html
    match = re.search(r'/(\d+)\.html', url)
    if match:
        return match.group(1)
        
    # Alternative pattern: j123456 in the URL
    match = re.search(r'j(\d+)', url)
    if match:
        return match.group(1)
        
    # If cannot extract, create a hash of the URL
    return hashlib.md5(url.encode()).hexdigest()


def clean_list_formatting(text: str) -> str:
    """
    Clean bullet points and list formatting from text
    
    Args:
        text: Original text with potential bullet points
        
    Returns:
        Cleaned text with consistent formatting
    """
    if not text:
        return text
        
    # Replace common bullet characters with a standard delimiter
    # Handle various bullet point formats
    cleaned_text = text
    
    # Replace bullet points at the beginning of lines (•, -, *, etc.)
    cleaned_text = re.sub(r'(?m)^[\s]*[•\-\*\+\✓\✔\→\⇒\»\◆\◇\◈\○\●\◎\◉\▪\▫\□\■\★\☆]+\s*', '- ', cleaned_text)
    
    # Replace number bullet points at the beginning of lines (1., 2., i., ii., etc.)
    cleaned_text = re.sub(r'(?m)^[\s]*(?:\d+\.|\d+\)|\(\d+\)|[ivxIVX]+\.|\([ivxIVX]+\))\s*', '- ', cleaned_text)
    
    # Replace bullet points inside text after new lines
    cleaned_text = re.sub(r'\n[\s]*[•\-\*\+\✓\✔\→\⇒\»\◆\◇\◈\○\●\◎\◉\▪\▫\□\■\★\☆]+\s*', '\n- ', cleaned_text)
    
    # Replace number bullet points inside text after new lines
    cleaned_text = re.sub(r'\n[\s]*(?:\d+\.|\d+\)|\(\d+\)|[ivxIVX]+\.|\([ivxIVX]+\))\s*', '\n- ', cleaned_text)
    
    # Remove redundant new lines
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Fix spacing around standard bullet points
    cleaned_text = re.sub(r'●\s*', '- ', cleaned_text)
    
    return cleaned_text.strip()


def clean_location_text(location_text: str) -> str:
    """
    Clean location text by removing dashes and colons
    
    Args:
        location_text: Original location text
        
    Returns:
        Cleaned location text
    """
    # Replace pattern like "- Hà Nội: " with just "Hà Nội "
    cleaned_text = re.sub(r'^\s*-\s*([^:]+):\s*', r'\1 ', location_text)
    # Also handle cases with multiple locations
    cleaned_text = re.sub(r'\n\s*-\s*([^:]+):\s*', r'\n\1 ', cleaned_text)
    return cleaned_text.strip()


def parse_html_content(content: Tag) -> str:
    """
    Parse HTML content and preserve list formatting properly
    
    Args:
        content: HTML content Tag
        
    Returns:
        Formatted text with line breaks for list items
    """
    if not content:
        return ""
        
    # Extract text from individual elements to preserve structure
    result = []
    
    # Process list items specially
    list_items = content.select('li')
    if list_items:
        for item in list_items:
            item_text = item.get_text(strip=True)
            if item_text:
                result.append(f"- {item_text}")
    else:
        # If no list items, just get the text
        result.append(content.get_text(strip=True))
        
    return "\n".join(result)


def find_content_after_heading(heading_tag: Tag) -> Optional[Tag]:
    """
    Find the content that follows a heading tag
    
    Args:
        heading_tag: The heading Tag object
        
    Returns:
        Tag containing the content or None if not found
    """
    # First try siblings
    next_siblings = list(heading_tag.next_siblings)
    for sibling in next_siblings:
        if sibling.name and sibling.get_text(strip=True):
            return sibling
    
    # If no suitable sibling, try parent's next sibling
    parent = heading_tag.parent
    if parent:
        parent_siblings = list(parent.next_siblings)
        for sibling in parent_siblings:
            if sibling.name and sibling.get_text(strip=True):
                return sibling
    
    return None 