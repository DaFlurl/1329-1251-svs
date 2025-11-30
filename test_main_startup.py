#!/usr/bin/env python3
"""
Test script to verify AgentDaf1.1 main.py startup
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_main_startup():
    """Test if the main.py can start properly"""
    print("Testing AgentDaf1.1 main.py startup...")
    
    try:
        # Import main
        from src.main import main
        print("+ Main module imported successfully")
        
        # Test that we can access the function
        print("+ Main function is accessible")
        
        # Test configuration imports
        from src.config.settings import Config
        print(f"+ Configuration loaded: DEBUG={Config.DEBUG}")
        
        print("+ Main.py is ready to run!")
        return True
        
    except Exception as e:
        print(f"- Error during main test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_startup()
    sys.exit(0 if success else 1)