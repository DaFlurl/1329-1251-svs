#!/bin/bash

# AgentDaf1.1 Docker Deployment Script
echo "🚀 Starting AgentDaf1.1 Docker Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start containers
echo "🔨 Building AgentDaf1.1 container..."
docker-compose build --no-cache

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check container status
echo "📊 Checking container status..."
docker-compose ps

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ AgentDaf1.1 is running successfully!"
    echo "🌐 Access the application at: http://localhost"
    echo "🔍 Health check: http://localhost/health"
    echo "📊 API: http://localhost/api/"
else
    echo "❌ Health check failed. Checking logs..."
    docker-compose logs agentdaf1-app
fi

echo "🎉 Deployment complete!"