# AgentDaf1.1 Development Guide

## Development Environment Setup

### Prerequisites
- Python 3.8+ (recommended: 3.14.0)
- Git
- Code editor (VS Code recommended)
- Docker (optional, for containerized development)

### Initial Setup

#### 1. Clone Repository
```bash
git clone <repository-url> AgentDaf1.1
cd AgentDaf1.1
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
# Basic dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Enterprise dependencies (optional)
pip install -r requirements-production.txt
```

#### 4. Development Tools
```bash
# Install development tools
pip install pytest black flake8 mypy pre-commit

# Set up pre-commit hooks
pre-commit install
```

## Project Structure

### Core Architecture
```
AgentDaf1.1/
├── stable_base.py              # Production-ready main system
├── simple_app.py              # Modern alternative dashboard
├── src/                       # Modular architecture
│   ├── main.py               # Main application entry point
│   ├── api/                  # REST API layer
│   ├── core/                 # Business logic
│   ├── tools/                # Utilities & AI tools
│   ├── config/               # Configuration
│   └── web/                  # Web interface components
├── enterprise/                # Microservices architecture
├── tests/                    # Test suite
├── docs/                     # Documentation
└── tools/                    # Development tools
```

### Module Responsibilities

#### 1. API Layer (`src/api/`)
- **flask_api.py**: Main Flask API implementation
- **enhanced_flask_api.py**: Advanced API with caching
- **github_integration.py**: GitHub API integration

#### 2. Core Logic (`src/core/`)
- **excel_processor.py**: Excel file processing
- **dashboard_generator.py**: HTML dashboard generation

#### 3. Tools (`src/tools/`)
- **memory_manager.py**: AI-powered memory management
- **task_manager.py**: Task scheduling and management
- **performance_monitor.py**: System performance monitoring
- **file_manager.py**: File operations and management
- **logger.py**: Logging utilities
- **security.py**: Security utilities

#### 4. Configuration (`src/config/`)
- **settings.py**: Application configuration
- **logging.py**: Logging configuration

## Development Workflow

### 1. Feature Development

#### Creating New Features
1. **Create Feature Branch**
```bash
git checkout -b feature/new-feature-name
```

2. **Implement Feature**
```python
# Example: New API endpoint
@app.route('/api/new-feature', methods=['GET'])
def new_feature():
    try:
        # Implementation logic
        data = get_feature_data()
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

3. **Add Tests**
```python
# tests/test_new_feature.py
def test_new_feature():
    response = client.get('/api/new-feature')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
```

4. **Update Documentation**
- Add API endpoint to API_REFERENCE.md
- Update user manual if needed
- Document configuration changes

### 2. Code Standards

#### Python Code Style
```python
# Use Black for formatting
black src/ tests/

# Use flake8 for linting
flake8 src/ tests/

# Use mypy for type checking
mypy src/
```

#### Code Structure Guidelines
```python
# Import order: standard library, third-party, local
import os
import sys
from typing import Dict, List, Optional

import flask
import pandas as pd

from src.core.excel_processor import ExcelProcessor
from src.config.settings import Config

class NewFeature:
    """Class docstring following Google style."""
    
    def __init__(self, config: Config) -> None:
        """Initialize new feature."""
        self.config = config
        self.data: List[Dict] = []
    
    def process_data(self, input_data: Dict) -> Optional[Dict]:
        """Process input data and return results.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Processed data dictionary or None if error
            
        Raises:
            ValueError: If input data is invalid
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        # Implementation
        return processed_data
```

### 3. Testing

#### Test Structure
```
tests/
├── test_suite.py           # Main test suite
├── test_api.py             # API tests
├── test_core.py            # Core logic tests
├── test_tools.py           # Tools tests
└── test_integration.py     # Integration tests
```

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

#### Writing Tests
```python
import pytest
from src.api.flask_api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert 'status' in response.json

def test_data_endpoint(client):
    """Test data endpoint."""
    response = client.get('/api/data')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
```

### 4. Database Development

#### Database Schema
```python
# Example: Database table creation
def create_players_table():
    """Create players table."""
    conn = sqlite3.connect('agentdaf1.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            alliance TEXT,
            rank INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
```

#### Database Operations
```python
class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self, db_path: str = 'agentdaf1.db'):
        self.db_path = db_path
    
    def get_players(self, limit: int = 100) -> List[Dict]:
        """Get players with optional limit."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM players ORDER BY score DESC LIMIT ?',
            (limit,)
        )
        
        players = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return players
```

### 5. API Development

#### REST API Guidelines
```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

def require_auth(f):
    """Authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not validate_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/players', methods=['GET'])
@require_auth
def get_players():
    """Get players endpoint."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        players = get_players_paginated(page, limit)
        
        return jsonify({
            'status': 'success',
            'data': players,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': len(players)
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

### 6. Frontend Development

#### HTML Templates
```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentDaf1.1 Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">AgentDaf1.1</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div id="dashboard-content">
            <!-- Dynamic content loaded here -->
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/dashboard.js"></script>
</body>
</html>
```

#### JavaScript Integration
```javascript
// static/js/dashboard.js
class Dashboard {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
        this.init();
    }
    
    init() {
        this.loadDashboard();
        this.startAutoRefresh();
    }
    
    async loadDashboard() {
        try {
            const response = await fetch('/api/data');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderDashboard(data.data);
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }
    
    renderDashboard(data) {
        // Render dashboard content
        const container = document.getElementById('dashboard-content');
        container.innerHTML = this.generateDashboardHTML(data);
    }
    
    startAutoRefresh() {
        setInterval(() => {
            this.loadDashboard();
        }, this.refreshInterval);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
```

## Configuration Management

### Environment Variables
```bash
# .env.example
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
PORT=8080
HOST=0.0.0.0

# Database
DATABASE_URL=sqlite:///agentdaf1.db

# Redis (optional)
REDIS_URL=redis://localhost:6379

# GitHub (optional)
GITHUB_TOKEN=your-github-token
GITHUB_REPO=your-repo-name
```

### Configuration Classes
```python
# src/config/settings.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class DatabaseConfig:
    url: str = os.getenv('DATABASE_URL', 'sqlite:///agentdaf1.db')
    echo: bool = False

@dataclass
class RedisConfig:
    url: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    decode_responses: bool = True

@dataclass
class AppConfig:
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    port: int = int(os.getenv('PORT', 8080))
    host: str = os.getenv('HOST', '0.0.0.0')
    secret_key: str = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    database: DatabaseConfig = DatabaseConfig()
    redis: Optional[RedisConfig] = None
```

## Performance Optimization

### Caching Strategy
```python
from functools import lru_cache
import redis

# Redis caching
redis_client = redis.Redis.from_url('redis://localhost:6379')

def cache_key(prefix: str, *args) -> str:
    """Generate cache key."""
    return f"{prefix}:{':'.join(map(str, args))}"

def get_cached_data(key: str, ttl: int = 300):
    """Get cached data with decorator."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = cache_key(key, *args, **kwargs)
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@get_cached_data('players', ttl=60)
def get_players():
    """Get players with caching."""
    # Database query
    return players_data
```

### Database Optimization
```python
# Use connection pooling
import sqlite3
from contextlib import contextmanager

class DatabasePool:
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

# Use transactions for batch operations
def batch_insert_players(players: List[Dict]):
    """Batch insert players with transaction."""
    conn = sqlite3.connect('agentdaf1.db')
    cursor = conn.cursor()
    
    try:
        conn.execute('BEGIN TRANSACTION')
        
        cursor.executemany(
            'INSERT INTO players (name, score, alliance) VALUES (?, ?, ?)',
            [(p['name'], p['score'], p.get('alliance')) for p in players]
        )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
```

## Security Best Practices

### Input Validation
```python
from werkzeug.utils import secure_filename
import re

def validate_filename(filename: str) -> bool:
    """Validate uploaded filename."""
    if not filename:
        return False
    
    # Check extension
    allowed_extensions = {'xlsx', 'xls'}
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False
    
    # Secure filename
    secure_name = secure_filename(filename)
    return secure_name == filename or bool(secure_name)

def sanitize_input(data: str) -> str:
    """Sanitize user input."""
    # Remove HTML tags
    data = re.sub(r'<[^>]+>', '', data)
    # Remove special characters
    data = re.sub(r'[^\w\s-]', '', data)
    return data.strip()
```

### Authentication & Authorization
```python
import jwt
from datetime import datetime, timedelta
from functools import wraps

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self, user_id: int, expires_in: int = 3600) -> str:
        """Generate JWT token."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Token has expired')
        except jwt.InvalidTokenError:
            raise Exception('Invalid token')

def require_auth(f):
    """Authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is required'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            payload = auth_manager.verify_token(token)
            request.current_user = payload
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated
```

## Deployment

### Development Deployment
```bash
# Run development server
python stable_base.py

# Or with Flask CLI
export FLASK_APP=stable_base.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8080
```

### Production Deployment
```bash
# Use Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 stable_base:app

# Or with Docker
docker build -t agentdaf1 .
docker run -p 8080:8080 agentdaf1
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "stable_base:app"]
```

## Debugging

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Setup application logging."""
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/agentdaf1.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AgentDaf1.1 startup')
```

### Debug Tools
```python
# Debug middleware
@app.before_request
def before_request():
    """Log request information."""
    app.logger.debug(f'Request: {request.method} {request.url}')
    app.logger.debug(f'Headers: {dict(request.headers)}')

@app.after_request
def after_request(response):
    """Log response information."""
    app.logger.debug(f'Response: {response.status_code}')
    return response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'Internal server error'}), 500
```

## Contributing Guidelines

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Ensure all tests pass
4. Update documentation
5. Submit pull request with description

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Error handling implemented

---

**Development Guide Version**: 1.0  
**Last Updated**: November 27, 2025  
**For AgentDaf1.1 v1.1.0**