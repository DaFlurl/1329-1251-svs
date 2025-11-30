#!/usr/bin/env python3
"""
AgentDaf1.1 API Server Launcher
Fixed import paths for reliable startup
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.api.flask_api import FlaskAPI
    
    logger.info("""
============================================================
                AgentDaf1.1 API Server                        
                                                             
  Starting Flask API Server...                                 
  Excel Processing: Ready                                      
  Dashboard Generator: Ready                                    
  API Endpoints: Ready                                         
  6 Core Tools: Ready                                          
                                                             
  Access: http://localhost:8080                               
  API Docs: http://localhost:8080/api/health                  
============================================================
    """)
    
    # Create and run Flask API
    app = FlaskAPI()
    app.app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )
    
except ImportError as e:
    logger.info(f"Import error: {e}")
    logger.info("Please ensure all dependencies are installed:")
    logger.info("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    logger.info(f"Error starting server: {e}")
    sys.exit(1)