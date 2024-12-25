# src/utils/logging_config.py

import logging
import sys
from typing import Optional

def setup_logger(name: str) -> logging.Logger:
    """Configure and get logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Avoid adding handlers multiple times
        logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger