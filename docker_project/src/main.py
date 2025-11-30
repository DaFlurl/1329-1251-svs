# Core modules for AgentDaf1.1
__version__ = "1.0.0"

# Import standard library modules
import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import uuid

# Flask and web imports
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS

# Database imports
try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    create_engine = create_engine  # Make available globally
except ImportError:
    create_engine = None

# Utility imports
try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None

# Configuration
class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8080'))
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/agentdaf1.db')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_REPO = os.getenv('GITHUB_REPO', '')

# Database setup
if create_engine:
    # Ensure data directory exists
    db_path = Config.DATABASE_URL.replace('sqlite:///', '')
    import os
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(Config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()

# Logging setup
logging.basicConfig(
    level=logging.INFO if not Config.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Utility functions
def get_current_time() -> datetime:
    """Get current time in UTC"""
    return datetime.now(timezone.utc)

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024:
            return f"{bytes_value} {unit}"
        bytes_value = bytes_value / 1024
    return f"{bytes_value:.1f} GB"

def safe_json_loads(file_path: str) -> Optional[Dict]:
    """Safely load JSON file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return None

# Database Models
@dataclass
class Task:
    """Task model for task management"""
    title: str
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = 'pending'
    priority: str = 'medium'
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics data model"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    uptime: float
    boot_time: float
    processes_running: int
    load_average: List[float]

@dataclass
class SystemStatus:
    """System status information"""
    status: str
    message: str
    last_check: datetime
    details: Dict[str, Any]

@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    refresh_interval: int = 30
    max_history_points: int = 100
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'cpu': 80.0,
        'memory': 85.0,
        'disk': 90.0,
        'uptime': 95.0
    })

# Initialize database (moved to app creation to avoid module-level execution)

# Flask Application Factory
def create_app():
    """Create and configure Flask application with proper factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG
    app.config['DATABASE_URL'] = Config.DATABASE_URL
    
    # CORS setup
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize database if available
    if create_engine:
        try:
            # Create database tables
            Base.metadata.create_all(engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
        
        try:
            # Try to import database from main project
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from src.database.database_manager import DatabaseManager
            logger.info("Database manager imported successfully")
        except ImportError:
            try:
                from . import database
                database.init_db(app)
            except ImportError:
                logger.warning("Database module not available")
    
    # Register routes
    register_routes(app)
    
    return app

def register_routes(app):
    """Register all application routes"""
    
    # Context processor
    @app.context_processor
    def inject_config():
        """Inject configuration into templates"""
        return {
            'config': Config,
            'current_time': get_current_time()
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Basic health check endpoint"""
        try:
            return jsonify({
                'status': 'healthy',
                'timestamp': get_current_time().isoformat(),
                'version': '1.0.0'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({'error': 'Health check failed'}), 500

    # System metrics endpoint
    @app.route('/api/stats', methods=['GET'])
    def get_system_stats():
        """Get system performance metrics"""
        try:
            # Mock system metrics for demo
            metrics = PerformanceMetrics(
                timestamp=get_current_time(),
                cpu_percent=25.5,
                memory_percent=67.8,
                disk_usage=45.2,
                uptime=99.9,
                boot_time=12.3,
                processes_running=156,
                load_average=[1.2, 1.5, 1.8]
            )
            
            return jsonify({
                'metrics': metrics.__dict__,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Stats endpoint failed: {e}")
            return jsonify({'error': 'Failed to get system stats'}), 500

    # Task management endpoints
    @app.route('/api/tasks', methods=['GET'])
    def get_tasks():
        """Get all tasks"""
        try:
            # Mock tasks data
            tasks = [
                Task(
                    id="task-1",
                    title="System Health Check",
                    description="Monitor system health metrics",
                    status="completed",
                    priority="high",
                    created_at=get_current_time(),
                    completed_at=get_current_time(),
                    created_by="system"
                ),
                Task(
                    id="task-2", 
                    title="Database Optimization",
                    description="Optimize database queries and indexes",
                    status="in_progress",
                    priority="medium",
                    created_at=get_current_time(),
                    created_by="admin"
                )
            ]
            
            return jsonify({
                'tasks': [task.__dict__ for task in tasks],
                'count': len(tasks)
            })
        except Exception as e:
            logger.error(f"Get tasks failed: {e}")
            return jsonify({'error': 'Failed to get tasks'}), 500

    @app.route('/api/tasks', methods=['POST'])
    def create_task():
        """Create a new task"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            task = Task(
                title=data.get('title', ''),
                description=data.get('description', ''),
                priority=data.get('priority', 'medium'),
                created_at=get_current_time(),
                created_by='api_user'
            )
            
            # Save to database if available
            if create_engine:
                try:
                    # Try to import database from main project
                    import sys
                    from pathlib import Path
                    sys.path.append(str(Path(__file__).parent.parent.parent))
                    from src.database.database_manager import DatabaseManager
                    db = DatabaseManager()
                    # Note: This would need proper task saving implementation
                    logger.info("Task would be saved to database")
                except ImportError:
                    try:
                        from . import database
                        database.save_task(task)
                    except ImportError:
                        logger.warning("Database module not available")
            
            logger.info(f"Created task: {task.title}")
            
            return jsonify({
                'task': task.__dict__,
                'status': 'created'
            }), 201
        except Exception as e:
            logger.error(f"Create task failed: {e}")
            return jsonify({'error': 'Failed to create task'}), 500

    # File management endpoints
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Handle file upload"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No filename provided'}), 400
            
            # Save uploaded file
            filename = f"uploads/{file.filename}"
            os.makedirs('uploads', exist_ok=True)
            file.save(filename)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'size': os.path.getsize(filename) if os.path.exists(filename) else 0
            })
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return jsonify({'error': 'File upload failed'}), 500

    # Dashboard endpoint
    @app.route('/api/dashboards', methods=['GET'])
    def get_dashboards():
        """Get available dashboards"""
        try:
            dashboards = [
                {
                    'id': 'system-overview',
                    'title': 'System Overview',
                    'description': 'Real-time system metrics and status',
                    'url': '/dashboard/system',
                    'last_updated': get_current_time().isoformat()
                },
                {
                    'id': 'performance-metrics',
                    'title': 'Performance Metrics',
                    'description': 'Detailed performance analysis and trends',
                    'url': '/dashboard/performance',
                    'last_updated': get_current_time().isoformat()
                }
            ]
            
            return jsonify({
                'dashboards': dashboards
            })
        except Exception as e:
            logger.error(f"Get dashboards failed: {e}")
            return jsonify({'error': 'Failed to get dashboards'}), 500

    # WebSocket endpoint for real-time updates
    @app.route('/ws/updates')
    def websocket_updates():
        """WebSocket endpoint for real-time updates"""
        if request.environ.get('HTTP_UPGRADE') == 'websocket':
            # Handle WebSocket upgrade
            return "WebSocket connection established"
        else:
            return "Use WebSocket protocol"

# Main application
def main():
    """Main application entry point"""
    app = create_app()
    
    # Create required directories
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    logger.info("Starting AgentDaf1.1 application")
    logger.info(f"Configuration loaded: DEBUG={Config.DEBUG}, PORT={Config.PORT}")
    
    return app

if __name__ == '__main__':
    app = main()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )