from .flask_api import FlaskAPI
from .config import ConfigManager
from .database import DatabaseManager
from .tools import ToolsManager
from .web import WebManager


class APIManager:
    """API Manager for handling Flask API endpoints and business logic."""
    
    def __init__(self, config_manager: ConfigManager, db_manager: DatabaseManager, tools_manager: ToolsManager, web_manager: WebManager):
        """Initialize API Manager with all required managers."""
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.tools_manager = tools_manager
        self.web_manager = web_manager
        self.flask_api = FlaskAPI(config_manager, db_manager, tools_manager, web_manager)
    
    def initialize_routes(self):
        """Initialize all Flask API routes."""
        return self.flask_api.initialize_routes()
    
    def get_status(self):
        """Get API manager status."""
        return {
            "managers_loaded": True,
            "flask_api_ready": self.flask_api is not None,
            "routes_initialized": self.initialize_routes() is not None
        }