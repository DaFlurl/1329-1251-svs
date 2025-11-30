#!/usr/bin/env python3
"""
Configuration Manager Module - Handles system configuration, settings, and environment variables
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ConfigSettings:
    """Configuration settings data structure"""
    database_path: str
    log_level: str
    debug_mode: bool
    api_host: str
    api_port: int
    secret_key: str
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    jwt_secret_key: Optional[str] = None

class ConfigManager:
    """Configuration management class"""
    
    def __init__(self, config_file: str = "config/config.json"):
        """Initialize configuration manager"""
        self.config_file = config_file
        self.config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables"""
        try:
            # Load from file first
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                    logger.info(f"Configuration loaded from {self.config_file}")
            
            # Override with environment variables
            env_overrides = {
                'database_path': os.getenv('DB_PATH', 'data/agentdaf1.db'),
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'debug_mode': os.getenv('DEBUG', 'False').lower() == 'true',
                'api_host': os.getenv('HOST', '0.0.0.0'),
                'api_port': int(os.getenv('PORT', '8080')),
                'secret_key': os.getenv('SECRET_KEY', ''),
                'github_token': os.getenv('GITHUB_TOKEN'),
                'github_repo': os.getenv('GITHUB_REPO'),
                'jwt_secret_key': os.getenv('JWT_SECRET_KEY')
            }
            
            # Apply environment overrides
            for key, value in env_overrides.items():
                if value is not None:
                    self.config_data[key] = value
                    logger.debug(f"Environment override applied: {key}={value}")
            
            # Set defaults for missing values
            defaults = {
                'database_path': 'data/agentdaf1.db',
                'log_level': 'INFO',
                'debug_mode': False,
                'api_host': '0.0.0.0',
                'api_port': 8080,
                'check_interval': 60,
                'thresholds': {
                    'cpu_percent': 80.0,
                    'memory_percent': 85.0,
                    'disk_usage': 90.0,
                    'process_count': 300,
                    'load_average': 2.0,
                    'temperature': 70.0
                }
            }
            
            # Apply defaults
            for key, default_value in defaults.items():
                if key not in self.config_data:
                    self.config_data[key] = default_value
                    logger.debug(f"Default applied: {key}={default_value}")
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        try:
            self.config_data[key] = value
            self._save_config()
            logger.info(f"Configuration updated: {key}={value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set configuration: {e}")
            return False
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            # Ensure config directory exists
            config_dir = Path(self.config_file).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2)
                logger.debug(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_database_path(self) -> str:
        """Get database path"""
        return self.get('database_path')
    
    def get_log_level(self) -> str:
        """Get log level"""
        return self.get('log_level')
    
    def get_debug_mode(self) -> bool:
        """Get debug mode"""
        return self.get('debug_mode')
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return {
            'host': self.get('api_host'),
            'port': self.get('api_port')
        }
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get monitoring thresholds"""
        return self.get('thresholds', {})
    
    def get_github_config(self) -> Dict[str, Any]:
        """Get GitHub configuration"""
        return {
            'token': self.get('github_token'),
            'repo': self.get('github_repo')
        }
    
    def get_jwt_config(self) -> Dict[str, Any]:
        """Get JWT configuration"""
        return {
            'secret_key': self.get('jwt_secret_key')
        }
    
    def get_all_settings(self) -> ConfigSettings:
        """Get all configuration as structured object"""
        return ConfigSettings(
            database_path=self.get_database_path(),
            log_level=self.get_log_level(),
            debug_mode=self.get_debug_mode(),
            api_host=self.get('api_host'),
            api_port=self.get('api_port'),
            secret_key=self.get('secret_key'),
            github_token=self.get('github_token'),
            github_repo=self.get('github_repo'),
            jwt_secret_key=self.get('jwt_secret_key')
        )
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        try:
            # Check required fields
            required_fields = ['database_path', 'secret_key']
            for field in required_fields:
                if not self.get(field):
                    logger.error(f"Required configuration field missing: {field}")
                    return False
            
            # Validate numeric values
            numeric_fields = ['api_port']
            for field in numeric_fields:
                value = self.get(field)
                if value is not None and not isinstance(value, (int, float)):
                    logger.error(f"Invalid numeric value for {field}: {value}")
                    return False
            
            # Validate thresholds
            thresholds = self.get_thresholds()
            for threshold_name, threshold_value in thresholds.items():
                if not isinstance(threshold_value, (int, float)) or threshold_value <= 0:
                    logger.error(f"Invalid threshold value for {threshold_name}: {threshold_value}")
                    return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def reload(self):
        """Reload configuration from file"""
        self._load_config()
        logger.info("Configuration reloaded")

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    return config_manager

def load_config_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from specific file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config file {file_path}: {e}")
        return {}

def save_config_file(file_path: str, config_data: Dict[str, Any]) -> bool:
    """Save configuration to specific file"""
    try:
        config_dir = Path(file_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save config file {file_path}: {e}")
        return False

if __name__ == "__main__":
    # Test configuration manager
    config = get_config()
    settings = config.get_all_settings()
    logger.info("🔧 Configuration Manager Test")
    logger.info("=" * 40)
    logger.info(f"Database Path: {settings.database_path}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"Debug Mode: {settings.debug_mode}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")
    logger.info(f"Secret Key: {'*' * len(settings.secret_key) if settings.secret_key else 'None'}")
    logger.info(f"GitHub Token: {'Set' if settings.github_token else 'None'}")
    logger.info(f"Thresholds: {settings.thresholds}")
    logger.info("=" * 40)
    logger.info(f"Validation: {'✅ Passed' if config.validate_config() else '❌ Failed'}")