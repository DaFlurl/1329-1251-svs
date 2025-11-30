#!/bin/bash

# AgentDaf1 Development Startup Script
# Quick start for development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="agentdaf1"
ENV_FILE=".env"
LOG_FILE="./logs/startup.log"

# Create necessary directories
mkdir -p ./logs
mkdir -p ./uploads
mkdir -p ./data
mkdir -p ./backups

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a $LOG_FILE
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a $LOG_FILE
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a $LOG_FILE
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log "Docker is running"
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        error "docker-compose is not installed or not in PATH"
        exit 1
    fi
    log "docker-compose is available"
}

# Setup environment
setup_environment() {
    log "Setting up development environment..."
    
    # Copy .env file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example $ENV_FILE
            log "Created .env file from .env.example"
            warning "Please update $ENV_FILE with your configuration"
        else
            warning ".env.example not found. Creating basic .env file"
            cat > $ENV_FILE << EOF
# Development Environment
DEBUG=true
ENVIRONMENT=development
DB_PASSWORD=dev_password
JWT_SECRET=dev_jwt_secret_change_me
GRAFANA_PASSWORD=admin
EOF
        fi
    fi
    
    # Create Python virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        log "Virtual environment created and dependencies installed"
    fi
    
    # Install Node.js dependencies if they exist
    if [ -f "enterprise/web/package.json" ]; then
        log "Installing Node.js dependencies..."
        cd enterprise/web
        npm install
        cd ../..
        log "Node.js dependencies installed"
    fi
}

# Start development services
start_dev_services() {
    log "Starting development services..."
    
    # Start core services
    docker-compose -f docker-compose.yml up -d postgres redis rabbitmq
    
    # Wait for services to be ready
    log "Waiting for core services to be ready..."
    sleep 15
    
    # Start application services
    docker-compose -f docker-compose.yml up -d agentdaf1-app gateway data-service analytics-service websocket-service
    
    # Wait for application services
    sleep 10
    
    # Start web services
    docker-compose -f docker-compose.yml up -d web-server web-app
    
    log "All development services started"
}

# Start local development servers
start_local_servers() {
    log "Starting local development servers..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start Flask API in background
    info "Starting Flask API server on port 8080..."
    python app.py > ./logs/flask.log 2>&1 &
    FLASK_PID=$!
    echo $FLASK_PID > ./logs/flask.pid
    
    # Start FastAPI server in background
    info "Starting FastAPI server on port 8000..."
    python src/main.py > ./logs/fastapi.log 2>&1 &
    FASTAPI_PID=$!
    echo $FASTAPI_PID > ./logs/fastapi.pid
    
    # Start WebSocket server in background
    info "Starting WebSocket server on port 8004..."
    python services/websocket_service.py > ./logs/websocket.log 2>&1 &
    WEBSOCKET_PID=$!
    echo $WEBSOCKET_PID > ./logs/websocket.pid
    
    # Start static file server for website
    info "Starting static file server on port 8082..."
    cd gitsitestylewebseite
    python -m http.server 8082 > ../logs/website.log 2>&1 &
    WEBSITE_PID=$!
    echo $WEBSITE_PID > ../logs/website.pid
    cd ..
    
    log "All local servers started"
}

# Check service health
check_services() {
    log "Checking service health..."
    
    # Check Docker services
    services=("agentdaf1-postgres" "agentdaf1-redis" "agentdaf1-rabbitmq" "agentdaf1-app" "agentdaf1-gateway")
    
    for service in "${services[@]}"; do
        if docker ps | grep -q $service; then
            log "✓ $service is running"
        else
            warning "$service is not running"
        fi
    done
    
    # Check local servers
    if [ -f "./logs/flask.pid" ]; then
        FLASK_PID=$(cat ./logs/flask.pid)
        if ps -p $FLASK_PID > /dev/null; then
            log "✓ Flask server is running (PID: $FLASK_PID)"
        else
            warning "Flask server is not running"
        fi
    fi
    
    if [ -f "./logs/fastapi.pid" ]; then
        FASTAPI_PID=$(cat ./logs/fastapi.pid)
        if ps -p $FASTAPI_PID > /dev/null; then
            log "✓ FastAPI server is running (PID: $FASTAPI_PID)"
        else
            warning "FastAPI server is not running"
        fi
    fi
    
    if [ -f "./logs/websocket.pid" ]; then
        WEBSOCKET_PID=$(cat ./logs/websocket.pid)
        if ps -p $WEBSOCKET_PID > /dev/null; then
            log "✓ WebSocket server is running (PID: $WEBSOCKET_PID)"
        else
            warning "WebSocket server is not running"
        fi
    fi
    
    if [ -f "./logs/website.pid" ]; then
        WEBSITE_PID=$(cat ./logs/website.pid)
        if ps -p $WEBSITE_PID > /dev/null; then
            log "✓ Website server is running (PID: $WEBSITE_PID)"
        else
            warning "Website server is not running"
        fi
    fi
}

# Show access URLs
show_urls() {
    log "Development environment is ready!"
    echo ""
    echo "Access URLs:"
    echo "  Main Application:    http://localhost:8080"
    echo "  API Gateway:         http://localhost:8000"
    echo "  Enhanced Dashboard:   http://localhost:8082/enhanced-dashboard.html"
    echo "  Static Website:      http://localhost:8082"
    echo "  WebSocket:           ws://localhost:8004"
    echo "  RabbitMQ Management: http://localhost:15672 (admin/admin123)"
    echo "  Grafana:            http://localhost:3001 (admin/admin)"
    echo "  Prometheus:         http://localhost:9090"
    echo ""
    echo "Logs:"
    echo "  Flask:    ./logs/flask.log"
    echo "  FastAPI:  ./logs/fastapi.log"
    echo "  WebSocket: ./logs/websocket.log"
    echo "  Website:  ./logs/website.log"
    echo ""
    echo "To stop all services, run: ./scripts/stop-dev.sh"
}

# Stop development services
stop_services() {
    log "Stopping development services..."
    
    # Stop local servers
    if [ -f "./logs/flask.pid" ]; then
        FLASK_PID=$(cat ./logs/flask.pid)
        kill $FLASK_PID 2>/dev/null || true
        rm ./logs/flask.pid
        log "Stopped Flask server"
    fi
    
    if [ -f "./logs/fastapi.pid" ]; then
        FASTAPI_PID=$(cat ./logs/fastapi.pid)
        kill $FASTAPI_PID 2>/dev/null || true
        rm ./logs/fastapi.pid
        log "Stopped FastAPI server"
    fi
    
    if [ -f "./logs/websocket.pid" ]; then
        WEBSOCKET_PID=$(cat ./logs/websocket.pid)
        kill $WEBSOCKET_PID 2>/dev/null || true
        rm ./logs/websocket.pid
        log "Stopped WebSocket server"
    fi
    
    if [ -f "./logs/website.pid" ]; then
        WEBSITE_PID=$(cat ./logs/website.pid)
        kill $WEBSITE_PID 2>/dev/null || true
        rm ./logs/website.pid
        log "Stopped Website server"
    fi
    
    # Stop Docker services
    docker-compose -f docker-compose.yml down
    
    log "All development services stopped"
}

# Show help
show_help() {
    echo "AgentDaf1 Development Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start development environment (default)"
    echo "  stop      Stop development environment"
    echo "  restart   Restart development environment"
    echo "  status    Check service status"
    echo "  logs      Show service logs"
    echo "  setup     Setup development environment only"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 stop"
    echo "  $0 status"
}

# Main script logic
case "$1" in
    "start"|"")
        check_docker
        check_docker_compose
        setup_environment
        start_dev_services
        start_local_servers
        sleep 5
        check_services
        show_urls
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        check_docker
        check_docker_compose
        start_dev_services
        start_local_servers
        sleep 5
        check_services
        show_urls
        ;;
    "status")
        check_services
        ;;
    "logs")
        log "Showing logs..."
        tail -f ./logs/*.log
        ;;
    "setup")
        check_docker
        check_docker_compose
        setup_environment
        log "Development environment setup completed"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

log "Script completed successfully"