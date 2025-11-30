"""
Import Fix Module for AgentDaf1.1
Resolves common import issues and provides fallback imports
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add src directory to Python path
src_dir = project_root / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Environment setup
os.environ.setdefault('PYTHONPATH', str(project_root))

# Import aliases for common modules
try:
    from src.core.excel_processor import ExcelProcessor
except ImportError:
    ExcelProcessor = None

try:
    from src.core.dashboard_generator import DashboardGenerator
except ImportError:
    DashboardGenerator = None

try:
    from src.config.settings import Config
except ImportError:
    Config = None

try:
    from src.config.logging import setup_logging
except ImportError:
    def setup_logging(*args, **kwargs):
        import logging
        logging.basicConfig(level=logging.INFO)

try:
    from src.api.github_integration import GitHubIntegration
except ImportError:
    GitHubIntegration = None

try:
    from src.api.flask_api import FlaskAPI
except ImportError:
    FlaskAPI = None

try:
    from src.tools.memory_manager import memory_manager
except ImportError:
    memory_manager = None

try:
    from src.tools.task_manager import task_manager
except ImportError:
    task_manager = None

# Export all available modules
__all__ = [
    'ExcelProcessor',
    'DashboardGenerator', 
    'Config',
    'setup_logging',
    'GitHubIntegration',
    'FlaskAPI',
    'memory_manager',
    'task_manager'
]