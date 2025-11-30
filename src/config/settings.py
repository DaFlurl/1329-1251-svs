"""
Settings Configuration - Application settings and environment variables
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "agentdaf1"
    user: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None


@dataclass
class SecurityConfig:
    secret_key: str = "your-secret-key-change-in-production"
    jwt_secret_key: str = "your-jwt-secret-change-in-production"
    jwt_expiration_hours: int = 24
    password_hash_rounds: int = 12
    enable_cors: bool = True
    cors_origins: list = field(default_factory=lambda: ["http://localhost:3000"])


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_json_logging: bool = False


@dataclass
class AppConfig:
    # Basic settings
    name: str = "AgentDaf1.1"
    version: str = "1.1.0"
    debug: bool = False
    environment: str = "development"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1

    # File paths
    base_dir: str = field(
        default_factory=lambda: str(Path(__file__).parent.parent.parent)
    )
    data_dir: str = field(default="")
    upload_folder: str = field(default="")
    logs_folder: str = field(default="")

    # Database
    database_url: str = "sqlite:///data/agentdaf1.db"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    # Redis
    redis: RedisConfig = field(default_factory=RedisConfig)

    # Security
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Logging
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Features
    enable_websocket: bool = True
    enable_dashboard: bool = True
    enable_api: bool = True
    enable_monitoring: bool = True

    # External services
    github_token: Optional[str] = None
    github_repo: Optional[str] = None

    # Performance
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    request_timeout: int = 30
    session_timeout: int = 3600

    def __post_init__(self):
        """Initialize derived paths after object creation"""
        if not self.data_dir:
            self.data_dir = os.path.join(self.base_dir, "data")
        if not self.upload_folder:
            self.upload_folder = os.path.join(self.data_dir, "uploads")
        if not self.logs_folder:
            self.logs_folder = os.path.join(self.data_dir, "logs")

        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.logs_folder, exist_ok=True)


class SettingsManager:
    def __init__(self):
        self.config = AppConfig()
        self._load_from_env()
        self._load_from_file()

    def _load_from_env(self):
        """Load settings from environment variables"""
        # Basic settings
        self.config.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.config.environment = os.getenv("ENVIRONMENT", "development")
        self.config.host = os.getenv("HOST", self.config.host)
        self.config.port = int(os.getenv("PORT", self.config.port))

        # Security
        self.config.security.secret_key = os.getenv(
            "SECRET_KEY", self.config.security.secret_key
        )
        self.config.security.jwt_secret_key = os.getenv(
            "JWT_SECRET_KEY", self.config.security.jwt_secret_key
        )
        self.config.security.jwt_expiration_hours = int(
            os.getenv("JWT_EXPIRATION_HOURS", self.config.security.jwt_expiration_hours)
        )

        # Database
        self.config.database_url = os.getenv("DATABASE_URL", self.config.database_url)
        if "DATABASE_HOST" in os.environ:
            host = os.getenv("DATABASE_HOST")
            if host:
                self.config.database.host = host
        if "DATABASE_PORT" in os.environ:
            port = os.getenv("DATABASE_PORT")
            if port:
                self.config.database.port = int(port)
        if "DATABASE_NAME" in os.environ:
            name = os.getenv("DATABASE_NAME")
            if name:
                self.config.database.name = name
        if "DATABASE_USER" in os.environ:
            user = os.getenv("DATABASE_USER")
            if user:
                self.config.database.user = user
        if "DATABASE_PASSWORD" in os.environ:
            password = os.getenv("DATABASE_PASSWORD")
            if password:
                self.config.database.password = password

        # Redis
        if "REDIS_HOST" in os.environ:
            host = os.getenv("REDIS_HOST")
            if host:
                self.config.redis.host = host
        if "REDIS_PORT" in os.environ:
            port = os.getenv("REDIS_PORT")
            if port:
                self.config.redis.port = int(port)
        if "REDIS_PASSWORD" in os.environ:
            password = os.getenv("REDIS_PASSWORD")
            if password:
                self.config.redis.password = password

        # Logging
        self.config.logging.level = os.getenv("LOG_LEVEL", self.config.logging.level)
        if "LOG_FILE" in os.environ:
            self.config.logging.file_path = os.getenv("LOG_FILE")
        self.config.logging.enable_json_logging = (
            os.getenv("LOG_JSON", "false").lower() == "true"
        )

        # Features
        self.config.enable_websocket = (
            os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true"
        )
        self.config.enable_dashboard = (
            os.getenv("ENABLE_DASHBOARD", "true").lower() == "true"
        )
        self.config.enable_api = os.getenv("ENABLE_API", "true").lower() == "true"
        self.config.enable_monitoring = (
            os.getenv("ENABLE_MONITORING", "true").lower() == "true"
        )

        # External services
        self.config.github_token = os.getenv("GITHUB_TOKEN")
        self.config.github_repo = os.getenv("GITHUB_REPO")

        # Performance
        if "MAX_UPLOAD_SIZE" in os.environ:
            size = os.getenv("MAX_UPLOAD_SIZE")
            if size:
                self.config.max_upload_size = int(size)
        if "REQUEST_TIMEOUT" in os.environ:
            timeout = os.getenv("REQUEST_TIMEOUT")
            if timeout:
                self.config.request_timeout = int(timeout)
        if "SESSION_TIMEOUT" in os.environ:
            timeout = os.getenv("SESSION_TIMEOUT")
            if timeout:
                self.config.session_timeout = int(timeout)

    def _load_from_file(self):
        """Load settings from configuration files"""
        config_files = [
            os.path.join(self.config.base_dir, "config", "config.json"),
            os.path.join(self.config.base_dir, ".env.json"),
            os.path.join(self.config.base_dir, "config.json"),
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding='utf-8') as f:
                        file_config = json.load(f)
                    self._update_config_from_dict(file_config)
                    logger.info(f"Loaded configuration from {config_file}")
                    break
                except Exception as e:
                    logger.warning(f"Error loading config from {config_file}: {e}")

    def _update_config_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary"""
        # Basic settings
        if "name" in config_dict:
            self.config.name = config_dict["name"]
        if "version" in config_dict:
            self.config.version = config_dict["version"]
        if "debug" in config_dict:
            self.config.debug = config_dict["debug"]
        if "environment" in config_dict:
            self.config.environment = config_dict["environment"]
        if "host" in config_dict:
            self.config.host = config_dict["host"]
        if "port" in config_dict:
            self.config.port = config_dict["port"]

        # Database
        if "database" in config_dict:
            db_config = config_dict["database"]
            if "url" in db_config:
                self.config.database_url = db_config["url"]
            if "host" in db_config:
                self.config.database.host = db_config["host"]
            if "port" in db_config:
                self.config.database.port = db_config["port"]
            if "name" in db_config:
                self.config.database.name = db_config["name"]
            if "user" in db_config:
                self.config.database.user = db_config["user"]
            if "password" in db_config:
                self.config.database.password = db_config["password"]

        # Security
        if "security" in config_dict:
            sec_config = config_dict["security"]
            if "secret_key" in sec_config:
                self.config.security.secret_key = sec_config["secret_key"]
            if "jwt_secret_key" in sec_config:
                self.config.security.jwt_secret_key = sec_config["jwt_secret_key"]
            if "jwt_expiration_hours" in sec_config:
                self.config.security.jwt_expiration_hours = sec_config[
                    "jwt_expiration_hours"
                ]

        # Logging
        if "logging" in config_dict:
            log_config = config_dict["logging"]
            if "level" in log_config:
                self.config.logging.level = log_config["level"]
            if "file_path" in log_config:
                self.config.logging.file_path = log_config["file_path"]
            if "enable_json_logging" in log_config:
                self.config.logging.enable_json_logging = log_config[
                    "enable_json_logging"
                ]

        # Features
        if "features" in config_dict:
            feat_config = config_dict["features"]
            if "enable_websocket" in feat_config:
                self.config.enable_websocket = feat_config["enable_websocket"]
            if "enable_dashboard" in feat_config:
                self.config.enable_dashboard = feat_config["enable_dashboard"]
            if "enable_api" in feat_config:
                self.config.enable_api = feat_config["enable_api"]
            if "enable_monitoring" in feat_config:
                self.config.enable_monitoring = feat_config["enable_monitoring"]

    def get_database_url(self) -> str:
        """Get complete database URL"""
        if (
            self.config.database_url
            and self.config.database_url != "sqlite:///data/agentdaf1.db"
        ):
            return self.config.database_url

        # Build SQLite URL
        if not self.config.database_url.startswith("sqlite"):
            db_path = os.path.join(self.config.data_dir, "agentdaf1.db")
            return f"sqlite:///{db_path}"

        return self.config.database_url

    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.config.redis.password:
            return f"redis://:{self.config.redis.password}@{self.config.redis.host}:{self.config.redis.port}/{self.config.redis.db}"
        return f"redis://{self.config.redis.host}:{self.config.redis.port}/{self.config.redis.db}"

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.config.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.config.environment.lower() == "development"

    def get_cors_origins(self) -> list:
        """Get CORS origins list"""
        return self.config.security.cors_origins

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "debug": self.config.debug,
            "environment": self.config.environment,
            "host": self.config.host,
            "port": self.config.port,
            "database_url": self.get_database_url(),
            "redis_url": self.get_redis_url(),
            "enable_websocket": self.config.enable_websocket,
            "enable_dashboard": self.config.enable_dashboard,
            "enable_api": self.config.enable_api,
            "enable_monitoring": self.config.enable_monitoring,
            "base_dir": self.config.base_dir,
            "data_dir": self.config.data_dir,
            "upload_folder": self.config.upload_folder,
            "logs_folder": self.config.logs_folder,
        }

    def save_to_file(self, file_path: str):
        """Save current configuration to file"""
        try:
            config_dict = self.to_dict()
            with open(file_path, "w") as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def validate(self) -> bool:
        """Validate configuration"""
        errors = []

        # Check required settings
        if (
            not self.config.security.secret_key
            or self.config.security.secret_key == "your-secret-key-change-in-production"
        ):
            if self.is_production():
                errors.append("SECRET_KEY must be set in production")

        if (
            not self.config.security.jwt_secret_key
            or self.config.security.jwt_secret_key
            == "your-jwt-secret-change-in-production"
        ):
            if self.is_production():
                errors.append("JWT_SECRET_KEY must be set in production")

        # Check paths
        if not os.path.exists(self.config.base_dir):
            errors.append(f"Base directory does not exist: {self.config.base_dir}")

        # Check ports
        if not (1 <= self.config.port <= 65535):
            errors.append(f"Invalid port number: {self.config.port}")

        if errors:
            for error in errors:
                logger.error(f"Configuration validation error: {error}")
            return False

        return True


# Global settings manager instance
settings = SettingsManager()


# Convenience functions
def get_settings() -> AppConfig:
    """Get application configuration"""
    return settings.config


def get_database_url() -> str:
    """Get database connection URL"""
    return settings.get_database_url()


def get_redis_url() -> str:
    """Get Redis connection URL"""
    return settings.get_redis_url()


def is_production() -> bool:
    """Check if running in production mode"""
    return settings.is_production()


def is_development() -> bool:
    """Check if running in development mode"""
    return settings.is_development()


# Backwards compatible Config object
class Config:
    """Compatibility wrapper exposing older uppercase-style constants expected
    by legacy modules and tests.
    """

    # Map values from the live settings instance
    SECRET_KEY = settings.config.security.secret_key
    JWT_SECRET_KEY = settings.config.security.jwt_secret_key
    DEBUG = settings.config.debug
    ENVIRONMENT = settings.config.environment
    HOST = settings.config.host
    PORT = settings.config.port
    UPLOAD_FOLDER = settings.config.upload_folder
    BASE_DIR = settings.config.base_dir
    DATA_DIR = settings.config.data_dir
    LOGS_FOLDER = settings.config.logs_folder

    # External services
    GITHUB_TOKEN = settings.config.github_token
    GITHUB_REPO = settings.config.github_repo

    # Repo owner / name convenience attributes
    GITHUB_REPO_OWNER = None
    GITHUB_REPO_NAME = None

    # Allowed extensions for uploads
    ALLOWED_EXTENSIONS = ["xlsx", "xls", "csv", "json"]

    @staticmethod
    def init_repo_parts():
        if Config.GITHUB_REPO:
            try:
                parts = Config.GITHUB_REPO.strip().split("/")
                if len(parts) >= 2:
                    Config.GITHUB_REPO_OWNER = parts[-2]
                    Config.GITHUB_REPO_NAME = parts[-1]
            except (IndexError, AttributeError, ValueError):
                Config.GITHUB_REPO_OWNER = None
                Config.GITHUB_REPO_NAME = None


# Initialize repository parts
Config.init_repo_parts()
