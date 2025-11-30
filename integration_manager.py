#!/usr/bin/env python3
"""
AgentDaf1.1 Integration Manager
Complete integration of frontend with backend services
"""

import os
import sys
import json
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from database import get_db_manager
from auth import get_auth_manager
from src.config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/integration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class IntegrationManager:
    """Manages the complete integration of frontend and backend services"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.auth_manager = get_auth_manager()
        self.running = False
        self.processes = {}
        self.threads = {}
        
        # Ensure required directories exist
        self.ensure_directories()
        
        # Initialize database with sample data if needed
        self.initialize_database()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            'data/uploads',
            'data/processed',
            'logs',
            'backups',
            'gitsitestylewebseite/data'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
    
    def initialize_database(self):
        """Initialize database with sample data if empty"""
        try:
            stats = self.db_manager.get_database_stats()
            if stats.get('players_count', 0) == 0:
                logger.info("Initializing database with sample data...")
                self.db_manager.initialize_sample_data()
                logger.info("Database initialized with sample data")
            else:
                logger.info(f"Database already contains {stats.get('players_count', 0)} players")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
    
    def create_sample_data_files(self):
        """Create sample data files for the frontend"""
        try:
            # Get current data from database
            players = self.db_manager.get_all_players()
            alliances = self.db_manager.get_all_alliances()
            
            # Create combined data structure
            combined_data = {
                'positive': players[:len(players)//2] if players else [],
                'negative': players[len(players)//2:] if players else [],
                'combined': players,
                'metadata': {
                    'totalPlayers': len(players),
                    'totalAlliances': len(alliances),
                    'lastUpdate': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'dataFile': 'live_data.json'
                },
                'statistics': {
                    'totalPlayers': len(players),
                    'totalAlliances': len(alliances),
                    'totalScore': sum(p['score'] for p in players),
                    'averageScore': sum(p['score'] for p in players) // len(players) if players else 0,
                    'highestScore': max(p['score'] for p in players) if players else 0,
                    'activeGames': len(players)
                }
            }
            
            # Save data files
            data_dir = Path('gitsitestylewebseite/data')
            data_dir.mkdir(exist_ok=True)
            
            # Current data file
            with open(data_dir / 'monday_data.json', 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            # Historical data file (copy with different timestamp)
            historical_data = combined_data.copy()
            historical_data['metadata']['lastUpdate'] = '2025-11-16 12:00:00'
            historical_data['metadata']['dataFile'] = 'scoreboard-data.json'
            
            with open(data_dir / 'scoreboard-data.json', 'w', encoding='utf-8') as f:
                json.dump(historical_data, f, indent=2, ensure_ascii=False)
            
            # Default data file
            with open(data_dir / 'default_data.json', 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Sample data files created successfully")
            
        except Exception as e:
            logger.error(f"Error creating sample data files: {str(e)}")
    
    def start_enhanced_api_server(self):
        """Start the enhanced Flask API server"""
        try:
            logger.info("Starting Enhanced Flask API Server...")
            
            # Import here to avoid circular imports
            from src.api.enhanced_flask_api import EnhancedFlaskAPI
            
            # Create API instance
            api = EnhancedFlaskAPI()
            
            # Start in a separate thread
            def run_api():
                try:
                    api.run(host='0.0.0.0', port=8080, debug=False)
                except Exception as e:
                    logger.error(f"API server error: {str(e)}")
            
            api_thread = threading.Thread(target=run_api, daemon=True)
            api_thread.start()
            self.threads['api'] = api_thread
            
            logger.info("Enhanced Flask API Server started on http://localhost:8080")
            
        except Exception as e:
            logger.error(f"Failed to start API server: {str(e)}")
    
    def start_websocket_service(self):
        """Start the WebSocket service"""
        try:
            logger.info("Starting WebSocket Service...")
            
            # Import here to avoid circular imports
            from services.websocket_service import WebSocketService
            
            # Create WebSocket service
            ws_service = WebSocketService(host='0.0.0.0', port=8081)
            
            # Start in a separate thread
            ws_thread = ws_service.start()
            self.threads['websocket'] = ws_thread
            
            logger.info("WebSocket Service started on ws://localhost:8081")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket service: {str(e)}")
    
    def start_simple_server(self):
        """Start a simple file server for static files"""
        try:
            logger.info("Starting static file server...")
            
            # Use Python's built-in HTTP server
            def run_static_server():
                import http.server
                import socketserver
                
                os.chdir('gitsitestylewebseite')
                
                with socketserver.TCPServer(("", 8082), http.server.SimpleHTTPRequestHandler) as httpd:
                    logger.info("Static file server started on http://localhost:8082")
                    httpd.serve_forever()
            
            static_thread = threading.Thread(target=run_static_server, daemon=True)
            static_thread.start()
            self.threads['static'] = static_thread
            
        except Exception as e:
            logger.error(f"Failed to start static server: {str(e)}")
    
    def setup_cors_and_security(self):
        """Setup CORS and security configurations"""
        try:
            # Create CORS configuration file
            cors_config = {
                "origins": ["http://localhost:8080", "http://localhost:8082", "*"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allowed_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Content-Length", "X-Total-Count"],
                "supports_credentials": True,
                "max_age": 86400
            }
            
            with open('config/cors.json', 'w') as f:
                json.dump(cors_config, f, indent=2)
            
            # Create security configuration
            security_config = {
                "jwt_secret_key": Config.SECRET_KEY,
                "token_expiry_hours": 24,
                "refresh_token_days": 7,
                "rate_limiting": {
                    "requests_per_minute": 100,
                    "burst_size": 20
                },
                "file_upload": {
                    "max_size_mb": 16,
                    "allowed_extensions": [".xlsx", ".xls", ".json"],
                    "scan_uploads": True
                },
                "cors": cors_config
            }
            
            with open('config/security.json', 'w') as f:
                json.dump(security_config, f, indent=2)
            
            logger.info("CORS and security configurations created")
            
        except Exception as e:
            logger.error(f"Error setting up CORS and security: {str(e)}")
    
    def create_integration_config(self):
        """Create integration configuration file"""
        try:
            integration_config = {
                "services": {
                    "api_server": {
                        "url": "http://localhost:8080",
                        "endpoints": {
                            "auth": "/api/auth",
                            "players": "/api/players",
                            "alliances": "/api/alliances",
                            "upload": "/api/upload/excel",
                            "stats": "/api/stats",
                            "health": "/api/health"
                        }
                    },
                    "websocket": {
                        "url": "ws://localhost:8081",
                        "reconnect_interval": 5000,
                        "max_reconnect_attempts": 10
                    },
                    "static_server": {
                        "url": "http://localhost:8082",
                        "frontend_path": "/gitsitestylewebseite"
                    }
                },
                "database": {
                    "type": "sqlite",
                    "path": "data/agentdaf1.db",
                    "backup_interval_hours": 24
                },
                "features": {
                    "real_time_updates": True,
                    "file_upload": True,
                    "authentication": True,
                    "data_export": True,
                    "monitoring": True
                },
                "monitoring": {
                    "health_check_interval": 60,
                    "log_level": "INFO",
                    "metrics_collection": True
                }
            }
            
            with open('config/integration.json', 'w') as f:
                json.dump(integration_config, f, indent=2)
            
            logger.info("Integration configuration created")
            
        except Exception as e:
            logger.error(f"Error creating integration config: {str(e)}")
    
    def start_monitoring(self):
        """Start system monitoring"""
        def monitor_system():
            while self.running:
                try:
                    # Check API health
                    import requests
                    try:
                        response = requests.get('http://localhost:8080/api/health', timeout=5)
                        if response.status_code == 200:
                            logger.info("API Server: Healthy")
                        else:
                            logger.warning(f"API Server: Unhealthy (Status: {response.status_code})")
                    except requests.RequestException as e:
                        logger.error(f"API Server: Connection failed - {str(e)}")
                    
                    # Log system stats
                    stats = self.db_manager.get_database_stats()
                    logger.info(f"Database: {stats.get('players_count', 0)} players, {stats.get('alliances_count', 0)} alliances")
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {str(e)}")
                    time.sleep(30)
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
        self.threads['monitoring'] = monitor_thread
        
        logger.info("System monitoring started")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self):
        """Shutdown all services"""
        logger.info("Shutting down Integration Manager...")
        self.running = False
        
        # Terminate any subprocesses
        for name, process in self.processes.items():
            try:
                if process.is_alive():
                    process.terminate()
                    logger.info(f"Terminated process: {name}")
            except Exception as e:
                logger.error(f"Error terminating process {name}: {str(e)}")
        
        logger.info("Integration Manager shutdown complete")
    
    def start_all_services(self):
        """Start all integrated services"""
        logger.info("🚀 Starting AgentDaf1.1 Integrated Services...")
        
        self.running = True
        
        # Create configurations
        self.setup_cors_and_security()
        self.create_integration_config()
        
        # Create sample data files
        self.create_sample_data_files()
        
        # Start services
        self.start_enhanced_api_server()
        self.start_websocket_service()
        self.start_simple_server()
        self.start_monitoring()
        
        # Wait a moment for services to start
        time.sleep(3)
        
        # Print startup information
        self.print_startup_info()
        
        logger.info("✅ All services started successfully!")
    
    def print_startup_info(self):
        """Print startup information"""
        logger.info("""
╔════════════════════════════════════════════════════════════╗
║              AgentDaf1.1 Integration Complete               ║
╠════════════════════════════════════════════════════════════╣
║                                                              ║
║  🌐 Main Dashboard: http://localhost:8080                   ║
║  📊 Enhanced UI:   http://localhost:8082/enhanced-dashboard.html ║
║  🔌 WebSocket:      ws://localhost:8081                     ║
║                                                              ║
║  📱 API Endpoints:                                           ║
║     • Authentication: /api/auth                            ║
║     • Players:        /api/players                         ║
║     • Alliances:      /api/alliances                       ║
║     • File Upload:    /api/upload/excel                    ║
║     • System Stats:   /api/stats                           ║
║     • Health Check:   /api/health                          ║
║                                                              ║
║  🔐 Default Login:                                            ║
║     • Admin:  admin / admin123                              ║
║     • User:   user  / user123                               ║
║                                                              ║
║  📁 Data Files:                                               ║
║     • Database:       data/agentdaf1.db                    ║
║     • Uploads:        data/uploads/                        ║
║     • Frontend Data:  gitsitestylewebseite/data/           ║
║                                                              ║
║  🛠️  Features Enabled:                                        ║
║     • Real-time updates via WebSocket                       ║
║     • JWT authentication & authorization                    ║
║     • Excel file processing                                 ║
║     • Database persistence                                  ║
║     • CORS enabled for cross-origin requests               ║
║     • System monitoring & logging                          ║
║     • File upload/download capabilities                     ║
║     • Error handling & fallback mechanisms                  ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
        """)
    
    def run(self):
        """Run the integration manager"""
        try:
            self.start_all_services()
            
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Integration manager error: {str(e)}")
        finally:
            self.shutdown()

def main():
    """Main entry point"""
    integration_manager = IntegrationManager()
    integration_manager.run()

if __name__ == '__main__':
    main()