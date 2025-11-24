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

class FileHistoryManager:
    def __init__(self, base_dir="C:\\Users\\flori\\Desktop\\AgentDaf1\\github-dashboard"):
        self.base_dir = Path(base_dir)
        self.history_dir = self.base_dir / "file_history"
        self.history_file = self.history_dir / "file_history.json"
        self.backups_dir = self.history_dir / "backups"
        
        # Create directories if they don't exist
        self.history_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
        
        # Initialize history file if it doesn't exist
        self.init_history()
        
    def init_history(self):
        """Initialize the history tracking file"""
        if not self.history_file.exists():
            initial_history = {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_changes": 0,
                "files": {}
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(initial_history, f, indent=2, ensure_ascii=False)
    
    def load_history(self):
        """Load the current history"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return {"files": {}}
    
    def save_history(self, history):
        """Save the history file"""
        try:
            history["last_updated"] = datetime.now().isoformat()
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
    
    def backup_file(self, file_path, version_info):
        """Create a backup of the file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None
                
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backups_dir / backup_name
            
            # Copy file to backup directory
            shutil.copy2(file_path, backup_path)
            
            # Store backup info
            backup_info = {
                "backup_path": str(backup_path),
                "original_path": str(file_path),
                "timestamp": datetime.now().isoformat(),
                "size": file_path.stat().st_size,
                "hash": self.get_file_hash(file_path),
                "version": version_info
            }
            
            return backup_info
            
        except Exception as e:
            print(f"Error backing up file {file_path}: {e}")
            return None
    
    def record_change(self, file_path, change_type="modified", description="", author="System"):
        """Record a file change in the history"""
        try:
            file_path = Path(file_path)
            relative_path = str(file_path.relative_to(self.base_dir))
            
            # Load current history
            history = self.load_history()
            
            # Initialize file entry if it doesn't exist
            if relative_path not in history["files"]:
                history["files"][relative_path] = {
                    "created": datetime.now().isoformat(),
                    "changes": [],
                    "current_version": 0
                }
            
            file_entry = history["files"][relative_path]
            
            # Increment version
            file_entry["current_version"] += 1
            current_version = file_entry["current_version"]
            
            # Create backup
            version_info = f"v{current_version}"
            backup_info = self.backup_file(file_path, version_info)
            
            # Record the change
            change_record = {
                "version": current_version,
                "type": change_type,
                "timestamp": datetime.now().isoformat(),
                "description": description,
                "author": author,
                "hash": self.get_file_hash(file_path),
                "backup": backup_info
            }
            
            file_entry["changes"].append(change_record)
            file_entry["last_modified"] = datetime.now().isoformat()
            
            # Update totals
            history["total_changes"] += 1
            
            # Save history
            self.save_history(history)
            
            print(f"Recorded change: {relative_path} - {change_type} (v{current_version})")
            return change_record
            
        except Exception as e:
            print(f"Error recording change for {file_path}: {e}")
            return None
    
    def get_file_history(self, file_path):
        """Get the complete history of a specific file"""
        try:
            file_path = Path(file_path)
            relative_path = str(file_path.relative_to(self.base_dir))
            
            history = self.load_history()
            return history["files"].get(relative_path, {})
            
        except Exception as e:
            print(f"Error getting file history: {e}")
            return {}
    
    def restore_file(self, file_path, version=None, timestamp=None):
        """Restore a file to a specific version"""
        try:
            file_path = Path(file_path)
            relative_path = str(file_path.relative_to(self.base_dir))
            
            history = self.load_history()
            file_entry = history["files"].get(relative_path, {})
            
            if not file_entry or not file_entry["changes"]:
                print(f"No history found for {relative_path}")
                return False
            
            # Find the specific change to restore
            target_change = None
            for change in reversed(file_entry["changes"]):
                if version and change["version"] == version:
                    target_change = change
                    break
                elif timestamp and change["timestamp"].startswith(timestamp):
                    target_change = change
                    break
            
            if not target_change or not target_change.get("backup"):
                print(f"Could not find specified version for {relative_path}")
                return False
            
            # Restore from backup
            backup_path = Path(target_change["backup"]["backup_path"])
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                print(f"Restored {relative_path} to {target_change['version']}")
                return True
            else:
                print(f"Backup file not found: {backup_path}")
                return False
                
        except Exception as e:
            print(f"Error restoring file: {e}")
            return False
    
    def list_all_changes(self, limit=50):
        """List all recent changes across all files"""
        try:
            history = self.load_history()
            all_changes = []
            
            for file_path, file_entry in history["files"].items():
                for change in file_entry["changes"]:
                    change["file_path"] = file_path
                    all_changes.append(change)
            
            # Sort by timestamp (most recent first)
            all_changes.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return all_changes[:limit]
            
        except Exception as e:
            print(f"Error listing changes: {e}")
            return []
    
    def generate_report(self):
        """Generate a comprehensive history report"""
        try:
            history = self.load_history()
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_files": len(history["files"]),
                    "total_changes": history["total_changes"],
                    "history_size_mb": round(self.get_history_size() / (1024*1024), 2)
                },
                "files": {}
            }
            
            for file_path, file_entry in history["files"].items():
                report["files"][file_path] = {
                    "created": file_entry["created"],
                    "current_version": file_entry["current_version"],
                    "total_changes": len(file_entry["changes"]),
                    "last_modified": file_entry["last_modified"],
                    "recent_changes": file_entry["changes"][-5:]  # Last 5 changes
                }
            
            return report
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
    
    def get_history_size(self):
        """Calculate total size of history directory"""
        try:
            total_size = 0
            for file_path in self.history_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0
    
    def cleanup_old_backups(self, keep_days=30):
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 3600)
            removed_count = 0
            
            for backup_file in self.backups_dir.rglob("*"):
                if backup_file.is_file() and backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
                    removed_count += 1
            
            print(f"Cleaned up {removed_count} old backup files")
            return removed_count
            
        except Exception as e:
            print(f"Error cleaning up backups: {e}")
            return 0

# Convenience functions for common operations
def track_file_change(file_path, change_type="modified", description="", author="System"):
    """Track a file change"""
    manager = FileHistoryManager()
    return manager.record_change(file_path, change_type, description, author)

def get_file_history(file_path):
    """Get history for a specific file"""
    manager = FileHistoryManager()
    return manager.get_file_history(file_path)

def restore_file_version(file_path, version=None):
    """Restore file to specific version"""
    manager = FileHistoryManager()
    return manager.restore_file(file_path, version=version)

def generate_history_report():
    """Generate complete history report"""
    manager = FileHistoryManager()
    return manager.generate_report()

if __name__ == "__main__":
    # Example usage
    manager = FileHistoryManager()
    
    # Track current files
    files_to_track = [
        "scoreboard.html",
        "scoreboard-data.json", 
        "scoreboard_new.html",
        "index.html"
    ]
    
    for file_name in files_to_track:
        file_path = manager.base_dir / file_name
        if file_path.exists():
            manager.record_change(file_path, "tracked", f"Initial tracking of {file_name}")
    
    # Generate report
    report = manager.generate_report()
    if report:
        print(f"History Report Generated")
        print(f"Total Files: {report['summary']['total_files']}")
        print(f"Total Changes: {report['summary']['total_changes']}")
        print(f"History Size: {report['summary']['history_size_mb']} MB")