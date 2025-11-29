#!/usr/bin/env python3
"""
File History and Memory Management System for AgentDaf1 Scoreboard
Tracks all changes, creates backups, and maintains version history
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import hashlib
from typing import Dict, Any, List, Optional

class FileHistoryManager:
    """Manages file history, backups, and version control"""
    
    def __init__(self, base_dir: str = "C://Users//flori//Desktop//AgentDaf1//github-dashboard"):
        self.base_dir = Path(base_dir)
        self.history_dir = self.base_dir / "file_history"
        self.history_file = self.history_dir / "file_history.json"
        self.backups_dir = self.history_dir / "backups"
        
        # Create directories if they don't exist
        self.history_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
        
        # Initialize history file if it doesn't exist
        self.init_history()
        
    def init_history(self) -> None:
        """Initialize history tracking file"""
        if not self.history_file.exists():
            initial_history = {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_changes": 0,
                "files": {}
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(initial_history, f, indent=2, ensure_ascii=False)
    
    def load_history(self) -> Dict[str, Any]:
        """Load current history"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return {"files": {}}
    
    def save_history(self, history: Dict[str, Any]) -> bool:
        """Save history file"""
        try:
            history["last_updated"] = datetime.now().isoformat()
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def backup_file(self, file_path: str, description: str = "") -> bool:
        """Create backup of file with timestamp"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                print(f"File not found: {file_path}")
                return False
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backups_dir / backup_name
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            
            # Update history
            history = self.load_history()
            relative_path = str(source_path.relative_to(self.base_dir))
            
            if relative_path not in history["files"]:
                history["files"][relative_path] = {
                    "original_path": str(source_path),
                    "backups": [],
                    "total_backups": 0
                }
            
            backup_info = {
                "backup_path": str(backup_path),
                "timestamp": datetime.now().isoformat(),
                "description": description,
                "file_hash": self.get_file_hash(source_path),
                "file_size": source_path.stat().st_size
            }
            
            history["files"][relative_path]["backups"].append(backup_info)
            history["files"][relative_path]["total_backups"] = len(history["files"][relative_path]["backups"])
            history["total_changes"] = sum(1 for file_data in history["files"].values() for _ in file_data["backups"])
            
            self.save_history(history)
            
            print(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_file(self, file_path: str, backup_timestamp: str) -> bool:
        """Restore file from backup"""
        try:
            source_path = Path(file_path)
            relative_path = str(source_path.relative_to(self.base_dir))
            
            history = self.load_history()
            if relative_path not in history["files"]:
                print(f"No backup history found for {file_path}")
                return False
            
            # Find the backup
            backup_info = None
            for backup in history["files"][relative_path]["backups"]:
                if backup_timestamp in backup["timestamp"]:
                    backup_info = backup
                    break
            
            if not backup_info:
                print(f"Backup not found for timestamp: {backup_timestamp}")
                return False
            
            backup_path = Path(backup_info["backup_path"])
            if not backup_path.exists():
                print(f"Backup file not found: {backup_path}")
                return False
            
            # Create backup of current file before restoring
            if source_path.exists():
                self.backup_file(file_path, f"Before restore from {backup_timestamp}")
            
            # Restore file
            shutil.copy2(backup_path, source_path)
            print(f"File restored: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error restoring file: {e}")
            return False
    
    def list_backups(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all backups or backups for specific file"""
        try:
            history = self.load_history()
            backups = []
            
            if file_path:
                # Backups for specific file
                source_path = Path(file_path)
                relative_path = str(source_path.relative_to(self.base_dir))
                
                if relative_path in history["files"]:
                    for backup in history["files"][relative_path]["backups"]:
                        backups.append({
                            "file": relative_path,
                            **backup
                        })
            else:
                # All backups
                for file_path, file_data in history["files"].items():
                    for backup in file_data["backups"]:
                        backups.append({
                            "file": file_path,
                            **backup
                        })
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
            return backups
            
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> bool:
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            history = self.load_history()
            removed_count = 0
            
            for file_path, file_data in history["files"].items():
                backups_to_keep = []
                
                for backup in file_data["backups"]:
                    backup_time = datetime.fromisoformat(backup["timestamp"]).timestamp()
                    
                    if backup_time >= cutoff_date:
                        backups_to_keep.append(backup)
                    else:
                        # Delete backup file
                        backup_path = Path(backup["backup_path"])
                        if backup_path.exists():
                            backup_path.unlink()
                            removed_count += 1
                            print(f"Deleted old backup: {backup_path}")
                
                file_data["backups"] = backups_to_keep
                file_data["total_backups"] = len(backups_to_keep)
            
            self.save_history(history)
            print(f"Cleanup completed. Removed {removed_count} old backups.")
            return True
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False
    
    def get_file_stats(self) -> Dict[str, Any]:
        """Get statistics about tracked files"""
        try:
            history = self.load_history()
            stats = {
                "total_files": len(history["files"]),
                "total_backups": history["total_changes"],
                "total_size": 0,
                "files_by_type": {},
                "oldest_backup": None,
                "newest_backup": None
            }
            
            all_timestamps = []
            
            for file_path, file_data in history["files"].items():
                file_ext = Path(file_path).suffix.lower()
                if file_ext not in stats["files_by_type"]:
                    stats["files_by_type"][file_ext] = 0
                stats["files_by_type"][file_ext] += 1
                
                for backup in file_data["backups"]:
                    stats["total_size"] += backup.get("file_size", 0)
                    all_timestamps.append(backup["timestamp"])
            
            if all_timestamps:
                all_timestamps.sort()
                stats["oldest_backup"] = all_timestamps[0]
                stats["newest_backup"] = all_timestamps[-1]
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def export_history(self, export_path: str) -> bool:
        """Export history to external file"""
        try:
            history = self.load_history()
            stats = self.get_file_stats()
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "statistics": stats,
                "history": history
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"History exported to: {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False

# Global instance
file_history_manager = FileHistoryManager()

if __name__ == "__main__":
    # Test the file history manager
    print("Testing File History Manager...")
    
    # Test backup
    test_file = "C://Users//flori//Desktop//AgentDaf1//github-dashboard//scoreboard.html"
    if os.path.exists(test_file):
        file_history_manager.backup_file(test_file, "Test backup")
        
        # List backups
        backups = file_history_manager.list_backups(test_file)
        print(f"Found {len(backups)} backups for {test_file}")
        
        # Get stats
        stats = file_history_manager.get_file_stats()
        print(f"Stats: {stats}")
    else:
        print(f"Test file not found: {test_file}")