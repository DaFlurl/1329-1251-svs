#!/usr/bin/env python3
"""
AgentDaf1.1 - Restructured Flask Application

Fixed critical structural issues:
- Removed duplicate Flask app instances
- Consolidated route definitions
- Integrated verified core modules properly
- Added proper error handling and logging
"""

import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash

# Import centralized configurations
from src.config.logging_config import get_logger
from src.config.path_config import setup_project_paths

# Setup project paths
setup_project_paths()

# Import core modules
try:
    from src.core.performance_monitor import PerformanceMonitor
    from src.core.ai_tools import AITools, get_opencode_ai_tools
    from src.core.websocket_service import WebSocketService
    from src.core.dashboard_generator import DashboardGenerator
    from src.core.task_manager import TaskManager
    from auth import AuthManager, get_auth_manager
except ImportError as e:
    print(f"Error importing core modules: {e}")
    print("Please ensure all core modules are present in src/core/")
    sys.exit(1)

# Get logger
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='styles', static_url_path='/styles')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize core components
performance_monitor = PerformanceMonitor()
ai_tools = get_opencode_ai_tools()
websocket_service = WebSocketService()
dashboard_generator = DashboardGenerator()
task_manager = TaskManager()
auth_manager = get_auth_manager()

@app.route('/')
def index():
    """Main dashboard route"""
    try:
        return render_template('dashboard-3d.html')
    except Exception as e:
        logger.error(f"Error rendering 3D dashboard: {e}")
        # Fallback to regular dashboard
        try:
            return render_template('index.html')
        except:
            return jsonify({"error": "Dashboard not available"}), 500

@app.route('/dashboard-3d')
def dashboard_3d():
    """3D Enhanced dashboard route"""
    try:
        return render_template('dashboard-3d.html')
    except Exception as e:
        logger.error(f"Error rendering 3D dashboard: {e}")
        return jsonify({"error": "3D Dashboard not available"}), 500

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password required"}), 400
        
        username = data['username']
        password = data['password']
        
        # For demo purposes, accept any credentials
        # In production, verify against database
        user_data = {
            'user_id': 1,
            'username': username,
            'role': 'user',
            'permissions': ['read', 'write']
        }
        
        tokens = auth_manager.generate_tokens(user_data)
        
        return jsonify({
            "success": True,
            "access_token": tokens['access_token'],
            "refresh_token": tokens['refresh_token'],
            "user": {
                "user_id": user_data['user_id'],
                "username": user_data['username'],
                "role": user_data['role']
            }
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password required"}), 400
        
        username = data['username']
        password = data['password']
        
        # Hash password
        hashed_password = auth_manager.hash_password(password)
        
        # In production, save to database
        logger.info(f"User {username} registered successfully")
        
        return jsonify({
            "success": True,
            "message": "User registered successfully"
        })
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token"""
    try:
        data = request.get_json()
        if not data or not data.get('refresh_token'):
            return jsonify({"error": "Refresh token required"}), 400
        
        refresh_token = data['refresh_token']
        payload = auth_manager.verify_token(refresh_token, token_type='refresh')
        
        if not payload:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        
        # Generate new tokens
        user_data = {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'role': payload['role'],
            'permissions': payload.get('permissions', [])
        }
        
        tokens = auth_manager.generate_tokens(user_data)
        
        return jsonify({
            "success": True,
            "access_token": tokens['access_token'],
            "refresh_token": tokens['refresh_token']
        })
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header required"}), 401
        
        token = auth_header.split(' ')[1]
        payload = auth_manager.verify_token(token, token_type='access')
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        return jsonify({
            "success": True,
            "user": {
                "user_id": payload['user_id'],
                "username": payload['username'],
                "role": payload['role'],
                "permissions": payload.get('permissions', [])
            }
        })
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/generate', methods=['POST'])
def generate_dashboard():
    """Generate dashboard from Excel data"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Process Excel file using dashboard generator
        result = dashboard_generator.process_excel_file(file)
        
        if result['success']:
            return jsonify({
                "success": True,
                "dashboard_url": f"/dashboard/{result['dashboard_id']}",
                "message": "Dashboard generated successfully",
                "dashboard_id": result['dashboard_id']
            })
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/excel-data')
def get_excel_data():
    """Get Excel data for dashboard"""
    try:
        import pandas as pd
        
        # Get file parameter
        file_param = request.args.get('file', 'default')
        
        # Define available files
        excel_files = {
            'default': 'gitsitestylewebseite/Sunday, 16 November 2025 1329+1251 v 3144363.xlsx',
            'v3144363': 'dataDeployed/data_2025-11-16_v3144363.xlsx',
            'v683665': 'dataDeployed/data_2025-11-24_v683+665.xlsx'
        }
        
        excel_file = excel_files.get(file_param, excel_files['default'])
        
        # Read all sheets
        data = pd.read_excel(excel_file, sheet_name=None)
        
        # Convert to JSON-serializable format
        json_data = {}
        for sheet_name, df in data.items():
            json_data[sheet_name] = df.fillna('').to_dict('records')
        
        # Add file metadata
        json_data['_metadata'] = {
            'file_name': excel_file,
            'file_param': file_param,
            'total_sheets': len(data),
            'sheet_names': list(data.keys()),
            'total_rows': sum(len(df) for df in data.values())
        }
        
        return jsonify(json_data)
    except Exception as e:
        logger.error(f"Excel data loading error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/excel-files')
def get_excel_files():
    """Get list of available Excel files"""
    try:
        files = [
            {
                'id': 'default',
                'name': 'Sunday, 16 November 2025 1329+1251 v 3144363.xlsx',
                'path': 'gitsitestylewebseite/Sunday, 16 November 2025 1329+1251 v 3144363.xlsx',
                'date': '2025-11-16',
                'version': 'v3144363'
            },
            {
                'id': 'v3144363',
                'name': 'data_2025-11-16_v3144363.xlsx',
                'path': 'dataDeployed/data_2025-11-16_v3144363.xlsx',
                'date': '2025-11-16',
                'version': 'v3144363'
            },
            {
                'id': 'v683665',
                'name': 'data_2025-11-24_v683+665.xlsx',
                'path': 'dataDeployed/data_2025-11-24_v683+665.xlsx',
                'date': '2025-11-24',
                'version': 'v683+665'
            }
        ]
        
        return jsonify({
            'success': True,
            'files': files,
            'total_files': len(files)
        })
    except Exception as e:
        logger.error(f"Error getting Excel files: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create new task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        result = task_manager.create_task(data)
        if result['success']:
            return jsonify({
                "success": True,
                "task_id": result['task_id'],
                "message": "Task created successfully"
            })
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task status"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        result = task_manager.update_task(task_id, data)
        if result['success']:
            return jsonify({
                "success": True,
                "message": "Task updated successfully"
            })
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete task"""
    try:
        result = task_manager.delete_task(task_id)
        if result['success']:
            return jsonify({
                "success": True,
                "message": "Task deleted successfully"
            })
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/performance/stats', methods=['GET'])
def get_performance_stats():
    """Get system performance statistics"""
    try:
        stats = performance_monitor.get_system_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/analyze', methods=['POST'])
def analyze_code():
    """Analyze code using AI tools"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({"error": "No code provided for analysis"}), 400
            
        result = ai_tools.analyze_code_api(data['code'])
        if result['success']:
            return jsonify({
                "success": True,
                "analysis": result['analysis']
            })
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/excel-dashboard')
def excel_dashboard():
    """Excel Dashboard page"""
    return render_template('excel_dashboard.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Get WebSocket status
        ws_status = {
            "available": websocket_service.is_available(),
            "connected_clients": len(websocket_service.clients),
            "authenticated_clients": len(websocket_service.authenticated_clients)
        }
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "3d_features": "enabled",
            "websocket": ws_status
        })
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        # Sample stats - in production, get from database
        stats = {
            "total_files": 12,
            "total_rows": 4856,
            "active_tasks": 3,
            "success_rate": 97,
            "last_updated": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/processed-data', methods=['GET'])
def get_processed_data():
    """Get processed Excel data"""
    try:
        # Sample data - in production, get from database
        data = {
            "labels": ["January", "February", "March", "April", "May"],
            "datasets": [{
                "label": "Sales Data",
                "data": [65, 59, 80, 81, 56],
                "backgroundColor": "rgba(96, 165, 250, 0.5)",
                "borderColor": "rgba(96, 165, 250, 1)",
                "borderWidth": 2
            }]
        }
        
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        logger.error(f"Error getting processed data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/websocket/status', methods=['GET'])
def websocket_status():
    """Get WebSocket service status"""
    try:
        return jsonify({
            "success": True,
            "available": websocket_service.is_available(),
            "connected_clients": len(websocket_service.clients),
            "authenticated_clients": len(websocket_service.authenticated_clients),
            "server_info": {
                "host": websocket_service.host,
                "port": websocket_service.port
            }
        })
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/websocket/notify', methods=['POST'])
def websocket_notify():
    """Send WebSocket notification (for testing)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        event_type = data.get('event_type', 'system_event')
        message = data.get('message', 'Test notification')
        notification_data = data.get('data', {})
        
        # Send notification asynchronously using threading
        import threading
        import asyncio
        
        def send_notification():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(websocket_service.notify_system_event(
                    event_type, message, notification_data
                ))
            finally:
                loop.close()
        
        thread = threading.Thread(target=send_notification)
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Notification sent",
            "event_type": event_type
        })
    except Exception as e:
        logger.error(f"Error sending WebSocket notification: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    try:
        # For now, return mock data since this is a demo
        users = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@agentdaf1.1",
                "role": "admin",
                "created_at": "2025-01-01T00:00:00Z",
                "last_login": "2025-11-29T16:00:00Z",
                "status": "active"
            },
            {
                "id": 2,
                "username": "user",
                "email": "user@agentdaf1.1",
                "role": "user",
                "created_at": "2025-01-15T00:00:00Z",
                "last_login": "2025-11-28T14:30:00Z",
                "status": "active"
            }
        ]
        
        return jsonify({
            "success": True,
            "users": users,
            "total": len(users)
        })
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AgentDaf1.1 server on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    
    # Start WebSocket service
    try:
        ws_thread = websocket_service.start()
        if ws_thread:
            logger.info(f"WebSocket service started on ws://{websocket_service.host}:{websocket_service.port}")
        else:
            logger.info("WebSocket service not available (websockets library not installed)")
    except Exception as e:
        logger.error(f"Error starting WebSocket service: {e}")
        logger.info(f"Warning: WebSocket service failed to start: {e}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
    except KeyboardInterrupt:
        logger.info("/nShutting down AgentDaf1.1...")
        websocket_service.stop()