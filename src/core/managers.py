"""
Core managers for AgentDaf1.1 platform.

This module provides unified access to all core components and services
including dashboard generation, task management, performance monitoring,
AI tools, and WebSocket communication.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Configuration for dashboard generation."""
    title: str
    description: str
    refresh_interval: int = 30
    theme: str = "default"
    layout: str = "grid"


@dataclass
class TaskConfig:
    """Configuration for task management."""
    name: str
    description: str
    priority: str = "medium"
    status: str = "pending"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    threshold: Optional[float] = None
    category: str = "system"


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    channel: str = "default"


class BaseManager:
    """Base class for all managers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self) -> bool:
        """Initialize the manager."""
        try:
            return await self._initialize_impl()
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
            return False
    
    async def _initialize_impl(self) -> bool:
        """Implementation-specific initialization."""
        raise NotImplementedError
    
    async def cleanup(self) -> bool:
        """Cleanup resources."""
        try:
            return await self._cleanup_impl()
        except Exception as e:
            self.logger.error(f"Failed to cleanup {self.__class__.__name__}: {e}")
            return False
    
    async def _cleanup_impl(self) -> bool:
        """Implementation-specific cleanup."""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        raise NotImplementedError


class DashboardGenerator(BaseManager):
    """Manager for dashboard generation and management."""
    
    def __init__(self):
        super().__init__()
        self.active_dashboards: Dict[str, DashboardConfig] = {}
        self.dashboard_cache: Dict[str, str] = {}
    
    async def _initialize_impl(self) -> bool:
        """Initialize dashboard generator."""
        try:
            # Load existing dashboards from database or config
            self.logger.info("Initializing Dashboard Generator")
            return True
        except Exception as e:
            self.logger.error(f"Dashboard generator initialization failed: {e}")
            return False
    
    async def create_dashboard(self, config: DashboardConfig) -> str:
        """Create a new dashboard."""
        dashboard_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_dashboards[dashboard_id] = config
        
        # Generate dashboard HTML
        dashboard_html = self._generate_dashboard_html(config, dashboard_id)
        
        # Cache the dashboard
        self.dashboard_cache[dashboard_id] = dashboard_html
        
        self.logger.info(f"Created dashboard: {config.title} (ID: {dashboard_id})")
        return dashboard_id
    
    def _generate_dashboard_html(self, config: DashboardConfig, dashboard_id: str) -> str:
        """Generate dashboard HTML."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard-header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .dashboard-content {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .widget {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .widget h3 {{ margin: 0 0 10px 0; color: #333; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .status-indicator {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }}
        .status-good {{ background-color: #28a745; }}
        .status-warning {{ background-color: #ffc107; }}
        .status-error {{ background-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>{config.title}</h1>
        <p>{config.description}</p>
        <button onclick="refreshDashboard('{dashboard_id}')">Refresh</button>
    </div>
    <div class="dashboard-content">
        <div class="widget">
            <h3>System Status</h3>
            <div class="metric-value">Online</div>
        </div>
        <div class="widget">
            <h3>Performance</h3>
            <div class="metric-value">98.5%</div>
        </div>
    </div>
    <script>
        function refreshDashboard(id) {{
            // Refresh dashboard data
            console.log('Refreshing dashboard: ' + id);
        }}
    </script>
</body>
</html>
        """
    
    def get_dashboard(self, dashboard_id: str) -> Optional[str]:
        """Get dashboard HTML by ID."""
        return self.dashboard_cache.get(dashboard_id)
    
    def list_dashboards(self) -> Dict[str, DashboardConfig]:
        """List all active dashboards."""
        return self.active_dashboards
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        if dashboard_id in self.active_dashboards:
            del self.active_dashboards[dashboard_id]
            if dashboard_id in self.dashboard_cache:
                del self.dashboard_cache[dashboard_id]
            self.logger.info(f"Deleted dashboard: {dashboard_id}")
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get dashboard generator status."""
        return {
            "active_dashboards": len(self.active_dashboards),
            "cached_dashboards": len(self.dashboard_cache),
            "last_refresh": datetime.now().isoformat()
        }


class TaskManager(BaseManager):
    """Manager for task scheduling and execution."""
    
    def __init__(self):
        super().__init__()
        self.tasks: Dict[str, TaskConfig] = {}
        self.task_queue: List[str] = []
    
    async def _initialize_impl(self) -> bool:
        """Initialize task manager."""
        try:
            self.logger.info("Initializing Task Manager")
            return True
        except Exception as e:
            self.logger.error(f"Task manager initialization failed: {e}")
            return False
    
    async def create_task(self, config: TaskConfig) -> str:
        """Create a new task."""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.tasks[task_id] = config
        
        self.logger.info(f"Created task: {config.name} (ID: {task_id})")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[TaskConfig]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status_filter: Optional[str] = None) -> Dict[str, TaskConfig]:
        """List tasks with optional status filter."""
        if status_filter:
            return {k: v for k, v in self.tasks.items() if v.status == status_filter}
        return self.tasks
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.logger.info(f"Updated task {task_id} status to {status}")
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get task manager status."""
        return {
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == "pending"]),
            "in_progress_tasks": len([t for t in self.tasks.values() if t.status == "in_progress"]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"])
        }


class PerformanceMonitor(BaseManager):
    """Manager for system performance monitoring."""
    
    def __init__(self):
        super().__init__()
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.alert_thresholds: Dict[str, float] = {
            "cpu": 80.0,
            "memory": 85.0,
            "disk": 90.0
        }
    
    async def _initialize_impl(self) -> bool:
        """Initialize performance monitor."""
        try:
            self.logger.info("Initializing Performance Monitor")
            return True
        except Exception as e:
            self.logger.error(f"Performance monitor initialization failed: {e}")
            return False
    
    async def record_metric(self, metric: PerformanceMetric) -> bool:
        """Record a performance metric."""
        self.metrics[metric.name] = metric
        
        # Check threshold
        if metric.threshold and metric.value > metric.threshold:
            await self._trigger_alert(metric)
        
        self.logger.info(f"Recorded metric: {metric.name} = {metric.value} {metric.unit}")
        return True
    
    async def _trigger_alert(self, metric: PerformanceMetric):
        """Trigger performance alert."""
        self.logger.warning(f"Performance alert: {metric.name} ({metric.value}) exceeds threshold ({metric.threshold})")
        # Here you could integrate with notification system
    
    def get_metrics(self, category_filter: Optional[str] = None) -> Dict[str, PerformanceMetric]:
        """Get metrics with optional category filter."""
        if category_filter:
            return {k: v for k, v in self.metrics.items() if v.category == category_filter}
        return self.metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get performance monitor status."""
        if not self.metrics:
            return {"status": "no_data"}
        
        latest_metric = max(self.metrics.values(), key=lambda m: m.timestamp)
        return {
            "metrics_count": len(self.metrics),
            "latest_update": latest_metric.timestamp.isoformat(),
            "alerts_triggered": len([m for m in self.metrics.values() 
                                if m.threshold and m.value > m.threshold])
        }


class AITools(BaseManager):
    """Manager for AI-powered tools and analysis."""
    
    def __init__(self):
        super().__init__()
        self.analysis_cache: Dict[str, Any] = {}
        self.tools_enabled: List[str] = ["code_analysis", "test_generation", "performance_profiling"]
    
    async def _initialize_impl(self) -> bool:
        """Initialize AI tools."""
        try:
            self.logger.info("Initializing AI Tools")
            return True
        except Exception as e:
            self.logger.error(f"AI tools initialization failed: {e}")
            return False
    
    async def analyze_code(self, code_content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze code content."""
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Perform basic code analysis
        lines = code_content.split('/n')
        analysis_result = {
            "analysis_id": analysis_id,
            "type": analysis_type,
            "lines_count": len(lines),
            "functions_count": len([line for line in lines if 'def ' in line]),
            "classes_count": len([line for line in lines if 'class ' in line]),
            "imports": [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')],
            "complexity_score": self._calculate_complexity(code_content),
            "timestamp": datetime.now().isoformat()
        }
        
        self.analysis_cache[analysis_id] = analysis_result
        return analysis_result
    
    def _calculate_complexity(self, code_content: str) -> float:
        """Calculate code complexity score."""
        # Simple complexity based on control structures and nesting
        lines = code_content.split('/n')
        complexity = 0.0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('if ', 'for ', 'while ', 'try:', 'except:', 'with ')):
                complexity += 1.0
            elif stripped.startswith(('def ', 'class ')):
                complexity += 2.0
        
        return min(complexity, 10.0)  # Cap at 10
    
    async def generate_tests(self, function_code: str, test_type: str = "unit") -> Dict[str, Any]:
        """Generate test cases for code."""
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Simple test generation based on function analysis
        test_result = {
            "test_id": test_id,
            "type": test_type,
            "generated_tests": self._generate_test_cases(function_code),
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Generated {test_type} tests for function")
        return test_result
    
    def _generate_test_cases(self, function_code: str) -> List[str]:
        """Generate test cases from function code."""
        # Extract function name
        lines = function_code.split('/n')
        function_name = "unknown_function"
        
        for line in lines:
            if line.strip().startswith('def '):
                function_name = line.strip().split('(')[0].replace('def ', '').strip()
                break
        
        # Generate basic test cases
        test_cases = [
            f"def test_{function_name}_basic():",
            f"    # Test basic functionality",
            f"    assert {function_name}() is not None",
            f"    # Add more specific test cases here",
            f"    pass"
        ]
        
        return test_cases
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result by ID."""
        return self.analysis_cache.get(analysis_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI tools status."""
        return {
            "enabled_tools": self.tools_enabled,
            "cached_analyses": len(self.analysis_cache),
            "last_analysis": datetime.now().isoformat()
        }


class WebSocketService(BaseManager):
    """Manager for WebSocket communication."""
    
    def __init__(self):
        super().__init__()
        self.connections: Dict[str, Any] = {}
        self.message_queue: List[WebSocketMessage] = []
        self.channels: Dict[str, List[str]] = {}
    
    async def _initialize_impl(self) -> bool:
        """Initialize WebSocket service."""
        try:
            self.logger.info("Initializing WebSocket Service")
            return True
        except Exception as e:
            self.logger.error(f"WebSocket service initialization failed: {e}")
            return False
    
    async def add_connection(self, connection_id: str, user_id: Optional[str] = None) -> bool:
        """Add a new WebSocket connection."""
        self.connections[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        
        self.logger.info(f"Added WebSocket connection: {connection_id}")
        return True
    
    async def remove_connection(self, connection_id: str) -> bool:
        """Remove a WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]
            self.logger.info(f"Removed WebSocket connection: {connection_id}")
            return True
        return False
    
    async def broadcast_message(self, message: WebSocketMessage) -> int:
        """Broadcast message to all connections."""
        sent_count = 0
        for connection_id, connection in self.connections.items():
            # In a real implementation, this would send via WebSocket
            sent_count += 1
            self.logger.debug(f"Broadcasting to connection {connection_id}")
        
        self.message_queue.append(message)
        self.logger.info(f"Broadcasted message to {sent_count} connections")
        return sent_count
    
    async def send_to_channel(self, channel: str, message: WebSocketMessage) -> int:
        """Send message to specific channel."""
        if channel not in self.channels:
            self.channels[channel] = []
        
        sent_count = 0
        for connection_id in self.channels[channel]:
            # Send to specific connections
            sent_count += 1
        
        self.message_queue.append(message)
        self.logger.info(f"Sent message to channel '{channel}': {sent_count} connections")
        return sent_count
    
    def get_status(self) -> Dict[str, Any]:
        """Get WebSocket service status."""
        return {
            "active_connections": len(self.connections),
            "message_queue_size": len(self.message_queue),
            "active_channels": len(self.channels),
            "last_broadcast": datetime.now().isoformat() if self.message_queue else None
        }


# Manager registry for easy access
class ManagerRegistry:
    """Registry for all core managers."""
    
    def __init__(self):
        self.dashboard_generator = DashboardGenerator()
        self.task_manager = TaskManager()
        self.performance_monitor = PerformanceMonitor()
        self.ai_tools = AITools()
        self.websocket_service = WebSocketService()
    
    async def initialize_all(self) -> Dict[str, bool]:
        """Initialize all managers."""
        results = {}
        
        managers = [
            ("dashboard_generator", self.dashboard_generator),
            ("task_manager", self.task_manager),
            ("performance_monitor", self.performance_monitor),
            ("ai_tools", self.ai_tools),
            ("websocket_service", self.websocket_service)
        ]
        
        for name, manager in managers:
            results[name] = await manager.initialize()
        
        return results
    
    def get_manager(self, name: str) -> Optional[BaseManager]:
        """Get manager by name."""
        manager_map = {
            "dashboard_generator": self.dashboard_generator,
            "task_manager": self.task_manager,
            "performance_monitor": self.performance_monitor,
            "ai_tools": self.ai_tools,
            "websocket_service": self.websocket_service
        }
        return manager_map.get(name)
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all managers."""
        return {
            "dashboard_generator": self.dashboard_generator.get_status(),
            "task_manager": self.task_manager.get_status(),
            "performance_monitor": self.performance_monitor.get_status(),
            "ai_tools": self.ai_tools.get_status(),
            "websocket_service": self.websocket_service.get_status()
        }


# Export main managers for easy import
__all__ = [
    'DashboardGenerator',
    'TaskManager', 
    'PerformanceMonitor',
    'AITools',
    'WebSocketService',
    'ManagerRegistry',
    'DatabaseManager',
    'ConfigManager'
]

class DatabaseManager(BaseManager):
    """Manager for database operations and SQLite connection management."""
    
    def __init__(self):
        super().__init__()
        self.db_path = "data/agentdaf1.db"
        self.connection = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def _initialize_impl(self) -> bool:
        """Initialize database manager and create SQLite connection."""
        try:
            import sqlite3
            self.connection = sqlite3.connect(self.db_path)
            
            # Create tables if they don't exist
            await self._create_tables()
            
            self.logger.info(f"Database initialized: {self.db_path}")
            return True
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def _create_tables(self):
        """Create necessary database tables."""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        
        # Create dashboards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboards (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                html_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                assigned_to TEXT,
                due_date TIMESTAMP,
                tags TEXT,  -- JSON array stored as TEXT
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create performance_metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                threshold REAL,
                category TEXT DEFAULT 'system'
            )
        """)
        
        # Create ai_analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_analyses (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                result TEXT,  -- JSON stored as TEXT
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create websockets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS websockets (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                channel TEXT DEFAULT 'default'
            )
        """)
        
        self.connection.commit()
        self.logger.info("Database tables created/verified")
    
    async def _cleanup_impl(self) -> bool:
        """Cleanup database connections."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.logger.info("Database connection closed")
            return True
        except Exception as e:
            self.logger.error(f"Database cleanup failed: {e}")
            return False
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query."""
        if not self.connection:
            self.logger.error("Database not connected")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Get column names from cursor description
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            results = []
            for row in rows:
                result = {}
                for i, column in enumerate(columns):
                    result[column] = row[i]
                results.append(result)
            
            return results
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []
    
    async def execute_insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Execute an INSERT query."""
        if not self.connection:
            self.logger.error("Database not connected")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Build dynamic INSERT query
            columns = list(data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            
            self.logger.debug(f"Inserted into {table}: {data}")
            return True
        except Exception as e:
            self.logger.error(f"Insert execution failed: {e}")
            return False
    
    async def execute_update(self, table: str, set_clause: str, data: Dict[str, Any]) -> bool:
        """Execute an UPDATE query."""
        if not self.connection:
            self.logger.error("Database not connected")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Build dynamic UPDATE query
            set_clauses = []
            values = []
            
            for key, value in data.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            set_clause = ', '.join(set_clauses)
            query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
            
            cursor.execute(query, tuple(values + [data.get('id')]))
            self.connection.commit()
            
            self.logger.debug(f"Updated {table}: {data}")
            return True
        except Exception as e:
            self.logger.error(f"Update execution failed: {e}")
            return False
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Get dashboard by ID."""
        results = await self.execute_query(
            "SELECT id, title, description, html_content, created_at, updated_at FROM dashboards WHERE id = ?",
            (dashboard_id,)
        )
        return results[0] if results else None
    
    async def save_dashboard(self, dashboard_id: str, title: str, description: str, html_content: str) -> bool:
        """Save or update dashboard."""
        data = {
            "id": dashboard_id,
            "title": title,
            "description": description,
            "html_content": html_content,
            "updated_at": datetime.now().isoformat()
        }
        
        return await self.execute_insert("dashboards", data)
    
    async def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all dashboards."""
        return await self.execute_query("SELECT id, title, description, created_at, updated_at FROM dashboards ORDER BY created_at DESC")
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        return await self.execute_update("dashboards", "id = ?", {"id": dashboard_id})
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        results = await self.execute_query(
            "SELECT id, name, description, priority, status, assigned_to, due_date, tags, created_at, updated_at FROM tasks WHERE id = ?",
            (task_id,)
        )
        return results[0] if results else None
    
    async def save_task(self, task_id: str, name: str, description: str, priority: str = "medium", status: str = "pending", assigned_to: Optional[str] = None, due_date: Optional[datetime] = None, tags: Optional[List[str]] = None) -> bool:
        """Save or update task."""
        import json
        
        data = {
            "id": task_id,
            "name": name,
            "description": description,
            "priority": priority,
            "status": status,
            "assigned_to": assigned_to,
            "due_date": due_date.isoformat() if due_date else None,
            "tags": json.dumps(tags) if tags else None,
            "updated_at": datetime.now().isoformat()
        }
        
        return await self.execute_insert("tasks", data)
    
    async def list_tasks(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks with optional status filter."""
        if status_filter:
            return await self.execute_query(
                "SELECT id, name, description, priority, status, assigned_to, due_date, tags, created_at, updated_at FROM tasks WHERE status = ? ORDER BY created_at DESC",
                (status_filter,)
            )
        else:
            return await self.execute_query("SELECT id, name, description, priority, status, assigned_to, due_date, tags, created_at, updated_at FROM tasks ORDER BY created_at DESC")
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status."""
        return await self.execute_update("tasks", "status = ?", {"id": task_id, "status": status})
    
    async def get_performance_metric(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Get performance metric by name."""
        results = await self.execute_query(
            "SELECT id, name, value, unit, timestamp, threshold, category FROM performance_metrics WHERE name = ? ORDER BY timestamp DESC",
            (metric_name,)
        )
        return results[0] if results else None
    
    async def record_metric(self, metric_name: str, value: float, unit: str, category: str = "system", threshold: Optional[float] = None) -> bool:
        """Record a performance metric."""
        data = {
            "id": f"metric_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "threshold": threshold
        }
        
        return await self.execute_insert("performance_metrics", data)
    
    async def get_metrics(self, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get metrics with optional category filter."""
        if category_filter:
            return await self.execute_query(
                "SELECT id, name, value, unit, timestamp, threshold, category FROM performance_metrics WHERE category = ? ORDER BY timestamp DESC",
                (category_filter,)
            )
        else:
            return await self.execute_query("SELECT id, name, value, unit, timestamp, threshold, category FROM performance_metrics ORDER BY timestamp DESC")
    
    async def save_analysis(self, analysis_id: str, analysis_type: str, content: str, result: str) -> bool:
        """Save AI analysis result."""
        data = {
            "id": analysis_id,
            "type": analysis_type,
            "content": content,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.execute_insert("ai_analyses", data)
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result by ID."""
        results = await self.execute_query(
            "SELECT id, type, content, result, timestamp FROM ai_analyses WHERE id = ?",
            (analysis_id,)
        )
        return results[0] if results else None
    
    async def get_websocket_connections(self) -> List[Dict[str, Any]]:
        """Get all WebSocket connections."""
        return await self.execute_query("SELECT id, user_id, connected_at, last_ping, channel FROM websockets ORDER BY connected_at DESC")
    
    async def add_websocket_connection(self, connection_id: str, user_id: Optional[str] = None) -> bool:
        """Add WebSocket connection."""
        data = {
            "id": connection_id,
            "user_id": user_id,
            "connected_at": datetime.now().isoformat(),
            "last_ping": datetime.now().isoformat(),
            "channel": "default"
        }
        
        return await self.execute_insert("websockets", data)
    
    async def remove_websocket_connection(self, connection_id: str) -> bool:
        """Remove WebSocket connection."""
        return await self.execute_update("websockets", "id = ?", {"id": connection_id})
    
    def get_connection(self):
        """Get database connection for external use."""
        return self.connection
    
    def get_status(self) -> Dict[str, Any]:
        """Get database manager status."""
        if not self.connection:
            return {"status": "not_connected", "database_path": self.db_path}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM dashboards")
            dashboard_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM performance_metrics")
            metric_count = cursor.fetchone()[0]
            
            return {
                "status": "connected",
                "database_path": self.db_path,
                "dashboard_count": dashboard_count,
                "task_count": task_count,
                "metric_count": metric_count,
                "connection_active": True
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class ConfigManager(BaseManager):
    """Manager for configuration management and environment variables."""
    
    def __init__(self):
        super().__init__()
        self.config_data: Dict[str, Any] = {}
        self.config_file = "config/config.json"
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def _initialize_impl(self) -> bool:
        """Initialize configuration manager."""
        try:
            # Load configuration from file
            self._load_config()
            
            # Load environment variables
            self._load_env_vars()
            
            self.logger.info("Configuration manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"Configuration manager initialization failed: {e}")
            return False
    
    def _load_config(self):
        """Load configuration from JSON file."""
        try:
            import os
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config_data = json.load(f)
                    self.logger.debug(f"Loaded configuration from {self.config_file}")
            else:
                # Create default configuration
                self.config_data = {
                    "app": {
                        "name": "AgentDaf1.1",
                        "version": "1.0.0",
                        "debug": False
                    },
                    "database": {
                        "path": "data/agentdaf1.db",
                        "backup_enabled": True,
                        "backup_interval": 3600  # 1 hour
                    },
                    "websocket": {
                        "port": 8081,
                        "max_connections": 100
                    },
                    "performance_monitoring": {
                        "enabled": True,
                        "alert_thresholds": {
                            "cpu": 80.0,
                            "memory": 85.0,
                            "disk": 90.0
                        }
                    }
                }
                
                # Save default configuration
                self._save_config()
                self.logger.info(f"Created default configuration at {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    def _load_env_vars(self):
        """Load environment variables into configuration."""
        import os
        
        env_mappings = {
            "SECRET_KEY": ["app.secret_key"],
            "DEBUG": ["app.debug"],
            "HOST": ["app.host"],
            "PORT": ["app.port"],
            "GITHUB_TOKEN": ["github.token"],
            "GITHUB_REPO": ["github.repo"],
            "JWT_SECRET_KEY": ["jwt.secret_key"]
        }
        
        for env_var, config_paths in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to the nested config path
                current = self.config_data
                for path in config_paths:
                    if '.' in path:
                        parts = path.split('.')
                        current = current.get(parts[0], {})
                    else:
                        current = current
                
                current[config_paths[-1]] = value
                self.config_data = current
                self.logger.debug(f"Loaded environment variable {env_var} -> {config_paths[-1]}")
    
    def _save_config(self):
        """Save configuration to JSON file."""
        try:
            import os
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
                self.logger.debug(f"Saved configuration to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    async def _cleanup_impl(self) -> bool:
        """Cleanup configuration manager resources."""
        try:
            # Clear any cached data
            self.config_data.clear()
            self.logger.info("Configuration manager cleanup completed")
            return True
        except Exception as e:
            self.logger.error(f"Configuration manager cleanup failed: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        current = self.config_data
        
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current.get(keys[-1], default)
    
    def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value by key."""
        keys = key.split('.')
        current = self.config_data
        
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                current = {}
        
        current[keys[-1]] = value
        self.config_data = current
        
        # Save to file if needed
        try:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
        
        self.logger.debug(f"Set configuration {key} = {value}")
        return True
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration data."""
        return self.config_data.copy()
    
    def reload_config(self) -> bool:
        """Reload configuration from file."""
        try:
            self._load_config()
            self._load_env_vars()
            self.logger.info("Configuration reloaded")
            return True
        except Exception as e:
            self.logger.error(f"Configuration reload failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration manager status."""
        import os
        return {
            "config_loaded": bool(self.config_data),
            "config_file_exists": os.path.exists(self.config_file),
            "config_file_path": self.config_file,
            "last_reload": datetime.now().isoformat()
        }