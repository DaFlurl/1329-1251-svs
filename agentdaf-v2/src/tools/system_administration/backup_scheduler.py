#!/usr/bin/env python3
"""
AgentDaf1.1 - Backup Scheduler Tool
Automated backup scheduling and restoration
"""

import json
import time
import threading
import shutil
import zipfile
import hashlib
import sqlite3
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import schedule
import os

class BackupScheduler:
    """Automated backup scheduling and restoration"""
    
    def __init__(self):
        self.name = "Backup Scheduler"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Project paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.backup_dir = self.project_root / "backups"
        self.backup_db_path = self.backup_dir / "backup_schedule.db"
        
        # Ensure directories exist
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.config = {
            "default_retention_days": 30,
            "compression_enabled": True,
            "encryption_enabled": False,
            "backup_formats": ["zip", "tar.gz"],
            "max_backup_size_gb": 10,
            "auto_cleanup": True,
            "backup_on_startup": False,
            "cloud_backup": {
                "enabled": False,
                "provider": "aws_s3",  # aws_s3, google_cloud, azure
                "bucket": "",
                "region": "us-east-1"
            }
        }
        
        # Initialize backup database
        self._init_backup_db()
        
        # Load existing schedules
        self.schedules = {}
        self._load_schedules()
        
        # Start scheduler thread
        self.scheduler_running = True
        self._start_scheduler()
        
        self.logger.info(f"Backup Scheduler initialized: {self.name} v{self.version}")
    
    def _init_backup_db(self):
        """Initialize backup tracking database"""
        conn = sqlite3.connect(str(self.backup_db_path))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS backup_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                source_path TEXT NOT NULL,
                backup_type TEXT NOT NULL,
                schedule_cron TEXT NOT NULL,
                retention_days INTEGER,
                compression_enabled BOOLEAN DEFAULT 1,
                encryption_enabled BOOLEAN DEFAULT 0,
                cloud_backup BOOLEAN DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                created_at REAL,
                last_run REAL,
                next_run REAL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS backup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_name TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                backup_type TEXT NOT NULL,
                size_bytes INTEGER,
                checksum TEXT,
                status TEXT NOT NULL,
                started_at REAL,
                completed_at REAL,
                error_message TEXT
            )
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_schedule_name ON backup_history(schedule_name)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_completed_at ON backup_history(completed_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_schedules(self):
        """Load backup schedules from database"""
        conn = sqlite3.connect(str(self.backup_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backup_schedules WHERE active = 1")
        
        for row in cursor.fetchall():
            schedule_id = row[0]
            schedule_data = {
                "id": schedule_id,
                "name": row[1],
                "source_path": row[2],
                "backup_type": row[3],
                "schedule_cron": row[4],
                "retention_days": row[5],
                "compression_enabled": bool(row[6]),
                "encryption_enabled": bool(row[7]),
                "cloud_backup": bool(row[8]),
                "active": bool(row[9]),
                "created_at": row[10],
                "last_run": row[11],
                "next_run": row[12]
            }
            self.schedules[schedule_id] = schedule_data
            
            # Schedule the job
            self._schedule_job(schedule_data)
        
        conn.close()
    
    def _start_scheduler(self):
        """Start the backup scheduler thread"""
        def run_scheduler():
            while self.scheduler_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Scheduler error: {str(e)}")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def _schedule_job(self, schedule_data: Dict[str, Any]):
        """Schedule a backup job"""
        cron_expression = schedule_data["schedule_cron"]
        schedule_name = schedule_data["name"]
        
        try:
            # Parse cron expression (simplified - supports basic patterns)
            if cron_expression == "daily":
                schedule.every().day.at("02:00").do(self._execute_backup, schedule_data["id"])
            elif cron_expression == "weekly":
                schedule.every().sunday.at("02:00").do(self._execute_backup, schedule_data["id"])
            elif cron_expression == "hourly":
                schedule.every().hour.do(self._execute_backup, schedule_data["id"])
            elif cron_expression.startswith("every_"):
                # Custom intervals like "every_30_minutes", "every_2_hours"
                parts = cron_expression.split("_")
                if len(parts) >= 3:
                    interval = int(parts[1])
                    unit = parts[2]
                    
                    if unit.startswith("minute"):
                        schedule.every(interval).minutes.do(self._execute_backup, schedule_data["id"])
                    elif unit.startswith("hour"):
                        schedule.every(interval).hours.do(self._execute_backup, schedule_data["id"])
                    elif unit.startswith("day"):
                        schedule.every(interval).days.do(self._execute_backup, schedule_data["id"])
            
            self.logger.info(f"Scheduled backup job: {schedule_name} ({cron_expression})")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule job {schedule_name}: {str(e)}")
    
    def _execute_backup(self, schedule_id: int):
        """Execute a backup job"""
        if schedule_id not in self.schedules:
            return
        
        schedule_data = self.schedules[schedule_id]
        start_time = time.time()
        
        try:
            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{schedule_data['name']}_{timestamp}"
            
            # Determine backup format
            backup_format = "zip" if schedule_data["compression_enabled"] else "tar"
            
            # Create backup
            backup_path = self._create_backup(
                schedule_data["source_path"],
                backup_filename,
                backup_format,
                schedule_data["compression_enabled"],
                schedule_data["encryption_enabled"]
            )
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Get file size
            size_bytes = backup_path.stat().st_size
            
            # Update schedule
            with self.lock:
                schedule_data["last_run"] = start_time
                schedule_data["next_run"] = self._calculate_next_run(schedule_data["schedule_cron"])
            
            # Save to database
            conn = sqlite3.connect(str(self.backup_db_path))
            conn.execute('''
                UPDATE backup_schedules 
                SET last_run = ?, next_run = ? 
                WHERE id = ?
            ''', (start_time, schedule_data["next_run"], schedule_id))
            
            conn.execute('''
                INSERT INTO backup_history 
                (schedule_name, backup_path, backup_type, size_bytes, checksum, status, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                schedule_data["name"],
                str(backup_path),
                backup_format,
                size_bytes,
                checksum,
                "completed",
                start_time,
                time.time()
            ))
            
            conn.commit()
            conn.close()
            
            # Cloud backup if enabled
            if schedule_data["cloud_backup"]:
                self._upload_to_cloud(backup_path, schedule_data["name"])
            
            # Cleanup old backups
            if self.config["auto_cleanup"]:
                self._cleanup_old_backups(schedule_data["name"], schedule_data["retention_days"])
            
            self.logger.info(f"Backup completed: {schedule_data['name']} -> {backup_path}")
            
        except Exception as e:
            error_message = str(e)
            
            # Log error to database
            conn = sqlite3.connect(str(self.backup_db_path))
            conn.execute('''
                INSERT INTO backup_history 
                (schedule_name, backup_type, status, started_at, completed_at, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                schedule_data["name"],
                "error",
                "failed",
                start_time,
                time.time(),
                error_message
            ))
            conn.commit()
            conn.close()
            
            self.logger.error(f"Backup failed: {schedule_data['name']} - {error_message}")
    
    def _create_backup(self, source_path: str, backup_name: str, 
                      backup_format: str, compress: bool, encrypt: bool) -> Path:
        """Create backup file"""
        source = Path(source_path)
        backup_path = self.backup_dir / f"{backup_name}.{backup_format}"
        
        if backup_format == "zip":
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED) as zipf:
                if source.is_file():
                    zipf.write(source, source.name)
                else:
                    for file_path in source.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source.parent)
                            zipf.write(file_path, arcname)
        
        elif backup_format == "tar.gz":
            import tarfile
            mode = "w:gz" if compress else "w"
            with tarfile.open(backup_path, mode) as tarf:
                tarf.add(source, arcname=source.name)
        
        # Encryption would be implemented here if needed
        if encrypt:
            # Placeholder for encryption implementation
            pass
        
        return backup_path
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _calculate_next_run(self, cron_expression: str) -> float:
        """Calculate next run time based on cron expression"""
        now = datetime.now()
        
        if cron_expression == "daily":
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif cron_expression == "weekly":
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            days_ahead = 6 - now.weekday()  # Sunday is 6
            if days_ahead <= 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
        elif cron_expression == "hourly":
            next_run = now.replace(minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(hours=1)
        elif cron_expression.startswith("every_"):
            parts = cron_expression.split("_")
            if len(parts) >= 3:
                interval = int(parts[1])
                unit = parts[2]
                
                if unit.startswith("minute"):
                    next_run = now + timedelta(minutes=interval)
                elif unit.startswith("hour"):
                    next_run = now + timedelta(hours=interval)
                elif unit.startswith("day"):
                    next_run = now + timedelta(days=interval)
                else:
                    next_run = now + timedelta(hours=1)
            else:
                next_run = now + timedelta(hours=1)
        else:
            next_run = now + timedelta(hours=1)
        
        return next_run.timestamp()
    
    def _upload_to_cloud(self, backup_path: Path, schedule_name: str):
        """Upload backup to cloud storage (placeholder)"""
        # This would implement cloud upload logic
        # AWS S3, Google Cloud Storage, or Azure Blob Storage
        self.logger.info(f"Cloud upload not implemented: {backup_path}")
    
    def _cleanup_old_backups(self, schedule_name: str, retention_days: int):
        """Clean up old backups based on retention policy"""
        if retention_days <= 0:
            return
        
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        conn = sqlite3.connect(str(self.backup_db_path))
        cursor = conn.cursor()
        
        # Get old backups
        cursor.execute('''
            SELECT backup_path FROM backup_history 
            WHERE schedule_name = ? AND completed_at < ? AND status = 'completed'
        ''', (schedule_name, cutoff_time))
        
        old_backups = cursor.fetchall()
        deleted_files = []
        
        for (backup_path,) in old_backups:
            try:
                backup_file = Path(backup_path)
                if backup_file.exists():
                    backup_file.unlink()
                    deleted_files.append(backup_path)
            except Exception as e:
                self.logger.error(f"Failed to delete old backup {backup_path}: {str(e)}")
        
        # Update database
        if deleted_files:
            placeholders = ','.join(['?' for _ in deleted_files])
            cursor.execute(f'''
                DELETE FROM backup_history WHERE backup_path IN ({placeholders})
            ''', deleted_files)
            conn.commit()
        
        conn.close()
        
        if deleted_files:
            self.logger.info(f"Cleaned up {len(deleted_files)} old backups for {schedule_name}")
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new backup schedule"""
        try:
            # Validate required fields
            required_fields = ["name", "source_path", "backup_type", "schedule_cron"]
            for field in required_fields:
                if field not in schedule_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Check if source path exists
            source_path = Path(schedule_data["source_path"])
            if not source_path.exists():
                return {"success": False, "error": f"Source path does not exist: {source_path}"}
            
            # Set defaults
            schedule_data.setdefault("retention_days", self.config["default_retention_days"])
            schedule_data.setdefault("compression_enabled", self.config["compression_enabled"])
            schedule_data.setdefault("encryption_enabled", self.config["encryption_enabled"])
            schedule_data.setdefault("cloud_backup", self.config["cloud_backup"]["enabled"])
            schedule_data.setdefault("active", True)
            schedule_data["created_at"] = time.time()
            
            # Save to database
            conn = sqlite3.connect(str(self.backup_db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO backup_schedules 
                (name, source_path, backup_type, schedule_cron, retention_days, 
                 compression_enabled, encryption_enabled, cloud_backup, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                schedule_data["name"],
                schedule_data["source_path"],
                schedule_data["backup_type"],
                schedule_data["schedule_cron"],
                schedule_data["retention_days"],
                schedule_data["compression_enabled"],
                schedule_data["encryption_enabled"],
                schedule_data["cloud_backup"],
                schedule_data["active"],
                schedule_data["created_at"]
            ))
            
            schedule_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Add to schedules
            schedule_data["id"] = schedule_id
            schedule_data["next_run"] = self._calculate_next_run(schedule_data["schedule_cron"])
            self.schedules[schedule_id] = schedule_data
            
            # Schedule the job
            if schedule_data["active"]:
                self._schedule_job(schedule_data)
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "schedule": schedule_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_schedules(self) -> Dict[str, Any]:
        """Get all backup schedules"""
        return {
            "success": True,
            "schedules": list(self.schedules.values()),
            "total": len(self.schedules)
        }
    
    def get_backup_history(self, schedule_name: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get backup history"""
        conn = sqlite3.connect(str(self.backup_db_path))
        cursor = conn.cursor()
        
        if schedule_name:
            cursor.execute('''
                SELECT * FROM backup_history 
                WHERE schedule_name = ? 
                ORDER BY completed_at DESC 
                LIMIT ?
            ''', (schedule_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM backup_history 
                ORDER BY completed_at DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
    
    def restore_backup(self, backup_path: str, target_path: str) -> Dict[str, Any]:
        """Restore backup to target path"""
        try:
            backup_file = Path(backup_path)
            target = Path(target_path)
            
            if not backup_file.exists():
                return {"success": False, "error": "Backup file does not exist"}
            
            # Create target directory if it doesn't exist
            target.mkdir(parents=True, exist_ok=True)
            
            # Extract backup
            if backup_file.suffix == ".zip":
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(target)
            elif backup_file.suffix in [".tar", ".gz"]:
                import tarfile
                with tarfile.open(backup_file, 'r:*') as tarf:
                    tarf.extractall(target)
            else:
                return {"success": False, "error": "Unsupported backup format"}
            
            return {
                "success": True,
                "backup_path": backup_path,
                "target_path": target_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """Delete backup schedule"""
        try:
            if schedule_id not in self.schedules:
                return {"success": False, "error": "Schedule not found"}
            
            schedule_name = self.schedules[schedule_id]["name"]
            
            # Remove from database
            conn = sqlite3.connect(str(self.backup_db_path))
            conn.execute("DELETE FROM backup_schedules WHERE id = ?", (schedule_id,))
            conn.commit()
            conn.close()
            
            # Remove from memory
            del self.schedules[schedule_id]
            
            # Cancel scheduled job (simplified - would need job reference)
            schedule.clear()
            
            # Reschedule remaining jobs
            for schedule_data in self.schedules.values():
                if schedule_data["active"]:
                    self._schedule_job(schedule_data)
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "schedule_name": schedule_name
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get backup scheduler status"""
        active_schedules = sum(1 for s in self.schedules.values() if s["active"])
        
        # Get recent backup stats
        conn = sqlite3.connect(str(self.backup_db_path))
        cursor = conn.cursor()
        
        # Last 24 hours
        yesterday = time.time() - (24 * 60 * 60)
        cursor.execute('''
            SELECT COUNT(*), SUM(size_bytes) FROM backup_history 
            WHERE completed_at > ? AND status = 'completed'
        ''', (yesterday,))
        recent_count, recent_size = cursor.fetchone()
        
        # Total backups
        cursor.execute('''
            SELECT COUNT(*), SUM(size_bytes) FROM backup_history 
            WHERE status = 'completed'
        ''')
        total_count, total_size = cursor.fetchone()
        
        conn.close()
        
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "schedules": {
                "total": len(self.schedules),
                "active": active_schedules,
                "inactive": len(self.schedules) - active_schedules
            },
            "backups": {
                "recent_24h": recent_count or 0,
                "recent_size_24h": recent_size or 0,
                "total": total_count or 0,
                "total_size": total_size or 0
            },
            "config": self.config,
            "backup_directory": str(self.backup_dir),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
backup_scheduler = BackupScheduler()