#!/usr/bin/env python3
"""
AgentDaf1.1 Production WSGI Entry Point
For use with Gunicorn in production environment
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Production environment setup
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONPATH', str(project_root))

# Import the Flask app
from src.api.flask_api import create_app
app = create_app()

# Production configuration
app.config['DEBUG'] = True
app.config['TESTING'] = True

if __name__ == "__main__":
    app.run()