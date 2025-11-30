#!/usr/bin/env python3
"""
Test src/main.py startup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("[TEST] Testing src/main.py import...")
    from src.main import main
    print("[OK] src/main.py import successful")
    
    print("[TEST] Testing main function availability...")
    if callable(main):
        print("[OK] main function is callable")
    else:
        print("[ERROR] main is not callable")
        sys.exit(1)
    
    print("[SUCCESS] src/main.py startup test completed successfully!")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Startup error: {e}")
    sys.exit(1)