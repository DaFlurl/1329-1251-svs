#!/bin/bash

# AgentDaf1 Deployment Script
# Automated deployment and container management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="agentdaf1"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Create necessary directories
mkdir -p $BACKUP_DIR
mkdir -p ./logs

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

# Backup current data
backup_data() {
    log "Creating backup of current data..."
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    mkdir -p $BACKUP_PATH
    
    # Backup database
    if docker ps | grep -q "postgres"; then
        docker exec agentdaf1-postgres pg_dump -U agentdaf1 agentdaf1 > $BACKUP_PATH/database.sql 2>/dev/null || warning "Could not backup database"
    fi
    
    # Backup important directories
    cp -r ./data $BACKUP_PATH/ 2>/dev/null || warning "Could not backup data directory"
    cp -r ./uploads $BACKUP_PATH/ 2>/dev/null || warning "Could not backup uploads directory"
    cp -r ./gitsitestylewebseite $BACKUP_PATH/ 2>/dev/null || warning "Could not backup website directory"
    
    log "Backup created: $BACKUP_PATH"
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    docker-compose build --no-cache
    log "Docker images built successfully"
}

# Start services
start_services() {
    log "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    log "Checking service health..."
    
    services=("agentdaf1-app" "agentdaf1-redis" "agentdaf1-postgres" "agentdaf1-nginx")
    
    for service in "${services[@]}"; do
        if docker ps | grep -q $service; then
            health=$(docker inspect --format='{{.State.Health.Status}}' $service 2>/dev/null || echo "no-healthcheck")
            if [ "$health" = "healthy" ] || [ "$health" = "no-healthcheck" ]; then
                log "✓ $service is healthy"
            else
                warning "$service health status: $health"
            fi
        else
            warning "$service is not running"
        fi
    done
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    if docker ps | grep -q "agentdaf1-app"; then
        docker exec agentdaf1-app python -m alembic upgrade head 2>/dev/null || warning "Could not run migrations"
    fi
}

# Stop services
stop_services() {
    log "Stopping services..."
    docker-compose down
    log "Services stopped"
}

# Clean up Docker resources
cleanup_docker() {
    log "Cleaning up Docker resources..."
    docker system prune -f
    docker volume prune -f
    log "Docker cleanup completed"
}

# Deploy to production
deploy_production() {
    log "Starting production deployment..."
    
    check_docker
    check_docker_compose
    backup_data
    
    # Stop existing services
    stop_services
    
    # Build and start new services
    build_images
    start_services
    run_migrations
    
    log "Production deployment completed successfully"
}

# Deploy to development
deploy_development() {
    log "Starting development deployment..."
    
    check_docker
    check_docker_compose
    
    # Start services in development mode
    docker-compose -f docker-compose.yml up -d
    
    log "Development deployment completed"
}

# Update services only
update_services() {
    log "Updating services..."
    
    check_docker
    check_docker_compose
    
    # Pull latest images
    docker-compose pull
    
    # Restart services
    docker-compose up -d --force-recreate
    
    log "Services updated successfully"
}

# Show logs
show_logs() {
    log "Showing logs..."
    docker-compose logs -f --tail=100
}

# Show status
show_status() {
    log "Service status:"
    docker-compose ps
    
    log "\nResource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Restore from backup
restore_backup() {
    if [ -z "$1" ]; then
        error "Please provide backup name: ./deploy.sh restore backup_name"
        exit 1
    fi
    
    BACKUP_PATH="$BACKUP_DIR/$1"
    
    if [ ! -d "$BACKUP_PATH" ]; then
        error "Backup not found: $BACKUP_PATH"
        exit 1
    fi
    
    log "Restoring from backup: $BACKUP_PATH"
    
    # Stop services
    stop_services
    
    # Restore database
    if [ -f "$BACKUP_PATH/database.sql" ]; then
        docker-compose up -d postgres
        sleep 10
        docker exec agentdaf1-postgres psql -U agentdaf1 -c "DROP DATABASE IF EXISTS agentdaf1;"
        docker exec agentdaf1-postgres psql -U agentdaf1 -c "CREATE DATABASE agentdaf1;"
        docker exec -i agentdaf1-postgres psql -U agentdaf1 agentdaf1 < $BACKUP_PATH/database.sql
    fi
    
    # Restore directories
    if [ -d "$BACKUP_PATH/data" ]; then
        rm -rf ./data
        cp -r $BACKUP_PATH/data ./
    fi
    
    if [ -d "$BACKUP_PATH/uploads" ]; then
        rm -rf ./uploads
        cp -r $BACKUP_PATH/uploads ./
    fi
    
    log "Backup restored successfully"
}

# Show help
show_help() {
    echo "AgentDaf1 Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  production     Deploy to production environment"
    echo "  development    Deploy to development environment"
    echo "  update         Update existing services"
    echo "  stop           Stop all services"
    echo "  start          Start all services"
    echo "  restart        Restart all services"
    echo "  logs           Show service logs"
    echo "  status         Show service status"
    echo "  cleanup        Clean up Docker resources"
    echo "  backup         Create backup"
    echo "  restore [name] Restore from backup"
    echo "  health         Check service health"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 production"
    echo "  $0 restore backup_20231101_120000"
    echo "  $0 logs"
}

# Main script logic
case "$1" in
    "production")
        deploy_production
        ;;
    "development")
        deploy_development
        ;;
    "update")
        update_services
        ;;
    "stop")
        stop_services
        ;;
    "start")
        start_services
        ;;
    "restart")
        stop_services
        start_services
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        cleanup_docker
        ;;
    "backup")
        backup_data
        ;;
    "restore")
        restore_backup "$2"
        ;;
    "health")
        check_service_health
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