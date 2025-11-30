"""
File Manager Tool for AgentDaf1.1
Advanced file operations, monitoring, and management
"""

import os
import shutil
import hashlib
import json
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """File information data structure"""
    path: str
    name: str
    size: int
    modified_time: float
    created_time: float
    file_type: str
    extension: str
    md5_hash: Optional[str] = None
    is_directory: bool = False
    permissions: str = ""

@dataclass
class FileOperation:
    """File operation record"""
    operation: str
    source: str
    destination: Optional[str]
    timestamp: float
    success: bool
    error: Optional[str] = None

class FileWatcher(FileSystemEventHandler):
    """File system event handler"""
    
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback
        super().__init__()
    
    def on_modified(self, event):
        if not event.is_directory and hasattr(event, 'src_path') and event.src_path:
            self.callback("modified", event.src_path)
    
    def on_created(self, event):
        if not event.is_directory and hasattr(event, 'src_path') and event.src_path:
            self.callback("created", event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and hasattr(event, 'src_path') and event.src_path:
            self.callback("deleted", event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory and hasattr(event, 'src_path') and event.src_path and hasattr(event, 'dest_path') and event.dest_path:
            self.callback("moved", f"{event.src_path} -> {event.dest_path}")

class FileManager:
    """Advanced file management system"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.operations_history: List[FileOperation] = []
        self.watched_paths: Dict[str, Observer] = {}
        self.callbacks: List[Callable] = []
        
    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """Get detailed file information"""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return None
            
            stat = path_obj.stat()
            
            file_info = FileInfo(
                path=str(path_obj.absolute()),
                name=path_obj.name,
                size=stat.st_size,
                modified_time=stat.st_mtime,
                created_time=stat.st_ctime,
                file_type="directory" if path_obj.is_dir() else "file",
                extension=path_obj.suffix.lower() if path_obj.is_file() else "",
                is_directory=path_obj.is_dir(),
                permissions=oct(stat.st_mode)[-3:]
            )
            
            # Calculate MD5 hash for files (only for files < 10MB)
            if path_obj.is_file() and stat.st_size < 10 * 1024 * 1024:
                file_info.md5_hash = self._calculate_md5(path_obj)
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating MD5 for {file_path}: {e}")
            return ""
    
    def list_directory(self, directory: str = None, 
                      recursive: bool = False,
                      include_hidden: bool = False,
                      file_filter: str = None) -> List[FileInfo]:
        """List directory contents"""
        try:
            dir_path = Path(directory) if directory else self.base_path
            
            if not dir_path.exists() or not dir_path.is_dir():
                return []
            
            files = []
            
            if recursive:
                pattern = "**/*"
                if file_filter:
                    pattern = f"**/{file_filter}"
                paths = dir_path.glob(pattern)
            else:
                pattern = "*"
                if file_filter:
                    pattern = file_filter
                paths = dir_path.glob(pattern)
            
            for path in paths:
                if not include_hidden and path.name.startswith('.'):
                    continue
                
                file_info = self.get_file_info(str(path))
                if file_info:
                    files.append(file_info)
            
            return sorted(files, key=lambda x: (not x.is_directory, x.name.lower()))
            
        except Exception as e:
            logger.error(f"Error listing directory {directory}: {e}")
            return []
    
    def copy_file(self, source: str, destination: str, 
                 overwrite: bool = False) -> bool:
        """Copy file or directory"""
        operation = FileOperation(
            operation="copy",
            source=source,
            destination=destination,
            timestamp=time.time(),
            success=False
        )
        
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                raise FileNotFoundError(f"Source not found: {source}")
            
            if dest_path.exists() and not overwrite:
                raise FileExistsError(f"Destination exists: {destination}")
            
            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=overwrite)
            else:
                shutil.copy2(source_path, dest_path)
            
            operation.success = True
            logger.info(f"Copied {source} to {destination}")
            
        except Exception as e:
            operation.error = str(e)
            logger.error(f"Error copying {source} to {destination}: {e}")
        
        self.operations_history.append(operation)
        return operation.success
    
    def move_file(self, source: str, destination: str,
                 overwrite: bool = False) -> bool:
        """Move file or directory"""
        operation = FileOperation(
            operation="move",
            source=source,
            destination=destination,
            timestamp=time.time(),
            success=False
        )
        
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                raise FileNotFoundError(f"Source not found: {source}")
            
            if dest_path.exists() and not overwrite:
                raise FileExistsError(f"Destination exists: {destination}")
            
            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))
            
            operation.success = True
            logger.info(f"Moved {source} to {destination}")
            
        except Exception as e:
            operation.error = str(e)
            logger.error(f"Error moving {source} to {destination}: {e}")
        
        self.operations_history.append(operation)
        return operation.success
    
    def delete_file(self, file_path: str, permanent: bool = False) -> bool:
        """Delete file or directory"""
        operation = FileOperation(
            operation="delete",
            source=file_path,
            destination=None,
            timestamp=time.time(),
            success=False
        )
        
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                raise FileNotFoundError(f"Path not found: {file_path}")
            
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()
            
            operation.success = True
            logger.info(f"Deleted {file_path}")
            
        except Exception as e:
            operation.error = str(e)
            logger.error(f"Error deleting {file_path}: {e}")
        
        self.operations_history.append(operation)
        return operation.success
    
    def create_directory(self, directory: str, parents: bool = True) -> bool:
        """Create directory"""
        operation = FileOperation(
            operation="create_directory",
            source=directory,
            destination=None,
            timestamp=time.time(),
            success=False
        )
        
        try:
            dir_path = Path(directory)
            dir_path.mkdir(parents=parents, exist_ok=True)
            
            operation.success = True
            logger.info(f"Created directory: {directory}")
            
        except Exception as e:
            operation.error = str(e)
            logger.error(f"Error creating directory {directory}: {e}")
        
        self.operations_history.append(operation)
        return operation.success
    
    def find_duplicates(self, directory: str = None) -> Dict[str, List[str]]:
        """Find duplicate files by MD5 hash"""
        try:
            dir_path = Path(directory) if directory else self.base_path
            hash_map: Dict[str, List[str]] = {}
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    file_info = self.get_file_info(str(file_path))
                    if file_info and file_info.md5_hash:
                        if file_info.md5_hash not in hash_map:
                            hash_map[file_info.md5_hash] = []
                        hash_map[file_info.md5_hash].append(str(file_path))
            
            # Return only duplicates
            return {h: files for h, files in hash_map.items() if len(files) > 1}
            
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return {}
    
    def get_directory_size(self, directory: str = None) -> Dict[str, Any]:
        """Get directory size statistics"""
        try:
            dir_path = Path(directory) if directory else self.base_path
            
            total_size = 0
            file_count = 0
            dir_count = 0
            extension_counts: Dict[str, int] = {}
            
            for path in dir_path.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
                    file_count += 1
                    
                    ext = path.suffix.lower()
                    if ext:
                        extension_counts[ext] = extension_counts.get(ext, 0) + 1
                elif path.is_dir():
                    dir_count += 1
            
            return {
                "total_size": total_size,
                "total_size_mb": total_size / 1024 / 1024,
                "total_size_gb": total_size / 1024 / 1024 / 1024,
                "file_count": file_count,
                "directory_count": dir_count,
                "extension_counts": extension_counts,
                "largest_extensions": sorted(extension_counts.items(), 
                                          key=lambda x: x[1], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Error getting directory size: {e}")
            return {}
    
    def start_watching(self, directory: str, callback: Callable[[str, str], None]) -> bool:
        """Start watching directory for changes"""
        try:
            if directory in self.watched_paths:
                logger.warning(f"Already watching {directory}")
                return False
            
            observer = Observer()
            event_handler = FileWatcher(callback)
            observer.schedule(event_handler, directory, recursive=True)
            observer.start()
            
            self.watched_paths[directory] = observer
            logger.info(f"Started watching {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting to watch {directory}: {e}")
            return False
    
    def stop_watching(self, directory: str) -> bool:
        """Stop watching directory"""
        try:
            if directory not in self.watched_paths:
                logger.warning(f"Not watching {directory}")
                return False
            
            observer = self.watched_paths[directory]
            observer.stop()
            observer.join()
            
            del self.watched_paths[directory]
            logger.info(f"Stopped watching {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping watch for {directory}: {e}")
            return False
    
    def stop_all_watching(self):
        """Stop all directory watching"""
        for directory in list(self.watched_paths.keys()):
            self.stop_watching(directory)
    
    def get_operations_history(self, hours: int = 24) -> List[FileOperation]:
        """Get file operations history"""
        cutoff_time = time.time() - (hours * 3600)
        return [op for op in self.operations_history if op.timestamp >= cutoff_time]
    
    def save_file_index(self, directory: str = None, output_file: str = None) -> bool:
        """Save file index to JSON file"""
        try:
            files = self.list_directory(directory, recursive=True)
            
            if not output_file:
                output_file = f"file_index_{int(time.time())}.json"
            
            data = {
                "generated_at": time.time(),
                "directory": directory or str(self.base_path),
                "files": [asdict(file_info) for file_info in files],
                "total_files": len(files),
                "total_size": sum(f.size for f in files)
            }
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"File index saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving file index: {e}")
            return False
    
    def cleanup_temp_files(self, max_age_days: int = 7) -> Dict[str, Any]:
        """Clean up temporary files"""
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 3600)
            deleted_files = []
            total_size_freed = 0
            
            temp_patterns = [
                "**/*.tmp",
                "**/*.temp",
                "**/*~",
                "**/.DS_Store",
                "**/Thumbs.db"
            ]
            
            for pattern in temp_patterns:
                for file_path in self.base_path.glob(pattern):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        size = file_path.stat().st_size
                        if self.delete_file(str(file_path)):
                            deleted_files.append(str(file_path))
                            total_size_freed += size
            
            return {
                "deleted_files": len(deleted_files),
                "size_freed": total_size_freed,
                "size_freed_mb": total_size_freed / 1024 / 1024,
                "files": deleted_files
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
            return {"deleted_files": 0, "size_freed": 0, "files": []}

# Global file manager instance
file_manager = FileManager()