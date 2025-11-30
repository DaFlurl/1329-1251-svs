#!/bin/bash
# Docker Performance Monitor Start Script
# Starts all Docker services and monitoring

set -e

echo "🚀 Starting Docker Performance Monitor..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
mkdir -p data logs backups

# Start monitoring container
echo "📊 Starting performance monitoring container..."
docker run -d \
  --name performance-monitor \
  --restart unless-stopped \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/configs:/app/configs" \
  -v "$(pwd)/logs:/app/logs" \
  --network host \
  performance-monitor:latest

# Wait for container to be ready
echo "⏳ Waiting for monitoring container to be ready..."
sleep 5

# Check if container is running
if docker ps | grep -q performance-monitor; then
    echo "✅ Performance monitor started successfully"
    echo "📊 Monitoring data will be saved in: ./data"
    echo "📋 Logs available in: ./logs"
    echo "⚙️  Configuration in: ./configs"
    
    # Show container status
    echo ""
    echo "📦 Container Status:"
    docker ps --filter "name=performance-monitor" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # Show how to access monitoring
    echo ""
    echo "🔧 Management Commands:"
    echo "  View logs:        docker logs -f performance-monitor"
    echo "  Stop monitoring:   docker stop performance-monitor"
    echo "  Restart:          docker restart performance-monitor"
    echo "  View data:         docker exec performance-monitor python /app/src/performance_monitor.py --export"
    echo "  Web dashboard:     Access http://localhost:8080 (when enabled)"
else
    echo "❌ Failed to start performance monitor"
    exit 1
fi