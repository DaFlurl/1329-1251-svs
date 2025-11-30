#!/usr/bin/env python3
"""
AgentDaf1.1 Backup and Recovery System
Automated backup creation and recovery functionality
"""

import os
import shutil
import json
import sqlite3
import zipfile
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

class BackupManager:
    """Backup and recovery manager for AgentDaf1.1"""
    
    def __init__(self, backup_dir: str = "backups", retention_days: int = 30):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.retention_days = retention_days
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup backup logger"""
        logger = logging.getLogger('backup_manager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.backup_dir / 'backup.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def create_full_backup(self, include_config: bool = True) -> Dict[str, Any]:
        """Create full system backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"agentdaf1_full_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        backup_info = {
            'backup_name': backup_name,
            'timestamp': timestamp,
            'backup_path': str(backup_path),
            'type': 'full',
            'components': []
        }
        
        try:
            # Backup database
            db_backup = self._backup_database(backup_path)
            if db_backup:
                backup_info['components'].append(db_backup)
            
            # Backup configuration files
            if include_config:
                config_backup = self._backup_config(backup_path)
                if config_backup:
                    backup_info['components'].append(config_backup)
            
            # Backup application files
            app_backup = self._backup_application(backup_path)
            if app_backup:
                backup_info['components'].append(app_backup)
            
            # Create backup metadata
            metadata_path = backup_path / 'backup_metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            # Create compressed archive
            archive_path = self._create_archive(backup_path)
            backup_info['archive_path'] = str(archive_path)
            backup_info['archive_size_mb'] = round(archive_path.stat().st_size / (1024 * 1024), 2)
            
            # Remove uncompressed directory
            shutil.rmtree(backup_path)
            
            self.logger.info(f"Full backup created: {backup_name}")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            # Cleanup on failure
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise
    
    def _backup_database(self, backup_path: Path) -> Optional[Dict]:
        """Backup database files"""
        try:
            db_backup_dir = backup_path / 'database'
            db_backup_dir.mkdir(exist_ok=True)
            
            # Backup main database
            if os.path.exists('data/agentdaf1.db'):
                shutil.copy2('data/agentdaf1.db', db_backup_dir / 'agentdaf1.db')
            
            # Backup any additional database files
            data_dir = Path('data')
            if data_dir.exists():
                for db_file in data_dir.glob('*.db'):
                    if db_file.name != 'agentdaf1.db':
                        shutil.copy2(db_file, db_backup_dir / db_file.name)
            
            return {
                'component': 'database',
                'files_copied': len(list(db_backup_dir.glob('*.db'))),
                'size_mb': sum(f.stat().st_size for f in db_backup_dir.glob('*.db')) / (1024 * 1024)
            }
        except Exception as e:
            self.logger.error(f"Database backup failed: {str(e)}")
            return None
    
    def _backup_config(self, backup_path: Path) -> Optional[Dict]:
        """Backup configuration files"""
        try:
            config_backup_dir = backup_path / 'config'
            config_backup_dir.mkdir(exist_ok=True)
            
            config_files = [
                '.env', '.env.production',
                'gunicorn.conf.py', 'nginx-production.conf',
                'agentdaf1.service', 'requirements-production.txt'
            ]
            
            copied_files = []
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, config_backup_dir / config_file)
                    copied_files.append(config_file)
            
            # Backup config directory if exists
            if os.path.exists('config'):
                shutil.copytree('config', config_backup_dir / 'config_dir', dirs_exist_ok=True)
            
            return {
                'component': 'configuration',
                'files_copied': len(copied_files),
                'files': copied_files
            }
        except Exception as e:
            self.logger.error(f"Config backup failed: {str(e)}")
            return None
    
    def _backup_application(self, backup_path: Path) -> Optional[Dict]:
        """Backup core application files"""
        try:
            app_backup_dir = backup_path / 'application'
            app_backup_dir.mkdir(exist_ok=True)
            
            # Core application files
            core_files = [
                'simple_app.py', 'wsgi.py', 'database.py', 'auth.py',
                'test_production.py', 'PRODUCTION_DEPLOYMENT.md'
            ]
            
            copied_files = []
            for app_file in core_files:
                if os.path.exists(app_file):
                    shutil.copy2(app_file, app_backup_dir / app_file)
                    copied_files.append(app_file)
            
            # Backup src directory if exists
            if os.path.exists('src'):
                shutil.copytree('src', app_backup_dir / 'src', dirs_exist_ok=True)
            
            return {
                'component': 'application',
                'files_copied': len(copied_files),
                'files': copied_files
            }
        except Exception as e:
            self.logger.error(f"Application backup failed: {str(e)}")
            return None
    
    def _create_archive(self, backup_path: Path) -> Path:
        """Create compressed archive of backup"""
        archive_path = self.backup_dir / f"{backup_path.name}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_path)
                    zipf.write(file_path, arcname)
        
        return archive_path
    
    def restore_backup(self, backup_name: str, components: List[str] = None) -> Dict[str, Any]:
        """Restore from backup"""
        backup_archive = self.backup_dir / f"{backup_name}.zip"
        
        if not backup_archive.exists():
            raise FileNotFoundError(f"Backup archive not found: {backup_name}")
        
        # Extract backup
        temp_extract_dir = self.backup_dir / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        temp_extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(backup_archive, 'r') as zipf:
                zipf.extractall(temp_extract_dir)
            
            # Read backup metadata
            metadata_path = temp_extract_dir / 'backup_metadata.json'
            with open(metadata_path, 'r') as f:
                backup_info = json.load(f)
            
            restore_info = {
                'backup_name': backup_name,
                'timestamp': backup_info['timestamp'],
                'restored_components': [],
                'errors': []
            }
            
            # Restore components
            for component in backup_info['components']:
                comp_name = component['component']
                
                if components and comp_name not in components:
                    continue
                
                try:
                    if comp_name == 'database':
                        self._restore_database(temp_extract_dir / 'database')
                    elif comp_name == 'configuration':
                        self._restore_config(temp_extract_dir / 'config')
                    elif comp_name == 'application':
                        self._restore_application(temp_extract_dir / 'application')
                    
                    restore_info['restored_components'].append(comp_name)
                    
                except Exception as e:
                    restore_info['errors'].append(f"{comp_name}: {str(e)}")
                    self.logger.error(f"Restore {comp_name} failed: {str(e)}")
            
            self.logger.info(f"Backup restored: {backup_name}")
            return restore_info
            
        finally:
            # Cleanup temp directory
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
    
    def _restore_database(self, db_backup_dir: Path):
        """Restore database files"""
        if not db_backup_dir.exists():
            return
        
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        # Copy database files
        for db_file in db_backup_dir.glob('*.db'):
            shutil.copy2(db_file, data_dir / db_file.name)
    
    def _restore_config(self, config_backup_dir: Path):
        """Restore configuration files"""
        if not config_backup_dir.exists():
            return
        
        # Copy individual config files
        for config_file in config_backup_dir.glob('*'):
            if config_file.is_file() and config_file.name != 'backup_metadata.json':
                shutil.copy2(config_file, config_file.name)
        
        # Restore config directory if exists
        config_dir = config_backup_dir / 'config_dir'
        if config_dir.exists():
            shutil.copytree(config_dir, 'config', dirs_exist_ok=True)
    
    def _restore_application(self, app_backup_dir: Path):
        """Restore application files"""
        if not app_backup_dir.exists():
            return
        
        # Copy application files
        for app_file in app_backup_dir.glob('*'):
            if app_file.is_file():
                shutil.copy2(app_file, app_file.name)
            elif app_file.is_dir() and app_file.name == 'src':
                shutil.copytree(app_file, 'src', dirs_exist_ok=True)
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob('*.zip'):
            try:
                # Extract metadata from zip
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    if 'backup_metadata.json' in zipf.namelist():
                        with zipf.open('backup_metadata.json') as f:
                            metadata = json.load(f)
                        
                        backups.append({
                            'name': backup_file.stem,
                            'timestamp': metadata['timestamp'],
                            'type': metadata['type'],
                            'components': [c['component'] for c in metadata['components']],
                            'size_mb': round(backup_file.stat().st_size / (1024 * 1024), 2),
                            'created_at': datetime.fromtimestamp(backup_file.stat().st_ctime)
                        })
            except Exception as e:
                self.logger.warning(f"Could not read backup metadata for {backup_file.name}: {str(e)}")
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """Remove old backups beyond retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        removed_backups = []
        
        for backup_file in self.backup_dir.glob('*.zip'):
            if datetime.fromtimestamp(backup_file.stat().st_ctime) < cutoff_date:
                try:
                    backup_file.unlink()
                    removed_backups.append(backup_file.name)
                    self.logger.info(f"Removed old backup: {backup_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to remove backup {backup_file.name}: {str(e)}")
        
        return {
            'removed_count': len(removed_backups),
            'removed_backups': removed_backups,
            'retention_days': self.retention_days
        }
    
    def schedule_automatic_backups(self, schedule_type: str = 'daily', time: str = '02:00'):
        """Schedule automatic backups"""
        if schedule_type == 'daily':
            schedule.every().day.at(time).do(self._scheduled_backup)
        elif schedule_type == 'weekly':
            schedule.every().week.at(time).do(self._scheduled_backup)
        elif schedule_type == 'hourly':
            schedule.every().hour.do(self._scheduled_backup)
        
        self.logger.info(f"Scheduled {schedule_type} backups at {time}")
    
    def _scheduled_backup(self):
        """Execute scheduled backup"""
        try:
            backup_info = self.create_full_backup()
            self.logger.info(f"Scheduled backup completed: {backup_info['backup_name']}")
            
            # Cleanup old backups
            cleanup_info = self.cleanup_old_backups()
            if cleanup_info['removed_count'] > 0:
                self.logger.info(f"Cleaned up {cleanup_info['removed_count']} old backups")
                
        except Exception as e:
            self.logger.error(f"Scheduled backup failed: {str(e)}")
    
    def start_scheduler(self):
        """Start the backup scheduler"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Global backup manager instance
backup_manager = BackupManager()

def get_backup_manager() -> BackupManager:
    """Get global backup manager instance"""
    return backup_manager

# CLI interface for backup operations
def backup_cli():
    """Command line interface for backup operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AgentDaf1.1 Backup Manager')
    parser.add_argument('action', choices=['create', 'list', 'restore', 'cleanup', 'schedule'])
    parser.add_argument('--name', help='Backup name for restore')
    parser.add_argument('--components', nargs='+', help='Components to restore')
    parser.add_argument('--schedule-type', choices=['daily', 'weekly', 'hourly'], default='daily')
    parser.add_argument('--time', default='02:00', help='Schedule time (HH:MM)')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        backup_info = backup_manager.create_full_backup()
        logger.info(f"Backup created: {backup_info['backup_name']}")
        logger.info(f"Archive: {backup_info['archive_path']}")
        logger.info(f"Size: {backup_info['archive_size_mb']} MB")
    
    elif args.action == 'list':
        backups = backup_manager.list_backups()
        logger.info(f"Found {len(backups)} backups:")
        for backup in backups:
            logger.info(f"  {backup['name']} - {backup['created_at']} - {backup['size_mb']} MB")
    
    elif args.action == 'restore':
        if not args.name:
            logger.info("Error: --name required for restore")
            return
        
        restore_info = backup_manager.restore_backup(args.name, args.components)
        logger.info(f"Restored backup: {restore_info['backup_name']}")
        logger.info(f"Components: {', '.join(restore_info['restored_components'])}")
        if restore_info['errors']:
            logger.info(f"Errors: {', '.join(restore_info['errors'])}")
    
    elif args.action == 'cleanup':
        cleanup_info = backup_manager.cleanup_old_backups()
        logger.info(f"Removed {cleanup_info['removed_count']} old backups")
    
    elif args.action == 'schedule':
        backup_manager.schedule_automatic_backups(args.schedule_type, args.time)
        logger.info(f"Scheduled {args.schedule_type} backups at {args.time}")
        logger.info("Scheduler started... (Press Ctrl+C to stop)")
        backup_manager.start_scheduler()

if __name__ == "__main__":
    backup_cli()