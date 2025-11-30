#!/usr/bin/env python3
"""
AgentDaf1.1 Quick Fix Script
Fixes common import and configuration issues
"""

import os
import sys
from pathlib import Path

def fix_imports():
    """Fix import issues by updating sys.path"""
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    
    # Add to sys.path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(project_root)
    os.environ['FLASK_APP'] = 'wsgi.py'
    os.environ['FLASK_ENV'] = 'development'
    
    logger.info(f"+ Project root: {project_root}")
    logger.info(f"+ Source directory: {src_dir}")
    logger.info(f"+ Python path updated")

def create_missing_files():
    """Create missing essential files"""
    project_root = Path(__file__).parent
    
    # Create essential directories
    dirs_to_create = [
        'data',
        'logs', 
        'data/uploads',
        'memory_cache'
    ]
    
    for dir_path in dirs_to_create:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"+ Created directory: {dir_path}")
    
    # Create simple requirements if missing
    requirements_file = project_root / 'requirements.txt'
    if not requirements_file.exists():
        basic_requirements = """flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
openpyxl==3.1.2
psutil==5.9.5
python-dotenv==1.0.0
"""
        requirements_file.write_text(basic_requirements)
        logger.info("+ Created requirements.txt")

def check_environment():
    """Check and display environment status"""
    logger.info("/n=== Environment Status ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {Path.cwd()}")
    logger.info(f"Script location: {Path(__file__).parent}")
    
    # Check key files
    key_files = [
        '.env',
        '.env.merged', 
        'src/main.py',
        'wsgi.py',
        'requirements.txt'
    ]
    
    logger.info("/n=== Key Files Status ===")
    for file_path in key_files:
        full_path = Path(__file__).parent / file_path
        status = "+" if full_path.exists() else "-"
        logger.info(f"{status} {file_path}")

def main():
    """Main fix function"""
    logger.info("AgentDaf1.1 Quick Fix Tool")
    logger.info("=" * 40)
    
    try:
        fix_imports()
        create_missing_files()
        check_environment()
        
        logger.info("/n" + "=" * 40)
        logger.info("+ Fix completed successfully!")
        logger.info("/nNext steps:")
        logger.info("1. Install dependencies: pip install -r requirements.txt")
        logger.info("2. Run the application: python src/main.py")
        logger.info("3. Or use WSGI: gunicorn wsgi:app")
        
    except Exception as e:
        logger.info(f"- Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())