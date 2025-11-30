#!/usr/bin/env python3
"""
AgentDaf1.1 - Database Manager Tool
Advanced database operations and management
"""

import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class DatabaseManager:
    """Advanced database operations and management"""
    
    def __init__(self):
        self.name = "Database Manager"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
        self.connections = {}
        self.query_history = []
        self.migration_history = []
        self.performance_stats = {}
        self.lock = threading.Lock()
        
        # Default database path
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.default_db_path = self.project_root / "data" / "agentdaf1.db"
        
        # Ensure data directory exists
        self.default_db_path.parent.mkdir(exist_ok=True)
        
        self.logger.info(f"Database Manager initialized: {self.name} v{self.version}")
    
    def get_connection(self, db_path: str = None) -> sqlite3.Connection:
        """Get database connection with connection pooling"""
        db_path = db_path or str(self.default_db_path)
        
        if db_path not in self.connections:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            self.connections[db_path] = conn
            
        return self.connections[db_path]
    
    def execute_query(self, query: str, params: tuple = None, db_path: str = None) -> Dict[str, Any]:
        """Execute SQL query with performance tracking"""
        start_time = time.time()
        conn = self.get_connection(db_path)
        
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            execution_time = time.time() - start_time
            
            # Determine query type
            query_lower = query.lower().strip()
            if query_lower.startswith('select'):
                result = {
                    "type": "select",
                    "data": [dict(row) for row in cursor.fetchall()],
                    "row_count": len(cursor.fetchall()) if cursor.description else 0
                }
            elif query_lower.startswith('insert'):
                result = {
                    "type": "insert",
                    "last_id": cursor.lastrowid,
                    "row_count": cursor.rowcount
                }
            elif query_lower.startswith('update'):
                result = {
                    "type": "update", 
                    "row_count": cursor.rowcount
                }
            elif query_lower.startswith('delete'):
                result = {
                    "type": "delete",
                    "row_count": cursor.rowcount
                }
            else:
                result = {
                    "type": "other",
                    "row_count": cursor.rowcount
                }
            
            conn.commit()
            
            # Track performance
            with self.lock:
                self.query_history.append({
                    "query": query,
                    "params": params,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
                
                # Keep only last 1000 queries
                if len(self.query_history) > 1000:
                    self.query_history = self.query_history[-1000:]
            
            result["execution_time"] = execution_time
            result["success"] = True
            
            return result
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Query execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def get_schema_info(self, db_path: str = None) -> Dict[str, Any]:
        """Get database schema information"""
        conn = self.get_connection(db_path)
        
        try:
            # Get all tables
            tables_query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """
            tables_result = self.execute_query(tables_query, db_path=db_path)
            
            schema = {}
            for table_info in tables_result["data"]:
                table_name = table_info["name"]
                
                # Get table schema
                pragma_query = f"PRAGMA table_info({table_name})"
                pragma_result = self.execute_query(pragma_query, db_path=db_path)
                
                # Get foreign keys
                fk_query = f"PRAGMA foreign_key_list({table_name})"
                fk_result = self.execute_query(fk_query, db_path=db_path)
                
                # Get indexes
                index_query = f"PRAGMA index_list({table_name})"
                index_result = self.execute_query(index_query, db_path=db_path)
                
                schema[table_name] = {
                    "columns": pragma_result["data"],
                    "foreign_keys": fk_result["data"],
                    "indexes": index_result["data"]
                }
            
            return {
                "success": True,
                "schema": schema,
                "table_count": len(schema)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_backup(self, backup_path: str = None, db_path: str = None) -> Dict[str, Any]:
        """Create database backup"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(self.project_root / "backups" / f"backup_{timestamp}.db")
        
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        source_db = db_path or str(self.default_db_path)
        
        try:
            source_conn = sqlite3.connect(source_db)
            backup_conn = sqlite3.connect(str(backup_path))
            
            # Use SQLite backup API
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "timestamp": datetime.now().isoformat(),
                "size": backup_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_backup(self, backup_path: str, target_db: str = None) -> Dict[str, Any]:
        """Restore database from backup"""
        target_db = target_db or str(self.default_db_path)
        
        try:
            backup_conn = sqlite3.connect(backup_path)
            target_conn = sqlite3.connect(target_db)
            
            # Use SQLite backup API
            backup_conn.backup(target_conn)
            
            backup_conn.close()
            target_conn.close()
            
            return {
                "success": True,
                "backup_path": backup_path,
                "target_db": target_db,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def optimize_database(self, db_path: str = None) -> Dict[str, Any]:
        """Optimize database performance"""
        operations = [
            "VACUUM",
            "ANALYZE",
            "REINDEX"
        ]
        
        results = {}
        conn = self.get_connection(db_path)
        
        for operation in operations:
            try:
                start_time = time.time()
                conn.execute(operation)
                execution_time = time.time() - start_time
                results[operation] = {
                    "success": True,
                    "execution_time": execution_time
                }
            except Exception as e:
                results[operation] = {
                    "success": False,
                    "error": str(e)
                }
        
        conn.commit()
        return {
            "success": True,
            "operations": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_performance_stats(self, db_path: str = None) -> Dict[str, Any]:
        """Get database performance statistics"""
        conn = self.get_connection(db_path)
        
        try:
            # Get database page count and size
            page_count_result = self.execute_query("PRAGMA page_count", db_path=db_path)
            page_size_result = self.execute_query("PRAGMA page_size", db_path=db_path)
            
            # Get cache statistics
            cache_size_result = self.execute_query("PRAGMA cache_size", db_path=db_path)
            
            # Calculate database size
            page_count = page_count_result["data"][0]["page_count"] if page_count_result["data"] else 0
            page_size = page_size_result["data"][0]["page_size"] if page_size_result["data"] else 0
            db_size = page_count * page_size
            
            # Analyze recent query performance
            recent_queries = [q for q in self.query_history 
                             if datetime.fromisoformat(q["timestamp"]) > datetime.now() - timedelta(hours=1)]
            
            if recent_queries:
                avg_execution_time = sum(q["execution_time"] for q in recent_queries) / len(recent_queries)
                slow_queries = [q for q in recent_queries if q["execution_time"] > 1.0]
            else:
                avg_execution_time = 0
                slow_queries = []
            
            return {
                "success": True,
                "database_size": db_size,
                "page_count": page_count,
                "page_size": page_size,
                "cache_size": cache_size_result["data"][0]["cache_size"] if cache_size_result["data"] else 0,
                "query_stats": {
                    "total_queries": len(self.query_history),
                    "recent_queries": len(recent_queries),
                    "avg_execution_time": avg_execution_time,
                    "slow_queries": len(slow_queries)
                },
                "connections": len(self.connections)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get database manager status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "connections": len(self.connections),
            "query_history_size": len(self.query_history),
            "default_database": str(self.default_db_path),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
database_manager = DatabaseManager()