# -*- coding: utf-8 -*-
"""
File management utilities for Docker Performance Monitor
"""

import os
import shutil
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FileManager:
    """File management utilities"""
    
    @staticmethod
    def ensure_directory(path: Path) -> bool:
        """Ensure directory exists"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.info(f"Error creating directory {path}: {e}")
            return False
    
    @staticmethod
    def backup_file(source: Path, backup_dir: Path) -> bool:
        """Create backup of file"""
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.stem}_{timestamp}{source.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(source, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            logger.info(f"Error creating backup: {e}")
            return False
    
    @staticmethod
    def cleanup_old_files(directory: Path, days: int = 7) -> int:
        """Remove files older than specified days"""
        try:
            if not directory.exists():
                return 0
                
            cutoff_time = datetime.now() - timedelta(days=days)
            removed_count = 0
            
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        removed_count += 1
            
            logger.info(f"Cleaned {removed_count} old files from {directory}")
            return removed_count
        except Exception as e:
            logger.info(f"Error cleaning files: {e}")
            return 0
    
    @staticmethod
    def get_directory_size(directory: Path) -> Dict[str, int]:
        """Get directory size information"""
        try:
            if not directory.exists():
                return {'total_files': 0, 'total_size': 0}
                
            total_size = 0
            file_count = 0
            
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size
            
            return {
                'total_files': file_count,
                'total_size': total_size,
                'total_size_mb': total_size / (1024 * 1024)
            }
        except Exception as e:
            logger.info(f"Error getting directory size: {e}")
            return {'total_files': 0, 'total_size': 0}
    
    @staticmethod
    def export_data(data: dict, filename: Path, format_type: str = 'json') -> bool:
        """Export data to file"""
        try:
            filename.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type.lower() == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format_type.lower() == 'csv':
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    if isinstance(data, list) and data:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                    else:
                        writer = csv.DictWriter(f, fieldnames=data.keys())
                        writer.writeheader()
                        writer.writerow(data)
            
            logger.info(f"Data exported to {filename}")
            return True
        except Exception as e:
            logger.info(f"Error exporting data: {e}")
            return False