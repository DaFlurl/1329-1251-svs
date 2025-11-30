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
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash

# Import core modules
try:
    from src import ConfigManager, DatabaseManager, ToolsManager, APIManager, WebManager
except ImportError as e:
    logger.info(f"Error importing core modules: {e}")
    logger.info("Please ensure all core modules are present in src/core/")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize core components using unified managers
dashboard_generator = managers.get_dashboard_generator()
task_manager = managers.get_task_manager()
performance_monitor = managers.get_performance_monitor()
ai_tools = managers.get_ai_tools()

@app.route('/')
def index():
    """Main dashboard route"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
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

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        tasks = task_manager.get_all_tasks()
        return jsonify({"success": True, "tasks": tasks})
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
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
            
        result = ai_tools.analyze_code(data['code'])
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

@app.route('/dashboard/<dashboard_id>')
def view_dashboard(dashboard_id):
    """View generated dashboard"""
    try:
        dashboard_data = dashboard_generator.get_dashboard(dashboard_id)
        if dashboard_data:
            return render_template('dashboard.html', dashboard=dashboard_data)
        else:
            return "Dashboard not found", 404
    except Exception as e:
        logger.error(f"Error viewing dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        })
    except Exception as e:
        logger.error(f"Error in health check: {e}")
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
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)