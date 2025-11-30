#!/usr/bin/env python3
"""
AgentDaf1.1 Component Status Checker
Tests all major components and reports status
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_component(file_path):
    """Test a single component"""
    if not os.path.exists(file_path):
        return False, "File not found"
    
    try:
        # Try to import the module
        spec = importlib.util.spec_from_file_location("test_module", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return True, "Working"
    except Exception as e:
        return False, str(e)[:80]

def main():
    """Main testing function"""
    logger.info("AgentDaf1.1 Project Status Report")
    logger.info("=================================")
    logger.info()
    
    # Define components to test
    components = [
        # Core Application
        ("app.py", "Main Application"),
        ("src/main.py", "Main Entry Point"),
        ("database.py", "Database Module"),
        ("auth.py", "Authentication"),
        ("wsgi.py", "WSGI Server"),
        
        # API Components
        ("src/api/flask_api.py", "Flask API"),
        ("src/api/enhanced_flask_api.py", "Enhanced API"),
        ("src/api/github_integration.py", "GitHub Integration"),
        
        # Core Processing
        ("src/core/excel_processor.py", "Excel Processor"),
        ("src/core/dashboard_generator.py", "Dashboard Generator"),
        ("src/excel_workflow.py", "Excel Workflow"),
        
        # AI Tools
        ("src/tools/ai_tools.py", "AI Tools"),
        ("src/tools/neural_memory.py", "Neural Memory"),
        ("src/tools/docker_mcp_tools.py", "Docker MCP Tools"),
        
        # Tools Directory
        ("tools/auto_repair.py", "Auto Repair"),
        ("tools/health_monitor.py", "Health Monitor"),
        # ("tools/mcp_manager.py", "MCP Manager"),  # Removed - unused
        ("tools/tools_launcher.py", "Tools Launcher"),
        
        # Services
        ("services/websocket_service.py", "WebSocket Service"),
        ("services/notification_service.py", "Notification Service"),
        ("services/file_service.py", "File Service"),
        
        # Configuration
        ("src/config/settings.py", "Settings"),
        ("src/config/config_loader.py", "Config Loader"),
        
        # Docker Components
        ("docker_project/docker_startup.py", "Docker Startup"),
        
        # Test Files
        ("tests/test_suite.py", "Test Suite"),
        ("tests/test_memory_ai_tools.py", "Memory Tests"),
    ]
    
    working_count = 0
    failed_count = 0
    
    # Test each component
    for file_path, description in components:
        is_working, status = test_component(file_path)
        
        if is_working:
            logger.info(f"[OK] {file_path:<35} - {description}")
            working_count += 1
        else:
            logger.info(f"[FAIL] {file_path:<35} - {description} ({status})")
            failed_count += 1
    
    logger.info()
    logger.info("Summary:")
    logger.info(f"[OK] Working: {working_count} components")
    logger.info(f"[FAIL] Not Working: {failed_count} components")
    logger.info(f"[TOTAL] Total: {working_count + failed_count} components")
    
    # Calculate percentage
    total = working_count + failed_count
    if total > 0:
        percentage = (working_count / total) * 100
        logger.info(f"[RATE] Success Rate: {percentage:.1f}%")

if __name__ == "__main__":
    main()