#!/bin/bash

# Grace Docker Deploy Script
# Handles deployment of the Grace system using Docker Compose

set -e

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
ENV_FILE="${ENV_FILE:-.env.docker}"
PROJECT_NAME="${PROJECT_NAME:-grace}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found"
        log_info "Please copy .env.example to $ENV_FILE and configure your settings"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Validate environment configuration
validate_environment() {
    log_info "Validating environment configuration..."

    # Check required environment variables
    required_vars=("GRACE_PORT" "FRONTEND_PORT" "OPENAI_API_KEY")

    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$ENV_FILE" || grep -q "^${var}=your_.*_here" "$ENV_FILE"; then
            log_error "Required environment variable $var is not set in $ENV_FILE"
            exit 1
        fi
    done

    log_success "Environment configuration validated"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    directories=("databases" "logs" "storage" "ml_artifacts")

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done

    log_success "Directories created"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest Docker images..."

    if docker-compose pull; then
        log_success "Images pulled successfully"
    else
        log_warning "Some images could not be pulled, will build locally if needed"
    fi
}

# Start services
start_services() {
    log_info "Starting Grace services..."

    # Start with build if images don't exist
    if docker-compose up -d --build; then
        log_success "Services started successfully"
    else
        log_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_health() {
    local max_attempts=30
    local attempt=1

    log_info "Waiting for services to become healthy..."

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Check backend health
        if curl -f -s "http://localhost:${GRACE_PORT:-8000}/health" > /dev/null 2>&1; then
            log_success "Backend is healthy"
            backend_healthy=true
        else
            log_info "Backend not ready yet..."
            backend_healthy=false
        fi

        # Check frontend health
        if curl -f -s "http://localhost:${FRONTEND_PORT:-5173}" > /dev/null 2>&1; then
            log_success "Frontend is healthy"
            frontend_healthy=true
        else
            log_info "Frontend not ready yet..."
            frontend_healthy=false
        fi

        # If both are healthy, we're done
        if [ "$backend_healthy" = true ] && [ "$frontend_healthy" = true ]; then
            log_success "All services are healthy!"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 10
    done

    log_error "Services failed to become healthy within $max_attempts attempts"
    return 1
}

# Show service status
show_status() {
    log_info "Service Status:"
    echo

    docker-compose ps

    echo
    log_info "Service URLs:"
    echo "  Backend API:  http://localhost:${GRACE_PORT:-8000}"
    echo "  Frontend UI:  http://localhost:${FRONTEND_PORT:-5173}"
    echo "  API Docs:     http://localhost:${GRACE_PORT:-8000}/docs"
    echo "  Health Check: http://localhost:${GRACE_PORT:-8000}/health"
}

# Stop services
stop_services() {
    log_info "Stopping Grace services..."

    if docker-compose down; then
        log_success "Services stopped successfully"
    else
        log_error "Failed to stop services"
        exit 1
    fi
}

# Restart services
restart_services() {
    log_info "Restarting Grace services..."

    if docker-compose restart; then
        log_success "Services restarted successfully"
        wait_for_health
    else
        log_error "Failed to restart services"
        exit 1
    fi
}

# Show logs
show_logs() {
    local service="${1:-}"
    local follow="${2:-false}"

    if [ -n "$service" ]; then
        log_info "Showing logs for service: $service"
        if [ "$follow" = "true" ]; then
            docker-compose logs -f "$service"
        else
            docker-compose logs "$service"
        fi
    else
        log_info "Showing logs for all services"
        if [ "$follow" = "true" ]; then
            docker-compose logs -f
        else
            docker-compose logs
        fi
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up Docker resources..."

    # Remove stopped containers
    docker container prune -f

    # Remove unused images
    docker image prune -f

    # Remove unused volumes (be careful with this)
    # docker volume prune -f

    log_success "Cleanup completed"
}

# Show usage
usage() {
    cat << EOF
Grace Docker Deploy Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    start           Start all services (default)
    stop            Stop all services
    restart         Restart all services
    status          Show service status
    logs [SERVICE]  Show logs (optionally for specific service)
    logs-follow     Follow logs for all services
    pull            Pull latest images
    cleanup         Clean up Docker resources
    health          Check service health

Options:
    -f, --file FILE       Docker Compose file (default: docker-compose.yml)
    -e, --env FILE        Environment file (default: .env.docker)
    -p, --project NAME    Project name (default: grace)
    -h, --help           Show this help

Environment Variables:
    COMPOSE_FILE    Docker Compose file
    ENV_FILE        Environment file
    PROJECT_NAME    Project name
    GRACE_PORT      Backend port
    FRONTEND_PORT   Frontend port

Examples:
    $0 start                    # Start all services
    $0 stop                     # Stop all services
    $0 status                   # Show status
    $0 logs backend             # Show backend logs
    $0 logs-follow              # Follow all logs
    $0 -f docker-compose.prod.yml start  # Use production compose file

Note: Make sure $ENV_FILE is configured with your settings before deployment.
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -e|--env)
                ENV_FILE="$2"
                shift 2
                ;;
            -p|--project)
                PROJECT_NAME="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            start|stop|restart|status|logs|logs-follow|pull|cleanup|health)
                COMMAND="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    local COMMAND="${1:-start}"

    parse_args "$@"

    case $COMMAND in
        start)
            check_prerequisites
            validate_environment
            create_directories
            pull_images
            start_services
            wait_for_health
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        logs-follow)
            show_logs "" true
            ;;
        pull)
            pull_images
            ;;
        cleanup)
            cleanup
            ;;
        health)
            wait_for_health
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            usage
            exit 1
            ;;
    esac
}

# Set Docker Compose command based on version
if docker compose version &> /dev/null; then
    docker-compose() {
        docker compose "$@"
    }
fi

# Export environment variables for docker-compose
export COMPOSE_FILE
export ENV_FILE
export PROJECT_NAME

# Run main function with all arguments
main "$@"