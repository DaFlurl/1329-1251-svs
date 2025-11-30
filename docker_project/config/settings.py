"""
Configuration settings for AgentDaf1.1 monitoring application.
"""

import os
from typing import Dict, Any

class Settings:
    """Application settings and configuration management."""
    
    def __init__(self):
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', '8080'))
        self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        self.database_url = os.getenv('DATABASE_URL', f'sqlite:///data/agentdaf1.db')
        self.upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_content_length = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
        self.allowed_extensions = os.getenv('ALLOWED_EXTENSIONS', 
            'xlsx,xls,csv,json,txt,md,py,js,html,css,png,jpg,jpeg,gif').split(',')
        
        # Performance settings
        self.performance_retention_days = int(os.getenv('PERFORMANCE_RETENTION_DAYS', '30'))
        self.metrics_collection_interval = int(os.getenv('METRICS_COLLECTION_INTERVAL', '60'))  # seconds
        
        # Security settings
        self.jwt_secret_key = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production')
        self.jwt_expiration_hours = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
        self.max_login_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
        self.session_timeout_minutes = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
        
        # Monitoring settings
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))  # seconds
        self.alert_threshold_cpu = float(os.getenv('ALERT_THRESHOLD_CPU', '80.0'))  # percentage
        self.alert_threshold_memory = float(os.getenv('ALERT_THRESHOLD_MEMORY', '85.0'))  # percentage
        self.alert_threshold_disk = float(os.getenv('ALERT_THRESHOLD_DISK', '90.0'))  # percentage
        
        # WebSocket settings
        self.websocket_port = int(os.getenv('WEBSOCKET_PORT', '8081'))
        self.websocket_ping_interval = int(os.getenv('WEBSOCKET_PING_INTERVAL', '30'))  # seconds
        
        # Docker settings
        self.docker_data_path = os.getenv('DOCKER_DATA_PATH', '/var/lib/agentdaf1')
        self.ssl_cert_path = os.getenv('SSL_CERT_PATH', 'ssl/cert.pem')
        self.ssl_key_path = os.getenv('SSL_KEY_PATH', 'ssl/key.pem')
        
        # API settings
        self.api_rate_limit = int(os.getenv('API_RATE_LIMIT', '100'))  # requests per minute
        self.api_timeout = int(os.getenv('API_TIMEOUT', '30'))  # seconds
        
        # File processing settings
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '8192'))  # bytes
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', '104857600'))  # 100MB
        
        # Dashboard settings
        self.dashboard_refresh_interval = int(os.getenv('DASHBOARD_REFRESH_INTERVAL', '5'))  # seconds
        self.max_dashboard_entries = int(os.getenv('MAX_DASHBOARD_ENTRIES', '1000'))
        
        # Logging settings
        self.log_file = os.getenv('LOG_FILE', 'logs/agentdaf1.log')
        self.log_max_size = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
        self.log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        # Cache settings
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))  # seconds
        self.cache_max_size = int(os.getenv('CACHE_MAX_SIZE', '100'))  # MB
        
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            'url': self.database_url,
            'echo': True,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'pool_size': 10,
            'max_overflow': 20
        }
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask application configuration."""
        return {
            'host': self.host,
            'port': self.port,
            'debug': self.debug,
            'secret_key': self.secret_key,
            'max_content_length': self.max_content_length,
            'upload_folder': self.upload_folder,
            'static_folder': 'static',
            'template_folder': 'templates'
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance monitoring configuration."""
        return {
            'retention_days': self.performance_retention_days,
            'collection_interval': self.metrics_collection_interval,
            'alert_threshold_cpu': self.alert_threshold_cpu,
            'alert_threshold_memory': self.alert_threshold_memory,
            'alert_threshold_disk': self.alert_threshold_disk
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            'jwt_secret_key': self.jwt_secret_key,
            'jwt_expiration_hours': self.jwt_expiration_hours,
            'max_login_attempts': self.max_login_attempts,
            'session_timeout_minutes': self.session_timeout_minutes
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            'health_check_interval': self.health_check_interval,
            'websocket_port': self.websocket_port,
            'websocket_ping_interval': self.websocket_ping_interval
        }
    
    def get_docker_config(self) -> Dict[str, Any]:
        """Get Docker configuration."""
        return {
            'data_path': self.docker_data_path,
            'ssl_cert_path': self.ssl_cert_path,
            'ssl_key_path': self.ssl_key_path
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            'rate_limit': self.api_rate_limit,
            'timeout': self.api_timeout
        }
    
    def get_file_processing_config(self) -> Dict[str, Any]:
        """Get file processing configuration."""
        return {
            'chunk_size': self.chunk_size,
            'max_file_size': self.max_file_size,
            'allowed_extensions': self.allowed_extensions
        }
    
    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration."""
        return {
            'refresh_interval': self.dashboard_refresh_interval,
            'max_entries': self.max_dashboard_entries
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'file': self.log_file,
            'max_size': self.log_max_size,
            'backup_count': self.log_backup_count
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            'ttl': self.cache_ttl,
            'max_size': self.cache_max_size
        }
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings."""
        return {
            'debug': self.debug,
            'host': self.host,
            'port': self.port,
            'secret_key': self.secret_key,
            'database_url': self.database_url,
            'upload_folder': self.upload_folder,
            'log_level': self.log_level,
            'max_content_length': self.max_content_length,
            'allowed_extensions': self.allowed_extensions,
            'performance': self.get_performance_config(),
            'security': self.get_security_config(),
            'monitoring': self.get_monitoring_config(),
            'docker': self.get_docker_config(),
            'api': self.get_api_config(),
            'file_processing': self.get_file_processing_config(),
            'dashboard': self.get_dashboard_config(),
            'logging': self.get_logging_config(),
            'cache': self.get_cache_config()
        }
    
    def validate_settings(self) -> Dict[str, str]:
        """Validate all settings and return validation results."""
        issues = []
        
        # Validate required settings
        if not self.secret_key or self.secret_key == 'dev-secret-key-change-in-production':
            issues.append('SECRET_KEY must be set to a secure value in production')
        
        if not self.jwt_secret_key or self.jwt_secret_key == 'your-jwt-secret-key-change-in-production':
            issues.append('JWT_SECRET_KEY must be set to a secure value in production')
        
        # Validate numeric settings
        numeric_settings = [
            ('port', self.port, 1, 65535),
            ('performance_retention_days', self.performance_retention_days, 1, 365),
            ('metrics_collection_interval', self.metrics_collection_interval, 10, 3600),
            ('jwt_expiration_hours', self.jwt_expiration_hours, 1, 168),  # 1 week max
            ('max_login_attempts', self.max_login_attempts, 1, 20),
            ('session_timeout_minutes', self.session_timeout_minutes, 1, 1440),  # 24 hours max
            ('health_check_interval', self.health_check_interval, 5, 300),
            ('websocket_port', self.websocket_port, 1, 65535),
            ('websocket_ping_interval', self.websocket_ping_interval, 10, 300),
            ('api_rate_limit', self.api_rate_limit, 1, 10000),
            ('api_timeout', self.api_timeout, 1, 300),
            ('chunk_size', self.chunk_size, 1024, 65536),
            ('max_file_size', self.max_file_size, 1024, 1073741824),  # 1GB max
            ('dashboard_refresh_interval', self.dashboard_refresh_interval, 1, 300),
            ('max_dashboard_entries', self.max_dashboard_entries, 10, 10000),
            ('log_max_size', self.log_max_size, 1048576, 1073741824),  # 1GB max
            ('log_backup_count', self.log_backup_count, 1, 100),
            ('cache_ttl', self.cache_ttl, 60, 86400),  # 24 hours max
            ('cache_max_size', self.cache_max_size, 1, 10240)  # 10GB max
        ]
        
        for setting_name, value, min_val, max_val in numeric_settings:
            if not isinstance(value, int) or value < min_val or value > max_val:
                issues.append(f'{setting_name} must be between {min_val} and {max_val}')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def get_env_summary(self) -> str:
        """Get environment summary for logging."""
        return f"""
Debug: {self.debug}
Host: {self.host}
Port: {self.port}
Database: {self.database_url}
Upload Folder: {self.upload_folder}
Log Level: {self.log_level}
Max Content Length: {self.max_content_length}
Allowed Extensions: {self.allowed_extensions}
Performance Retention: {self.performance_retention_days} days
Metrics Collection: {self.metrics_collection_interval}s
Alert Thresholds - CPU: {self.alert_threshold_cpu}%, Memory: {self.alert_threshold_memory}%, Disk: {self.alert_threshold_disk}%
JWT Expiration: {self.jwt_expiration_hours}h
Max Login Attempts: {self.max_login_attempts}
Session Timeout: {self.session_timeout_minutes}m
Health Check Interval: {self.health_check_interval}s
WebSocket Port: {self.websocket_port}
WebSocket Ping Interval: {self.websocket_ping_interval}s
API Rate Limit: {self.api_rate_limit}/min
API Timeout: {self.api_timeout}s
Chunk Size: {self.chunk_size} bytes
Max File Size: {self.max_file_size} bytes
Dashboard Refresh: {self.dashboard_refresh_interval}s
Max Dashboard Entries: {self.max_dashboard_entries}
Log File: {self.log_file}
Log Max Size: {self.log_max_size} bytes
Log Backup Count: {self.log_backup_count}
Cache TTL: {self.cache_ttl}s
Cache Max Size: {self.cache_max_size}MB
Docker Data Path: {self.docker_data_path}
SSL Cert Path: {self.ssl_cert_path}
SSL Key Path: {self.ssl_key_path}
        """.strip()

# Global settings instance
settings = Settings()