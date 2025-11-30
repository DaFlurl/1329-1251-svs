#!/usr/bin/env python3
"""
Test Excel Upload Script
"""
import requests
import os

def test_excel_upload():
    """Test Excel upload to API"""
    api_url = "http://localhost:8080"
    
    print("Testing Excel Upload...")
    
    # Check if test file exists
    if not os.path.exists('test_gaming_data.xlsx'):
        print("Test Excel file not found")
        return False
    
    try:
        # Test health first
        print("Checking API health...")
        health_response = requests.get(f"{api_url}/api/health")
        if health_response.status_code == 200:
            print(f"API is healthy: {health_response.json()}")
        else:
            print(f"API health check failed: {health_response.status_code}")
            return False
        
        # Upload Excel file
        print("Uploading Excel file...")
        with open('test_gaming_data.xlsx', 'rb') as f:
            files = {'file': ('test_gaming_data.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            upload_response = requests.post(f"{api_url}/api/upload", files=files)
        
        print(f"Upload status: {upload_response.status_code}")
        result = upload_response.json()
        print(f"Upload result: {result}")
        
        if upload_response.status_code == 200 and result.get('success'):
            print("Excel upload successful!")
            
            # Test dashboard access
            if 'data' in result and 'dashboard_url' in result['data']:
                dashboard_url = f"{api_url}{result['data']['dashboard_url']}"
                print(f"Dashboard URL: {dashboard_url}")
                
                # Test dashboard access
                dashboard_response = requests.get(dashboard_url)
                if dashboard_response.status_code == 200:
                    print("Dashboard accessible!")
                else:
                    print(f"Dashboard access failed: {dashboard_response.status_code}")
            
            return True
        else:
            print(f"Upload failed: {result}")
            return False
            
    except Exception as e:
        print(f"Error during upload test: {e}")
        return False

if __name__ == "__main__":
    success = test_excel_upload()
    if success:
        print("/nExcel upload test completed successfully!")
    else:
        print("/nExcel upload test failed!")