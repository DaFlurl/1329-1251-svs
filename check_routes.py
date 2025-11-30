#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.api.flask_api import FlaskAPI

def main():
    api = FlaskAPI()
    logger.info("Available Flask API Routes:")
    logger.info("=" * 40)
    
    for rule in api.app.url_map.iter_rules():
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
        logger.info(f"{rule.rule:<30} {methods}")

if __name__ == "__main__":
    main()