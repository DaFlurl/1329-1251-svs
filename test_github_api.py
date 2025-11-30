#!/usr/bin/env python3
"""
GitHub API Test Script for AgentDaf1.1
Tests all GitHub API endpoints
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8080"

def test_endpoint(endpoint, method='GET', data=None):
    """Test a specific API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        
        print(f"/n{'='*50}")
        print(f"TEST: {method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text}")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"/nERROR: Could not connect to {BASE_URL}")
        print("Make sure Flask API is running on port 8080")
        return False
    except Exception as e:
        print(f"/nERROR: {str(e)}")
        return False

def main():
    """Run all GitHub API tests"""
    print("GitHub API Test Suite for AgentDaf1.1")
    print(f"Testing against: {BASE_URL}")
    
    tests = [
        ("/api/github/info", "GET"),
        ("/api/github/files", "GET"),
        ("/api/github/webhooks", "GET"),
        ("/api/github/update", "POST", {"files": [{"path": "test.txt", "content": "test"}]}),
        ("/api/github/create-repo", "POST", {"repo_name": "test-repo", "description": "Test repository"}),
    ]
    
    results = []
    
    for test in tests:
        if len(test) == 2:
            endpoint, method = test
            success = test_endpoint(endpoint, method)
        else:
            endpoint, method, data = test
            success = test_endpoint(endpoint, method, data)
        
        results.append((endpoint, method, success))
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print(f"/n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    for endpoint, method, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{method:4} {endpoint:25} - {status}")
    
    print(f"/nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! GitHub API is working correctly.")
    else:
        print("Some tests failed. Check GitHub configuration.")

if __name__ == "__main__":
    main()