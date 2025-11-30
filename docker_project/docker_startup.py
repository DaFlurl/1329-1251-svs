# -*- coding: utf-8 -*-
"""
Docker startup utilities for performance monitoring system
"""

import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

def check_docker_installation() -> bool:
    """Check if Docker is installed and running"""
    try:
        # Check if Docker is installed
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.info("❌ Docker is not installed")
            return False
        
        # Check if Docker daemon is running
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.info("⏱️ Docker command timeout")
        return False
    except FileNotFoundError:
        logger.info("❌ Docker command not found")
        return False
    except Exception as e:
        logger.info(f"❌ Error checking Docker: {e}")
        return False

def setup_monitoring_environment(project_dir: str) -> bool:
    """Setup monitoring environment with proper directory structure"""
    try:
        base_path = Path(project_dir)
        
        # Create necessary directories
        directories = ['data', 'logs', 'backups', 'configs']
        for dir_name in directories:
            dir_path = base_path / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created directory: {dir_path}")
            else:
                logger.info(f"✅ Directory exists: {dir_path}")
        
        # Create default configuration
        config_path = base_path / 'configs' / 'monitoring_config.json'
        if not config_path.exists():
            default_config = {
                'thresholds': {
                    'cpu_percent': 80.0,
                    'memory_percent': 85.0,
                    'disk_percent': 90.0,
                    'network_error_rate': 5.0
                },
                'monitoring': {
                    'interval': 5,
                    'history_retention': 100
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Created default config: {config_path}")
        
        return True
    except Exception as e:
        logger.info(f"❌ Setup error: {e}")
        return False

def validate_project_structure(project_dir: str) -> Dict[str, bool]:
    """Validate project structure and return status"""
    try:
        base_path = Path(project_dir)
        
        required_files = [
            'docker_files/Dockerfile',
            'docker_files/docker-compose.yml',
            'scripts/start.sh',
            'src/performance_monitor.py',
            'src/config/settings.py',
            'src/file_manager.py',
            'docker_startup.py'
        ]
        
        required_dirs = [
            'docker_files', 'scripts', 'src', 'src/config', 'data', 'logs', 'backups', 'configs'
        ]
        
        results = {}
        
        # Check files
        for file_path in required_files:
            full_path = base_path / file_path
            results[file_path] = full_path.exists()
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            results[dir_name] = dir_path.exists() and dir_path.is_dir()
        
        return results
    except Exception as e:
        logger.info(f"❌ Validation error: {e}")
        return {}

def start_monitoring_container(project_dir: str) -> bool:
    """Start the performance monitoring container"""
    try:
        # Change to project directory
        os.chdir(project_dir)
        
        # Build Docker image
        logger.info("🔨 Building performance monitor image...")
        build_result = subprocess.run(['docker', 'build', '-t', 'performance-monitor', '.'], 
                                    capture_output=True, text=True, timeout=300)
        
        if build_result.returncode != 0:
            logger.info(f"❌ Docker build failed: {build_result.stderr}")
            return False
        
        logger.info("✅ Docker image built successfully")
        
        # Start container
        logger.info("🚀 Starting performance monitor container...")
        run_result = subprocess.run([
            'docker', 'run', '-d',
            '--name', 'performance-monitor',
            '--restart', 'unless-stopped',
            '-v', f'{project_dir}/data:/app/data',
            '-v', f'{project_dir}/configs:/app/configs',
            '-v', f'{project_dir}/logs:/app/logs',
            '--network', 'host',
            'performance-monitor:latest'
        ], capture_output=True, text=True, timeout=60)
        
        if run_result.returncode == 0:
            logger.info("✅ Performance monitor started successfully")
            logger.info(f"📊 Data directory: {project_dir}/data")
            logger.info(f"📋 Logs directory: {project_dir}/logs")
            logger.info(f"⚙️  Configs directory: {project_dir}/configs")
            return True
        else:
            logger.info(f"❌ Failed to start container: {run_result.stderr}")
            return False
            
    except Exception as e:
        logger.info(f"❌ Startup error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Docker Performance Monitor Startup')
    parser.add_argument('project_dir', help='Project directory path')
    parser.add_argument('--validate', action='store_true', help='Validate project structure only')
    parser.add_argument('--setup', action='store_true', help='Setup environment only')
    
    args = parser.parse_args()
    
    if args.validate:
        results = validate_project_structure(args.project_dir)
        logger.info("/n📋 Project Structure Validation:")
        logger.info("=" * 40)
        for item, status in results.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {item}: {status}")
        
        total_files = sum(1 for status in results.values() if status and 'file' in item)
        total_dirs = sum(1 for status in results.values() if status and 'dir' in item)
        
        logger.info(f"/n📊 Summary: {total_files}/{len([k for k in results.keys() if 'file' in k])} files found, {total_dirs}/{len([k for k in results.keys() if 'dir' in k])} directories found")
        
    elif args.setup:
        if setup_monitoring_environment(args.project_dir):
            logger.info("✅ Environment setup completed")
        else:
            logger.info("❌ Environment setup failed")
    else:
        if not check_docker_installation():
            logger.info("❌ Docker is not installed or not running")
        elif start_monitoring_container(args.project_dir):
            logger.info("✅ Monitoring system started")
        else:
            logger.info("❌ Failed to start monitoring")