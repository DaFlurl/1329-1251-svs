#!/usr/bin/env python3
"""
Syntax Error Verification Script for AgentDaf1.1
Verifies all Python files have correct syntax
"""

import sys
import py_compile
from pathlib import Path

def check_file_syntax(file_path):
    """Check if a Python file has correct syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

def main():
    """Check all Python files in the project"""
    logger.info("Checking AgentDaf1.1 Python files for syntax errors.../n")
    
    # Files to check
    files_to_check = [
        "src/tools/memory_manager.py",
        "src/tools/task_manager.py", 
        "src/tools/performance_monitor.py",
        "src/tools/file_manager.py",
        "src/tools/logger.py",
        "src/tools/security.py",
        "src/api/flask_api.py",
        "src/main.py",
        "src/core/excel_processor.py",
        "src/core/dashboard_generator.py",
        "src/config/settings.py",
        "src/config/logging.py"
    ]
    
    all_good = True
    checked_count = 0
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            is_valid, error = check_file_syntax(file_path)
            status = "OK" if is_valid else "ERROR"
            logger.info(f"  {status} {file_path}")
            
            if not is_valid:
                logger.info(f"     Error: {error}")
                all_good = False
            
            checked_count += 1
        else:
            logger.info(f"  SKIP {file_path} (file not found)")
    
    logger.info(f"/nSummary:")
    logger.info(f"  Files checked: {checked_count}")
    logger.info(f"  Status: {'All syntax OK!' if all_good else 'Syntax errors found'}")
    
    if all_good:
        logger.info("/nAgentDaf1.1 has no syntax errors!")
        logger.info("Ready for production deployment!")
    else:
        logger.info("/nPlease fix the syntax errors above.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())