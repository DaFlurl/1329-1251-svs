#!/bin/bash
# AgentDaf1.1 Simplified Deployment Script

echo "🚀 AgentDaf1.1 Simplified Deployment"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs data

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.simple.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if main application is running
echo "🔍 Checking service health..."
if curl -f http://localhost:8080/health &> /dev/null; then
    echo "✅ Main application is running on http://localhost:8080"
else
    echo "❌ Main application is not responding"
    docker-compose -f docker-compose.simple.yml logs agentdaf1-app
fi

# Check if nginx is running (optional)
if curl -f http://localhost/health &> /dev/null; then
    echo "✅ Nginx proxy is running on http://localhost"
fi

# Show running containers
echo "📊 Running containers:"
docker-compose -f docker-compose.simple.yml ps

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Access URLs:"
echo "   • Main App: http://localhost:8080"
echo "   • Health Check: http://localhost:8080/health"
echo "   • API Docs: http://localhost:8080/api"
echo ""
echo "🛠️ Management Commands:"
echo "   • View logs: docker-compose -f docker-compose.simple.yml logs -f"
echo "   • Stop services: docker-compose -f docker-compose.simple.yml down"
echo "   • Restart: docker-compose -f docker-compose.simple.yml restart"