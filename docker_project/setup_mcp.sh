#!/bin/bash
# AgentDaf1.1 MCP Sequential Thinking Setup Script

echo "🚀 Setting up MCP Sequential Thinking with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Pull the latest Sequential Thinking image
echo "📦 Pulling Sequential Thinking MCP image..."
docker pull mcp/sequentialthinking

# Build and start all services
echo "🔧 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Test MCP Sequential Thinking
echo "🧪 Testing MCP Sequential Thinking..."
python mcp_sequential_integration.py

echo "✅ Setup complete!"
echo ""
echo "🌐 Access Points:"
echo "   - Main App: http://localhost:8080"
echo "   - Grafana: http://localhost:3000 (admin/admin123)"
echo "   - Prometheus: http://localhost:9090"
echo "   - MCP Sequential Thinking: http://localhost:3001"
echo ""
echo "🧠 MCP Commands:"
echo "   - Test integration: python mcp_sequential_integration.py"
echo "   - View logs: docker-compose logs -f sequential-thinking"
echo "   - Stop services: docker-compose down"
echo "   - Restart MCP: docker-compose restart sequential-thinking"