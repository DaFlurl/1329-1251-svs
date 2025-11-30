"""
Centralized path configuration for AgentDaf1.1
"""

import sys
from pathlib import Path

def setup_project_paths():
    """Setup all necessary project paths"""
    # Get project root (assuming we're in src/ or root)
    current_file = Path(__file__).resolve()
    
    # If we're in src/config/, go up two levels to project root
    if current_file.name == "path_config.py":
        project_root = current_file.parent.parent
    else:
        # Default: assume we're in project root
        project_root = current_file.parent
    
    # Add src to path if not already there
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    return project_root

# Setup paths when module is imported
PROJECT_ROOT = setup_project_paths()