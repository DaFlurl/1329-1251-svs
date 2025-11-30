#!/usr/bin/env python3
"""
AgentDaf1.1 - Service Manager Tool
System service management and monitoring
"""

import json
import time
import threading
import subprocess
import psutil
import signal
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import sqlite3

class ServiceManager:
    """System service management and monitoring"""
    
    def __init__(self):
        self.name = "Service Manager"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Project paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.services_db_path = self.project_root / "data" / "services.db"
        self.logs_dir = self.project_root / "logs" / "services"
        
        # Ensure directories exist
        self.services_db_path.parent.mkdir(exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Service configuration
        self.config = {
            "auto_restart": True,
            "health_check_interval": 30,  # seconds
            "max_restart_attempts": 3,
            "restart_delay": 5,  # seconds
            "log_retention_days": 7,
            "resource_limits": {
                "max_memory_mb": 1024,
                "max_cpu_percent": 80
            }
        }
        
        # Initialize services database
        self._init_services_db()
        
        # Load services
        self.services = {}
        self.running_processes = {}
        self._load_services()
        
        # Start monitoring thread
        self.monitoring_running = True
        self._start_monitoring()
        
        self.logger.info(f"Service Manager initialized: {self.name} v{self.version}")
    
    def _init_services_db(self):
        """Initialize services database"""
        conn = sqlite3.connect(str(self.services_db_path))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                command TEXT NOT NULL,
                working_directory TEXT,
                environment TEXT,
                auto_start BOOLEAN DEFAULT 0,
                health_check_url TEXT,
                health_check_interval INTEGER DEFAULT 30,
                max_restarts INTEGER DEFAULT 3,
                dependencies TEXT,
                created_at REAL,
                last_started REAL,
                last_stopped REAL,
                restart_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'stopped'
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS service_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp REAL,
                process_id INTEGER
            )
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_service_name ON service_logs(service_name)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON service_logs(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_services(self):
        """Load services from database"""
        conn = sqlite3.connect(str(self.services_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services")
        
        for row in cursor.fetchall():
            service_data = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "command": row[3],
                "working_directory": row[4],
                "environment": json.loads(row[5]) if row[5] else {},
                "auto_start": bool(row[6]),
                "health_check_url": row[7],
                "health_check_interval": row[8],
                "max_restarts": row[9],
                "dependencies": json.loads(row[10]) if row[10] else [],
                "created_at": row[11],
                "last_started": row[12],
                "last_stopped": row[13],
                "restart_count": row[14],
                "status": row[15]
            }
            self.services[service_data["id"]] = service_data
            
            # Auto-start services
            if service_data["auto_start"] and service_data["status"] == "stopped":
                self._start_service(service_data["id"])
        
        conn.close()
    
    def _start_monitoring(self):
        """Start service monitoring thread"""
        def monitor_services():
            while self.monitoring_running:
                try:
                    self._check_service_health()
                    self._cleanup_old_logs()
                    time.sleep(self.config["health_check_interval"])
                except Exception as e:
                    self.logger.error(f"Service monitoring error: {str(e)}")
                    time.sleep(self.config["health_check_interval"])
        
        monitor_thread = threading.Thread(target=monitor_services, daemon=True)
        monitor_thread.start()
    
    def _check_service_health(self):
        """Check health of all running services"""
        for service_id, service in self.services.items():
            if service["status"] == "running":
                process_info = self.running_processes.get(service_id)
                
                if process_info:
                    process = process_info["process"]
                    
                    # Check if process is still running
                    if not process.is_alive():
                        self._log_service_event(
                            service["name"], 
                            "ERROR", 
                            f"Service process died unexpectedly"
                        )
                        
                        if self.config["auto_restart"] and service["restart_count"] < service["max_restarts"]:
                            self._restart_service(service_id)
                        else:
                            service["status"] = "stopped"
                            self._update_service_status(service_id, "stopped")
                    else:
                        # Check resource usage
                        try:
                            proc = psutil.Process(process.pid)
                            memory_mb = proc.memory_info().rss / 1024 / 1024
                            cpu_percent = proc.cpu_percent()
                            
                            if memory_mb > self.config["resource_limits"]["max_memory_mb"]:
                                self._log_service_event(
                                    service["name"],
                                    "WARNING",
                                    f"High memory usage: {memory_mb:.1f}MB"
                                )
                            
                            if cpu_percent > self.config["resource_limits"]["max_cpu_percent"]:
                                self._log_service_event(
                                    service["name"],
                                    "WARNING",
                                    f"High CPU usage: {cpu_percent:.1f}%"
                                )
                        
                        except psutil.NoSuchProcess:
                            pass  # Process already handled above
                
                # Health check URL
                if service.get("health_check_url"):
                    self._perform_health_check(service)
    
    def _perform_health_check(self, service: Dict[str, Any]):
        """Perform HTTP health check"""
        try:
            import requests
            response = requests.get(
                service["health_check_url"], 
                timeout=5
            )
            
            if response.status_code != 200:
                self._log_service_event(
                    service["name"],
                    "WARNING",
                    f"Health check failed: HTTP {response.status_code}"
                )
        except Exception as e:
            self._log_service_event(
                service["name"],
                "ERROR",
                f"Health check error: {str(e)}"
            )
    
    def _cleanup_old_logs(self):
        """Clean up old service logs"""
        cutoff_time = time.time() - (self.config["log_retention_days"] * 24 * 60 * 60)
        
        conn = sqlite3.connect(str(self.services_db_path))
        conn.execute("DELETE FROM service_logs WHERE timestamp < ?", (cutoff_time,))
        conn.commit()
        conn.close()
    
    def _start_service(self, service_id: int) -> Dict[str, Any]:
        """Start a service"""
        if service_id not in self.services:
            return {"success": False, "error": "Service not found"}
        
        service = self.services[service_id]
        
        if service["status"] == "running":
            return {"success": False, "error": "Service already running"}
        
        try:
            # Check dependencies
            for dep_name in service.get("dependencies", []):
                dep_service = next(
                    (s for s in self.services.values() if s["name"] == dep_name),
                    None
                )
                if not dep_service or dep_service["status"] != "running":
                    return {
                        "success": False, 
                        "error": f"Dependency {dep_name} not running"
                    }
            
            # Prepare environment
            env = os.environ.copy()
            env.update(service.get("environment", {}))
            
            # Start process
            working_dir = service.get("working_directory") or str(self.project_root)
            
            with open(self.logs_dir / f"{service['name']}.log", "a") as log_file:
                process = subprocess.Popen(
                    service["command"],
                    shell=True,
                    cwd=working_dir,
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            # Store process info
            self.running_processes[service_id] = {
                "process": process,
                "started_at": time.time()
            }
            
            # Update service status
            service["status"] = "running"
            service["last_started"] = time.time()
            self._update_service_status(service_id, "running")
            
            self._log_service_event(
                service["name"],
                "INFO",
                f"Service started with PID {process.pid}"
            )
            
            return {
                "success": True,
                "service_name": service["name"],
                "process_id": process.pid,
                "started_at": service["last_started"]
            }
            
        except Exception as e:
            self._log_service_event(
                service["name"],
                "ERROR",
                f"Failed to start service: {str(e)}"
            )
            return {"success": False, "error": str(e)}
    
    def _stop_service(self, service_id: int) -> Dict[str, Any]:
        """Stop a service"""
        if service_id not in self.services:
            return {"success": False, "error": "Service not found"}
        
        service = self.services[service_id]
        
        if service["status"] != "running":
            return {"success": False, "error": "Service not running"}
        
        try:
            process_info = self.running_processes.get(service_id)
            if process_info:
                process = process_info["process"]
                
                # Try graceful shutdown first
                process.terminate()
                
                # Wait for process to stop
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    process.kill()
                    process.wait()
                
                # Remove from running processes
                del self.running_processes[service_id]
            
            # Update service status
            service["status"] = "stopped"
            service["last_stopped"] = time.time()
            self._update_service_status(service_id, "stopped")
            
            self._log_service_event(
                service["name"],
                "INFO",
                "Service stopped"
            )
            
            return {
                "success": True,
                "service_name": service["name"],
                "stopped_at": service["last_stopped"]
            }
            
        except Exception as e:
            self._log_service_event(
                service["name"],
                "ERROR",
                f"Failed to stop service: {str(e)}"
            )
            return {"success": False, "error": str(e)}
    
    def _restart_service(self, service_id: int) -> Dict[str, Any]:
        """Restart a service"""
        if service_id not in self.services:
            return {"success": False, "error": "Service not found"}
        
        service = self.services[service_id]
        
        # Stop if running
        if service["status"] == "running":
            stop_result = self._stop_service(service_id)
            if not stop_result["success"]:
                return stop_result
        
        # Increment restart count
        service["restart_count"] += 1
        
        # Wait before restart
        time.sleep(self.config["restart_delay"])
        
        # Start service
        return self._start_service(service_id)
    
    def _update_service_status(self, service_id: int, status: str):
        """Update service status in database"""
        conn = sqlite3.connect(str(self.services_db_path))
        conn.execute('''
            UPDATE services 
            SET status = ?, last_started = ?, last_stopped = ?, restart_count = ?
            WHERE id = ?
        ''', (
            status,
            self.services[service_id].get("last_started"),
            self.services[service_id].get("last_stopped"),
            self.services[service_id].get("restart_count", 0),
            service_id
        ))
        conn.commit()
        conn.close()
    
    def _log_service_event(self, service_name: str, level: str, message: str):
        """Log service event"""
        conn = sqlite3.connect(str(self.services_db_path))
        conn.execute('''
            INSERT INTO service_logs (service_name, level, message, timestamp, process_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (service_name, level, message, time.time(), os.getpid()))
        conn.commit()
        conn.close()
        
        # Also log to standard logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{service_name}] {message}")
    
    def create_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new service"""
        try:
            # Validate required fields
            required_fields = ["name", "command"]
            for field in required_fields:
                if field not in service_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Check if service name already exists
            if any(s["name"] == service_data["name"] for s in self.services.values()):
                return {"success": False, "error": "Service name already exists"}
            
            # Set defaults
            service_data.setdefault("description", "")
            service_data.setdefault("working_directory", str(self.project_root))
            service_data.setdefault("environment", {})
            service_data.setdefault("auto_start", False)
            service_data.setdefault("health_check_url", "")
            service_data.setdefault("health_check_interval", 30)
            service_data.setdefault("max_restarts", 3)
            service_data.setdefault("dependencies", [])
            service_data.setdefault("created_at", time.time())
            service_data.setdefault("status", "stopped")
            
            # Save to database
            conn = sqlite3.connect(str(self.services_db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO services 
                (name, description, command, working_directory, environment, auto_start,
                 health_check_url, health_check_interval, max_restarts, dependencies, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                service_data["name"],
                service_data["description"],
                service_data["command"],
                service_data["working_directory"],
                json.dumps(service_data["environment"]),
                service_data["auto_start"],
                service_data["health_check_url"],
                service_data["health_check_interval"],
                service_data["max_restarts"],
                json.dumps(service_data["dependencies"]),
                service_data["created_at"],
                service_data["status"]
            ))
            
            service_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Add to services
            service_data["id"] = service_id
            self.services[service_id] = service_data
            
            # Auto-start if requested
            if service_data["auto_start"]:
                self._start_service(service_id)
            
            return {
                "success": True,
                "service_id": service_id,
                "service": service_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_services(self) -> Dict[str, Any]:
        """Get all services"""
        services_with_status = []
        
        for service in self.services.values():
            service_copy = service.copy()
            
            # Add current process info if running
            if service["status"] == "running" and service["id"] in self.running_processes:
                process_info = self.running_processes[service["id"]]
                try:
                    proc = psutil.Process(process_info["process"].pid)
                    service_copy["process_info"] = {
                        "pid": proc.pid,
                        "memory_mb": proc.memory_info().rss / 1024 / 1024,
                        "cpu_percent": proc.cpu_percent(),
                        "uptime": time.time() - process_info["started_at"]
                    }
                except psutil.NoSuchProcess:
                    service_copy["status"] = "stopped"
            
            services_with_status.append(service_copy)
        
        return {
            "success": True,
            "services": services_with_status,
            "total": len(services_with_status),
            "running": sum(1 for s in services_with_status if s["status"] == "running"),
            "stopped": sum(1 for s in services_with_status if s["status"] == "stopped")
        }
    
    def control_service(self, service_id: int, action: str) -> Dict[str, Any]:
        """Control a service (start, stop, restart)"""
        if action == "start":
            return self._start_service(service_id)
        elif action == "stop":
            return self._stop_service(service_id)
        elif action == "restart":
            return self._restart_service(service_id)
        else:
            return {"success": False, "error": f"Invalid action: {action}"}
    
    def get_service_logs(self, service_name: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get service logs"""
        conn = sqlite3.connect(str(self.services_db_path))
        cursor = conn.cursor()
        
        if service_name:
            cursor.execute('''
                SELECT * FROM service_logs 
                WHERE service_name = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (service_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM service_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "logs": logs,
            "total": len(logs)
        }
    
    def delete_service(self, service_id: int) -> Dict[str, Any]:
        """Delete a service"""
        try:
            if service_id not in self.services:
                return {"success": False, "error": "Service not found"}
            
            service = self.services[service_id]
            
            # Stop service if running
            if service["status"] == "running":
                self._stop_service(service_id)
            
            # Delete from database
            conn = sqlite3.connect(str(self.services_db_path))
            conn.execute("DELETE FROM services WHERE id = ?", (service_id,))
            conn.execute("DELETE FROM service_logs WHERE service_name = ?", (service["name"],))
            conn.commit()
            conn.close()
            
            # Remove from memory
            del self.services[service_id]
            
            return {
                "success": True,
                "service_id": service_id,
                "service_name": service["name"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get service manager status"""
        running_count = sum(1 for s in self.services.values() if s["status"] == "running")
        
        # System resource usage
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(self.project_root))
        
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "services": {
                "total": len(self.services),
                "running": running_count,
                "stopped": len(self.services) - running_count
            },
            "system_resources": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / 1024 / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024
            },
            "config": self.config,
            "logs_directory": str(self.logs_dir),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
service_manager = ServiceManager()