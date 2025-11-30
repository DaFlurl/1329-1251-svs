#!/usr/bin/env python3
"""
Simple 3D Dashboard Test
Tests basic 3D functionality without Unicode characters
"""

import os
import sys
import time
import requests
import subprocess
from datetime import datetime

def test_server_startup():
    """Test if Flask server starts successfully"""
    print("Testing server startup...")
    try:
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "simple_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Test health endpoint
        response = requests.get("http://localhost:8080/api/health", timeout=10)
        if response.status_code == 200:
            print("SUCCESS: Server started and responding")
            server_process.terminate()
            return True
        else:
            print("FAIL: Server not responding correctly")
            server_process.terminate()
            return False
            
    except Exception as e:
        print(f"FAIL: Error starting server - {e}")
        return False

def test_3d_files_exist():
    """Test if all 3D files exist"""
    print("Testing 3D files existence...")
    
    required_files = [
        'styles/3d-framework.css',
        'styles/3d-framework.js',
        'styles/3d-navigation.css',
        'styles/3d-navigation.js',
        'styles/3d-upload.css',
        'styles/3d-upload.js',
        'styles/3d-notifications.css',
        'styles/3d-notifications.js',
        'styles/3d-background.css',
        'styles/3d-background.js',
        'styles/3d-hover.css',
        'styles/3d-hover.js',
        'styles/3d-data-viz.css',
        'styles/3d-data-viz.js',
        'styles/3d-charts-advanced.js',
        'templates/dashboard-3d.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"FAIL: Missing files: {missing_files}")
        return False
    else:
        print("SUCCESS: All 3D files exist")
        return True

def test_3d_dashboard_route():
    """Test if 3D dashboard route is accessible"""
    print("Testing 3D dashboard route...")
    
    try:
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "simple_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Test 3D dashboard route
        response = requests.get("http://localhost:8080/dashboard-3d", timeout=10)
        if response.status_code == 200:
            print("SUCCESS: 3D dashboard route accessible")
            server_process.terminate()
            return True
        else:
            print(f"FAIL: 3D dashboard route returned {response.status_code}")
            server_process.terminate()
            return False
            
    except Exception as e:
        print(f"FAIL: Error accessing 3D dashboard - {e}")
        return False

def main():
    """Run all tests"""
    print("Simple 3D Dashboard Test Suite")
    print("=" * 40)
    
    tests = [
        ("3D Files Exist", test_3d_files_exist),
        ("Server Startup", test_server_startup),
        ("3D Dashboard Route", test_3d_dashboard_route)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY:")
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("SUCCESS: All tests passed! 3D system is ready.")
        return True
    else:
        print("WARNING: Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)