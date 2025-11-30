# AgentDaf1.1 Deployment Guide

## Deployment Options

### 1. Standalone Development Deployment
**Best for**: Development, testing, small-scale production

#### Quick Start
```bash
# Install dependencies
pip install flask flask-cors pandas openpyxl

# Run application
python stable_base.py

# Access at: http://localhost:8080
```

#### Production Configuration
```bash
# Set production environment
export FLASK_ENV=production
export DEBUG=False
export SECRET_KEY=your-production-secret-key

# Run with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 stable_base:app
```

### 2. Docker Deployment
**Best for**: Production, scaling, containerized environments

#### Basic Docker Deployment
```bash
# Build image
docker build -t agentdaf1 .

# Run container
docker run -d \
  --name agentdaf1 \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  agentdaf1
```

#### Docker Compose Deployment
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Enterprise Deployment
**Best for**: Large-scale production, high availability

#### Enterprise Services
```bash
# Deploy enterprise stack
docker-compose -f docker-compose.enterprise.yml up -d

# Services included:
# - API Gateway (FastAPI)
# - Application Server (Flask)
# - Redis Cache
# - Prometheus Monitoring
# - Nginx Reverse Proxy
# - PostgreSQL Database
```

## Environment Configuration

### Environment Variables
```bash
# Core Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secure-secret-key-here
PORT=8080
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=sqlite:///agentdaf1.db
# For PostgreSQL: postgresql://user:pass@localhost/dbname

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=/app/data/uploads

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/agentdaf1.log

# GitHub Integration (optional)
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_REPO=username/repository-name

# Monitoring Configuration
PROMETHEUS_ENABLED=True
PROMETHEUS_PORT=9090
```

### Configuration Files

#### .env Example
```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

#### config/production.py
```python
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///agentdaf1.db')
    SECRET_KEY = os.getenv('SECRET_KEY')
    REDIS_URL = os.getenv('REDIS_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
```

## Web Server Configuration

### Nginx Configuration

#### Basic Nginx Setup
```nginx
# /etc/nginx/sites-available/agentdaf1
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Proxy to Application
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static Files
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # File Uploads
    location /api/upload {
        client_max_body_size 16M;
        proxy_pass http://127.0.0.1:8080;
    }
}
```

#### Enable Site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/agentdaf1 /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Gunicorn Configuration

#### gunicorn.conf.py
```python
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "agentdaf1"

# Server mechanics
daemon = False
pidfile = "/app/run/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = "/tmp"

# SSL (if using HTTPS with Gunicorn)
# keyfile = "/path/to/ssl/private.key"
# certfile = "/path/to/ssl/cert.pem"
```

#### Start Gunicorn
```bash
# Create directories
mkdir -p logs run

# Set permissions
chown www-data:www-data logs run

# Start with configuration
gunicorn -c gunicorn.conf.py stable_base:app

# Or with systemd
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## Database Setup

### SQLite (Default)
```bash
# Database is created automatically
# Location: /app/data/agentdaf1.db

# Backup database
cp data/agentdaf1.db backups/agentdaf1_$(date +%Y%m%d_%H%M%S).db

# Restore database
cp backups/agentdaf1_backup.db data/agentdaf1.db
```

### PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE agentdaf1;
CREATE USER agentdaf1_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE agentdaf1 TO agentdaf1_user;
\q

# Update configuration
export DATABASE_URL="postgresql://agentdaf1_user:secure_password@localhost/agentdaf1"

# Run migrations (if using Alembic)
flask db upgrade
```

### Redis (Caching)
```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set password: requirepass your_redis_password
# Bind to localhost: bind 127.0.0.1

# Restart Redis
sudo systemctl restart redis-server

# Test connection
redis-cli ping
```

## SSL/TLS Configuration

### Let's Encrypt (Free SSL)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Configuration
```bash
# Generate private key
openssl genrsa -out private.key 2048

# Generate certificate signing request
openssl req -new -key private.key -out certificate.csr

# Generate self-signed certificate (for development)
openssl x509 -req -days 365 -in certificate.csr -signkey private.key -out certificate.crt

# Secure files
sudo chmod 600 private.key
sudo chmod 644 certificate.crt
```

## Monitoring and Logging

### Application Logging
```python
# Configure logging in production
import logging
from logging.handlers import RotatingFileHandler

def setup_production_logging(app):
    """Setup production logging."""
    if not app.debug:
        # File handler
        file_handler = RotatingFileHandler(
            '/app/logs/agentdaf1.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Error handler
        error_handler = RotatingFileHandler(
            '/app/logs/agentdaf1_errors.log',
            maxBytes=10240000,
            backupCount=10
        )
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('AgentDaf1.1 production startup')
```

### System Monitoring with Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'agentdaf1'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

### Health Checks
```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db_status = check_database_connection()
        
        # Check Redis connection (if configured)
        redis_status = check_redis_connection()
        
        # Check disk space
        disk_status = check_disk_space()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.1.0',
            'checks': {
                'database': db_status,
                'redis': redis_status,
                'disk': disk_status
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

## Security Hardening

### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application port (if not behind reverse proxy)
sudo ufw allow 8080/tcp

# Check status
sudo ufw status
```

### Application Security
```python
# Security headers middleware
@app.after_request
def security_headers(response):
    """Add security headers to responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/upload')
@limiter.limit("10 per minute")
def upload_file():
    """Upload endpoint with rate limiting."""
    pass
```

## Backup and Recovery

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/app/data/agentdaf1.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $DB_FILE $BACKUP_DIR/agentdaf1_$DATE.db

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /app/.env /app/config/

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/agentdaf1_$DATE.db s3://your-backup-bucket/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Schedule Backups
```bash
# Add to crontab
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /app/scripts/backup.sh >> /app/logs/backup.log 2>&1

# Weekly backup on Sunday at 3 AM
0 3 * * 0 /app/scripts/weekly_backup.sh >> /app/logs/backup.log 2>&1
```

## Performance Optimization

### Caching Strategy
```python
# Redis caching implementation
import redis
import json
from functools import wraps

redis_client = redis.Redis.from_url(os.getenv('REDIS_URL'))

def cache_result(expiration=300):
    """Cache decorator for expensive operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=60)
def get_dashboard_data():
    """Get dashboard data with caching."""
    # Expensive database query
    return dashboard_data
```

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_players_score ON players(score DESC);
CREATE INDEX idx_players_alliance ON players(alliance);
CREATE INDEX idx_alliances_name ON alliances(name);

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM players ORDER BY score DESC LIMIT 100;
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check logs
tail -f /app/logs/agentdaf1.log
tail -f /app/logs/gunicorn_error.log

# Check port usage
sudo netstat -tulpn | grep :8080

# Check permissions
ls -la /app/data/
ls -la /app/logs/
```

#### 2. Database Connection Issues
```bash
# Test database connection
sqlite3 /app/data/agentdaf1.db ".tables"

# Check database integrity
sqlite3 /app/data/agentdaf1.db "PRAGMA integrity_check;"

# Repair database (if corrupted)
sqlite3 /app/data/agentdaf1.db ".recover" | sqlite3 /app/data/agentdaf1_repaired.db
```

#### 3. High Memory Usage
```bash
# Monitor memory usage
ps aux | grep gunicorn
top -p $(pgrep -f gunicorn)

# Restart workers if needed
sudo systemctl reload gunicorn
```

### Performance Monitoring
```bash
# Monitor system resources
htop
iotop
nethogs

# Monitor application performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/api/health

# Monitor database performance
sqlite3 /app/data/agentdaf1.db "EXPLAIN QUERY PLAN SELECT * FROM players ORDER BY score DESC LIMIT 100;"
```

---

**Deployment Guide Version**: 1.0  
**Last Updated**: November 27, 2025  
**For AgentDaf1.1 v1.1.0**