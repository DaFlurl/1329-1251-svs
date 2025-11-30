"""
Core modules for AgentDaf1.1 platform.
"""

from .dashboard_generator import DashboardGenerator
from .task_manager import TaskManager, get_task_manager
from .performance_monitor import PerformanceMonitor
from .ai_tools import AITools, get_opencode_ai_tools
from .websocket_service import WebSocketService

# Create unified manager instances
class CoreManagers:
    """Unified manager for all core components."""
    
    def __init__(self):
        self._dashboard_generator = None
        self._task_manager = None
        self._performance_monitor = None
        self._ai_tools = None
        self._websocket_service = None
    
    def get_dashboard_generator(self) -> DashboardGenerator:
        """Get dashboard generator instance."""
        if self._dashboard_generator is None:
            self._dashboard_generator = DashboardGenerator()
        return self._dashboard_generator
    
    def get_task_manager(self) -> TaskManager:
        """Get task manager instance."""
        if self._task_manager is None:
            self._task_manager = get_task_manager()
        return self._task_manager
    
    def get_performance_monitor(self) -> PerformanceMonitor:
        """Get performance monitor instance."""
        if self._performance_monitor is None:
            self._performance_monitor = PerformanceMonitor()
        return self._performance_monitor
    
    def get_ai_tools(self) -> AITools:
        """Get AI tools instance."""
        if self._ai_tools is None:
            self._ai_tools = get_opencode_ai_tools()
        return self._ai_tools
    
    def get_websocket_service(self) -> WebSocketService:
        """Get WebSocket service instance."""
        if self._websocket_service is None:
            self._websocket_service = WebSocketService()
        return self._websocket_service

# Global managers instance
managers = CoreManagers()