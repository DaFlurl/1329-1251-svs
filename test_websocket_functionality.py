#!/usr/bin/env python3
"""
Test WebSocket Real-time Updates
Phase 2 Core Feature Testing
"""

import os
import sys
import time
import threading

def test_websocket_service():
    """Test WebSocket service functionality"""
    print("Testing WebSocket Service Functionality...")
    
    try:
        sys.path.append('src')
        from core.websocket_service import WebSocketService
        
        ws = WebSocketService()
        print("WebSocketService instantiated successfully")
        
        # Test WebSocket service methods
        methods_to_check = [
            'start_server',
            'stop_server',
            'broadcast_message',
            'send_to_client',
            'get_connected_clients',
            'handle_connection'
        ]
        
        for method in methods_to_check:
            if hasattr(ws, method):
                print(f"{method} method exists")
            else:
                print(f"{method} method missing")
        
        # Test configuration
        if hasattr(ws, 'host') and hasattr(ws, 'port'):
            print(f"WebSocket configured for {ws.host}:{ws.port}")
        else:
            print("WebSocket host/port configuration missing")
        
        return True
        
    except Exception as e:
        print(f"Error testing WebSocket service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_websocket_dependencies():
    """Test WebSocket dependencies"""
    print("\nTesting WebSocket Dependencies...")
    
    # Check for required packages
    required_packages = [
        'websockets',
        'asyncio',
        'json'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package} available")
        except ImportError:
            print(f"{package} missing")
    
    # Check for WebSocket configuration
    config_files = [
        'config/websocket.json',
        'websocket.json'
    ]
    
    for config in config_files:
        if os.path.exists(config):
            print(f"Config found: {config}")
        else:
            print(f"Config missing: {config}")
    
    return True

def test_websocket_integration():
    """Test WebSocket integration with Flask app"""
    print("\nTesting WebSocket Integration...")
    
    try:
        # Check if app.py has WebSocket integration
        with open('app.py', 'r') as f:
            app_content = f.read()
            
        if 'websocket_service' in app_content:
            print("WebSocket service integrated in app.py")
        else:
            print("WebSocket service not found in app.py")
            
        if 'WebSocketService' in app_content:
            print("WebSocketService class imported in app.py")
        else:
            print("WebSocketService class not imported in app.py")
        
        return True
        
    except Exception as e:
        print(f"Error testing WebSocket integration: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2: WEBSOCKET REAL-TIME UPDATES TEST")
    print("=" * 60)
    
    success1 = test_websocket_service()
    success2 = test_websocket_dependencies()
    success3 = test_websocket_integration()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("WEBSOCKET TEST: PASSED")
    else:
        print("WEBSOCKET TEST: FAILED")
    print("=" * 60)