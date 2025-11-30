# -*- coding: utf-8 -*-
"""
Configuration Loader for AgentDaf1.1
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.logger = logging.getLogger(__name__)
        self.configs = {}
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        try:
            config_path = self.config_dir / f"{config_name}.json"
            
            if not config_path.exists():
                self.logger.warning(f"Config not found: {config_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.configs[config_name] = config
            self.logger.info(f"Loaded config: {config_name}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config {config_name}: {e}")
            return None
    
    def save_config(self, config_name: str, config: Dict[str, Any]) -> bool:
        try:
            config_path = self.config_dir / f"{config_name}.json"
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.configs[config_name] = config
            self.logger.info(f"Saved config: {config_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config {config_name}: {e}")
            return False
    
    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        return self.configs.get(config_name)
    
    def load_env_config(self) -> Dict[str, Any]:
        env_config = {}
        env_vars = ['FLASK_ENV', 'DATABASE_URL', 'SECRET_KEY', 'PORT', 'HOST']
        
        for var in env_vars:
            value = os.getenv(var)
            if value is not None:
                env_config[var] = value
        
        return env_config

config_loader = ConfigLoader()
