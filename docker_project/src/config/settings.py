# -*- coding: utf-8 -*-
"""
Configuration settings for Docker Performance Monitor
"""

import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AppConfig:
    """Application configuration with path settings"""
    
    def __init__(self):
        # Base directories
        self.base_dir = Path(".")
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs" 
        self.backups_dir = self.base_dir / "backups"
        self.configs_dir = self.base_dir / "configs"
        
        # Docker settings
        self.docker_image = "performance-monitor:latest"
        self.container_name = "performance-monitor"
        self.exposed_port = 8080
        
        # Monitoring thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'network_error_rate': 5.0
        }
        
        # Logging configuration
        self.log_level = "INFO"
        self.log_format = "%(asctime)s - %(levelname)s - %(message)s"
        
        # Performance settings
        self.monitoring_interval = 5  # seconds
        self.history_retention = 100  # entries
        
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings as dictionary"""
        return {
            'base_dir': str(self.base_dir),
            'data_dir': str(self.data_dir),
            'logs_dir': str(self.logs_dir),
            'backups_dir': str(self.backups_dir),
            'configs_dir': str(self.configs_dir),
            'docker_image': self.docker_image,
            'container_name': self.container_name,
            'exposed_port': self.exposed_port,
            'thresholds': self.thresholds,
            'log_level': self.log_level,
            'log_format': self.log_format,
            'monitoring_interval': self.monitoring_interval,
            'history_retention': self.history_retention
        }
    
    def update_setting(self, key: str, value: Any):
        """Update a specific setting"""
        if hasattr(self, key):
            setattr(self, key, value)
            return True
        return False
    
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        import json
        try:
            settings = self.get_all_settings()
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.info(f"Error saving config: {e}")
            return False