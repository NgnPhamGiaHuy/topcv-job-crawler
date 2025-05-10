from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple


class CrawlerInterface(ABC):
    @abstractmethod
    def get_job_listings(self, page: int = 1) -> Tuple[List[Dict[str, Any]], bool]:
        pass
    
    @abstractmethod
    def get_job_details(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass


class ParserInterface(ABC):
    @abstractmethod
    def extract_job_listings(self, html_content: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def extract_job_details(self, html_content: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class PaginationInterface(ABC):
    @abstractmethod
    def has_more_pages(self, html_content: str, current_page: int) -> bool:
        pass


class StorageInterface(ABC):
    @abstractmethod
    def save_job(self, job: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def job_exists(self, job_id: str) -> bool:
        pass