"""
Configuration Loader Module

Centralized configuration loading for AgentDaf1.1 dashboard system.
Supports loading from JSON files, environment variables, and defaults.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """Configuration loader with support for multiple sources."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._cache = {}
    
    def load_config(self, config_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            config_name: Name of the config file (without .json extension)
            use_cache: Whether to use cached version if available
            
        Returns:
            Configuration dictionary
        """
        if use_cache and config_name in self._cache:
            return self._cache[config_name]
        
        config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Apply environment variable overrides
            config = self._apply_env_overrides(config, config_name.upper())
            
            if use_cache:
                self._cache[config_name] = config
            
            return config
            
        except (json.JSONDecodeError, IOError) as e:
            logger.info(f"Error loading config {config_name}: {e}")
            return {}
    
    def _apply_env_overrides(self, config: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}_"):
                config_key = key[len(prefix) + 1:].lower()
                # Convert string values to appropriate types
                config[config_key] = self._convert_env_value(value)
        
        return config
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard-specific configuration."""
        main_config = self.load_config('config')
        dashboard_config = self.load_config('dashboard')
        
        # Merge configurations, with dashboard_config taking precedence
        merged = {**main_config.get('dashboard', {}), **dashboard_config}
        
        return merged
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        main_config = self.load_config('config')
        return main_config.get('server', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.load_config('database')
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration."""
        return self.load_config('deployment')
    
    def get_paths(self) -> Dict[str, str]:
        """Get configured paths."""
        main_config = self.load_config('config')
        paths = main_config.get('paths', {})
        
        # Convert relative paths to absolute
        base_dir = paths.get('base_dir', os.getcwd())
        for key, path in paths.items():
            if key != 'base_dir' and not os.path.isabs(path):
                paths[key] = os.path.join(base_dir, path)
        
        return paths
    
    def reload_config(self, config_name: str) -> Dict[str, Any]:
        """Force reload of configuration from file."""
        if config_name in self._cache:
            del self._cache[config_name]
        return self.load_config(config_name, use_cache=False)
    
    def clear_cache(self):
        """Clear all cached configurations."""
        self._cache.clear()

# Global configuration loader instance
config_loader = ConfigLoader()

# Convenience functions
def get_dashboard_config() -> Dict[str, Any]:
    """Get dashboard configuration."""
    return config_loader.get_dashboard_config()

def get_server_config() -> Dict[str, Any]:
    """Get server configuration."""
    return config_loader.get_server_config()

def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return config_loader.get_database_config()

def get_deployment_config() -> Dict[str, Any]:
    """Get deployment configuration."""
    return config_loader.get_deployment_config()

def get_paths() -> Dict[str, str]:
    """Get configured paths."""
    return config_loader.get_paths()