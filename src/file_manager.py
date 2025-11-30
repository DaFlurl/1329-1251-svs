#!/usr/bin/env python3
"""
Optimized File Management Module for AgentDaf1.1

Provides efficient file operations with proper error handling,
logging, and cleanup capabilities.
"""

import os
import shutil
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import threading
import time

logger = logging.getLogger(__name__)

class FileManager:
    """Optimized file management with caching and cleanup."""
    
    def __init__(self, base_dir: str):
        """Initialize file manager."""
        self.base_dir = Path(base_dir)
        self.file_cache = {}
        self.cache_lock = threading.Lock()
        self.max_cache_size = 100
        self.max_file_age_days = 7
        logger.info(f"FileManager initialized with base_dir: {base_dir}")
    
    def ensure_directory(self, directory: str) -> Path:
        """Ensure directory exists with proper permissions."""
        dir_path = self.base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    def cleanup_old_files(self, directory: str, pattern: str = "*") -> Dict[str, int]:
        """Clean up old files based on age and pattern."""
        try:
            dir_path = self.ensure_directory(directory)
            current_time = datetime.now()
            cleaned_count = 0
            
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_age.days > self.max_file_age_days:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info(f"Removed old file: {file_path}")
            
            logger.info(f"Cleaned {cleaned_count} files from {directory}")
            return {'cleaned_files': cleaned_count}
            
        except Exception as e:
            logger.error(f'Cleanup failed: {str(e)}')
            return {'error': str(e)}
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {'error': 'File not found'}
            
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'extension': path.suffix.lower(),
                'readable_size': self._format_size(stat.st_size)
            }
            
        except Exception as e:
            logger.error(f'Error getting file info: {str(e)}')
            return {'error': str(e)}
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes} {unit}"
            size_bytes /= 1024
            if size_bytes < 1024:
                return f"{size_bytes:.1f} KB"
            size_bytes /= 1024
            if size_bytes < 1024:
                return f"{size_bytes:.1f} MB"
            size_bytes /= 1024
            return f"{size_bytes:.1f} GB"
    
    def optimize_storage(self) -> Dict[str, Any]:
        """Optimize storage usage and clean up old files."""
        try:
            # Clean up old files from different directories
            directories = ['uploads', 'logs', 'data']
            total_cleaned = 0
            
            for directory in directories:
                result = self.cleanup_old_files(directory)
                if 'cleaned_files' in result:
                    total_cleaned += result['cleaned_files']
            
            # Get storage statistics
            storage_info = self._get_storage_stats()
            
            optimization_result = {
                'success': True,
                'cleaned_files': total_cleaned,
                'storage_stats': storage_info,
                'optimization_time': datetime.now().isoformat()
            }
            
            logger.info(f"Storage optimization completed: {total_cleaned} files cleaned")
            return optimization_result
            
        except Exception as e:
            logger.error(f'Storage optimization failed: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _get_storage_stats(self) -> Dict[str, Any]:
        """Get current storage statistics."""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'directory_stats': {}
            }
            
            directories = ['uploads', 'logs', 'data']
            
            for directory in directories:
                dir_path = self.base_dir / directory
                if dir_path.exists():
                    file_count = 0
                    dir_size = 0
                    
                    for file_path in dir_path.rglob("*"):
                        if file_path.is_file():
                            file_count += 1
                            dir_size += file_path.stat().st_size
                    
                    stats['directory_stats'][directory] = {
                        'file_count': file_count,
                        'size_bytes': dir_size,
                        'size_readable': self._format_size(dir_size)
                    }
                    
                    stats['total_files'] += file_count
                    stats['total_size'] += dir_size
            
            stats['total_size_readable'] = self._format_size(stats['total_size'])
            
            return stats
            
        except Exception as e:
            logger.error(f'Error getting storage stats: {str(e)}')
            return {'error': str(e)}
    
    def backup_file(self, file_path: str, backup_dir: str = "backups") -> Dict[str, Any]:
        """Create backup of specified file."""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return {'error': 'Source file not found'}
            
            backup_path = self.ensure_directory(backup_dir) / f"{source_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{source_path.suffix}"
            
            shutil.copy2(source_path, backup_path)
            
            result = {
                'success': True,
                'backup_path': str(backup_path),
                'original_path': file_path,
                'backup_time': datetime.now().isoformat()
            }
            
            logger.info(f"File backed up: {file_path} -> {backup_path}")
            return result
            
        except Exception as e:
            logger.error(f'Backup failed: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def monitor_directory_changes(self, directory: str, callback=None) -> None:
        """Monitor directory for changes (placeholder for future implementation)."""
        # This would implement file system monitoring
        # For now, just log that monitoring is requested
        logger.info(f"Directory monitoring requested for: {directory}")
        pass