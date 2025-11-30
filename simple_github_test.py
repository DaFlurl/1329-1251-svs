#!/usr/bin/env python3
"""
Simple GitHub API Test
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("GitHub API Test")
    print("=" * 30)
    
    try:
        # Test imports
        from src.api.github_integration import GitHubIntegration
        from src.api.flask_api import FlaskAPI
        print("✓ Imports OK")
        
        # Test GitHub integration
        config = {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_REPO_OWNER': 'test_owner',
            'GITHUB_REPO_NAME': 'test_repo'
        }
        
        github = GitHubIntegration(config)
        print("✓ GitHub integration created")
        print(f"✓ Configured: {github._is_configured()}")
        
        # Test Flask API
        api = FlaskAPI()
        print("✓ Flask API created")
        
        # Test routes
        routes = [rule.rule for rule in api.app.url_map.iter_rules()]
        github_routes = [r for r in routes if '/github/' in r]
        
        print(f"✓ Found {len(github_routes)} GitHub routes:")
        for route in github_routes:
            print(f"  - {route}")
        
        print("/n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)