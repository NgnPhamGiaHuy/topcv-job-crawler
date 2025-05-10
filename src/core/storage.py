import os
import json
import pickle
import logging
import pandas as pd

from typing import Dict, List, Set, Any
from src.core.interfaces import StorageInterface

logger = logging.getLogger(__name__)


class JobStorage(StorageInterface):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jobs_csv_path = config['output']['jobs_csv'] 
        self.jobs_json_path = config['output']['jobs_json']
        self.job_cache_file = config['output']['job_cache_file']
        
        self.expected_fields = [
            'id', 'title', 'company_name', 'location', 'salary', 'experience',
            'posted_date', 'crawled_at', 'url', 'salary_min', 'salary_max',
            'salary_currency', 'salary_negotiable', 'description', 'requirements',
            'benefits', 'work_location', 'application_deadline'
        ]
        
        self._create_output_directories()
        self.job_ids = self._load_job_id_cache()
        
    def _create_output_directories(self) -> None:
        os.makedirs(os.path.dirname(self.jobs_json_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.jobs_csv_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.job_cache_file), exist_ok=True)
        
    def is_first_run(self) -> bool:
        return len(self.job_ids) == 0
        
    def job_exists(self, job_id: str) -> bool:
        return job_id in self.job_ids
        
    def save_job(self, job: Dict[str, Any]) -> bool:
        try:
            job_id = job['id']
            if self.job_exists(job_id):
                logger.debug(f"Job {job_id} already exists in cache, skipping")
                return False
                
            self._append_to_json(job)
            self._append_to_csv(job)
            
            self.job_ids.add(job_id)
            self._save_job_id_cache()
            
            logger.info(f"Job {job_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            return False
            
    def save_jobs_batch(self, jobs: List[Dict[str, Any]]) -> int:
        new_jobs_count = 0
        for job in jobs:
            if self.save_job(job):
                new_jobs_count += 1
                
        return new_jobs_count
            
    def get_job_count(self) -> int:
        return len(self.job_ids)
        
    def _load_job_id_cache(self) -> Set[str]:
        try:
            if os.path.exists(self.job_cache_file):
                with open(self.job_cache_file, 'rb') as f:
                    job_ids = pickle.load(f)
                logger.info(f"Loaded {len(job_ids)} job IDs from cache")
                return job_ids
            else:
                logger.info("No job ID cache found, initializing empty cache")
                return set()
        except Exception as e:
            logger.error(f"Error loading job ID cache: {str(e)}")
            return set()
            
    def _save_job_id_cache(self) -> None:
        try:
            with open(self.job_cache_file, 'wb') as f:
                pickle.dump(self.job_ids, f)
            logger.debug(f"Saved {len(self.job_ids)} job IDs to cache")
        except Exception as e:
            logger.error(f"Error saving job ID cache: {str(e)}")
            
    def _load_existing_jobs_json(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.jobs_json_path) or os.path.getsize(self.jobs_json_path) == 0:
            return []
            
        try:
            with open(self.jobs_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Error decoding JSON from {self.jobs_json_path}, initializing empty list")
            return []
        
    def _append_to_json(self, job: Dict[str, Any]) -> None:
        try:
            jobs = self._load_existing_jobs_json()
            jobs.append(job)
            
            with open(self.jobs_json_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error appending to JSON: {str(e)}")
    
    def _normalize_job_for_csv(self, job: Dict[str, Any]) -> Dict[str, Any]:
        normalized_job = {}
        
        for field in self.expected_fields:
            value = job.get(field, "")
            
            if value is None:
                normalized_job[field] = ""
            elif isinstance(value, (list, dict)):
                normalized_job[field] = json.dumps(value, ensure_ascii=False)
            else:
                normalized_job[field] = value
                
        return normalized_job
            
    def _append_to_csv(self, job: Dict[str, Any]) -> None:
        try:
            normalized_job = self._normalize_job_for_csv(job)
            df_new = pd.DataFrame([normalized_job])
            
            for col in self.expected_fields:
                if col not in df_new.columns:
                    df_new[col] = ""
            
            df_new = df_new[self.expected_fields]
            
            file_exists = os.path.exists(self.jobs_csv_path) and os.path.getsize(self.jobs_csv_path) > 0

            df_new.to_csv(
                self.jobs_csv_path, 
                mode='a' if file_exists else 'w',
                header=not file_exists, 
                index=False, 
                encoding='utf-8'
            )
                
        except Exception as e:
            logger.error(f"Error appending to CSV: {str(e)}") 