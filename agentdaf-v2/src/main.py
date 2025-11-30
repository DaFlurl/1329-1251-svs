"""
Main application entry point for AgentDaf1.1
Excel Dashboard System with Web Interface
"""

import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.flask_api import FlaskAPI
from src.config.settings import Config
from src.config.logging import setup_logging as setup_app_logging

def main():
    """Main application entry point"""
    # Setup logging
    setup_app_logging(Config)
    logger = logging.getLogger(__name__)
    
    try:
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'dashboards'), exist_ok=True)
        
        # Create and run Flask application
        logger.info("Starting AgentDaf1.1 Excel Dashboard System")
        logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")
        logger.info(f"Debug mode: {Config.DEBUG}")
        
        app = FlaskAPI()
        
        logger.info("""
╔════════════════════════════════════════════════════════════╗
║                AgentDaf1.1 Excel Dashboard System              ║
║                                                              ║
║  🚀 Starting Web Server...                                   ║
║  📊 Excel Processing: Ready                                 ║
║  🌐 Dashboard Generator: Ready                               ║
║  🔗 API Endpoints: Ready                                     ║
║                                                              ║
║  Access: http://localhost:8080                               ║
║  API Docs: http://localhost:8080/api/health                    ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()