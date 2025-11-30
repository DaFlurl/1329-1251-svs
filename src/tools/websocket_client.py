import websocket
import threading
import time
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger('agentdaf1.websocket_client')

class WebSocketClient:
    """
    A simple WebSocket client for sending messages.
    Designed for integration with the AgentDaf1.1 WebSocket service.
    """
    def __init__(self, uri: str, reconnect_interval: int = 5):
        self.uri = uri
        self.reconnect_interval = reconnect_interval
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_connected = False
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        logger.info(f"WebSocketClient initialized for URI: {self.uri}")

    def _on_open(self, ws):
        self.is_connected = True
        logger.info(f"WebSocket connection opened to {self.uri}")

    def _on_message(self, ws, message):
        logger.debug(f"Received message: {message}")
        # In a real scenario, you might want to process incoming messages
        pass

    def _on_error(self, ws, error):
        if self.is_connected: # Only log error if previously connected
            logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False
        logger.info(f"WebSocket connection closed. Code: {close_status_code}, Message: {close_msg}")
        if not self.stop_event.is_set():
            logger.info(f"Attempting to reconnect in {self.reconnect_interval} seconds...")
            time.sleep(self.reconnect_interval)
            self._run_forever() # Reconnect

    def _run_forever(self):
        while not self.stop_event.is_set():
            try:
                self.ws = websocket.WebSocketApp(
                    self.uri,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                self.ws.run_forever(ping_interval=10, ping_timeout=5)
            except Exception as e:
                logger.error(f"WebSocket run_forever failed: {e}. Retrying in {self.reconnect_interval}s")
                time.sleep(self.reconnect_interval)

    def start(self):
        """Start the WebSocket client in a separate thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("WebSocket client already running.")
            return

        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run_forever, daemon=True)
        self.thread.start()
        logger.info("WebSocket client thread started.")
        
        # Wait for a brief moment to allow connection attempt
        time.sleep(1) 

    def stop(self):
        """Stop the WebSocket client"""
        self.stop_event.set()
        if self.ws:
            self.ws.close()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=self.reconnect_interval + 1) # Wait for thread to finish
        logger.info("WebSocket client stopped.")

    def send_message(self, event_type: str, payload: Dict[str, Any]):
        """Send a JSON message over the WebSocket"""
        if not self.is_connected:
            logger.warning("WebSocket client not connected. Message not sent.")
            return False

        message = {
            "event": event_type,
            "data": payload,
            "timestamp": datetime.now().isoformat()
        }
        try:
            self.ws.send(json.dumps(message))
            logger.debug(f"Sent WebSocket message: {event_type}")
            return True
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.is_connected = False # Assume connection lost on send error
            return False

# Global instance for convenience
websocket_client: Optional[WebSocketClient] = None

def get_websocket_client(uri: str = "ws://localhost:8004", reconnect_interval: int = 5) -> WebSocketClient:
    global websocket_client
    if websocket_client is None:
        websocket_client = WebSocketClient(uri, reconnect_interval)
    elif websocket_client.uri != uri:
        logger.warning(f"WebSocket client already initialized with URI {websocket_client.uri}. "
                       f"Re-initializing with new URI {uri} is not recommended.")
        websocket_client.stop()
        websocket_client = WebSocketClient(uri, reconnect_interval)
    return websocket_client

