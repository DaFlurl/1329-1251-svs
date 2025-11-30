#!/usr/bin/env python3
"""
AgentDaf1.1 - Unified Managers Module

Provides centralized access to all core components with proper initialization
and lifecycle management.
"""

import logging
from typing import Optional
from .core.dashboard_generator import DashboardGenerator
from .core.task_manager import TaskManager
from .core.performance_monitor import PerformanceMonitor
from .core.ai_tools import AITools
from .core.websocket_service import WebSocketService

logger = logging.getLogger(__name__)

# Global instances for singleton pattern
_dashboard_generator: Optional[DashboardGenerator] = None
_task_manager: Optional[TaskManager] = None
_performance_monitor: Optional[PerformanceMonitor] = None
_ai_tools: Optional[AITools] = None
_websocket_service: Optional[WebSocketService] = None

def get_dashboard_generator() -> DashboardGenerator:
    """Get or create dashboard generator instance"""
    global _dashboard_generator
    if _dashboard_generator is None:
        try:
            _dashboard_generator = DashboardGenerator()
            logger.info("DashboardGenerator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DashboardGenerator: {e}")
            raise
    return _dashboard_generator

def get_task_manager() -> TaskManager:
    """Get or create task manager instance"""
    global _task_manager
    if _task_manager is None:
        try:
            _task_manager = TaskManager()
            logger.info("TaskManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TaskManager: {e}")
            raise
    return _task_manager

def get_performance_monitor() -> PerformanceMonitor:
    """Get or create performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        try:
            _performance_monitor = PerformanceMonitor()
            logger.info("PerformanceMonitor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PerformanceMonitor: {e}")
            raise
    return _performance_monitor

def get_ai_tools() -> AITools:
    """Get or create AI tools instance"""
    global _ai_tools
    if _ai_tools is None:
        try:
            _ai_tools = AITools()
            logger.info("AITools initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AITools: {e}")
            raise
    return _ai_tools

def get_websocket_service() -> WebSocketService:
    """Get or create WebSocket service instance"""
    global _websocket_service
    if _websocket_service is None:
        try:
            _websocket_service = WebSocketService()
            logger.info("WebSocketService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WebSocketService: {e}")
            raise
    return _websocket_service

def initialize_all():
    """Initialize all managers at once"""
    try:
        get_dashboard_generator()
        get_task_manager()
        get_performance_monitor()
        get_ai_tools()
        get_websocket_service()
        logger.info("All managers initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize managers: {e}")
        raise

def shutdown_all():
    """Cleanup all manager resources"""
    global _dashboard_generator, _task_manager, _performance_monitor, _ai_tools, _websocket_service
    
    try:
        if _performance_monitor:
            _performance_monitor.stop_monitoring()
        
        if _websocket_service:
            _websocket_service.stop()
        
        # Reset all instances
        _dashboard_generator = None
        _task_manager = None
        _performance_monitor = None
        _ai_tools = None
        _websocket_service = None
        
        logger.info("All managers shutdown successfully")
    except Exception as e:
        logger.error(f"Error during manager shutdown: {e}")

# Export functions for easy import
__all__ = [
    'get_dashboard_generator',
    'get_task_manager', 
    'get_performance_monitor',
    'get_ai_tools',
    'get_websocket_service',
    'initialize_all',
    'shutdown_all'
]