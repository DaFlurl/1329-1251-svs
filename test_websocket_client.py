#!/usr/bin/env python3
"""
Simple WebSocket client to test the AgentDaf1.1 WebSocket service.
Tests connection, message sending, and response handling.
"""

import asyncio
import json
import sys
import time
import websockets
from datetime import datetime

async def test_websocket_service():
    """Test WebSocket service connection and communication."""
    
    # WebSocket server address
    uri = "ws://localhost:8082"
    
    print(f"Connecting to WebSocket service at {uri}...")
    
    try:
        # Create WebSocket connection
        async with websockets.connect(uri) as websocket:
            print(f"[INFO] Successfully connected to {uri}")
            
            # Send test message
            test_message = {
                "type": "test",
                "timestamp": datetime.now().isoformat(),
                "data": "Hello from test client!"
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"Sent test message: {test_message}")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            
            if response:
                try:
                    response_data = json.loads(response)
                    print(f"[INFO] Received response: {response_data}")
                    
                    # Verify response structure
                    if response_data.get("type") == "response":
                        print("[OK] Service responded correctly!")
                        return True
                    else:
                            print(f"[WARNING] Unexpected response type: {response_data.get('type')}")
                        
                except json.JSONDecodeError as e:
                    print(f"[WARNING] Failed to parse JSON response: {e}")
                    
            else:
                print("[WARNING]  No response received within timeout period")
                return False
                
    except websockets.exceptions.ConnectionRefusedError:
        print(f"[ERROR] Connection refused - WebSocket service may not be running at {uri}")
        print("💡 Make sure the WebSocket service is started on localhost:8082")
        return False
        
    except websockets.exceptions.InvalidURI:
        print(f"❌ Invalid WebSocket URI: {uri}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

async def main():
    """Main test function."""
    print("[TOOL] Starting WebSocket Service Test")
    print("=" * 50)
    
    success = await test_websocket_service()
    
    print("=" * 50)
    if success:
        print("🎉 WebSocket Service Test PASSED")
        print("✅ Connection successful")
        print("✅ Message exchange working")
        print("✅ Response handling correct")
    else:
        print("❌ WebSocket Service Test FAILED")
        print("🔧 Check if service is running on localhost:8082")
        print("🔧 Verify service configuration and logs")

if __name__ == "__main__":
    asyncio.run(main())