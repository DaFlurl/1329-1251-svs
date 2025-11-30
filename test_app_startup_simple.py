#!/usr/bin/env python3
"""
Test app.py startup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("[TEST] Testing app.py import...")
    import app
    print("[OK] app.py import successful")
    
    print("[TEST] Testing Flask app creation...")
    flask_app = app.app
    print(f"[OK] Flask app created: {flask_app}")
    
    print("[TEST] Testing app configuration...")
    print(f"[OK] App name: {flask_app.name}")
    print(f"[OK] Debug mode: {flask_app.debug}")
    
    print("[SUCCESS] app.py startup test completed successfully!")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Startup error: {e}")
    sys.exit(1)