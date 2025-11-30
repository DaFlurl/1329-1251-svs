#!/usr/bin/env python3
"""
AgentDaf1.1 - Deployment Manager Tool
CI/CD pipeline management and deployment automation
"""

import json
import time
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import sqlite3
import shutil

class DeploymentManager:
    """CI/CD pipeline management and deployment automation"""
    
    def __init__(self):
        self.name = "Deployment Manager"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Project paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.deployment_db_path = self.project_root / "data" / "deployments.db"
        self.deployments_dir = self.project_root / "deployments"
        
        # Ensure directories exist
        self.deployment_db_path.parent.mkdir(exist_ok=True)
        self.deployments_dir.mkdir(exist_ok=True)
        
        # Deployment configuration
        self.config = {
            "default_strategy": "blue_green",  # blue_green, rolling, canary
            "health_check_timeout": 300,  # seconds
            "rollback_timeout": 60,  # seconds
            "max_concurrent_deployments": 3,
            "backup_before_deploy": True,
            "environments": ["development", "staging", "production"],
            "notification_channels": ["email", "slack"]
        }
        
        # Initialize deployment database
        self._init_deployment_db()
        
        self.logger.info(f"Deployment Manager initialized: {self.name} v{self.version}")
    
    def _init_deployment_db(self):
        """Initialize deployment database"""
        conn = sqlite3.connect(str(self.deployment_db_path))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                environment TEXT NOT NULL,
                strategy TEXT NOT NULL,
                source_path TEXT NOT NULL,
                target_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at REAL,
                started_at REAL,
                completed_at REAL,
                rollback_id INTEGER,
                metadata TEXT,
                FOREIGN KEY (rollback_id) REFERENCES deployments (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS deployment_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id INTEGER NOT NULL,
                step_name TEXT NOT NULL,
                step_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                started_at REAL,
                completed_at REAL,
                output TEXT,
                error_message TEXT,
                FOREIGN KEY (deployment_id) REFERENCES deployments (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS environments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                config TEXT NOT NULL,
                created_at REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_deployment(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deployment"""
        try:
            # Validate required fields
            required_fields = ["name", "environment", "source_path", "target_path"]
            for field in required_fields:
                if field not in deployment_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Validate environment
            if deployment_data["environment"] not in self.config["environments"]:
                return {"success": False, "error": f"Invalid environment: {deployment_data['environment']}"}
            
            # Validate paths
            source_path = Path(deployment_data["source_path"])
            target_path = Path(deployment_data["target_path"])
            
            if not source_path.exists():
                return {"success": False, "error": f"Source path does not exist: {source_path}"}
            
            # Set defaults
            deployment_data.setdefault("strategy", self.config["default_strategy"])
            deployment_data.setdefault("status", "pending")
            deployment_data.setdefault("created_at", time.time())
            deployment_data.setdefault("metadata", {})
            
            # Save to database
            conn = sqlite3.connect(str(self.deployment_db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO deployments 
                (name, environment, strategy, source_path, target_path, status, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deployment_data["name"],
                deployment_data["environment"],
                deployment_data["strategy"],
                str(source_path),
                str(target_path),
                deployment_data["status"],
                deployment_data["created_at"],
                json.dumps(deployment_data["metadata"])
            ))
            
            deployment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            deployment_data["id"] = deployment_id
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "deployment": deployment_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_deployment(self, deployment_id: int) -> Dict[str, Any]:
        """Execute a deployment"""
        try:
            # Get deployment from database
            conn = sqlite3.connect(str(self.deployment_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM deployments WHERE id = ?", (deployment_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {"success": False, "error": "Deployment not found"}
            
            deployment = {
                "id": row[0],
                "name": row[1],
                "environment": row[2],
                "strategy": row[3],
                "source_path": row[4],
                "target_path": row[5],
                "status": row[6],
                "created_at": row[7],
                "started_at": row[8],
                "completed_at": row[9],
                "rollback_id": row[10],
                "metadata": json.loads(row[11]) if row[11] else {}
            }
            
            if deployment["status"] != "pending":
                return {"success": False, "error": f"Deployment already {deployment['status']}"}
            
            # Update deployment status
            self._update_deployment_status(deployment_id, "running", started_at=time.time())
            
            # Execute deployment based on strategy
            if deployment["strategy"] == "blue_green":
                result = self._execute_blue_green_deployment(deployment)
            elif deployment["strategy"] == "rolling":
                result = self._execute_rolling_deployment(deployment)
            elif deployment["strategy"] == "canary":
                result = self._execute_canary_deployment(deployment)
            else:
                result = {"success": False, "error": f"Unknown deployment strategy: {deployment['strategy']}"}
            
            # Update final status
            final_status = "completed" if result["success"] else "failed"
            self._update_deployment_status(deployment_id, final_status, completed_at=time.time())
            
            return result
            
        except Exception as e:
            self._update_deployment_status(deployment_id, "failed", completed_at=time.time())
            return {"success": False, "error": str(e)}
    
    def _execute_blue_green_deployment(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute blue-green deployment"""
        try:
            source_path = Path(deployment["source_path"])
            target_path = Path(deployment["target_path"])
            
            # Create blue and green directories
            blue_dir = target_path / "blue"
            green_dir = target_path / "green"
            
            # Determine which is currently active
            current_active = None
            if blue_dir.exists():
                current_active = "blue"
            elif green_dir.exists():
                current_active = "green"
            
            # Deploy to inactive environment
            new_active = "green" if current_active == "blue" else "blue"
            new_dir = green_dir if new_active == "green" else blue_dir
            
            self._add_deployment_step(deployment["id"], f"Deploy to {new_active}", "deploy")
            
            # Backup current if exists
            if current_active:
                current_dir = green_dir if current_active == "green" else blue_dir
                backup_dir = target_path / f"backup_{current_active}_{int(time.time())}"
                shutil.move(str(current_dir), str(backup_dir))
            
            # Deploy new version
            shutil.copytree(str(source_path), str(new_dir), dirs_exist_ok=True)
            
            # Health check
            self._add_deployment_step(deployment["id"], "Health check", "verify")
            health_result = self._perform_health_check(new_dir)
            
            if not health_result["success"]:
                return {"success": False, "error": f"Health check failed: {health_result['error']}"}
            
            # Switch traffic (simplified - would involve load balancer configuration)
            self._add_deployment_step(deployment["id"], f"Switch traffic to {new_active}", "switch")
            
            return {
                "success": True,
                "strategy": "blue_green",
                "active_environment": new_active,
                "health_check": health_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_rolling_deployment(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rolling deployment"""
        try:
            source_path = Path(deployment["source_path"])
            target_path = Path(deployment["target_path"])
            
            self._add_deployment_step(deployment["id"], "Start rolling deployment", "deploy")
            
            # Backup current deployment
            if target_path.exists():
                backup_dir = target_path.parent / f"backup_{target_path.name}_{int(time.time())}"
                shutil.move(str(target_path), str(backup_dir))
            
            # Deploy new version
            shutil.copytree(str(source_path), str(target_path), dirs_exist_ok=True)
            
            # Health check
            self._add_deployment_step(deployment["id"], "Health check", "verify")
            health_result = self._perform_health_check(target_path)
            
            if not health_result["success"]:
                return {"success": False, "error": f"Health check failed: {health_result['error']}"}
            
            return {
                "success": True,
                "strategy": "rolling",
                "health_check": health_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_canary_deployment(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute canary deployment"""
        try:
            source_path = Path(deployment["source_path"])
            target_path = Path(deployment["target_path"])
            
            self._add_deployment_step(deployment["id"], "Start canary deployment", "deploy")
            
            # Deploy canary version (simplified - would deploy to subset of servers)
            canary_dir = target_path / "canary"
            shutil.copytree(str(source_path), str(canary_dir), dirs_exist_ok=True)
            
            # Health check on canary
            self._add_deployment_step(deployment["id"], "Canary health check", "verify")
            health_result = self._perform_health_check(canary_dir)
            
            if not health_result["success"]:
                return {"success": False, "error": f"Canary health check failed: {health_result['error']}"}
            
            # Promote canary to full deployment
            self._add_deployment_step(deployment["id"], "Promote canary", "promote")
            
            # Backup current and promote
            if target_path.exists():
                backup_dir = target_path.parent / f"backup_{target_path.name}_{int(time.time())}"
                shutil.move(str(target_path), str(backup_dir))
            
            shutil.move(str(canary_dir), str(target_path))
            
            return {
                "success": True,
                "strategy": "canary",
                "health_check": health_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def rollback_deployment(self, deployment_id: int, target_deployment_id: int = None) -> Dict[str, Any]:
        """Rollback a deployment"""
        try:
            # Get deployment to rollback
            conn = sqlite3.connect(str(self.deployment_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM deployments WHERE id = ?", (deployment_id,))
            row = cursor.fetchone()
            
            if not row:
                return {"success": False, "error": "Deployment not found"}
            
            deployment = {
                "id": row[0],
                "name": row[1],
                "environment": row[2],
                "strategy": row[3],
                "source_path": row[4],
                "target_path": row[5],
                "status": row[6],
                "rollback_id": row[10]
            }
            
            if deployment["rollback_id"]:
                return {"success": False, "error": "Deployment already rolled back"}
            
            # Find previous successful deployment if target not specified
            if not target_deployment_id:
                cursor.execute('''
                    SELECT id FROM deployments 
                    WHERE environment = ? AND status = 'completed' AND id < ?
                    ORDER BY id DESC LIMIT 1
                ''', (deployment["environment"], deployment_id))
                prev_row = cursor.fetchone()
                target_deployment_id = prev_row[0] if prev_row else None
            
            if not target_deployment_id:
                return {"success": False, "error": "No previous deployment found for rollback"}
            
            # Get target deployment
            cursor.execute("SELECT * FROM deployments WHERE id = ?", (target_deployment_id,))
            target_row = cursor.fetchone()
            
            if not target_row:
                return {"success": False, "error": "Target deployment not found"}
            
            target_deployment = {
                "id": target_row[0],
                "source_path": target_row[4],
                "target_path": target_row[5]
            }
            
            conn.close()
            
            # Perform rollback
            self._add_deployment_step(deployment_id, "Start rollback", "rollback")
            
            # Restore from backup or redeploy previous version
            target_path = Path(deployment["target_path"])
            backup_pattern = f"backup_{target_path.name}_*"
            
            backup_found = False
            for backup_dir in target_path.parent.glob(backup_pattern):
                if backup_dir.is_dir():
                    # Remove current deployment
                    if target_path.exists():
                        shutil.rmtree(str(target_path))
                    
                    # Restore backup
                    shutil.move(str(backup_dir), str(target_path))
                    backup_found = True
                    break
            
            if not backup_found:
                # Redeploy previous version
                if target_path.exists():
                    shutil.rmtree(str(target_path))
                shutil.copytree(str(target_deployment["source_path"]), str(target_path))
            
            # Update deployment record
            self._update_deployment_status(deployment_id, "rolled_back", completed_at=time.time())
            self._update_deployment_rollback(deployment_id, target_deployment_id)
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "target_deployment_id": target_deployment_id,
                "rollback_method": "backup" if backup_found else "redeploy"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _perform_health_check(self, deployment_path: Path) -> Dict[str, Any]:
        """Perform health check on deployment"""
        try:
            # Check if deployment directory exists
            if not deployment_path.exists():
                return {"success": False, "error": "Deployment directory not found"}
            
            # Check for essential files (simplified)
            essential_files = ["app.py", "main.py", "index.html", "package.json"]
            essential_found = any(
                (deployment_path / file).exists() for file in essential_files
            )
            
            if not essential_found:
                return {"success": False, "error": "No essential application files found"}
            
            # Try to run application health check (simplified)
            health_check_file = deployment_path / "health.py"
            if health_check_file.exists():
                try:
                    result = subprocess.run(
                        ["python", str(health_check_file)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        return {"success": True, "method": "health_script"}
                    else:
                        return {"success": False, "error": result.stderr}
                except subprocess.TimeoutExpired:
                    return {"success": False, "error": "Health check timeout"}
            
            # Default health check
            return {"success": True, "method": "file_check"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_deployment_step(self, deployment_id: int, step_name: str, step_type: str):
        """Add deployment step to database"""
        conn = sqlite3.connect(str(self.deployment_db_path))
        conn.execute('''
            INSERT INTO deployment_steps 
            (deployment_id, step_name, step_type, started_at)
            VALUES (?, ?, ?, ?)
        ''', (deployment_id, step_name, step_type, time.time()))
        conn.commit()
        conn.close()
    
    def _update_deployment_status(self, deployment_id: int, status: str, **kwargs):
        """Update deployment status"""
        conn = sqlite3.connect(str(self.deployment_db_path))
        
        set_clauses = ["status = ?"]
        values = [status]
        
        for key, value in kwargs.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        values.append(deployment_id)
        
        conn.execute(f'''
            UPDATE deployments 
            SET {", ".join(set_clauses)}
            WHERE id = ?
        ''', values)
        conn.commit()
        conn.close()
    
    def _update_deployment_rollback(self, deployment_id: int, rollback_id: int):
        """Update deployment rollback information"""
        conn = sqlite3.connect(str(self.deployment_db_path))
        conn.execute('''
            UPDATE deployments 
            SET rollback_id = ?
            WHERE id = ?
        ''', (rollback_id, deployment_id))
        conn.commit()
        conn.close()
    
    def get_deployments(self, environment: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get deployments"""
        conn = sqlite3.connect(str(self.deployment_db_path))
        cursor = conn.cursor()
        
        if environment:
            cursor.execute('''
                SELECT * FROM deployments 
                WHERE environment = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (environment, limit))
        else:
            cursor.execute('''
                SELECT * FROM deployments 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        deployments = []
        
        for row in cursor.fetchall():
            deployment = dict(zip(columns, row))
            if deployment["metadata"]:
                deployment["metadata"] = json.loads(deployment["metadata"])
            deployments.append(deployment)
        
        conn.close()
        
        return {
            "success": True,
            "deployments": deployments,
            "total": len(deployments)
        }
    
    def get_deployment_steps(self, deployment_id: int) -> Dict[str, Any]:
        """Get deployment steps"""
        conn = sqlite3.connect(str(self.deployment_db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM deployment_steps 
            WHERE deployment_id = ? 
            ORDER BY started_at ASC
        ''', (deployment_id,))
        
        columns = [desc[0] for desc in cursor.description]
        steps = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "steps": steps,
            "total": len(steps)
        }
    
    def configure_environment(self, environment: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure deployment environment"""
        try:
            if environment not in self.config["environments"]:
                return {"success": False, "error": f"Invalid environment: {environment}"}
            
            # Save environment configuration
            conn = sqlite3.connect(str(self.deployment_db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO environments (name, config, created_at)
                VALUES (?, ?, ?)
            ''', (environment, json.dumps(config), time.time()))
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "environment": environment,
                "config": config
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_environments(self) -> Dict[str, Any]:
        """Get all environments"""
        conn = sqlite3.connect(str(self.deployment_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM environments ORDER BY name")
        
        columns = [desc[0] for desc in cursor.description]
        environments = []
        
        for row in cursor.fetchall():
            env = dict(zip(columns, row))
            if env["config"]:
                env["config"] = json.loads(env["config"])
            environments.append(env)
        
        conn.close()
        
        return {
            "success": True,
            "environments": environments,
            "total": len(environments)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get deployment manager status"""
        # Get deployment statistics
        conn = sqlite3.connect(str(self.deployment_db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status, COUNT(*) FROM deployments 
            GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())
        
        cursor.execute('''
            SELECT COUNT(*) FROM deployments 
            WHERE created_at > ?
        ''', (time.time() - 86400,))  # Last 24 hours
        
        recent_deployments = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "deployments": {
                "total": sum(status_counts.values()),
                "by_status": status_counts,
                "recent_24h": recent_deployments
            },
            "environments": self.config["environments"],
            "strategies": ["blue_green", "rolling", "canary"],
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
deployment_manager = DeploymentManager()