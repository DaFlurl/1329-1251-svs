#!/usr/bin/env python3
"""
Test FlaskAPI instantiation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.api.flask_api import FlaskAPI
    print("[OK] FlaskAPI import successful")
    
    # Test instantiation
    app = FlaskAPI()
    print("[OK] FlaskAPI instantiation successful")
    
    # Test app configuration
    print(f"[OK] App name: {app.app.name}")
    print(f"[OK] Debug mode: {app.app.debug}")
    
    print("[SUCCESS] FlaskAPI test completed successfully!")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Instantiation error: {e}")
    sys.exit(1)