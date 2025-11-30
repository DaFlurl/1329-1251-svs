#!/usr/bin/env python3
"""
Quick Auto-Repair for AgentDaf1.1
Creates missing files automatically
"""

import os
from pathlib import Path

def create_missing_files():
    """Create missing files"""
    base_dir = Path.cwd()
    
    # Create services/notification_service.py
    notification_service = '''# -*- coding: utf-8 -*-
"""
Notification Service for AgentDaf1.1
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

class NotificationService:
    def __init__(self):
        self.notifications = []
        self.logger = logging.getLogger(__name__)
    
    def send_notification(self, title: str, message: str, level: str = "info") -> bool:
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        self.notifications.append(notification)
        self.logger.info(f"Notification: {title}")
        return True
    
    def get_notifications(self, limit: int = 50) -> List[Dict]:
        return self.notifications[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_notifications": len(self.notifications),
            "unread_notifications": len([n for n in self.notifications if not n["read"]])
        }

notification_service = NotificationService()
'''
    
    # Create services/file_service.py
    file_service = '''# -*- coding: utf-8 -*-
"""
File Service for AgentDaf1.1
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

class FileService:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.logger = logging.getLogger(__name__)
    
    def upload_file(self, file_data: bytes, filename: str, folder: str = "uploads") -> Dict[str, Any]:
        try:
            upload_dir = self.base_dir / folder
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / filename
            counter = 1
            original_name = filename
            while file_path.exists():
                stem = Path(original_name).stem
                suffix = Path(original_name).suffix
                filename = f"{stem}_{counter}{suffix}"
                file_path = upload_dir / filename
                counter += 1
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            file_hash = hashlib.md5(file_data).hexdigest()
            
            file_info = {
                "filename": filename,
                "path": str(file_path),
                "size": len(file_data),
                "hash": file_hash
            }
            
            self.logger.info(f"File uploaded: {filename}")
            return {"success": True, "file_info": file_info}
            
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    def list_files(self, folder: str = "uploads") -> List[Dict[str, Any]]:
        try:
            folder_path = self.base_dir / folder
            if not folder_path.exists():
                return []
            
            files = []
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })
            
            return files
        except Exception as e:
            self.logger.error(f"List files failed: {e}")
            return []

file_service = FileService()
'''
    
    # Create src/config/config_loader.py
    config_loader = '''# -*- coding: utf-8 -*-
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
'''
    
    # Write files
    files_created = []
    
    # Create directories
    (base_dir / 'services').mkdir(exist_ok=True)
    (base_dir / 'src' / 'config').mkdir(parents=True, exist_ok=True)
    
    # Write notification service
    notification_path = base_dir / 'services' / 'notification_service.py'
    with open(notification_path, 'w', encoding='utf-8') as f:
        f.write(notification_service)
    files_created.append(str(notification_path))
    
    # Write file service
    file_service_path = base_dir / 'services' / 'file_service.py'
    with open(file_service_path, 'w', encoding='utf-8') as f:
        f.write(file_service)
    files_created.append(str(file_service_path))
    
    # Write config loader
    config_path = base_dir / 'src' / 'config' / 'config_loader.py'
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_loader)
    files_created.append(str(config_path))
    
    return files_created

if __name__ == "__main__":
    logger.info("Creating missing files...")
    created = create_missing_files()
    
    logger.info(f"Created {len(created)} files:")
    for file_path in created:
        logger.info(f"  [OK] {file_path}")
    
    logger.info("Missing files created successfully!")