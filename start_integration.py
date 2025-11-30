#!/usr/bin/env python3
"""
AgentDaf1.1 Complete Integration Startup Script
Launches all services for frontend-backend integration
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def print_banner():
    """Print startup banner"""
    logger.info("""
╔════════════════════════════════════════════════════════════╗
║          AgentDaf1.1 Complete Integration Launcher          ║
║                                                              ║
║  🚀 Starting Frontend-Backend Integration System            ║
║  📊 Real-time Gaming Dashboard with Full Backend Services   ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("🔍 Checking dependencies...")
    
    required_modules = [
        'flask', 'flask_cors', 'flask_socketio',
        'jwt', 'bcrypt', 'requests',
        'openpyxl', 'pandas', 'websockets'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            logger.info(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            logger.info(f"  ❌ {module}")
    
    if missing_modules:
        logger.info(f"/n❌ Missing dependencies: {', '.join(missing_modules)}")
        logger.info("Please install them using:")
        logger.info("pip install -r requirements-integration.txt")
        return False
    
    logger.info("✅ All dependencies are installed!")
    return True

def setup_environment():
    """Setup environment variables and directories"""
    logger.info("🔧 Setting up environment...")
    
    # Create necessary directories
    directories = [
        'data/uploads',
        'data/processed', 
        'logs',
        'backups',
        'config',
        'gitsitestylewebseite/data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"  📁 Created directory: {directory}")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SECRET_KEY'] = 'agentdaf1-secret-key-change-in-production'
    os.environ['JWT_SECRET_KEY'] = 'agentdaf1-jwt-secret-change-in-production'
    
    logger.info("✅ Environment setup complete!")

def start_integration():
    """Start the complete integration system"""
    logger.info("🚀 Starting AgentDaf1.1 Integration System...")
    
    try:
        # Import and run the integration manager
        from integration_manager import IntegrationManager
        
        integration_manager = IntegrationManager()
        integration_manager.run()
        
    except KeyboardInterrupt:
        logger.info("/n👋 Shutting down AgentDaf1.1 Integration System...")
    except Exception as e:
        logger.info(f"❌ Error starting integration: {str(e)}")
        logger.info("Please check the logs for more details.")
        return False
    
    return True

def main():
    """Main entry point"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Start integration
    success = start_integration()
    
    if success:
        logger.info("✅ AgentDaf1.1 Integration System started successfully!")
    else:
        logger.info("❌ Failed to start AgentDaf1.1 Integration System")
        sys.exit(1)

if __name__ == '__main__':
    main()