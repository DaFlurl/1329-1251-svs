#!/usr/bin/env python3
"""
WebSocket Service for AgentDaf1.1
Real-time updates and notifications
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any
import threading
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db_manager
from auth import get_auth_manager

logger = logging.getLogger(__name__)

class WebSocketService:
    """WebSocket service for real-time updates"""
    
    def __init__(self, host: str = "localhost", port: int = 8082):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.authenticated_clients: Dict[websockets.WebSocketServerProtocol, Dict] = {}
        self.db_manager = get_db_manager()
        self.auth_manager = get_auth_manager()
        self.running = False
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new client"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        # Send welcome message
        await self.send_to_client(websocket, {
            'type': 'connected',
            'message': 'Connected to AgentDaf1.1 WebSocket service',
            'timestamp': datetime.now().isoformat()
        })
    
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a client"""
        self.clients.discard(websocket)
        if websocket in self.authenticated_clients:
            del self.authenticated_clients[websocket]
        logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def authenticate_client(self, websocket: websockets.WebSocketServerProtocol, token: str):
        """Authenticate a client with JWT token"""
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
    
    async def send_to_client(self, websocket: websockets.WebSocketServerProtocol, message: Dict):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"Error sending to client: {str(e)}")
    
    async def broadcast(self, message: Dict, authenticated_only: bool = False):
        """Broadcast message to all clients"""
        if self.clients:
            disconnected = set()
            target_clients = self.authenticated_clients.keys() if authenticated_only else self.clients
            
            for client in target_clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
                except Exception as e:
                    logger.error(f"Broadcast error: {str(e)}")
                    disconnected.add(client)
            
            # Remove disconnected clients
            for client in disconnected:
                await self.unregister_client(client)
    
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'authenticate':
                token = data.get('token')
                if token:
                    await self.authenticate_client(websocket, token)
            
            elif message_type == 'subscribe':
                # Handle subscription to specific data types
                await self.handle_subscription(websocket, data)
            
            elif message_type == 'get_stats':
                # Send current stats
                await self.send_stats_to_client(websocket)
            
            elif message_type == 'get_players':
                # Send current players
                await self.send_players_to_client(websocket)
            
            elif message_type == 'get_alliances':
                # Send current alliances
                await self.send_alliances_to_client(websocket)
            
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
    
    async def handle_subscription(self, websocket: websockets.WebSocketServerProtocol, data: Dict):
        """Handle client subscription to data types"""
        subscriptions = data.get('subscriptions', [])
        
        # Store client subscriptions (in a real implementation)
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
    
    async def send_stats_to_client(self, websocket: websockets.WebSocketServerProtocol):
        """Send current statistics to client"""
        try:
            stats = self.get_current_stats()
            await self.send_to_client(websocket, {
                'type': 'stats_update',
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error sending stats: {str(e)}")
    
    async def send_players_to_client(self, websocket: websockets.WebSocketServerProtocol):
        """Send current players to client"""
        try:
            players = self.db_manager.get_all_players()
            await self.send_to_client(websocket, {
                'type': 'players_update',
                'data': players,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error sending players: {str(e)}")
    
    async def send_alliances_to_client(self, websocket: websockets.WebSocketServerProtocol):
        """Send current alliances to client"""
        try:
            alliances = self.db_manager.get_all_alliances()
            await self.send_to_client(websocket, {
                'type': 'alliances_update',
                'data': alliances,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error sending alliances: {str(e)}")
    
    def get_current_stats(self) -> Dict:
        """Get current system statistics"""
        try:
            players = self.db_manager.get_all_players()
            alliances = self.db_manager.get_all_alliances()
            db_stats = self.db_manager.get_database_stats()
            
            return {
                'players': {
                    'total': len(players),
                    'active': len([p for p in players if p['score'] > 0]),
                    'average_score': sum(p['score'] for p in players) // len(players) if players else 0
                },
                'alliances': {
                    'total': len(alliances),
                    'active': len([a for a in alliances if a['members'] > 0])
                },
                'database': {
                    'size_mb': db_stats.get('database_size_mb', 0),
                    'tables': db_stats.get('tables', [])
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
    
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Client handling error: {str(e)}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
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
        def run_server():
            asyncio.run(self.start_server())
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        logger.info(f"WebSocket service started on ws://{self.host}:{self.port}")
        return server_thread

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

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start WebSocket service
    service = WebSocketService()
    try:
        asyncio.run(service.start_server())
    except KeyboardInterrupt:
        logger.info("WebSocket service stopped by user")
    except Exception as e:
        logger.error(f"WebSocket service error: {str(e)}")