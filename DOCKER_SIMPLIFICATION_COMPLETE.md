# AgentDaf1.1 Simplified Deployment Guide

## Overview
Successfully simplified Docker deployment from 12 complex services to 3 essential services.

## Services Reduced From 12 → 3

### Original Complex Setup (12 services):
- agentdaf1-app
- agentdaf1-websocket  
- agentdaf1-redis
- agentdaf1-nginx
- agentdaf1-postgres
- agentdaf1-mongodb
- agentdaf1-rabbitmq
- agentdaf1-prometheus
- agentdaf1-grafana
- agentdaf1-elasticsearch
- agentdaf1-kibana
- agentdaf1-jaeger

### Simplified Setup (3 services):
1. **agentdaf1-app** - Main Flask application
2. **redis** - Optional caching (256MB limit)
3. **nginx** - Optional reverse proxy

## Key Improvements

### ✅ Configuration Simplified
- Removed obsolete `version: '3.8'` field
- Single Docker Compose file: `docker-compose.simple.yml`
- Clear service dependencies and health checks
- Proper volume mounting for persistence

### ✅ Deployment Scripts
- **Windows**: `deploy-simple.bat`
- **Linux/Mac**: `deploy-simple.sh`
- Automated directory creation
- Health check validation
- Clear status reporting

### ✅ Resource Optimization
- Redis limited to 256MB memory
- Health checks for all services
- Proper restart policies
- Network isolation with dedicated bridge

## Deployment Commands

### Quick Start
```bash
# Windows
.\deploy-simple.bat

# Linux/Mac
chmod +x deploy-simple.sh
./deploy-simple.sh
```

### Manual Commands
```bash
# Create directories
mkdir -p uploads logs data

# Start services
docker-compose -f docker-compose.simple.yml up --build -d

# Check status
docker-compose -f docker-compose.simple.yml ps

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop services
docker-compose -f docker-compose.simple.yml down
```

## Access URLs
- **Main App**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **API Docs**: http://localhost:8080/api
- **Nginx Proxy**: http://localhost (optional)

## Service Dependencies
```
nginx → agentdaf1-app (depends on)
redis → independent (optional cache)
```

## Health Checks
- **App**: `/health` endpoint (30s interval)
- **Redis**: `redis-cli ping` (30s interval)  
- **Nginx**: HTTP localhost check (30s interval)

## Volumes
- `uploads/` - User uploaded files
- `logs/` - Application logs
- `data/` - SQLite database and app data
- `redis_data` - Redis persistence (Docker volume)

## Next Steps
1. Start Docker Desktop
2. Run deployment script
3. Verify all services healthy
4. Test application functionality

## Troubleshooting
- Ensure Docker Desktop is running
- Check port availability (8080, 80, 6379)
- Verify directory permissions
- Review service logs for errors

---
**Status**: ✅ COMPLETED - Docker deployment simplified from 12 to 3 services