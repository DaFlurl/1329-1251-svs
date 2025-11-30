#!/usr/bin/env python3
"""
Debug Excel Upload
"""
import requests
import traceback

def debug_upload():
    """Debug the upload process"""
    api_url = "http://localhost:8080"
    
    logger.info("=== DEBUG EXCEL UPLOAD ===")
    
    # Test with a simple file check first
    try:
        with open('test_gaming_data.xlsx', 'rb') as f:
            files = {'file': ('test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            logger.info("Sending request to /api/upload...")
            response = requests.post(f"{api_url}/api/upload", files=files)
            
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Text: {response.text}")
            
            if response.status_code != 200:
                logger.info("=== ERROR DETAILS ===")
                try:
                    error_json = response.json()
                    logger.info(f"Error JSON: {error_json}")
                except:
                    logger.info("Could not parse error as JSON")
                    
    except Exception as e:
        logger.info(f"Exception occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_upload()