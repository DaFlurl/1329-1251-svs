#!/usr/bin/env python3
"""
WebSocket Service for AgentDaf1.1
Real-time updates and notifications
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any, Optional
import threading

# Import centralized configurations
from src.config.path_config import PROJECT_ROOT
from src.config.optional_imports import websockets, WEBSOCKETS_AVAILABLE
from src.config.logging_config import get_logger

logger = get_logger(__name__)

class WebSocketService:
    """WebSocket service for real-time updates"""
    
    def __init__(self, host: str = "localhost", port: int = 8081):
        self.host = host
        self.port = port
        self.clients: Set = set()
        self.authenticated_clients: Dict = {}
        self.running = False
        self.server_thread = None
        
        # Try to get database and auth managers if available
        try:
            from src.database.database_manager import DatabaseManager
            from auth import AuthManager
            self.db_manager = DatabaseManager()
            self.auth_manager = AuthManager()
            logger.info("Database and auth managers loaded successfully")
        except ImportError as e:
            logger.warning(f"Database or auth managers not available: {str(e)}")
            self.db_manager = None
            self.auth_manager = None
        
        # Check if websockets is available
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("websockets library not installed, WebSocket service disabled")
            self.available = False
        else:
            self.available = True
        
    def is_available(self) -> bool:
        """Check if WebSocket service is available"""
        return self.available and WEBSOCKETS_AVAILABLE
        
    async def register_client(self, websocket):
        """Register a new client"""
        if not self.is_available():
            return
            
        self.clients.add(websocket)
        logger.info(f"Client connected: {getattr(websocket, 'remote_address', 'unknown')}")
        
        # Send welcome message
        await self.send_to_client(websocket, {
            'type': 'connected',
            'message': 'Connected to AgentDaf1.1 WebSocket service',
            'timestamp': datetime.now().isoformat()
        })
    
    async def unregister_client(self, websocket):
        """Unregister a client"""
        if not self.is_available():
            return
            
        self.clients.discard(websocket)
        if websocket in self.authenticated_clients:
            del self.authenticated_clients[websocket]
        logger.info(f"Client disconnected: {getattr(websocket, 'remote_address', 'unknown')}")
    
    async def authenticate_client(self, websocket, token: str):
        """Authenticate a client with JWT token"""
        if not self.is_available() or not self.auth_manager:
            return False
            
        try:
            payload = self.auth_manager.verify_token(token)
            if payload and payload.get('type') == 'access':
                self.authenticated_clients[websocket] = payload
                await self.send_to_client(websocket, {
                    'type': 'authenticated',
                    'user': {
                        'user_id': payload['user_id'],
                        'username': payload['username'],
                        'role': payload['role']
                    },
                    'timestamp': datetime.now().isoformat()
                })
                return True
            else:
                await self.send_to_client(websocket, {
                    'type': 'error',
                    'message': 'Invalid or expired token',
                    'timestamp': datetime.now().isoformat()
                })
                return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Authentication failed',
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    async def send_to_client(self, websocket, message: Dict):
        """Send message to specific client"""
        if not self.is_available():
            return
            
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending to client: {str(e)}")
            await self.unregister_client(websocket)
    
    async def broadcast(self, message: Dict, authenticated_only: bool = False):
        """Broadcast message to all clients"""
        if not self.is_available() or not self.clients:
            return
            
        disconnected = set()
        target_clients = self.authenticated_clients.keys() if authenticated_only else self.clients
        
        for client in target_clients:
            try:
                await client.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Broadcast error: {str(e)}")
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            await self.unregister_client(client)
    
    async def handle_message(self, websocket, message: str):
        """Handle incoming message from client"""
        if not self.is_available():
            return
            
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'authenticate':
                token = data.get('token')
                if token:
                    await self.authenticate_client(websocket, token)
            
            elif message_type == 'subscribe':
                await self.handle_subscription(websocket, data)
            
            elif message_type == 'get_stats':
                await self.send_stats_to_client(websocket)
            
            else:
                await self.send_to_client(websocket, {
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}',
                    'timestamp': datetime.now().isoformat()
                })
        
        except json.JSONDecodeError:
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Invalid JSON format',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Internal server error',
                'timestamp': datetime.now().isoformat()
            })
    
    async def handle_subscription(self, websocket, data: Dict):
        """Handle client subscription to data types"""
        if not self.is_available():
            return
            
        subscriptions = data.get('subscriptions', [])
        
        if websocket not in self.authenticated_clients:
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Authentication required for subscriptions',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        await self.send_to_client(websocket, {
            'type': 'subscribed',
            'subscriptions': subscriptions,
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_stats_to_client(self, websocket):
        """Send current statistics to client"""
        if not self.is_available():
            return
            
        try:
            stats = self.get_current_stats()
            await self.send_to_client(websocket, {
                'type': 'stats_update',
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error sending stats: {str(e)}")
    
    def get_current_stats(self) -> Dict:
        """Get current system statistics"""
        try:
            if self.db_manager:
                # Try to get real stats from database
                try:
                    players = self.db_manager.get_all_players()
                    alliances = self.db_manager.get_all_alliances()
                    db_stats = self.db_manager.get_database_stats()
                    
                    return {
                        'players': {
                            'total': len(players),
                            'active': len([p for p in players if p.get('score', 0) > 0]),
                            'average_score': sum(p.get('score', 0) for p in players) // len(players) if players else 0
                        },
                        'alliances': {
                            'total': len(alliances),
                            'active': len([a for a in alliances if a.get('members', 0) > 0])
                        },
                        'database': {
                            'size_mb': db_stats.get('database_size_mb', 0),
                            'tables': db_stats.get('tables', [])
                        },
                        'websocket': {
                            'connected_clients': len(self.clients),
                            'authenticated_clients': len(self.authenticated_clients)
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception:
                    pass
            
            # Fallback stats
            return {
                'players': {'total': 0, 'active': 0, 'average_score': 0},
                'alliances': {'total': 0, 'active': 0},
                'database': {'size_mb': 0, 'tables': []},
                'websocket': {
                    'connected_clients': len(self.clients),
                    'authenticated_clients': len(self.authenticated_clients)
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def notify_player_update(self, player_name: str, action: str, data: Dict = None):
        """Notify clients about player updates"""
        message = {
            'type': 'player_update',
            'action': action,
            'player_name': player_name,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast(message, authenticated_only=True)
    
    async def notify_alliance_update(self, alliance_name: str, action: str, data: Dict = None):
        """Notify clients about alliance updates"""
        message = {
            'type': 'alliance_update',
            'action': action,
            'alliance_name': alliance_name,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast(message, authenticated_only=True)
    
    async def notify_system_event(self, event_type: str, message: str, data: Dict = None):
        """Notify clients about system events"""
        broadcast_message = {
            'type': 'system_event',
            'event_type': event_type,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast(broadcast_message)
    
    async def periodic_stats_update(self):
        """Periodically send stats updates to all clients"""
        while self.running:
            try:
                stats = self.get_current_stats()
                await self.broadcast({
                    'type': 'stats_update',
                    'data': stats,
                    'timestamp': datetime.now().isoformat()
                })
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Periodic stats update error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def handle_client(self, websocket, path: str):
        """Handle client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except Exception as e:
            logger.error(f"Client handling error: {str(e)}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        if not self.is_available():
            logger.warning("WebSocket service not available, skipping server start")
            return
            
        self.running = True
        
        # Start periodic stats update task
        stats_task = asyncio.create_task(self.periodic_stats_update())
        
        try:
            logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info("WebSocket server started successfully")
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"WebSocket server error: {str(e)}")
        finally:
            self.running = False
            stats_task.cancel()
    
    def start(self):
        """Start the WebSocket server in a new thread"""
        if not self.is_available():
            logger.warning("WebSocket service not available, not starting server")
            return None
            
        def run_server():
            asyncio.run(self.start_server())
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        logger.info(f"WebSocket service started on ws://{self.host}:{self.port}")
        return self.server_thread
    
    def stop(self):
        """Stop the WebSocket server"""
        self.running = False
        if self.server_thread:
            logger.info("WebSocket service stopped")

# Global WebSocket service instance
websocket_service = WebSocketService()

def get_websocket_service() -> WebSocketService:
    """Get global WebSocket service instance"""
    return websocket_service

# Convenience functions for external use
async def notify_player_update(player_name: str, action: str, data: Dict = None):
    """Notify about player update"""
    await websocket_service.notify_player_update(player_name, action, data)

async def notify_alliance_update(alliance_name: str, action: str, data: Dict = None):
    """Notify about alliance update"""
    await websocket_service.notify_alliance_update(alliance_name, action, data)

async def notify_system_event(event_type: str, message: str, data: Dict = None):
    """Notify about system event"""
    await websocket_service.notify_system_event(event_type, message, data)