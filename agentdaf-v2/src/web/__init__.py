"""
Web module for AgentDaf1.1 dashboard and frontend management.
"""

import os
import sys
from typing import Optional, Dict, Any
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..config import ConfigManager
from ..database import DatabaseManager
from ..tools import ToolsManager
from ..api import APIManager


class WebManager:
    """
    Web management for AgentDaf1.1 dashboard and frontend.
    Handles Flask application setup, WebSocket communication, and frontend rendering.
    """
    
    def __init__(self, config_manager: ConfigManager, database_manager: DatabaseManager, 
                 tools_manager: ToolsManager, api_manager: APIManager):
        """
        Initialize the web management system.
        
        Args:
            config_manager: Configuration manager instance
            database_manager: Database manager instance
            tools_manager: Tools manager instance
            api_manager: API manager instance
        """
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.tools_manager = tools_manager
        self.api_manager = api_manager
        
        # Flask app setup
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = config_manager.get('SECRET_KEY')
        self.app.config['JWT_SECRET_KEY'] = config_manager.get('JWT_SECRET_KEY')
        
        # WebSocket setup
        self.socketio = SocketIO(self.app)
        
        # Session management
        self.sessions = {}
        
        # Initialize routes
        self._init_routes()
        self._init_websocket_events()
    
    def _init_routes(self):
        """Initialize Flask routes."""
        # API routes will be initialized by APIManager
        pass
    
    def _init_websocket_events(self):
        """Initialize WebSocket event handlers."""
        pass
    
    def create_app(self, debug: bool = False) -> Flask:
        """
        Create and configure Flask application.
        
        Args:
            debug: Enable debug mode
            
        Returns:
            Configured Flask application
        """
        # Configure Flask app
        self.app.config['DEBUG'] = debug
        
        # Enable CORS for all routes
        from flask_cors import CORS
        CORS(self.app)
        
        return self.app
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None
        """
        return self.sessions.get(session_id)
    
    def set_session_data(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Set session data.
        
        Args:
            session_id: Session identifier
            data: Session data dictionary
        """
        self.sessions[session_id] = data
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear session data.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def render_dashboard(self, dashboard_data: Dict[str, Any]) -> str:
        """
        Render dashboard HTML.
        
        Args:
            dashboard_data: Dashboard data dictionary
            
        Returns:
            Rendered HTML string
        """
        return render_template('dashboard.html', **dashboard_data)
    
    def emit_update(self, event: str, data: Dict[str, Any], room: str = None) -> None:
        """
        Emit WebSocket update to clients.
        
        Args:
            event: Event name
            data: Update data
            room: Room identifier (optional)
        """
        emit(event, data, room=room)
    
    def run_server(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False) -> None:
        """
        Run the Flask application.
        
        Args:
            host: Host address
            port: Port number
            debug: Enable debug mode
        """
        self.socketio.run(self.app, host=host, port=port, debug=debug)