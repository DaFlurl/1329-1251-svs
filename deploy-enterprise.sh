#!/bin/bash

# AgentDaf1.1 Enterprise Deployment Script
# This script deploys the complete enterprise microservices system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.enterprise.yml"
PROJECT_NAME="agentdaf1-enterprise"

echo -e "${BLUE}🚀 AgentDaf1.1 Enterprise Deployment${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Docker Compose file not found: $COMPOSE_FILE${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p enterprise/monitoring/prometheus
mkdir -p enterprise/monitoring/grafana/dashboards
mkdir -p enterprise/monitoring/grafana/datasources
mkdir -p enterprise/nginx/ssl
mkdir -p enterprise/database/init

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file with default values...${NC}"
    cat > .env << EOF
# Database Configuration
DB_PASSWORD=your_secure_password_here

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Grafana Configuration
GRAFANA_PASSWORD=admin

# Environment
ENVIRONMENT=production
EOF
    echo -e "${YELLOW}⚠️  Please edit .env file with your secure passwords before proceeding!${NC}"
    read -p "Press Enter to continue after editing .env file..."
fi

# Build and start services
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build

echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${BLUE}🏥 Checking service health...${NC}"
services=("gateway" "data-service" "analytics-service" "websocket-service" "postgres" "redis")

for service in "${services[@]}"; do
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps $service | grep -q "Up"; then
        echo -e "${GREEN}✅ $service is running${NC}"
    else
        echo -e "${RED}❌ $service is not running${NC}"
    fi
done

# Display access information
echo -e "${BLUE}🌐 Access Information:${NC}"
echo "=================================="
echo -e "${GREEN}📊 Main Dashboard:${NC}     http://localhost:3000"
echo -e "${GREEN}🚪 API Gateway:${NC}        http://localhost:8000"
echo -e "${GREEN}📈 Analytics Service:${NC}   http://localhost:8002"
echo -e "${GREEN}🔌 WebSocket Service:${NC}  http://localhost:8004"
echo -e "${GREEN}📊 Prometheus:${NC}         http://localhost:9090"
echo -e "${GREEN}📈 Grafana:${NC}            http://localhost:3001 (admin/admin)"
echo -e "${GREEN}🗄️  Database:${NC}           localhost:5432"
echo -e "${GREEN}🔴 Redis:${NC}              localhost:6379"

echo ""
echo -e "${BLUE}📚 API Documentation:${NC}"
echo -e "${GREEN}📖 Gateway Docs:${NC}        http://localhost:8000/docs"
echo -e "${GREEN}📊 Data Service Docs:${NC}   http://localhost:8001/docs"
echo -e "${GREEN}📈 Analytics Docs:${NC}     http://localhost:8002/docs"

echo ""
echo -e "${YELLOW}🔧 Management Commands:${NC}"
echo "=================================="
echo "View logs:        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f [service-name]"
echo "Stop services:    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down"
echo "Restart services: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart [service-name]"
echo "Update services:  docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME pull && docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d"

echo ""
echo -e "${GREEN}🎉 AgentDaf1.1 Enterprise deployment completed successfully!${NC}"
echo -e "${YELLOW}⚠️  Remember to change default passwords in production!${NC}"