"""Main application entry point for AgentDaf1.1
Excel Dashboard System with Web Interface
"""

import logging
import os
import sys

# Import centralized configurations
from src.config.path_config import PROJECT_ROOT
from src.config.logging_config import get_logger

from src.api.flask_api import FlaskAPI
from src.core.ai_tools import AITools
from src.core.excel_processor import ExcelProcessor
from src.core.managers import DatabaseManager, ConfigManager
from src.core.performance_monitor import PerformanceMonitor
from src.core.task_manager import TaskManager
from src.core.websocket_service import WebSocketService
from src.config.settings import Config


def main():
    """Main application entry point"""
    # Setup logging
    logger = get_logger(__name__)
    
    try:
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'dashboards'), exist_ok=True)
        
        # Create and run Flask application
        logger.info("Starting AgentDaf1.1 Excel Dashboard System")
        logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
        logger.info(f"Debug mode: {Config.DEBUG}")
        
        app = FlaskAPI()
        app.run(host='0.0.0.0', port=8080, debug=Config.DEBUG)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    
    logger.info("""
ROCKET: AgentDaf1.1 - Advanced AI Agent Platform
  DATA: Excel Processing & Dashboard Generation
  WEB: Web Application with WebSocket Support
  API: RESTful API with Comprehensive Endpoints
  ANALYTICS: Real-time Data Processing & Analytics
  SECURITY: JWT-based Authentication & Security
  TOOLS: Advanced Development Tools & Testing Suite
  TASKS: Task Management & Performance Monitoring
  ROCKET: Production Ready with Docker Support
  """)