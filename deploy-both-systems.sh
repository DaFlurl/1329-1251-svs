#!/bin/bash

# AgentDaf1.1 Dual System Deployment Script
# Deploys both Basic and Enterprise systems simultaneously

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}🚀 AgentDaf1.1 Dual System Deployment${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${YELLOW}This will deploy BOTH systems:${NC}"
echo -e "${GREEN}📊 Basic System${NC} (Ports 80, 8080, 6379)"
echo -e "${GREEN}🏢 Enterprise System${NC} (Ports 3000, 8000-8004, 3001, 9090, 5432)"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p uploads logs data ssl
mkdir -p enterprise/monitoring/prometheus
mkdir -p enterprise/monitoring/grafana/dashboards
mkdir -p enterprise/monitoring/grafana/datasources
mkdir -p enterprise/nginx/ssl
mkdir -p enterprise/database/init

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file with default values...${NC}"
    cat > .env << EOF
# Basic System Configuration
GITHUB_TOKEN=
GITHUB_REPO_OWNER=
GITHUB_REPO_NAME=

# Enterprise System Configuration
DB_PASSWORD=your_secure_password_here
JWT_SECRET=your-super-secret-jwt-key-change-in-production
GRAFANA_PASSWORD=admin
ENVIRONMENT=production
EOF
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration before proceeding!${NC}"
    read -p "Press Enter to continue after editing .env file..."
fi

echo ""
echo -e "${YELLOW}🔨 Building and Starting Basic System...${NC}"
docker-compose up -d --build

echo ""
echo -e "${YELLOW}🏢 Building and Starting Enterprise System...${NC}"
docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise up -d --build

# Wait for services to be ready
echo ""
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 45

echo ""
echo -e "${BLUE}🏥 Checking Service Health...${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}📊 BASIC SYSTEM:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}🏢 ENTERPRISE SYSTEM:${NC}"
docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise ps

echo ""
echo -e "${BLUE}🌐 ACCESS INFORMATION:${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}📊 BASIC SYSTEM:${NC}"
echo -e "   Main App:        http://localhost:8080"
echo -e "   Nginx Proxy:     http://localhost:80"
echo -e "   Redis:           localhost:6379"
echo ""
echo -e "${GREEN}🏢 ENTERPRISE SYSTEM:${NC}"
echo -e "   Premium Dashboard: http://localhost:3000"
echo -e "   API Gateway:      http://localhost:8000"
echo -e "   Data Service:     http://localhost:8001"
echo -e "   Analytics:        http://localhost:8002"
echo -e "   WebSocket:        http://localhost:8004"
echo -e "   Prometheus:       http://localhost:9090"
echo -e "   Grafana:          http://localhost:3001 (admin/admin)"
echo -e "   PostgreSQL:       localhost:5432"
echo -e "   Redis (Enterprise): localhost:6379"
echo ""
echo -e "${BLUE}📚 API DOCUMENTATION:${NC}"
echo -e "   Gateway Docs:     http://localhost:8000/docs"
echo -e "   Data Service:     http://localhost:8001/docs"
echo -e "   Analytics:        http://localhost:8002/docs"
echo ""
echo -e "${BLUE}🔧 MANAGEMENT COMMANDS:${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}📊 Basic System:${NC}"
echo -e "   View logs:        docker-compose logs -f [service-name]"
echo -e "   Stop basic:       docker-compose down"
echo -e "   Restart basic:     docker-compose restart [service-name]"
echo ""
echo -e "${GREEN}🏢 Enterprise System:${NC}"
echo -e "   View logs:        docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise logs -f [service-name]"
echo -e "   Stop enterprise:  docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise down"
echo -e "   Restart enterprise: docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise restart [service-name]"
echo ""
echo -e "${GREEN}🔄 BOTH SYSTEMS:${NC}"
echo -e "   Stop all:         docker-compose down && docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise down"
echo -e "   Restart all:      docker-compose restart && docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise restart"
echo ""
echo -e "${BLUE}📈 SYSTEM COMPARISON:${NC}"
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}📊 Basic System:${NC}    Simple, lightweight, good for development"
echo -e "${GREEN}🏢 Enterprise:${NC}       Full-featured, production-ready, AI-powered"
echo ""
echo -e "${YELLOW}💡 TIP: Use Basic System for quick testing, Enterprise System for full features!${NC}"
echo ""
echo -e "${GREEN}🎉 Both AgentDaf1.1 systems deployed successfully!${NC}"
echo -e "${YELLOW}⚠️  Remember to change default passwords in production!${NC}"