# AgentDaf1 Complete Setup Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### One-Command Setup
```bash
# Clone and setup
git clone <repository-url>
cd AgentDaf1.1
chmod +x scripts/*.sh
./scripts/start-dev.sh
```

### Windows Setup
```cmd
# Clone and setup
git clone <repository-url>
cd AgentDaf1.1
scripts\start-dev.bat
```

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Development](#development)
5. [Production Deployment](#production-deployment)
6. [Services](#services)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)
9. [API Documentation](#api-documentation)

## 🏗️ System Overview

AgentDaf1 is a comprehensive gaming dashboard system with the following components:

### Core Services
- **Main Application** (Port 8080) - Flask/FastAPI backend
- **API Gateway** (Port 8000) - Central API management
- **Data Service** (Port 8001) - Data processing and storage
- **Analytics Service** (Port 8002) - Analytics and reporting
- **WebSocket Service** (Port 8004) - Real-time communication
- **Web Frontend** (Port 3000) - React application
- **Static Website** (Port 8082) - HTML/CSS/JS dashboard

### Infrastructure
- **PostgreSQL** (Port 5432) - Primary database
- **Redis** (Port 6379) - Caching and sessions
- **RabbitMQ** (Port 5672/15672) - Message queuing
- **Nginx** (Port 80/443) - Load balancer and reverse proxy

### Monitoring Stack
- **Prometheus** (Port 9090) - Metrics collection
- **Grafana** (Port 3001) - Visualization and dashboards
- **Elasticsearch** (Port 9200) - Log storage and search
- **Kibana** (Port 5601) - Log visualization

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd AgentDaf1.1
```

### 2. Environment Setup
```bash
# Copy environment configuration
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Install Dependencies

#### Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

#### Node.js Dependencies
```bash
cd enterprise/web
npm install
cd ../..
```

### 4. Docker Setup
```bash
# Build and start containers
docker-compose up -d

# Or use the automated script
./scripts/deploy.sh development
```

## ⚙️ Configuration

### Environment Variables
Key configuration options in `.env`:

```bash
# Application
DEBUG=false
ENVIRONMENT=production
PORT=8080

# Database
DATABASE_URL=postgresql://agentdaf1:password@postgres:5432/agentdaf1
DB_PASSWORD=your_secure_password

# Security
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# External Services
GITHUB_TOKEN=your_github_token
GITHUB_REPO_OWNER=your_repo_owner
GITHUB_REPO_NAME=your_repo_name
```

### Database Setup
```bash
# Initialize database
docker-compose exec postgres psql -U agentdaf1 -d agentdaf1 -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# Run migrations (if using Alembic)
docker-compose exec agentdaf1-app python -m alembic upgrade head
```

## 🖥️ Development

### Start Development Environment
```bash
# Quick start
./scripts/start-dev.sh

# Or step by step
docker-compose -f docker-compose.yml up -d
source venv/bin/activate
python app.py
```

### VS Code Setup
1. Open project in VS Code
2. Install recommended extensions (`.vscode/extensions.json`)
3. Configure settings (`.vscode/settings.json`)
4. Use debug configurations (`.vscode/launch.json`)

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python -m pytest tests/test_api.py -v
```

### Code Quality
```bash
# Linting
flake8 src/ tests/

# Formatting
black src/ tests/

# Type checking
mypy src/
```

## 🚀 Production Deployment

### Automated Deployment
```bash
# Deploy to production
./scripts/deploy.sh production

# Update existing deployment
./scripts/deploy.sh update

# Check deployment status
./scripts/deploy.sh status
```

### Manual Deployment
```bash
# Build production images
docker-compose -f docker-compose.yml build --no-cache

# Start production services
docker-compose -f docker-compose.yml up -d

# Setup monitoring
./scripts/setup-monitoring.sh
./scripts/start-monitoring.sh
```

### SSL/HTTPS Setup
```bash
# Generate SSL certificates
certbot certonly --webroot -w /var/www/html -d yourdomain.com

# Update nginx configuration
cp nginx-production.conf nginx.conf
docker-compose restart nginx
```

## 📊 Services

### Main Application (Port 8080)
- **Flask API**: RESTful API endpoints
- **File Upload**: Excel file processing
- **Authentication**: JWT-based auth system
- **Dashboard**: Gaming data visualization

### API Gateway (Port 8000)
- **Route Management**: Request routing
- **Load Balancing**: Service distribution
- **Rate Limiting**: Request throttling
- **CORS**: Cross-origin handling

### Data Service (Port 8001)
- **CRUD Operations**: Data management
- **Excel Processing**: File parsing
- **Data Validation**: Quality checks
- **Storage**: Database operations

### Analytics Service (Port 8002)
- **Statistics**: Data analysis
- **Reporting**: Report generation
- **Metrics**: Performance tracking
- **Insights**: Business intelligence

### WebSocket Service (Port 8004)
- **Real-time Updates**: Live data sync
- **Notifications**: Event broadcasting
- **Chat**: Communication system
- **Collaboration**: Multi-user features

## 📈 Monitoring

### Access Monitoring Tools
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

### Key Metrics
- **System Health**: Service uptime and status
- **Performance**: Response times and throughput
- **Resources**: CPU, memory, disk usage
- **Application**: Custom business metrics

### Alerting
- **Service Down**: Immediate notifications
- **High Resource Usage**: Warning thresholds
- **Error Rates**: Anomaly detection
- **Custom Alerts**: Business rules

### Log Management
- **Centralized Logging**: All service logs
- **Log Rotation**: Automatic cleanup
- **Search & Filter**: Log analysis
- **Alerting**: Error notifications

## 🔧 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Check Docker status
docker info
docker-compose ps

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service-name]

# Clean up
docker system prune -f
```

#### Database Issues
```bash
# Check database connection
docker-compose exec postgres psql -U agentdaf1 -d agentdaf1 -c "SELECT 1;"

# Reset database
docker-compose down
docker volume rm agentdaf1_postgres_data
docker-compose up -d postgres
```

#### Application Issues
```bash
# Check application logs
tail -f logs/app.log

# Restart application
docker-compose restart agentdaf1-app

# Debug mode
DEBUG=true python app.py
```

### Performance Issues
1. **Check Resource Usage**: `docker stats`
2. **Monitor Database**: Slow query analysis
3. **Review Logs**: Error patterns
4. **Scale Services**: Load balancing

### Network Issues
1. **Check Ports**: `netstat -tulpn`
2. **Firewall Rules**: `ufw status`
3. **DNS Resolution**: `nslookup`
4. **Service Connectivity**: `curl` tests

## 📚 API Documentation

### Authentication
```bash
# Login
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Get token
Authorization: Bearer <jwt_token>
```

### Main Endpoints

#### Players
```bash
GET    /api/players          # List players
POST   /api/players          # Create player
GET    /api/players/{id}     # Get player
PUT    /api/players/{id}     # Update player
DELETE /api/players/{id}     # Delete player
```

#### Alliances
```bash
GET    /api/alliances        # List alliances
POST   /api/alliances        # Create alliance
GET    /api/alliances/{id}   # Get alliance
PUT    /api/alliances/{id}   # Update alliance
DELETE /api/alliances/{id}   # Delete alliance
```

#### Files
```bash
POST   /api/upload           # Upload file
GET    /api/files/{id}       # Download file
GET    /api/files            # List files
DELETE /api/files/{id}       # Delete file
```

### WebSocket Events
```javascript
// Connect
const ws = new WebSocket('ws://localhost:8004/ws');

// Events
ws.on('player_update', (data) => { /* handle */ });
ws.on('alliance_update', (data) => { /* handle */ });
ws.on('system_notification', (data) => { /* handle */ });
```

## 🛡️ Security

### Best Practices
1. **Change Default Passwords**: Update all default credentials
2. **Use HTTPS**: SSL/TLS encryption
3. **Environment Variables**: Secure configuration
4. **Regular Updates**: Keep dependencies current
5. **Access Control**: Principle of least privilege

### Security Headers
- **HSTS**: HTTPS enforcement
- **CSP**: Content Security Policy
- **XSS Protection**: Cross-site scripting prevention
- **Frame Options**: Clickjacking protection

## 📝 Scripts Reference

### Development Scripts
- `start-dev.sh` - Start development environment
- `stop-dev.sh` - Stop development environment
- `setup-monitoring.sh` - Setup monitoring stack

### Deployment Scripts
- `deploy.sh` - Production deployment
- `deploy.bat` - Windows deployment
- `start-monitoring.sh` - Start monitoring

### Utility Scripts
- `backup.sh` - Create backups
- `restore.sh` - Restore from backup
- `cleanup.sh` - System cleanup

## 🤝 Contributing

1. **Fork Repository**: Create your fork
2. **Create Branch**: `git checkout -b feature/name`
3. **Make Changes**: Implement your feature
4. **Run Tests**: Ensure all tests pass
5. **Submit PR**: Create pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- **Documentation**: This guide
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@agentdaf1.com

---

## 🎯 Quick Reference

### URLs
- **Main App**: http://localhost:8080
- **API Gateway**: http://localhost:8000
- **Website**: http://localhost:8082
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

### Commands
```bash
# Start everything
./scripts/start-dev.sh

# Deploy production
./scripts/deploy.sh production

# Check status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs
```

### Default Credentials
- **Admin**: admin / admin123
- **User**: user / user123
- **Database**: agentdaf1 / password
- **Grafana**: admin / admin
- **RabbitMQ**: admin / admin123

---

*Last updated: November 2025*