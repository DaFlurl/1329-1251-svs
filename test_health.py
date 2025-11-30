#!/usr/bin/env python3
"""
Test health endpoints
"""

import sys
import threading
import time
import requests
from app import app

def run_app():
    app.run(host='127.0.0.1', port=8080, debug=False)

def test_health_endpoint():
    """Test health endpoint"""
    print("Starting Flask app...")
    
    # Start app in background thread
    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get('http://127.0.0.1:8080/health', timeout=5)
        print(f'Health endpoint status: {response.status_code}')
        if response.status_code == 200:
            print('[OK] Health endpoint working correctly')
            print(f'Response: {response.json()}')
            return True
        else:
            print('[FAIL] Health endpoint returned error')
            return False
    except Exception as e:
        print(f'[FAIL] Error testing health endpoint: {e}')
        return False

if __name__ == "__main__":
    success = test_health_endpoint()
    sys.exit(0 if success else 1)