"""
Centralized logging configuration for AgentDaf1.1
"""

import logging

def setup_logging():
    """Centralized logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_logger(name: str) -> logging.Logger:
    """Get logger with standard configuration"""
    setup_logging()
    return logging.getLogger(name)