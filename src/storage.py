import os
import json
import pickle
import logging
import pandas as pd
from typing import Dict, List, Set, Any

logger = logging.getLogger(__name__)

class JobStorage:
    """Handles job data storage to different formats and deduplication"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize storage handler
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.jobs_json_path = config['output']['jobs_json']
        self.jobs_csv_path = config['output']['jobs_csv']
        self.job_cache_file = config['output']['job_cache_file']
        
        # Define expected fields for CSV with a fixed order
        self.expected_fields = [
            'id', 'title', 'company_name', 'location', 'salary', 'experience',
            'posted_date', 'crawled_at', 'url', 'salary_min', 'salary_max',
            'salary_currency', 'salary_negotiable', 'description', 'requirements',
            'benefits', 'work_location', 'application_deadline'
        ]
        
        # Initialize or load job ID cache
        self.job_ids = self._load_job_id_cache()
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.jobs_json_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.jobs_csv_path), exist_ok=True)
        
    def is_first_run(self) -> bool:
        """
        Check if this is the first run (no jobs collected yet)
        
        Returns:
            True if no jobs have been collected yet
        """
        return len(self.job_ids) == 0
        
    def save_job(self, job: Dict[str, Any]) -> bool:
        """
        Save a job to JSON and CSV if it's new
        
        Args:
            job: Job data dictionary
            
        Returns:
            True if job was saved, False if it was a duplicate
        """
        try:
            # Check if job is already in cache
            job_id = job['id']
            if job_id in self.job_ids:
                logger.debug(f"Job {job_id} already exists in cache, skipping")
                return False
                
            # Add to JSON
            self._append_to_json(job)
            
            # Add to CSV
            self._append_to_csv(job)
            
            # Add to cache and save cache
            self.job_ids.add(job_id)
            self._save_job_id_cache()
            
            logger.info(f"Job {job_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            return False
            
    def get_job_count(self) -> int:
        """
        Get the number of jobs in the cache
        
        Returns:
            Number of job IDs in cache
        """
        return len(self.job_ids)
        
    def _load_job_id_cache(self) -> Set[str]:
        """
        Load job ID cache from file or initialize empty cache
        
        Returns:
            Set of job IDs
        """
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
        """Save job ID cache to file"""
        try:
            with open(self.job_cache_file, 'wb') as f:
                pickle.dump(self.job_ids, f)
            logger.debug(f"Saved {len(self.job_ids)} job IDs to cache")
        except Exception as e:
            logger.error(f"Error saving job ID cache: {str(e)}")
            
    def _append_to_json(self, job: Dict[str, Any]) -> None:
        """
        Append job to JSON file
        
        Args:
            job: Job data dictionary
        """
        try:
            # Load existing data if file exists
            if os.path.exists(self.jobs_json_path) and os.path.getsize(self.jobs_json_path) > 0:
                with open(self.jobs_json_path, 'r', encoding='utf-8') as f:
                    try:
                        jobs = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(f"Error decoding JSON from {self.jobs_json_path}, initializing empty list")
                        jobs = []
            else:
                jobs = []
                
            # Append new job
            jobs.append(job)
            
            # Write back to file with indentation for readability
            with open(self.jobs_json_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error appending to JSON: {str(e)}")
    
    def _normalize_job_for_csv(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize job data for CSV export
        
        Args:
            job: Job data dictionary
            
        Returns:
            Normalized job data dictionary with consistent fields
        """
        normalized_job = {}
        
        # Ensure all expected fields are present with proper formatting
        for field in self.expected_fields:
            value = job.get(field, "")
            
            # Convert None to empty string
            if value is None:
                normalized_job[field] = ""
            # Convert lists or dictionaries to string representations
            elif isinstance(value, (list, dict)):
                normalized_job[field] = json.dumps(value, ensure_ascii=False)
            # Keep other values as is
            else:
                normalized_job[field] = value
                
        return normalized_job
            
    def _append_to_csv(self, job: Dict[str, Any]) -> None:
        """
        Append job to CSV file
        
        Args:
            job: Job data dictionary
        """
        try:
            # Normalize job data to ensure consistent structure
            normalized_job = self._normalize_job_for_csv(job)
            
            # Convert job to DataFrame with fixed column order
            df_new = pd.DataFrame([normalized_job])
            
            # Ensure the DataFrame has all columns in the expected order
            for col in self.expected_fields:
                if col not in df_new.columns:
                    df_new[col] = ""
            
            # Reorder columns to match expected fields
            df_new = df_new[self.expected_fields]
            
            # Append to existing file or create new one
            if os.path.exists(self.jobs_csv_path) and os.path.getsize(self.jobs_csv_path) > 0:
                df_new.to_csv(self.jobs_csv_path, mode='a', header=False, index=False, encoding='utf-8')
            else:
                df_new.to_csv(self.jobs_csv_path, index=False, encoding='utf-8')
                
        except Exception as e:
            logger.error(f"Error appending to CSV: {str(e)}")
            
    def save_jobs_batch(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Save a batch of jobs
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Number of new jobs saved
        """
        new_jobs_count = 0
        for job in jobs:
            if self.save_job(job):
                new_jobs_count += 1
                
        return new_jobs_count 