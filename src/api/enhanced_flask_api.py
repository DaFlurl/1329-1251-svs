#!/usr/bin/env python3
"""
Enhanced Flask API for AgentDaf1.1
Complete integration with gitsitestylewebseite frontend
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, render_template, send_file, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import logging
from datetime import datetime
import json
import threading
import time

from src.config.settings import Config
from database import get_db_manager
from auth import get_auth_manager, get_user_manager, token_required, create_auth_routes
from src.core.excel_processor import ExcelProcessor
from src.core.dashboard_generator import DashboardGenerator

logger = logging.getLogger(__name__)

class EnhancedFlaskAPI:
    """Enhanced Flask API with full frontend integration"""
    
    def __init__(self):
        # Set template folder to gitsitestylewebseite
        template_folder = Path(__file__).parent.parent / 'gitsitestylewebseite'
        static_folder = Path(__file__).parent.parent / 'gitsitestylewebseite'
        
        self.app = Flask(__name__, 
                        template_folder=str(template_folder),
                        static_folder=str(static_folder))
        self.app.config['SECRET_KEY'] = Config.SECRET_KEY
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        
        # Enable CORS
        CORS(self.app, origins="*")
        
        # Initialize SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize components
        self.db_manager = get_db_manager()
        self.auth_manager = get_auth_manager()
        self.user_manager = get_user_manager()
        self.excel_processor = ExcelProcessor()
        self.dashboard_generator = DashboardGenerator()
        
        # Setup routes
        self._setup_routes()
        self._setup_socketio_events()
        self._setup_error_handlers()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # ===== FRONTEND ROUTES =====
        
        @self.app.route('/')
        def index():
            """Serve main dashboard"""
            return render_template('dashboard.html')
        
        @self.app.route('/scoreboard')
        def scoreboard():
            """Serve scoreboard page"""
            return render_template('scoreboard.html')
        
        @self.app.route('/admin')
        @token_required
        def admin():
            """Serve admin panel"""
            return render_template('admin.html')
        
        # ===== AUTHENTICATION ROUTES =====
        create_auth_routes(self.app)
        
        # ===== API DATA ROUTES =====
        
        @self.app.route('/api/players')
        def get_players():
            """Get all players with rankings"""
            try:
                players = self.db_manager.get_all_players()
                return jsonify({
                    'success': True,
                    'data': players,
                    'count': len(players)
                })
            except Exception as e:
                logger.error(f"Get players error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/alliances')
        def get_alliances():
            """Get all alliances"""
            try:
                alliances = self.db_manager.get_all_alliances()
                return jsonify({
                    'success': True,
                    'data': alliances,
                    'count': len(alliances)
                })
            except Exception as e:
                logger.error(f"Get alliances error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/player/<username>')
        def get_player_details(username):
            """Get detailed player information"""
            try:
                player = self.db_manager.get_player(username)
                if not player:
                    return jsonify({'error': 'Player not found'}), 404
                
                sessions = self.db_manager.get_player_sessions(username, limit=20)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'player': player,
                        'sessions': sessions
                    }
                })
            except Exception as e:
                logger.error(f"Get player details error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/stats')
        def get_system_stats():
            """Get system statistics"""
            try:
                db_stats = self.db_manager.get_database_stats()
                
                # Calculate additional stats
                players = self.db_manager.get_all_players()
                alliances = self.db_manager.get_all_alliances()
                
                stats = {
                    'database': db_stats,
                    'players': {
                        'total': len(players),
                        'active': len([p for p in players if p['score'] > 0]),
                        'average_score': sum(p['score'] for p in players) // len(players) if players else 0
                    },
                    'alliances': {
                        'total': len(alliances),
                        'active': len([a for a in alliances if a['members'] > 0])
                    },
                    'system': {
                        'uptime': 'N/A',  # Would need proper uptime tracking
                        'version': '1.0.0',
                        'last_update': datetime.now().isoformat()
                    }
                }
                
                return jsonify({
                    'success': True,
                    'data': stats
                })
            except Exception as e:
                logger.error(f"Get system stats error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # ===== FILE UPLOAD AND PROCESSING =====
        
        @self.app.route('/api/upload/excel', methods=['POST'])
        @token_required
        def upload_excel():
            """Upload and process Excel file"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                if not self._allowed_file(file.filename):
                    return jsonify({'error': 'File type not allowed'}), 400
                
                # Save uploaded file
                filename = self._save_uploaded_file(file)
                if not filename:
                    return jsonify({'error': 'Failed to save file'}), 500
                
                # Process Excel file
                data = self.excel_processor.process_excel_file(filename)
                
                # Update database with new data
                self._update_database_from_excel(data)
                
                # Emit real-time update
                self.socketio.emit('data_updated', {
                    'type': 'excel_upload',
                    'timestamp': datetime.now().isoformat(),
                    'user': request.current_user['username']
                }, room='dashboard')
                
                return jsonify({
                    'success': True,
                    'message': 'File processed successfully',
                    'data': {
                        'filename': file.filename,
                        'players_processed': len(data.get('players', [])),
                        'timestamp': datetime.now().isoformat()
                    }
                })
                
            except Exception as e:
                logger.error(f"Upload Excel error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # ===== PLAYER MANAGEMENT =====
        
        @self.app.route('/api/player', methods=['POST'])
        @token_required
        def create_player():
            """Create new player"""
            try:
                data = request.get_json()
                if not data or not data.get('name'):
                    return jsonify({'error': 'Player name required'}), 400
                
                player_id = self.db_manager.add_player(
                    data['name'],
                    data.get('score', 0),
                    data.get('alliance'),
                    data.get('level', 1)
                )
                
                # Emit real-time update
                self.socketio.emit('player_created', {
                    'player_id': player_id,
                    'player_name': data['name'],
                    'timestamp': datetime.now().isoformat()
                }, room='dashboard')
                
                return jsonify({
                    'success': True,
                    'message': 'Player created successfully',
                    'data': {'player_id': player_id}
                }), 201
                
            except Exception as e:
                logger.error(f"Create player error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/player/<username>', methods=['PUT'])
        @token_required
        def update_player(username):
            """Update player information"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Update player score if provided
                if 'score' in data:
                    success = self.db_manager.update_player_score(username, data['score'])
                    if not success:
                        return jsonify({'error': 'Player not found'}), 404
                
                # Emit real-time update
                self.socketio.emit('player_updated', {
                    'username': username,
                    'updates': data,
                    'timestamp': datetime.now().isoformat()
                }, room='dashboard')
                
                return jsonify({
                    'success': True,
                    'message': 'Player updated successfully'
                })
                
            except Exception as e:
                logger.error(f"Update player error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # ===== ALLIANCE MANAGEMENT =====
        
        @self.app.route('/api/alliance', methods=['POST'])
        @token_required
        def create_alliance():
            """Create new alliance"""
            try:
                data = request.get_json()
                if not data or not data.get('name'):
                    return jsonify({'error': 'Alliance name required'}), 400
                
                alliance_id = self.db_manager.add_alliance(
                    data['name'],
                    data.get('total_score', 0),
                    data.get('members', 0),
                    data.get('description')
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Alliance created successfully',
                    'data': {'alliance_id': alliance_id}
                }), 201
                
            except Exception as e:
                logger.error(f"Create alliance error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # ===== GAME SESSIONS =====
        
        @self.app.route('/api/session', methods=['POST'])
        @token_required
        def log_game_session():
            """Log a game session"""
            try:
                data = request.get_json()
                if not data or not data.get('player_name'):
                    return jsonify({'error': 'Player name required'}), 400
                
                success = self.db_manager.log_game_session(
                    data['player_name'],
                    data.get('session_type', 'game'),
                    data.get('score_change', 0),
                    data.get('duration_seconds', 0)
                )
                
                if not success:
                    return jsonify({'error': 'Player not found'}), 404
                
                return jsonify({
                    'success': True,
                    'message': 'Game session logged successfully'
                })
                
            except Exception as e:
                logger.error(f"Log game session error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # ===== SYSTEM LOGS =====
        
        @self.app.route('/api/logs')
        @token_required
        def get_system_logs():
            """Get system logs"""
            try:
                level = request.args.get('level')
                limit = request.args.get('limit', 100, type=int)
                
                logs = self.db_manager.get_system_logs(level, limit)
                
                return jsonify({
                    'success': True,
                    'data': logs,
                    'count': len(logs)
                })
                
            except Exception as e:
                logger.error(f"Get system logs error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/log', methods=['POST'])
        @token_required
        def log_system_event():
            """Log a system event"""
            try:
                data = request.get_json()
                if not data or not data.get('message'):
                    return jsonify({'error': 'Message required'}), 400
                
                self.db_manager.log_system_event(
                    data.get('level', 'INFO'),
                    data['message'],
                    data.get('module', 'api')
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Event logged successfully'
                })
                
            except Exception as e:
                logger.error(f"Log system event error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # ===== HEALTH CHECK =====
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'services': {
                    'database': 'connected',
                    'auth': 'active',
                    'socketio': 'active'
                }
            })
    
    def _setup_socketio_events(self):
        """Setup SocketIO events for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {
                'message': 'Connected to AgentDaf1.1',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('join_dashboard')
        def handle_join_dashboard():
            """Join dashboard room for real-time updates"""
            join_room('dashboard')
            emit('joined_room', {'room': 'dashboard'})
        
        @self.socketio.on('leave_dashboard')
        def handle_leave_dashboard():
            """Leave dashboard room"""
            leave_room('dashboard')
            emit('left_room', {'room': 'dashboard'})
        
        @self.socketio.on('request_stats')
        def handle_request_stats():
            """Handle stats request"""
            try:
                players = self.db_manager.get_all_players()
                alliances = self.db_manager.get_all_alliances()
                
                stats = {
                    'players': {
                        'total': len(players),
                        'active': len([p for p in players if p['score'] > 0])
                    },
                    'alliances': {
                        'total': len(alliances),
                        'active': len([a for a in alliances if a['members'] > 0])
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                emit('stats_update', stats)
            except Exception as e:
                logger.error(f"Stats request error: {str(e)}")
                emit('error', {'message': 'Failed to get stats'})
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Resource not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {str(error)}")
            return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.errorhandler(413)
        def too_large(error):
            return jsonify({'error': 'File too large'}), 413
    
    def _start_background_tasks(self):
        """Start background tasks for real-time updates"""
        def stats_updater():
            """Background task to update stats periodically"""
            while True:
                try:
                    players = self.db_manager.get_all_players()
                    alliances = self.db_manager.get_all_alliances()
                    
                    stats = {
                        'players': {
                            'total': len(players),
                            'active': len([p for p in players if p['score'] > 0])
                        },
                        'alliances': {
                            'total': len(alliances),
                            'active': len([a for a in alliances if a['members'] > 0])
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.socketio.emit('stats_update', stats, room='dashboard')
                    
                except Exception as e:
                    logger.error(f"Background stats update error: {str(e)}")
                
                time.sleep(30)  # Update every 30 seconds
        
        # Start background thread
        stats_thread = threading.Thread(target=stats_updater, daemon=True)
        stats_thread.start()
    
    def _allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls', 'csv'}
    
    def _save_uploaded_file(self, file) -> str:
        """Save uploaded file and return path"""
        try:
            filename = file.filename or 'uploaded_file.xlsx'
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            file.save(file_path)
            return file_path
        except Exception as e:
            logger.error(f"Save file error: {str(e)}")
            return ""
    
    def _update_database_from_excel(self, data):
        """Update database with data from Excel file"""
        try:
            players = data.get('players', [])
            
            for player_data in players:
                self.db_manager.add_player(
                    player_data.get('name', ''),
                    player_data.get('score', 0),
                    player_data.get('alliance'),
                    player_data.get('level', 1)
                )
            
            logger.info(f"Updated database with {len(players)} players from Excel")
            
        except Exception as e:
            logger.error(f"Database update from Excel error: {str(e)}")
    
    def run(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
        """Run the Flask application with SocketIO"""
        logger.info(f"Starting Enhanced Flask API on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# Create application instance
def create_enhanced_app():
    """Application factory"""
    api = EnhancedFlaskAPI()
    return api.app

if __name__ == '__main__':
    app = EnhancedFlaskAPI()
    app.run(debug=True)