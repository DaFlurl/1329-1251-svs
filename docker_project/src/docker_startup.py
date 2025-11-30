# -*- coding: utf-8 -*-
"""
Docker startup and initialization script for AgentDaf1.1
Handles container initialization, service startup, and system preparation.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DockerInitializer:
    """Handles Docker container initialization and startup procedures"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.required_dirs = ['data', 'logs', 'uploads', 'ssl']
        self.config_file = project_root / 'config' / 'settings.json'
        
    def check_environment(self) -> Dict[str, Any]:
        """Check Docker environment and configuration"""
        env_info = {
            'docker_available': self._check_docker(),
            'project_root': str(self.project_root),
            'directories': {},
            'config_exists': self.config_file.exists()
        }
        
        # Check required directories
        for dir_name in self.required_dirs:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists()
            env_info['directories'][dir_name] = {
                'path': str(dir_path),
                'exists': exists,
                'writable': os.access(str(dir_path), os.W_OK) if exists else False
            }
            
            if not exists:
                logger.info(f"Creating directory: {dir_path}")
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    env_info['directories'][dir_name]['exists'] = True
                    env_info['directories'][dir_name]['writable'] = True
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {e}")
        
        # Load configuration if exists
        if env_info['config_exists']:
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    env_info['config'] = config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        return env_info
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            import docker
            docker_client = docker.from_env()
            docker_client.ping()
            return True
        except ImportError:
            logger.warning("Docker Python package not installed")
            return False
        except Exception as e:
            logger.error(f"Docker check failed: {e}")
            return False
    
    def create_directories(self) -> bool:
        """Create required directories if they don't exist"""
        success = True
        for dir_name in self.required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {e}")
                    success = False
        return success
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load or create default configuration"""
        default_config = {
            'app': {
                'host': '0.0.0.0',
                'port': 8080,
                'debug': False
            },
            'database': {
                'path': 'data/agentdaf1.db',
                'backup_enabled': True,
                'backup_path': 'backups/'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/agentdaf1.log'
            },
            'security': {
                'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key'),
                'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret'),
                'token_expiry_hours': 24
            },
            'docker': {
                'restart_policy': 'unless-stopped',
                'health_check_interval': 30,
                'max_memory': '512m',
                'max_cpu': '0.5'
            }
        }
        
        # Load existing config or create default
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                    # Merge with defaults (existing takes precedence)
                    config = {**default_config, **existing_config}
                    logger.info("Loaded existing configuration")
            except Exception as e:
                logger.error(f"Failed to load existing config: {e}")
                config = default_config
        else:
            config = default_config
            # Save default config
            try:
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    logger.info("Created default configuration")
            except Exception as e:
                logger.error(f"Failed to save default config: {e}")
                config = default_config
        
        return config
    
    def initialize_database(self, config: Dict[str, Any]) -> bool:
        """Initialize database based on configuration"""
        try:
            db_config = config.get('database', {})
            db_path = self.project_root / db_config.get('path', 'data/agentdaf1.db')
            
            # Ensure database directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Import database module from main project
            sys.path.append(str(self.project_root.parent))
            try:
                from src.database.database_manager import DatabaseManager
            except ImportError:
                try:
                    from database.database_manager import DatabaseManager
                except ImportError:
                    logger.warning("Database manager not available")
                    return True
            
            try:
                db = DatabaseManager(str(db_path))
                logger.info(f"Database initialized: {db_path}")
                return True
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            return False
    
    def setup_logging(self, config: Dict[str, Any]) -> bool:
        """Setup logging configuration"""
        try:
            log_config = config.get('logging', {})
            log_level_name = log_config.get('level', 'INFO').upper()
            log_level = getattr(logging, log_level_name)
            
            # Create logs directory
            logs_dir = self.project_root / 'logs'
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Configure logging
            log_filename = log_config.get('file', 'agentdaf1.log')
            # Handle case where log file includes directory path
            if '/' in log_filename or '//' in log_filename:
                log_file = self.project_root / log_filename
                # Ensure parent directory exists
                log_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                log_file = logs_dir / log_filename
            
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
            
            logger.info(f"Logging configured: {log_level} level, file: {log_file}")
            return True
            
        except Exception as e:
            logger.error(f"Logging setup failed: {e}")
            return False
    
    def generate_startup_scripts(self, config: Dict[str, Any]) -> bool:
        """Generate startup scripts for different environments"""
        scripts_dir = self.project_root / 'scripts'
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        app_config = config.get('app', {})
        host = app_config.get('host', '0.0.0.0')
        port = app_config.get('port', 8080)
        
        # Development startup script
        dev_script = scripts_dir / 'start_dev.bat'
        dev_content = f"""@echo off
echo Starting AgentDaf1.1 Development Server...
cd /d "{self.project_root}"
set HOST={host}
set PORT={port}
set DEBUG=True
python src/main.py
pause
"""
        
        # Production startup script
        prod_script = scripts_dir / 'start_prod.bat'
        prod_content = f"""@echo off
echo Starting AgentDaf1.1 Production Server...
cd /d "{self.project_root}"
set HOST={host}
set PORT={port}
set DEBUG=False
python src/main.py
pause
"""
        
        try:
            with open(dev_script, 'w', encoding='utf-8') as f:
                f.write(dev_content)
            with open(prod_script, 'w', encoding='utf-8') as f:
                f.write(prod_content)
            
            logger.info(f"Generated startup scripts: {dev_script}, {prod_script}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate startup scripts: {e}")
            return False
    
    def create_env_file(self, config: Dict[str, Any]) -> bool:
        """Create .env file from configuration"""
        env_file = self.project_root / '.env'
        
        # Extract key configuration values
        env_content = []
        
        # App configuration
        app_config = config.get('app', {})
        env_content.extend([
            f"HOST={app_config.get('host', '0.0.0.0')}",
            f"PORT={app_config.get('port', 8080)}",
            f"DEBUG={app_config.get('debug', False)}"
        ])
        
        # Database configuration
        db_config = config.get('database', {})
        env_content.extend([
            f"DB_PATH={db_config.get('path', 'data/agentdaf1.db')}"
        ])
        
        # Security configuration
        security_config = config.get('security', {})
        env_content.extend([
            f"JWT_SECRET_KEY={security_config.get('jwt_secret_key', 'your-secret-key')}",
            f"SESSION_TIMEOUT={security_config.get('session_timeout', 3600)}"
        ])
        
        # Docker configuration
        docker_config = config.get('docker', {})
        env_content.extend([
            f"DOCKER_IMAGE={docker_config.get('image', 'agentdaf1:latest')}"
        ])
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write('/n'.join(env_content))
            logger.info(f"Created environment file: {env_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create environment file: {e}")
            return False
    
    def display_status(self, env_info: Dict[str, Any]) -> None:
        """Display environment status and next steps"""
        logger.info("/n" + "="*60)
        logger.info("AgentDaf1.1 Docker Environment Status")
        logger.info("="*60)
        
        logger.info(f"Project Root: {env_info['project_root']}")
        logger.info(f"Docker Available: {'OK' if env_info['docker_available'] else 'FAILED'}")
        
        logger.info("/nDirectory Status:")
        for dir_name, dir_info in env_info['directories'].items():
            status = 'OK' if dir_info['exists'] else 'MISSING'
            writable = 'OK' if dir_info.get('writable', False) else 'NO'
            logger.info(f"  {dir_name}/: {status} (Writable: {writable})")
        
        if env_info['config_exists']:
            logger.info(f"/nConfiguration loaded from: {self.config_file}")
        else:
            logger.info(f"/nConfiguration file not found (will create defaults)")
        
        logger.info("/nNext Steps:")
        logger.info("1. Directory structure is ready")
        logger.info("2. Configuration system is in place") 
        logger.info("3. Database will be initialized on startup")
        logger.info("4. Startup scripts are ready")
        logger.info("5. Run 'python docker_startup.py' to complete initialization")
        logger.info("/nDocumentation:")
        logger.info("   - Complete setup: python docker_startup.py --init")
        logger.info("   - Start development: scripts/start_dev.bat")
        logger.info("   - Start production: scripts/start_prod.bat")

def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AgentDaf1.1 Docker Initialization')
    parser.add_argument('--init', action='store_true', 
                       help='Initialize Docker environment')
    parser.add_argument('--check', action='store_true',
                       help='Check Docker environment status')
    parser.add_argument('--project-root', type=str, 
                       help='Project root directory path')
    
    args = parser.parse_args()
    
    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        # Default to current directory
        project_root = Path.cwd()
    
    # Initialize Docker environment
    initializer = DockerInitializer(project_root)
    
    if args.check:
        env_info = initializer.check_environment()
        initializer.display_status(env_info)
    elif args.init:
        logger.info("Initializing AgentDaf1.1 Docker Environment...")
        
        # Check and create directories
        if not initializer.create_directories():
            logger.info("FAILED: Failed to create required directories")
            return 1
        
        # Load configuration
        config = initializer.load_configuration()
        if not config:
            logger.info("FAILED: Failed to load configuration")
            return 1
        
        # Setup logging
        if not initializer.setup_logging(config):
            logger.info("FAILED: Failed to setup logging")
            return 1
        
        # Initialize database
        if not initializer.initialize_database(config):
            logger.info("FAILED: Failed to initialize database")
            return 1
        
        # Generate startup scripts
        if not initializer.generate_startup_scripts(config):
            logger.info("FAILED: Failed to generate startup scripts")
            return 1
        
        # Create environment file
        if not initializer.create_env_file(config):
            logger.info("FAILED: Failed to create environment file")
            return 1
        
        logger.info("/nSUCCESS: Docker environment initialized successfully!")
        logger.info(f"Project root: {project_root}")
        logger.info("Ready to start with: scripts/start_dev.bat (development) or scripts/start_prod.bat (production)")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()