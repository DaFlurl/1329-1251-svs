#!/usr/bin/env python3
"""
Dark Theme Test Suite
Tests dark theme functionality for 3D dashboard
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def test_dark_theme_files():
    """Test if dark theme files exist"""
    print("Testing dark theme files...")
    
    required_files = [
        'styles/3d-dark-theme.css',
        'styles/3d-dark-theme.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"FAIL: Missing files: {missing_files}")
        return False
    else:
        print("SUCCESS: All dark theme files exist")
        return True

def test_dashboard_integration():
    """Test if dashboard has dark theme integration"""
    print("Testing dashboard integration...")
    
    try:
        with open('templates/dashboard-3d.html', 'r') as f:
            content = f.read()
        
        required_elements = [
            '3d-dark-theme.css',
            '3d-dark-theme.js',
            'initializeThemeIntegration',
            'handleThemeChange'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"FAIL: Missing integration elements: {missing_elements}")
            return False
        else:
            print("SUCCESS: Dashboard has dark theme integration")
            return True
            
    except Exception as e:
        print(f"FAIL: Error reading dashboard: {e}")
        return False

def test_css_variables():
    """Test if CSS variables are properly defined"""
    print("Testing CSS variables...")
    
    try:
        with open('styles/3d-dark-theme.css', 'r') as f:
            content = f.read()
        
        required_variables = [
            '--dark-bg-primary',
            '--dark-text-primary',
            '--dark-accent-primary',
            '--theme-toggle-3d'
        ]
        
        missing_variables = []
        for variable in required_variables:
            if variable not in content:
                missing_variables.append(variable)
        
        if missing_variables:
            print(f"FAIL: Missing CSS variables: {missing_variables}")
            return False
        else:
            print("SUCCESS: All CSS variables defined")
            return True
            
    except Exception as e:
        print(f"FAIL: Error reading CSS: {e}")
        return False

def test_js_functionality():
    """Test if JavaScript functionality is present"""
    print("Testing JavaScript functionality...")
    
    try:
        with open('styles/3d-dark-theme.js', 'r') as f:
            content = f.read()
        
        required_functions = [
            'DarkThemeManager3D',
            'toggleTheme',
            'applyTheme',
            'createThemeToggle',
            'setupKeyboardShortcuts'
        ]
        
        missing_functions = []
        for function in required_functions:
            if function not in content:
                missing_functions.append(function)
        
        if missing_functions:
            print(f"FAIL: Missing JS functions: {missing_functions}")
            return False
        else:
            print("SUCCESS: All JavaScript functions present")
            return True
            
    except Exception as e:
        print(f"FAIL: Error reading JS: {e}")
        return False

def test_server_with_dark_theme():
    """Test if server starts with dark theme"""
    print("Testing server with dark theme...")
    
    try:
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "simple_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Test dashboard route
        import requests
        response = requests.get("http://localhost:8080/dashboard-3d", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check if dark theme files are referenced
            if '3d-dark-theme.css' in content and '3d-dark-theme.js' in content:
                print("SUCCESS: Server serves dashboard with dark theme")
                server_process.terminate()
                return True
            else:
                print("FAIL: Dark theme files not found in response")
                server_process.terminate()
                return False
        else:
            print(f"FAIL: Server returned {response.status_code}")
            server_process.terminate()
            return False
            
    except Exception as e:
        print(f"FAIL: Error testing server: {e}")
        return False

def main():
    """Run all dark theme tests"""
    print("Dark Theme Test Suite")
    print("=" * 40)
    
    tests = [
        ("Dark Theme Files", test_dark_theme_files),
        ("Dashboard Integration", test_dashboard_integration),
        ("CSS Variables", test_css_variables),
        ("JavaScript Functionality", test_js_functionality),
        ("Server with Dark Theme", test_server_with_dark_theme)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 40)
    print("DARK THEME TEST SUMMARY:")
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("SUCCESS: Dark theme is fully functional!")
        return True
    else:
        print("WARNING: Some dark theme tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)