import os
import logging

from typing import Dict, Any

def create_required_directories(config: Dict[str, Any]) -> None:
    logger = logging.getLogger(__name__)
    
    os.makedirs(os.path.dirname(config['output']['jobs_json']), exist_ok=True)
    os.makedirs(os.path.dirname(config['output']['jobs_csv']), exist_ok=True)
    
    os.makedirs(os.path.dirname(config['logging']['log_file']), exist_ok=True)
    
    logger.debug("Created required directories") 