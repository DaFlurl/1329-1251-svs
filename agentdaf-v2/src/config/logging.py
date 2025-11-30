"""
Enhanced Logging Configuration Module for AgentDaf1.1
Centralized logging setup with structured logging and multiple handlers
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'exc_info', 
                          'exc_text', 'stack_info', 'lineno', 'funcName', 
                          'created', 'msecs', 'relativeCreated', 'thread', 
                          'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    COLORS = {
        'DEBUG': '/033[36m',    # Cyan
        'INFO': '/033[32m',     # Green
        'WARNING': '/033[33m',  # Yellow
        'ERROR': '/033[31m',    # Red
        'CRITICAL': '/033[35m',  # Magenta
        'RESET': '/033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format: [LEVEL] [TIMESTAMP] [LOGGER] MESSAGE
        formatted = (
            f"{color}[{record.levelname}]{reset} "
            f"[{datetime.fromtimestamp(record.created).strftime('%H:%M:%S')}] "
            f"[{record.name}] {record.getMessage()}"
        )
        
        if record.exc_info:
            formatted += f"/n{self.formatException(record.exc_info)}"
        
        return formatted

class LoggingConfig:
    """Centralized logging configuration manager"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Log levels
        self.LOG_LEVELS = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        # Default configuration
        self.config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    '()': StructuredFormatter
                },
                'colored': {
                    '()': ColoredFormatter,
                    'format': '[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s'
                },
                'simple': {
                    'format': '[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s'
                }
            },
            'handlers': {},
            'loggers': {},
            'root': {}
        }
        
        self._setup_handlers()
        self._setup_loggers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        
        # Console handler (colored for development)
        console_handler = {
            'class': 'logging.StreamHandler',
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'formatter': 'colored' if sys.stdout.isatty() else 'simple',
            'stream': 'ext://sys.stdout'
        }
        self.config['handlers']['console'] = console_handler
        
        # File handler for all logs
        file_handler = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': str(self.log_dir / 'agentdaf1.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'encoding': 'utf-8'
        }
        self.config['handlers']['file'] = file_handler
        
        # Error file handler
        error_handler = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'json',
            'filename': str(self.log_dir / 'errors.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5MB
            'backupCount': 3,
            'encoding': 'utf-8'
        }
        self.config['handlers']['error_file'] = error_handler
    
    def _setup_loggers(self):
        """Setup specific loggers"""
        
        # Root logger
        self.config['root'] = {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
        
        # Application logger
        self.config['loggers']['agentdaf1'] = {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        }
        
        # Security logger
        self.config['loggers']['agentdaf1.security'] = {
            'level': 'INFO',
            'handlers': ['console', 'file', 'error_file'],
            'propagate': False
        }
        
        # Performance logger
        self.config['loggers']['agentdaf1.performance'] = {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
        
        # Database logger
        self.config['loggers']['agentdaf1.database'] = {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
        
        # API logger
        self.config['loggers']['agentdaf1.api'] = {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
        
        # WebSocket logger
        self.config['loggers']['agentdaf1.websocket'] = {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    
    def setup_logging(self, app_config=None):
        """Apply logging configuration"""
        # Handle backward compatibility
        if app_config and hasattr(app_config, 'LOGS_FOLDER'):
            self.log_dir = Path(app_config.LOGS_FOLDER)
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self._setup_handlers()  # Re-setup with new directory
        
        import logging.config as logging_config
        logging_config.dictConfig(self.config)
        
        # Set specific logger levels for third-party libraries
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        # Log startup message
        logger = logging.getLogger('agentdaf1')
        logger.info("AgentDaf1.1 logging system initialized", extra={
            'log_dir': str(self.log_dir),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'handlers': list(self.config['handlers'].keys())
        })
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance"""
        return logging.getLogger(f'agentdaf1.{name}')

# Global logging configuration instance
logging_config = LoggingConfig()

# Convenience functions for backward compatibility
def setup_logging(app_config=None):
    """Setup logging for application"""
    logging_config.setup_logging(app_config)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging_config.get_logger(name)

# Security logging helpers
def log_security_event(event_type: str, user_id: Optional[str] = None, 
                     details: Optional[Dict[str, Any]] = None):
    """Log security events"""
    security_logger = logging.getLogger('agentdaf1.security')
    security_logger.info(f"Security event: {event_type}", extra={
        'event_type': event_type,
        'user_id': user_id,
        'details': details or {},
        'category': 'security'
    })

def log_performance_metric(metric_name: str, value: float, 
                       unit: str = 'ms', details: Optional[Dict[str, Any]] = None):
    """Log performance metrics"""
    perf_logger = logging.getLogger('agentdaf1.performance')
    perf_logger.info(f"Performance metric: {metric_name} = {value}{unit}", extra={
        'metric_name': metric_name,
        'value': value,
        'unit': unit,
        'details': details or {},
        'category': 'performance'
    })

# Initialize logging with environment variables
def initialize_from_env():
    """Initialize logging from environment variables"""
    env_config = {}
    
    # Log level
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    if log_level.upper() in logging_config.LOG_LEVELS:
        env_config['root'] = {'level': log_level.upper()}
    
    # Log directory
    log_dir = os.getenv('LOG_DIR')
    if log_dir:
        logging_config.log_dir = Path(log_dir)
        logging_config.log_dir.mkdir(exist_ok=True)
        logging_config._setup_handlers()  # Re-setup with new directory
    
    # JSON logging mode
    json_logging = os.getenv('JSON_LOGGING', 'false').lower() == 'true'
    if json_logging:
        env_config.setdefault('formatters', {})['console'] = {'()': StructuredFormatter}
    
    if env_config:
        setup_logging()

# Auto-initialize when module is imported
initialize_from_env()