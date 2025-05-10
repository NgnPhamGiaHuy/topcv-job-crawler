import re
import logging
import hashlib

from bs4 import Tag
from typing import Optional

logger = logging.getLogger(__name__)


def extract_job_id(url: str) -> str:
    match = re.search(r'/(\d+)\.html', url)

    if match:
        return match.group(1)

    match = re.search(r'j(\d+)', url)

    if match:
        return match.group(1)

    return hashlib.md5(url.encode()).hexdigest()


def clean_list_formatting(text: str) -> str:
    if not text:
        return text

    bullet_patterns = [
        r'(?m)^[\s]*[•\-\*\+\✓\✔\→\⇒\»\◆\◇\◈\○\●\◎\◉\▪\▫\□\■\★\☆]+\s*',
        r'(?m)^[\s]*(?:\d+\.|\d+\)|\(\d+\)|[ivxIVX]+\.|\([ivxIVX]+\))\s*',
        r'\n[\s]*[•\-\*\+\✓\✔\→\⇒\»\◆\◇\◈\○\●\◎\◉\▪\▫\□\■\★\☆]+\s*',
        r'\n[\s]*(?:\d+\.|\d+\)|\(\d+\)|[ivxIVX]+\.|\([ivxIVX]+\))\s*',
    ]
    
    cleaned_text = text
    
    for pattern in bullet_patterns:
        cleaned_text = re.sub(pattern, '- ', cleaned_text)
    
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    cleaned_text = re.sub(r'●\s*', '- ', cleaned_text)

    return cleaned_text.strip()


def clean_location_text(location_text: str) -> str:
    if not location_text:
        return ""
        
    cleaned_text = re.sub(r'^\s*-\s*([^:]+):\s*', r'\1 ', location_text)
    cleaned_text = re.sub(r'\n\s*-\s*([^:]+):\s*', r'\n\1 ', cleaned_text)

    return cleaned_text.strip()


def parse_html_content(content: Tag) -> str:
    if not content:
        return ""

    result = []
    list_items = content.select('li')

    if list_items:
        for item in list_items:
            item_text = item.get_text(strip=True)

            if item_text:
                result.append(f"- {item_text}")
    else:
        result.append(content.get_text(strip=True))

    return "\n".join(result)


def find_content_after_heading(heading_tag: Tag) -> Optional[Tag]:
    for sibling in heading_tag.next_siblings:
        if sibling.name and sibling.get_text(strip=True):
            return sibling

    parent = heading_tag.parent

    if parent:
        for sibling in parent.next_siblings:
            if sibling.name and sibling.get_text(strip=True):
                return sibling

    return None