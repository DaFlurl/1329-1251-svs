#!/usr/bin/env python3
"""
Test all core module imports
"""

import sys
import traceback

modules_to_test = [
    'src.core.dashboard_generator',
    'src.core.task_manager', 
    'src.core.ai_tools',
    'src.core.websocket_service',
    'src.tools.file_manager',
    'src.tools.security',
    'src.tools.mcp_lsp_interface',
    'src.config.logger',
    'src.database.database_manager',
    'src.api.flask_api',
    'src.main',
    'app'
]

def test_imports():
    """Test all module imports"""
    success_count = 0
    total_count = len(modules_to_test)
    failed_imports = []
    
    print("Testing Core Module Imports...")
    print("=" * 50)
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"[OK] {module_name}")
            success_count += 1
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            print(f"[FAIL] {module_name}")
            print(f"   Error: {str(e)[:100]}")
    
    print("=" * 50)
    print(f"SUMMARY: {success_count}/{total_count} modules import successfully")
    
    if failed_imports:
        print(f"\nFailed imports ({len(failed_imports)}):")
        for module_name, error in failed_imports:
            print(f"  - {module_name}: {error}")
    else:
        print(f"\nAll core modules import successfully!")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)