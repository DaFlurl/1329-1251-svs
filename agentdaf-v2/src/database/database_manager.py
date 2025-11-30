"""
Database management module for AgentDaf1.1 application.

This module provides database operations, table management, and schema handling
for the SQLite database backend.
"""

import sqlite3
import json
import logging
import threading
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages SQLite database operations including table creation, CRUD operations,
    and schema management for the AgentDaf1.1 application.
    """
    
    def __init__(self, db_path: str = "data/agentdaf1.db"):
        """
        Initialize database connection and create tables if they don't exist.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.lock = threading.Lock()
        
        # Initialize database
        self._initialize_database()
        
    def _initialize_database(self) -> None:
        """
        Initialize database connection and create required tables.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            self._create_tables()
            
            logger.info(f"Database initialized at {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_tables(self) -> None:
        """
        Create all necessary tables for the application.
        """
        tables = {
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''',
            
            'api_keys': '''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    key_name TEXT NOT NULL,
                    key_value TEXT NOT NULL,
                    permissions TEXT DEFAULT 'read',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''',
            
            'processed_data': '''
                CREATE TABLE IF NOT EXISTS processed_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    processing_status TEXT DEFAULT 'pending',
                    data_summary TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''',
            
            'system_logs': '''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT NOT NULL,
                    function_name TEXT,
                    details TEXT,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''',
            
            'dashboards': '''
                CREATE TABLE IF NOT EXISTS dashboards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''',
            
            'tasks': '''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    task_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'medium',
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''',
            
            'task_dependencies': '''
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    depends_on_task_id INTEGER NOT NULL,
                    dependency_type TEXT DEFAULT 'finish_to_start',
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (depends_on_task_id) REFERENCES tasks (id)
                )
            ''',
            
            'notifications': '''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    notification_type TEXT DEFAULT 'info',
                    is_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            '''
        }
        
        with self.lock:
            cursor = self.connection.cursor()
            try:
                for table_name, sql in tables.items():
                    cursor.execute(sql)
                    logger.info(f"Created table: {table_name}")
                    
                self.connection.commit()
                logger.info("All database tables created successfully")
                
            except sqlite3.Error as e:
                logger.error(f"Failed to create table: {e}")
                self.connection.rollback()
                raise
            finally:
                cursor.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection with thread safety.
        """
        if not self.connection:
            self._initialize_database()
        return self.connection
    
    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False, 
                    fetch_all: bool = False) -> Optional[Union[sqlite3.Row, List[sqlite3.Row]]]:
        """
        Execute a database query with parameters.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Return single row or None
            fetch_all: Return all rows or empty list
            
        Returns:
            Query result
        """
        with self.lock:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                    
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount if cursor.rowcount > 0 else None
                    
                connection.commit()
                return result
                
            except sqlite3.Error as e:
                logger.error(f"Query execution failed: {e}")
                connection.rollback()
                raise
            finally:
                cursor.close()
    
    # User management operations
    def create_user(self, username: str, email: str, password_hash: str, 
                   role: str = "user") -> int:
        """
        Create a new user account.
        
        Args:
            username: Unique username
            email: User email address
            password_hash: Hashed password
            role: User role (admin, user)
            
        Returns:
            User ID if successful, None otherwise
        """
        query = '''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
        
        try:
            result = self.execute_query(query, (username, email, password_hash, role), fetch_one=True)
            if result:
                logger.info(f"Created user: {username}")
                return result['id']
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[sqlite3.Row]:
        """
        Retrieve user by username.
        """
        query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
        return self.execute_query(query, (username,), fetch_one=True)
    
    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        """
        Retrieve user by ID.
        """
        query = "SELECT * FROM users WHERE id = ? AND is_active = 1"
        return self.execute_query(query, (user_id,), fetch_one=True)
    
    def update_user_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp.
        """
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        try:
            self.execute_query(query, (user_id,))
            logger.info(f"Updated login time for user {user_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update user login: {e}")
            return False
    
    # API key management
    def create_api_key(self, user_id: int, key_name: str, key_value: str, 
                      permissions: str = "read", expires_at: Optional[datetime] = None) -> int:
        """
        Create a new API key for user.
        """
        query = '''
            INSERT INTO api_keys (user_id, key_name, key_value, permissions, created_at, expires_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        '''
        
        try:
            result = self.execute_query(query, (user_id, key_name, key_value, permissions, expires_at), fetch_one=True)
            if result:
                logger.info(f"Created API key: {key_name} for user {user_id}")
                return result['id']
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Failed to create API key: {e}")
            return None
    
    def get_api_keys(self, user_id: int) -> List[sqlite3.Row]:
        """
        Get all API keys for a user.
        """
        query = '''
            SELECT * FROM api_keys 
            WHERE user_id = ? AND is_active = 1 
            ORDER BY created_at DESC
        '''
        return self.execute_query(query, (user_id,), fetch_all=True)
    
    # Data processing operations
    def create_processed_data_entry(self, user_id: int, file_name: str, file_type: str, 
                                    file_path: str, file_size: int = 0) -> int:
        """
        Create a new processed data entry.
        """
        query = '''
            INSERT INTO processed_data 
            (user_id, file_name, file_type, file_path, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
        
        try:
            result = self.execute_query(query, (user_id, file_name, file_type, file_path, file_size), fetch_one=True)
            if result:
                logger.info(f"Created processed data entry: {file_name}")
                return result['id']
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Failed to create processed data entry: {e}")
            return None
    
    def get_processed_data(self, user_id: int, limit: int = 50, 
                           status: Optional[str] = None) -> List[sqlite3.Row]:
        """
        Get processed data entries for a user.
        """
        query = '''
            SELECT * FROM processed_data 
            WHERE user_id = ? 
            {status_filter}
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        
        params = [user_id, limit]
        if status:
            query = query.replace("{status_filter}", "AND processing_status = ?")
            params.append(status)
        
        try:
            return self.execute_query(query, tuple(params), fetch_all=True)
        except sqlite3.Error as e:
            logger.error(f"Failed to get processed data: {e}")
            return []
    
    def update_processing_status(self, data_id: int, status: str, 
                        error_message: Optional[str] = None) -> bool:
        """
        Update the processing status of a data entry.
        """
        query = '''
            UPDATE processed_data 
            SET processing_status = ?, processed_at = CURRENT_TIMESTAMP, error_message = ?
            WHERE id = ?
        '''
        
        try:
            self.execute_query(query, (status, error_message, data_id))
            logger.info(f"Updated processing status for data {data_id} to {status}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update processing status: {e}")
            return False
    
    # Dashboard operations
    def create_dashboard(self, user_id: int, title: str, description: str = "", 
                      config: Optional[str] = None) -> int:
        """
        Create a new dashboard.
        """
        query = '''
            INSERT INTO dashboards (user_id, title, description, config, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        '''
        
        try:
            result = self.execute_query(query, (user_id, title, description, config), fetch_one=True)
            if result:
                logger.info(f"Created dashboard: {title}")
                return result['id']
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Failed to create dashboard: {e}")
            return None
    
    def get_dashboards(self, user_id: int) -> List[sqlite3.Row]:
        """
        Get all dashboards for a user.
        """
        query = '''
            SELECT * FROM dashboards 
            WHERE user_id = ? AND is_active = 1 
            ORDER BY updated_at DESC
        '''
        
        try:
            return self.execute_query(query, (user_id,), fetch_all=True)
        except sqlite3.Error as e:
            logger.error(f"Failed to get dashboards: {e}")
            return []
    
    # Task management operations
    def create_task(self, user_id: int, title: str, task_type: str, 
                  description: str = "", priority: str = "medium", 
                  config: Optional[str] = None) -> int:
        """
        Create a new task.
        """
        query = '''
            INSERT INTO tasks (user_id, title, description, task_type, priority, config, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        '''
        
        try:
            result = self.execute_query(query, (user_id, title, description, task_type, priority, config), fetch_one=True)
            if result:
                logger.info(f"Created task: {title}")
                return result['id']
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Failed to create task: {e}")
            return None
    
    def get_tasks(self, user_id: int, status: Optional[str] = None, 
                 limit: int = 20) -> List[sqlite3.Row]:
        """
        Get tasks for a user with optional filtering.
        """
        query = '''
            SELECT * FROM tasks 
            WHERE user_id = ? 
            {status_filter}
            ORDER BY priority DESC, created_at DESC 
            LIMIT ?
        '''
        
        params = [user_id, limit]
        if status:
            query = query.replace("{status_filter}", "AND status = ?")
            params.append(status)
        
        try:
            return self.execute_query(query, tuple(params), fetch_all=True)
        except sqlite3.Error as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    # System logging
    def log_system_event(self, level: str, message: str, module: str = "", 
                    function_name: Optional[str] = None, details: Optional[str] = None, 
                    user_id: Optional[int] = None) -> bool:
        """
        Log a system event.
        """
        query = '''
            INSERT INTO system_logs (level, message, module, function_name, details, user_id, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
        
        try:
            self.execute_query(query, (level, message, module, function_name, details, user_id))
            logger.info(f"Logged system event: {level} - {message}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to log system event: {e}")
            return False
    
    def get_system_logs(self, level: Optional[str] = None, limit: int = 50, 
                      user_id: Optional[int] = None) -> List[sqlite3.Row]:
        """
        Get system logs with optional filtering.
        """
        query = '''
            SELECT * FROM system_logs 
            WHERE 1=1 {level_filter} {user_filter}
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        
        params = [limit]
        filters = []
        
        if level:
            query = query.replace("{level_filter}", "AND level = ?")
            filters.append(level)
            params.append(level)
        
        if user_id:
            query = query.replace("{user_filter}", "AND user_id = ?")
            filters.append(user_id)
            params.append(user_id)
        
        # Replace the first placeholder with actual filters
        if filters:
            actual_query = query.replace("WHERE 1=1", f"WHERE 1=1 {' AND '.join(filters)}")
        else:
            actual_query = query.replace("WHERE 1=1", "WHERE 1=1")
        
        try:
            return self.execute_query(actual_query, tuple(params), fetch_all=True)
        except sqlite3.Error as e:
            logger.error(f"Failed to get system logs: {e}")
            return []
    
    # Schema and maintenance operations
    def get_table_info(self, table_name: str) -> List[sqlite3.Row]:
        """
        Get information about a specific table.
        """
        query = f"PRAGMA table_info({table_name})"
        try:
            return self.execute_query(query, fetch_all=True)
        except sqlite3.Error as e:
            logger.error(f"Failed to get table info: {e}")
            return []
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database.
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False
    
    def close(self) -> None:
        """
        Close database connection.
        """
        with self.lock:
            if self.connection:
                self.connection.close()
                self.connection = None
                logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()