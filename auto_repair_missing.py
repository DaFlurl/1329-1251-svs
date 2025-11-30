#!/usr/bin/env python3
"""
Auto-Repair Script for AgentDaf1.1
Automatically fixes missing files and issues
"""

import os
import sys
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoRepair:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.repaired_files = []
        self.removed_files = []
        self.errors = []
        
    def check_missing_files(self):
        """Check for missing files that are referenced but don't exist"""
        missing_files = []
        
        # Files that are referenced but missing
        referenced_files = [
            'services/notification_service.py',
            'services/file_service.py', 
            'src/config/config_loader.py'
        ]
        
        for file_path in referenced_files:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                
        return missing_files
    
    def create_notification_service(self):
        """Create notification service if needed"""
        service_path = self.base_dir / 'services' / 'notification_service.py'
        
        content = '''# -*- coding: utf-8 -*-
"""
Notification Service for AgentDaf1.1
Handles system notifications and alerts
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.notifications = []
        self.logger = logging.getLogger(__name__)
        
    def send_notification(self, title: str, message: str, level: str = "info") -> bool:
        """Send a notification"""
        try:
            notification = {
                "id": len(self.notifications) + 1,
                "title": title,
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            self.notifications.append(notification)
            self.logger.info(f"Notification sent: {title} - {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
    
    def get_notifications(self, limit: int = 50, unread_only: bool = False) -> List[Dict]:
        """Get notifications"""
        notifications = self.notifications
        
        if unread_only:
            notifications = [n for n in notifications if not n["read"]]
            
        return notifications[-limit:] if limit > 0 else notifications
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        try:
            for notification in self.notifications:
                if notification["id"] == notification_id:
                    notification["read"] = True
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    def clear_notifications(self) -> bool:
        """Clear all notifications"""
        try:
            self.notifications.clear()
            self.logger.info("All notifications cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear notifications: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        total = len(self.notifications)
        unread = len([n for n in self.notifications if not n["read"]])
        
        return {
            "total_notifications": total,
            "unread_notifications": unread,
            "read_notifications": total - unread
        }

# Global instance
notification_service = NotificationService()
'''
        
        try:
            service_path.parent.mkdir(parents=True, exist_ok=True)
            with open(service_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.repaired_files.append(str(service_path))
            logger.info(f"Created notification service: {service_path}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to create notification service: {e}")
            return False
    
    def create_file_service(self):
        """Create file service if needed"""
        service_path = self.base_dir / 'services' / 'file_service.py'
        
        content = '''# -*- coding: utf-8 -*-
"""
File Service for AgentDaf1.1
Handles file operations and management
"""

import os
import shutil
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class FileService:
    """Service for managing files"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.logger = logging.getLogger(__name__)
        
    def upload_file(self, file_data: bytes, filename: str, folder: str = "uploads") -> Dict[str, Any]:
        """Upload a file"""
        try:
            upload_dir = self.base_dir / folder
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / filename
            
            # Handle duplicate filenames
            counter = 1
            original_name = filename
            while file_path.exists():
                stem = Path(original_name).stem
                suffix = Path(original_name).suffix
                filename = f"{stem}_{counter}{suffix}"
                file_path = upload_dir / filename
                counter += 1
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Calculate file hash
            file_hash = hashlib.md5(file_data).hexdigest()
            
            # Get file info
            file_info = {
                "filename": filename,
                "original_name": original_name,
                "path": str(file_path),
                "size": len(file_data),
                "hash": file_hash,
                "upload_time": datetime.now().isoformat(),
                "folder": folder
            }
            
            self.logger.info(f"File uploaded: {filename}")
            return {"success": True, "file_info": file_info}
            
        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}")
            return {"success": False, "error": str(e)}
    
    def list_files(self, folder: str = "uploads") -> List[Dict[str, Any]]:
        """List files in a folder"""
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
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "folder": folder
                    })
            
            return sorted(files, key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
    
    def delete_file(self, filename: str, folder: str = "uploads") -> bool:
        """Delete a file"""
        try:
            file_path = self.base_dir / folder / filename
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"File deleted: {filename}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete file: {e}")
            return False
    
    def get_file_info(self, filename: str, folder: str = "uploads") -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            file_path = self.base_dir / folder / filename
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            return {
                "filename": filename,
                "path": str(file_path),
                "size": stat.st_size,
                "hash": file_hash,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "folder": folder
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            return None
    
    def cleanup_old_files(self, folder: str = "uploads", days: int = 30) -> int:
        """Clean up old files"""
        try:
            folder_path = self.base_dir / folder
            if not folder_path.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            deleted_count = 0
            
            for file_path in folder_path.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup files: {e}")
            return 0

# Global instance
file_service = FileService()
'''
        
        try:
            service_path.parent.mkdir(parents=True, exist_ok=True)
            with open(service_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.repaired_files.append(str(service_path))
            logger.info(f"Created file service: {service_path}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to create file service: {e}")
            return False
    
    def create_config_loader(self):
        """Create config loader if needed"""
        config_path = self.base_dir / 'src' / 'config' / 'config_loader.py'
        
        content = '''# -*- coding: utf-8 -*-
"""
Configuration Loader for AgentDaf1.1
Handles loading and managing configuration files
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """Configuration loader and manager"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.logger = logging.getLogger(__name__)
        self.configs = {}
        
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load a configuration file"""
        try:
            config_path = self.config_dir / f"{config_name}.json"
            
            if not config_path.exists():
                self.logger.warning(f"Config file not found: {config_path}")
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
        """Save a configuration file"""
        try:
            config_path = self.config_dir / f"{config_name}.json"
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.configs[config_name] = config
            self.logger.info(f"Saved config: {config_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config {config_name}: {e}")
            return False
    
    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get a loaded configuration"""
        return self.configs.get(config_name)
    
    def reload_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Reload a configuration file"""
        return self.load_config(config_name)
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded configurations"""
        return self.configs.copy()
    
    def load_env_config(self) -> Dict[str, Any]:
        """Load environment configuration"""
        env_config = {}
        
        # Common environment variables
        env_vars = [
            'FLASK_ENV',
            'FLASK_DEBUG', 
            'DATABASE_URL',
            'SECRET_KEY',
            'UPLOAD_FOLDER',
            'LOG_LEVEL',
            'PORT',
            'HOST'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value is not None:
                env_config[var] = value
        
        self.logger.info("Loaded environment configuration")
        return env_config
    
    def merge_configs(self, *config_names: str) -> Dict[str, Any]:
        """Merge multiple configurations"""
        merged = {}
        
        for config_name in config_names:
            config = self.get_config(config_name)
            if config:
                merged.update(config)
        
        return merged
    
    def validate_config(self, config: Dict[str, Any], required_keys: List[str]) -> bool:
        """Validate configuration has required keys"""
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            self.logger.error(f"Missing required config keys: {missing_keys}")
            return False
        
        return True

# Global instance
config_loader = ConfigLoader()
'''
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.repaired_files.append(str(config_path))
            logger.info(f"Created config loader: {config_path}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to create config loader: {e}")
            return False
    
    def remove_unused_imports(self):
        """Remove unused imports and clean up files"""
        # This would analyze and remove unused imports
        # For now, just log that this would happen
        logger.info("Unused import cleanup would be performed here")
    
    def fix_import_errors(self):
        """Fix common import errors"""
        fixes = []
        
        # Common import fixes
        import_fixes = {
            'from src.core.excel_processor': 'from .excel_processor',
            'from src.core.dashboard_generator': 'from .dashboard_generator', 
            'from src.config.settings': 'from .settings',
            'from src.tools.neural_memory': 'from .neural_memory',
            'from src.tools.ai_tools': 'from .ai_tools'
        }
        
        for file_path in self.base_dir.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for old_import, new_import in import_fixes.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                        fixes.append(f"{file_path}: {old_import} -> {new_import}")
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
            except Exception as e:
                self.errors.append(f"Failed to fix imports in {file_path}: {e}")
        
        return fixes
    
    def run_auto_repair(self):
        """Run complete auto-repair process"""
        logger.info("Starting auto-repair process...")
        
        # Check missing files
        missing_files = self.check_missing_files()
        
        if missing_files:
            logger.info(f"Found missing files: {missing_files}")
            
            # Create missing files
            for missing_file in missing_files:
                if 'notification_service.py' in missing_file:
                    self.create_notification_service()
                elif 'file_service.py' in missing_file:
                    self.create_file_service()
                elif 'config_loader.py' in missing_file:
                    self.create_config_loader()
        
        # Fix import errors
        import_fixes = self.fix_import_errors()
        if import_fixes:
            logger.info(f"Fixed {len(import_fixes)} import issues")
        
        # Clean up
        self.remove_unused_imports()
        
        logger.info("Auto-repair process completed")
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate repair report"""
        return {
            "repaired_files": self.repaired_files,
            "removed_files": self.removed_files,
            "errors": self.errors,
            "summary": {
                "files_repaired": len(self.repaired_files),
                "files_removed": len(self.removed_files),
                "errors": len(self.errors)
            }
        }

def main():
    """Main auto-repair function"""
    logger.info("AgentDaf1.1 Auto-Repair Tool")
    logger.info("============================")
    
    # Get base directory
    base_dir = input("Enter base directory (press Enter for current): ").strip()
    if not base_dir:
        base_dir = Path.cwd()
    
    # Run auto-repair
    repair = AutoRepair(base_dir)
    repair.run_auto_repair()
    
    # Generate report
    report = repair.generate_report()
    
    logger.info("/nAuto-Repair Results:")
    logger.info(f"✅ Files Repaired: {report['summary']['files_repaired']}")
    logger.info(f"🗑️  Files Removed: {report['summary']['files_removed']}")
    logger.info(f"❌ Errors: {report['summary']['errors']}")
    
    if report['repaired_files']:
        logger.info("/nRepaired Files:")
        for file_path in report['repaired_files']:
            logger.info(f"  ✅ {file_path}")
    
    if report['errors']:
        logger.info("/nErrors:")
        for error in report['errors']:
            logger.info(f"  ❌ {error}")

if __name__ == "__main__":
    main()