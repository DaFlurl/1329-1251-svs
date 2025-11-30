"""
Enterprise WebSocket Service
Real-time data streaming and communication hub
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
import redis
from prometheus_client import Counter, Gauge, Histogram
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
WEBSOCKET_CONNECTIONS = Gauge('websocket_connections_active', 'Active WebSocket connections')
MESSAGES_SENT = Counter('websocket_messages_sent_total', 'Total messages sent', ['type'])
MESSAGES_RECEIVED = Counter('websocket_messages_received_total', 'Total messages received', ['type'])
CONNECTION_DURATION = Histogram('websocket_connection_duration_seconds', 'Connection duration')

class ConnectionManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_subscriptions: Dict[str, Set[str]] = {}
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        
    async def connect(self, websocket: WebSocketServerProtocol, client_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.user_subscriptions[client_id] = set()
        
        WEBSOCKET_CONNECTIONS.inc()
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "server_time": time.time()
        }, client_id)
        
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
        # Notify other clients about new connection
        await self.broadcast_message({
            "type": "user_connected",
            "client_id": client_id,
            "total_users": len(self.active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_client=client_id)
    
    async def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.user_subscriptions[client_id]
            
            WEBSOCKET_CONNECTIONS.dec()
            
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
            
            # Notify other clients about disconnection
            await self.broadcast_message({
                "type": "user_disconnected",
                "client_id": client_id,
                "total_users": len(self.active_connections),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
                MESSAGES_SENT.labels(type='personal').inc()
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_client: str = None):
        """Broadcast a message to all connected clients"""
        message_str = json.dumps(message)
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            if client_id != exclude_client:
                try:
                    await websocket.send_text(message_str)
                    MESSAGES_SENT.labels(type='broadcast').inc()
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    async def subscribe_to_channel(self, client_id: str, channel: str):
        """Subscribe a client to a specific data channel"""
        if client_id in self.user_subscriptions:
            self.user_subscriptions[client_id].add(channel)
            
            await self.send_personal_message({
                "type": "subscription_confirmed",
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)
            
            logger.info(f"Client {client_id} subscribed to {channel}")
    
    async def unsubscribe_from_channel(self, client_id: str, channel: str):
        """Unsubscribe a client from a specific data channel"""
        if client_id in self.user_subscriptions:
            self.user_subscriptions[client_id].discard(channel)
            
            await self.send_personal_message({
                "type": "subscription_cancelled",
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)
            
            logger.info(f"Client {client_id} unsubscribed from {channel}")
    
    async def send_to_channel(self, channel: str, message: Dict[str, Any]):
        """Send a message to all clients subscribed to a channel"""
        message_str = json.dumps(message)
        disconnected_clients = []
        
        for client_id, subscriptions in self.user_subscriptions.items():
            if channel in subscriptions and client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(message_str)
                    MESSAGES_SENT.labels(type='channel').inc()
                except Exception as e:
                    logger.error(f"Error sending to channel {channel} for {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
        
        # Also publish to Redis for cross-service communication
        self.redis_client.publish(f"ws_channel:{channel}", json.dumps(message))

class DataStreamer:
    """Handles real-time data streaming from various sources"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.running = False
        
    async def start_streaming(self):
        """Start real-time data streaming"""
        self.running = True
        
        # Start Redis subscription listener
        asyncio.create_task(self.redis_listener())
        
        # Start periodic data updates
        asyncio.create_task(self.periodic_updates())
        
        # Start live score updates simulation
        asyncio.create_task(self.simulate_live_updates())
        
        logger.info("Data streaming started")
    
    async def stop_streaming(self):
        """Stop real-time data streaming"""
        self.running = False
        logger.info("Data streaming stopped")
    
    async def redis_listener(self):
        """Listen for Redis pub/sub messages"""
        pubsub = self.redis_client.pubsub()
        
        # Subscribe to data update channels
        channels = [
            'data_updates',
            'player_updates',
            'alliance_updates',
            'system_notifications'
        ]
        
        for channel in channels:
            pubsub.subscribe(channel)
        
        logger.info(f"Subscribed to Redis channels: {channels}")
        
        while self.running:
            try:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    data = json.loads(message['data'])
                    await self.handle_redis_message(message['channel'], data)
            except Exception as e:
                logger.error(f"Error in Redis listener: {e}")
                await asyncio.sleep(1)
    
    async def handle_redis_message(self, channel: str, data: Dict[str, Any]):
        """Handle incoming Redis messages"""
        message_type = data.get('type', 'unknown')
        
        if message_type == 'player_update':
            await self.connection_manager.send_to_channel('players', {
                "type": "player_update",
                "player": data.get('player'),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif message_type == 'alliance_update':
            await self.connection_manager.send_to_channel('alliances', {
                "type": "alliance_update",
                "alliance": data.get('alliance'),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif message_type == 'leaderboard_update':
            await self.connection_manager.send_to_channel('leaderboard', {
                "type": "leaderboard_update",
                "top_players": data.get('top_players', []),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif message_type == 'system_notification':
            await self.connection_manager.broadcast_message({
                "type": "system_notification",
                "title": data.get('title', 'System Notification'),
                "message": data.get('message', ''),
                "level": data.get('level', 'info'),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def periodic_updates(self):
        """Send periodic data updates"""
        while self.running:
            try:
                # Send statistics update every 30 seconds
                await self.send_statistics_update()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error in periodic updates: {e}")
                await asyncio.sleep(5)
    
    async def send_statistics_update(self):
        """Send current statistics to all clients"""
        try:
            # Get current statistics from data service
            stats = await self.get_current_statistics()
            
            await self.connection_manager.send_to_channel('statistics', {
                "type": "statistics_update",
                "statistics": stats,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error sending statistics update: {e}")
    
    async def get_current_statistics(self) -> Dict[str, Any]:
        """Get current statistics from data service"""
        try:
            # This would normally call the data service API
            # For now, return mock data
            return {
                "total_players": 407,
                "total_alliances": 12,
                "total_score": 2847650,
                "avg_score": 6997,
                "active_games": 3,
                "last_update": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def simulate_live_updates(self):
        """Simulate live score updates for demonstration"""
        while self.running:
            try:
                # Simulate random player score changes
                await asyncio.sleep(45)  # Every 45 seconds
                
                # Random player update
                player_update = {
                    "name": f"Player_{random.randint(1, 100)}",
                    "score": random.randint(1000, 50000),
                    "change": random.randint(-100, 500),
                    "alliance": f"Alliance_{random.choice(['A', 'B', 'C'])}"
                }
                
                await self.connection_manager.send_to_channel('players', {
                    "type": "live_score_update",
                    "player": player_update,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in live updates simulation: {e}")

class WebSocketService:
    """Enterprise WebSocket Service"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.data_streamer = DataStreamer(self.connection_manager)
        
    async def handle_websocket(self, websocket: WebSocketServerProtocol, client_id: str):
        """Handle individual WebSocket connection"""
        connection_start_time = time.time()
        
        try:
            await self.connection_manager.connect(websocket, client_id)
            
            # Start data streaming if this is the first connection
            if len(self.connection_manager.active_connections) == 1:
                await self.data_streamer.start_streaming()
            
            # Handle messages from this client
            async for message in websocket:
                await self.handle_client_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} connection closed")
        except Exception as e:
            logger.error(f"Error handling WebSocket for {client_id}: {e}")
        finally:
            await self.connection_manager.disconnect(client_id)
            
            # Stop data streaming if no more connections
            if len(self.connection_manager.active_connections) == 0:
                await self.data_streamer.stop_streaming()
            
            # Record connection duration
            CONNECTION_DURATION.observe(time.time() - connection_start_time)
    
    async def handle_client_message(self, client_id: str, message: str):
        """Handle incoming message from a client"""
        try:
            data = json.loads(message)
            message_type = data.get('type', 'unknown')
            
            MESSAGES_RECEIVED.labels(type=message_type).inc()
            
            if message_type == 'subscribe':
                channel = data.get('channel')
                if channel:
                    await self.connection_manager.subscribe_to_channel(client_id, channel)
            
            elif message_type == 'unsubscribe':
                channel = data.get('channel')
                if channel:
                    await self.connection_manager.unsubscribe_from_channel(client_id, channel)
            
            elif message_type == 'ping':
                await self.connection_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, client_id)
            
            elif message_type == 'get_current_data':
                # Send current data snapshot
                await self.send_current_data_snapshot(client_id)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
    
    async def send_current_data_snapshot(self, client_id: str):
        """Send current data snapshot to a client"""
        try:
            # Get current data from data service
            players = await self.get_current_players()
            alliances = await self.get_current_alliances()
            statistics = await self.data_streamer.get_current_statistics()
            
            await self.connection_manager.send_personal_message({
                "type": "data_snapshot",
                "players": players,
                "alliances": alliances,
                "statistics": statistics,
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)
            
        except Exception as e:
            logger.error(f"Error sending data snapshot: {e}")
    
    async def get_current_players(self) -> List[Dict[str, Any]]:
        """Get current players data"""
        # This would normally call the data service
        return []
    
    async def get_current_alliances(self) -> List[Dict[str, Any]]:
        """Get current alliances data"""
        # This would normally call the data service
        return []

# Global service instance
websocket_service = WebSocketService()

# FastAPI app for WebSocket endpoint
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import random

app = FastAPI(
    title="AgentDaf1.1 WebSocket Service",
    description="Real-time data streaming service",
    version="3.0.0"
)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket_service.handle_websocket(websocket, client_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "websocket",
        "active_connections": len(websocket_service.connection_manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest
    from fastapi import Response
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)