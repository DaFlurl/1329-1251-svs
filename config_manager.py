# AgentDaf1 Scoreboard - Configuration Management

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Centralized configuration management for AgentDaf1 Scoreboard"""
    
    def __init__(self, config_file: str = ".env"):
        self.config_file = Path(config_file)
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from .env file"""
        if not self.config_file.exists():
            self.create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    self.config[key.strip()] = self.parse_value(value.strip())
    
    def parse_value(self, value: str) -> Any:
        """Parse configuration value to appropriate type"""
        # Handle boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = """# AgentDaf1 Scoreboard Configuration

## Project Settings
PROJECT_NAME=AgentDaf1 Scoreboard
VERSION=2.0.0
ENVIRONMENT=production

## Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=False

## History API Server
HISTORY_API_PORT=5001
HISTORY_API_HOST=0.0.0.0

## File Paths
BASE_DIR=C:\\Users\\flori\\Desktop\\AgentDaf1\\github-dashboard
EXCEL_FILE=Sunday, 16 November 2025 1329+1251 v 3144363.xlsx
DATA_FILE=scoreboard-data.json
HISTORY_DIR=file_history
BACKUPS_DIR=file_history/backups

## History & Backup Settings
ENABLE_HISTORY_TRACKING=True
ENABLE_AUTO_BACKUP=True
BACKUP_RETENTION_DAYS=30
MAX_HISTORY_SIZE_MB=500
AUTO_BACKUP_INTERVAL=3600

## Scoreboard Settings
AUTO_REFRESH_INTERVAL=30000
MAX_PLAYERS_DISPLAY=1000
DEFAULT_SORT_COLUMN=score
DEFAULT_SORT_ORDER=desc

## Theme & UI
DEFAULT_THEME=gradient
ENABLE_DARK_MODE=False
RESPONSIVE_DESIGN=True
ANIMATIONS_ENABLED=True

## Excel Processing
SUPPORTED_FORMATS=.xlsx,.xls,.csv,.json
MAX_FILE_SIZE_MB=50
AUTO_DETECT_HEADERS=True
ENCODING=utf-8

## API Settings
API_RATE_LIMIT=100
CORS_ENABLED=True
API_TIMEOUT=30

## GitHub Pages Deployment
GITHUB_PAGES_ENABLED=True
GITHUB_REPO=DaFlurl/1329-1251-svs
GITHUB_BRANCH=main
DEPLOY_URL=https://daflurl.github.io/1329-1251-svs

## Docker Configuration
DOCKER_ENABLED=True
DOCKER_IMAGE=agentdaf1/scoreboard:latest
DOCKER_PORT=8000

## Logging
LOG_LEVEL=INFO
LOG_FILE=scoreboard.log
LOG_MAX_SIZE_MB=10
LOG_BACKUP_COUNT=5

## Security
ENABLE_AUTH=False
SECRET_KEY=your-secret-key-here
SESSION_TIMEOUT=3600

## Performance
CACHE_ENABLED=True
CACHE_TTL=300
MAX_CONCURRENT_USERS=50
ENABLE_COMPRESSION=True

## Features
LIVE_SCOREBOARD=True
REAL_TIME_UPDATES=True
FILE_HISTORY=True
VERSION_CONTROL=True
EXCEL_IMPORT=True
DATA_EXPORT=True
ALLIANCE_STATS=True
MULTI_TAB_VIEW=True
SEARCH_FILTER=True
AUTO_REFRESH=True
BACKUP_RESTORE=True
API_ENDPOINTS=True
"""
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(default_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration"""
        return {
            'host': self.get('HOST', '0.0.0.0'),
            'port': self.get('PORT', 8000),
            'debug': self.get('DEBUG', False)
        }
    
    def get_history_api_config(self) -> Dict[str, Any]:
        """Get history API configuration"""
        return {
            'host': self.get('HISTORY_API_HOST', '0.0.0.0'),
            'port': self.get('HISTORY_API_PORT', 5001)
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database/file configuration"""
        return {
            'base_dir': self.get('BASE_DIR', '.'),
            'data_file': self.get('DATA_FILE', 'scoreboard-data.json'),
            'history_dir': self.get('HISTORY_DIR', 'file_history'),
            'backups_dir': self.get('BACKUPS_DIR', 'file_history/backups')
        }
    
    def get_features_config(self) -> Dict[str, bool]:
        """Get features configuration"""
        features = [
            'LIVE_SCOREBOARD', 'REAL_TIME_UPDATES', 'FILE_HISTORY',
            'VERSION_CONTROL', 'EXCEL_IMPORT', 'DATA_EXPORT',
            'ALLIANCE_STATS', 'MULTI_TAB_VIEW', 'SEARCH_FILTER',
            'AUTO_REFRESH', 'BACKUP_RESTORE', 'API_ENDPOINTS'
        ]
        
        return {feature.lower(): self.get(feature, False) for feature in features}
    
    def export_config(self, filename: str = "config_export.json"):
        """Export configuration to JSON file"""
        export_data = {
            'timestamp': str(Path().resolve()),
            'config': self.config,
            'server': self.get_server_config(),
            'history_api': self.get_history_api_config(),
            'database': self.get_database_config(),
            'features': self.get_features_config()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def import_config(self, filename: str):
        """Import configuration from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        if 'config' in import_data:
            self.config.update(import_data['config'])
            self.save_config()

# Global configuration instance
config = ConfigManager()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config.get(key, default)

def set_config(key: str, value: Any):
    """Set configuration value"""
    config.set(key, value)

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return config.get(feature.upper(), False)

if __name__ == "__main__":
    # Test configuration management
    print("Testing Configuration Management")
    print(f"Project Name: {get_config('PROJECT_NAME')}")
    print(f"Version: {get_config('VERSION')}")
    print(f"Server Port: {get_config('PORT')}")
    print(f"History Tracking: {is_feature_enabled('FILE_HISTORY')}")
    
    # Export configuration
    export_file = config.export_config()
    print(f"Configuration exported to: {export_file}")