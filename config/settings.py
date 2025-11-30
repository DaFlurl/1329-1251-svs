"""
Application Configuration Module

Central configuration management for AgentDaf1.1 dashboard system.
"""

import os
from pathlib import Path

class AppConfig:
    """Application configuration settings."""
    
    def __init__(self):
        # Base paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.UPLOAD_FOLDER = self.BASE_DIR / 'data' / 'uploads'
        self.LOGS_FOLDER = self.BASE_DIR / 'logs'
        
        # Create directories if they don't exist
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Flask configuration
        self.SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        # File upload settings
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
        self.ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
        
        # GitHub integration settings
        self.GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
        self.GITHUB_REPO = os.environ.get('GITHUB_REPO', '')
        self.GITHUB_API_URL = 'https://api.github.com'
        
    @property
    def UPLOAD_FOLDER(self):
        return str(self.upload_folder)
    
    @property
    def DATA_FOLDER(self):
        return str(self.data_dir)
    
    @property
    def LOGS_FOLDER(self):
        return str(self.logs_folder)

# Global configuration instance
app_config = AppConfig()