"""
AgentDaf1.1 - Advanced AI-powered Excel data processing platform.

This package provides comprehensive tools for data analysis, dashboard generation,
and intelligent automation capabilities.
"""

# Import core managers
from .core import managers, DashboardGenerator, TaskManager, PerformanceMonitor, AITools

# Import other managers (these will be created if missing)
try:
    from .config import ConfigManager
except ImportError:
    class ConfigManager:
        def __init__(self):
            pass

try:
    from .database import DatabaseManager
except ImportError:
    class DatabaseManager:
        def __init__(self):
            pass

try:
    from .tools import ToolsManager
except ImportError:
    class ToolsManager:
        def __init__(self):
            pass

try:
    from .api import APIManager
except ImportError:
    class APIManager:
        def __init__(self):
            pass

try:
    from .web import WebManager
except ImportError:
    class WebManager:
        def __init__(self):
            pass

# Export all managers
__all__ = [
    'managers', 'ConfigManager', 'DatabaseManager', 'ToolsManager', 
    'APIManager', 'WebManager', 'DashboardGenerator', 'TaskManager', 
    'PerformanceMonitor', 'AITools'
]