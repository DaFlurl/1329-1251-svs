from .tools_manager import ToolsManager

__all__ = ['ToolsManager']

def get_tools_manager():
    """Get the tools manager instance."""
    return ToolsManager()