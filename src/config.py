import os
import yaml
import logging
from typing import Dict, Any

def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Dict containing configuration settings
    """
    try:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # Validate required sections
        required_sections = ['crawling', 'output', 'logging', 'runtime']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section '{section}' in config file")
                
        return config
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        raise

def configure_logging(config: Dict[str, Any]) -> None:
    """
    Configure logging based on settings in config
    
    Args:
        config: Configuration dictionary
    """
    log_config = config['logging']
    log_file = log_config['log_file']
    log_level = getattr(logging, log_config['log_level'])
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Logging configured successfully") 