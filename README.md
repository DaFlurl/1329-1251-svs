# AgentDaf1.1 - Excel Dashboard System

A comprehensive dashboard system for processing and visualizing Excel game scoreboards with web-based interface and GitHub integration.

## 🚀 Features

### Core Capabilities
- **📊 Excel Processing**: Advanced parsing and analysis of complex spreadsheets with game data
- **🎯 Dynamic Dashboard Generation**: AI-powered HTML dashboards with multiple tabs and interactive charts
- **📈 Data Visualization**: Interactive charts, graphs, and tables with real-time updates
- **🔄 Real-time Updates**: WebSocket communication for live data synchronization and notifications
- **🌐 GitHub Integration**: Direct file updates through GitHub API with commit tracking
- **🌍 Multi-language Support**: English interface with German data compatibility (Ümlaute, etc.)
- **🔒 Enterprise Security**: JWT authentication with role-based access control and API key management
- **⚡ Performance Monitoring**: Built-in system metrics, health checks, and performance profiling
- **🛠️ Auto-Repair**: Self-healing capabilities for common data issues and format problems
- **🤖 AI Tools**: Smart data analysis, pattern detection, and automated insights generation

### Advanced Features
- **💾 Memory Management**: Working, episodic, and semantic memory systems for intelligent data processing
- **📋 Task Management**: Async task scheduling and execution with progress tracking
- **🐳 Docker Support**: Full containerization with multi-environment deployment
- **📊 Analytics**: Comprehensive data analysis, reporting, and export capabilities
- **🔧 Config Management**: YAML-based configuration with environment-specific settings
- **🧪 Testing**: Built-in test framework with automated test generation

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│   HTML/CSS/JS   │
│   Dashboard UI    │
├─────────────────┤
│                 │
│   WebSocket API   │
│   Real-time     │
│   Updates        │
├─────────────────┤
│                 │
│   Flask Backend  │
│   REST API      │
│   Authentication  │
│   Excel Processing│
│   GitHub Integration│
├─────────────────┤
│                 │
│   AI Tools      │
│   Analysis       │
│   Test Gen       │
│   Performance    │
├─────────────────┤
│                 │
│   Database       │
│   SQLite         │
│   Memory Mgmt    │
│   Task Queue     │
├─────────────────┤
│                 │
│   File System    │
│   Excel Files    │
│   Config Mgmt    │
│   Docker Volumes │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - Core engine requirement
- **Docker & Docker Compose** - For containerized deployment
- **4GB+ RAM** - Recommended for smooth operation
- **Modern web browser** - For dashboard interface

### Installation & Setup

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/agentdaf1.1.git
cd agentdaf1.1
```

#### 2. Environment Configuration
```bash
# Copy the environment template and configure
cp config/app_config.yaml.example config/app_config.yaml
cp config/logging_config.yaml.example config/logging_config.yaml

# Edit with your specific settings
nano config/app_config.yaml
```

#### 3. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

#### 4. Initialize Database
```bash
# Create data directory and initialize SQLite database
python -c "from src.core.database import init_database; init_database()"
```

#### 5. Start Application
```bash
# Development mode
python src/main.py --debug

# Production mode
python src/main.py --production
```

#### 6. Access Dashboard
- **Development**: http://localhost:8080
- **Production**: https://your-domain.com

### Docker Deployment

#### Development Environment
```bash
# Build and run with hot reload
docker-compose up --build
```

#### Production Environment
```bash
# Build optimized image
docker build -t agentdaf1.1:latest .

# Deploy with production configuration
docker-compose -f docker-compose.production.yml up -d
```

## 📖 Usage Guide

### Excel Data Processing
1. **Upload Files**: Drag & drop Excel files or use API upload
2. **Configure Analysis**: Set processing parameters, analysis rules, and visualization options
3. **Generate Dashboard**: Automatic creation of interactive HTML dashboards
4. **Real-time Updates**: Live data synchronization through WebSocket connections

### API Integration
```bash
# Upload Excel file for processing
curl -X POST -F "file=@game_data.xlsx" \
  -F "config={'auto_generate_dashboard': true, 'analysis_type': 'sports'}" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  http://localhost:8080/api/upload

# List all dashboards
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  http://localhost:8080/api/dashboards

# Get dashboard details
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  http://localhost:8080/api/dashboards/123
```

### WebSocket Real-time Communication
```javascript
// Connect to WebSocket for live updates
const ws = new WebSocket('ws://localhost:8080/ws');

// Authenticate with JWT token
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'YOUR_JWT_TOKEN'
  }));
};

// Handle real-time data updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'dashboard_update':
      updateDashboardUI(data.dashboard);
      break;
    case 'data_processed':
      showProcessingComplete(data.results);
      break;
    case 'new_file_uploaded':
      handleNewFile(data.fileInfo);
      break;
    case 'system_alert':
      handleSystemAlert(data.alert);
      break;
  }
};

function updateDashboardUI(dashboardData) {
  // Update your dashboard UI with new data
  console.log('Dashboard updated:', dashboardData);
}

function showProcessingComplete(results) {
  // Show notification when processing is complete
  alert('Data processing complete!', 'success');
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=false
HOST=0.0.0.0
PORT=8080
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=sqlite:///data/agentdaf1.db
BACKUP_ENABLED=true
BACKUP_INTERVAL=3600

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
TOKEN_EXPIRY=3600
BCRYPT_ROUNDS=12

# GitHub Integration
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_REPO=yourusername/your-repo
GITHUB_AUTO_COMMIT=true

# Performance Configuration
MAX_FILE_SIZE=100MB
CACHE_TTL=300
WORKER_THREADS=4

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=logs/agentdaf1.log
```

### Configuration Files

#### Application Config (`config/app_config.yaml`)
```yaml
app:
  name: "AgentDaf1.1"
  version: "1.0.0"
  debug: false
  host: "0.0.0.0"
  port: 8080
  
database:
  type: "sqlite"
  url: "sqlite:///data/agentdaf1.db"
  backup_enabled: true
  backup_interval: 3600
  
security:
  jwt_secret_key: "${JWT_SECRET_KEY}"
  token_expiry: 3600
  bcrypt_rounds: 12
  
github:
  token: "${GITHUB_TOKEN}"
  repo: "${GITHUB_REPO}"
  auto_commit: true
  branch: "main"
  
performance:
  max_file_size: "100MB"
  cache_ttl: 300
  worker_threads: 4
  
logging:
  level: "INFO"
  format: "json"
  file_path: "logs/agentdaf1.log"
```

#### Logging Config (`config/logging_config.yaml`)
```yaml
logging:
  handlers:
    console:
      level: "DEBUG"
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file:
      level: "INFO"
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      filename: "logs/agentdaf1.log"
      max_bytes: 10485760  # 10MB
      backup_count: 5
  
  loggers:
    app:
      level: "DEBUG"
      handlers: ["console", "file"]
    database:
      level: "WARNING"
      handlers: ["file"]
    security:
      level: "INFO"
      handlers: ["console", "file"]
```

## 🐳 Docker Deployment

### Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG}
      - DATABASE_URL=sqlite:///data/agentdaf1.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### Production Environment
```yaml
# docker-compose.production.yml
version: '3.8'
services:
  app:
    image: agentdaf1.1:latest
    ports:
      - "80:8080"
      - "443:443"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=sqlite:///data/agentdaf1.db
      - NGINX_HOST=nginx
    volumes:
      - agentdaf1_data:/app/data
      - agentdaf1_logs:/app/logs
      - agentdaf1_uploads:/app/uploads
      - ssl_certs:/etc/nginx/ssl
    restart: unless-stopped
    depends_on:
      - nginx
      - redis
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
      
  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

## 🔐 Security

### Authentication Flow
1. **User Registration**: Email/password with bcrypt hashing
2. **JWT Login**: Token-based authentication with configurable expiration
3. **Role Management**: Admin, User, Analyst roles with fine-grained permissions
4. **Session Management**: Secure token refresh with automatic cleanup

### API Security Features
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Rate Limiting**: Request throttling and DDoS protection
- **Input Validation**: Comprehensive data sanitization and validation
- **SQL Injection Prevention**: Parameterized queries with proper escaping
- **HTTPS Support**: SSL/TLS encryption for production environments

## 📊 API Documentation

### Authentication Endpoints
```http
# User Registration
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "role": "analyst"
}

# User Login
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response:
{
  "token": "eyJ0eXA4...",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "role": "analyst"
  }
}

# Token Refresh
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "old_expired_token"
}

# Get Current User
GET /api/auth/me
Authorization: Bearer YOUR_TOKEN
```

### Data Processing Endpoints
```http
# Upload Excel File
POST /api/upload
Content-Type: multipart/form-data

curl -X POST -F "file=@data.xlsx" \
  -F "config={'analysis_type': 'financial', 'auto_generate_dashboard': true}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/api/upload

Response:
{
  "upload_id": "uuid-123",
  "status": "processing",
  "message": "File uploaded successfully for processing"
}
```

### Dashboard Management
```http
# List All Dashboards
GET /api/dashboards
Authorization: Bearer YOUR_TOKEN

Response:
[
  {
    "id": "dash_001",
    "title": "Game Scores Dashboard",
    "created_at": "2024-01-15T10:30:00Z",
    "tabs": ["overview", "detailed_stats", "trends"]
  }
]
```

### WebSocket API
```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8080/ws');

// Authentication handshake
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'YOUR_JWT_TOKEN'
  }));
};

// Handle real-time data updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'dashboard_update':
      updateDashboardUI(data.dashboard);
      break;
    case 'processing_complete':
      showCompletionNotification(data.results);
      break;
    case 'new_file_uploaded':
      handleNewFileUpload(data.fileInfo);
      break;
    case 'system_alert':
      handleSystemAlert(data.alert);
      break;
  }
};
```

## 🧪 Development

### Project Structure
```
AgentDaf1.1/
├── src/
│   ├── main.py              # Main application entry point
│   ├── excel_workflow.py     # Core Excel processing engine
│   ├── excel_tools.py       # Excel utilities and helpers
│   ├── github_integration.py # GitHub API integration
│   ├── dashboard_generator.py # HTML dashboard generator
│   ├── config/
│   │   ├── settings.py      # Application configuration
│   │   └── logging.py       # Logging configuration
│   └── core/
│       ├── database.py        # Database operations
│       └── memory.py          # Memory management
├── data/                        # Application data directory
├── logs/                         # Application logs
├── uploads/                      # Temporary file storage
├── docs/                         # Documentation
│   ├── user_manual.md       # User documentation
│   └── api_reference.md     # API documentation
├── tests/                        # Test suites
├── config/                       # Configuration files
│   ├── app_config.yaml      # Application settings
│   └── logging_config.yaml   # Logging configuration
├── requirements.txt               # Python dependencies
├── Dockerfile                   # Docker configuration
└── docker-compose.yml            # Docker Compose setup
```

### Setting Up Development Environment
```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python -c "from src.core.database import init_database; init_database()"

# 4. Start development server
python src/main.py --debug
```

### Code Standards & Best Practices
- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Use comprehensive type annotations
- **Error Handling**: Implement comprehensive try-catch blocks
- **Logging**: Add structured logging for debugging
- **Testing**: Write unit tests for all new features
- **Security**: Follow OWASP security guidelines
- **Documentation**: Update API docs for all changes

## 🚀 Deployment

### Production Deployment
```bash
# 1. Build optimized Docker image
docker build -t agentdaf1.1:latest .

# 2. Deploy to production
docker-compose -f docker-compose.production.yml up -d

# 3. Health check
curl -f http://localhost:8080/api/health

# 4. View logs
docker-compose logs -f app
```

### Environment-Specific Deployment
```bash
# Development
export DEBUG=True
export LOG_LEVEL=DEBUG

# Staging
export DEBUG=False
export LOG_LEVEL=INFO

# Production
export DEBUG=False
export LOG_LEVEL=WARNING
```

## 📈 Monitoring & Performance

### System Health
```bash
# Application health check
curl http://localhost:8080/api/health

# System metrics
curl http://localhost:8080/api/stats

# Performance monitoring
curl http://localhost:8080/api/performance
```

### Log Management
```bash
# Real-time log monitoring
tail -f logs/agentdaf1.log

# Error monitoring
grep ERROR logs/agentdaf1.log | tail -f
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### **Database Connection Issues**
```bash
# Check database file permissions
ls -la data/agentdaf1.db

# Recreate database if needed
python -c "from src.core.database import init_database; init_database(force=True)"
```

#### **Docker Container Issues**
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs app

# Restart services
docker-compose restart app

# Clean up resources
docker-compose down -v
docker system prune -f
```

#### **Performance Optimization**
```bash
# Monitor resource usage
docker stats

# Profile application
python -m cProfile src/main.py

# Optimize database queries
python tools/db_optimizer.py
```

#### **Authentication Issues**
```bash
# Test JWT token validity
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/api/auth/me

# Refresh expired token
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "old_token"}' \
  http://localhost:8080/api/auth/refresh
```

## 🤝 Contributing

### Development Workflow
1. **Fork Repository**: Clone and create your own branch
2. **Feature Development**: Create feature branches from main
3. **Code Standards**: Follow PEP 8 and project conventions
4. **Testing**: Comprehensive test coverage with pytest
5. **Documentation**: Keep docs updated with API changes
6. **Pull Request**: Submit changes with clear descriptions

### Code Quality Standards
- **Python**: PEP 8 compliance with type hints
- **JavaScript**: ES6+ features with proper linting
- **Testing**: Minimum 80% test coverage required
- **Security**: OWASP guidelines implementation

### Commit Message Format
- `feat: add new feature` - New functionality
- `fix: resolve issue` - Bug fixes
- `docs: update documentation` - Documentation updates
- `refactor: improve performance` - Code improvements

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for complete details.

## 📞 Support & Contact

### Getting Help
- **Documentation**: Check the [docs/](docs/) directory for comprehensive guides
- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/agentdaf1.1/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/yourusername/agentdaf1.1/discussions) for questions

### Contact Information
- **Maintainer**: AgentDaf1.1 Development Team
- **Email**: support@agentdaf1.1.com
- **Website**: https://agentdaf1.1.com

---

**AgentDaf1.1** - Transform your Excel data into actionable insights with AI-powered precision. 🚀
