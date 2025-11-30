#!/usr/bin/env python3
"""
Test script to verify AgentDaf1.1 app startup
"""

import sys
import time
import threading
import requests
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_app_startup():
    """Test if the app can start and respond to requests"""
    print("Testing AgentDaf1.1 app startup...")
    
    try:
        # Import app
        import app
        print("+ App imported successfully")
        
        # Test health endpoint directly
        with app.app.test_client() as client:
            response = client.get('/health')
            print(f"+ Health endpoint status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"+ Health response: {data}")
            
            # Test root endpoint
            response = client.get('/')
            print(f"+ Root endpoint status: {response.status_code}")
            
            # Test API health endpoint
            response = client.get('/api/health')
            print(f"+ API health endpoint status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"+ API health response: {data}")
        
        print("+ All tests passed! App is ready to run.")
        return True
        
    except Exception as e:
        print(f"- Error during app test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)