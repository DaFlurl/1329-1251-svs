from .config_manager import ConfigManager
from .database_manager import DatabaseManager
from .tools_manager import ToolsManager

__all__ = ['ToolsManager']

def get_tools_manager():
    """Get the tools manager instance."""
    return ToolsManager()