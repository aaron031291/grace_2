#!/bin/bash

# Grace Docker Build Script
# Builds and tags Docker images for the Grace system

set -e

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-graceai}"
IMAGE_NAME="${IMAGE_NAME:-grace}"
VERSION="${VERSION:-latest}"
BUILD_PLATFORMS="${BUILD_PLATFORMS:-linux/amd64,linux/arm64}"

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

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    log_success "Docker is available"
}

# Build backend image
build_backend() {
    log_info "Building Grace backend image..."

    local backend_tag="${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:${VERSION}"

    docker build \
        --target production \
        --tag "$backend_tag" \
        --label "org.opencontainers.image.title=Grace Backend" \
        --label "org.opencontainers.image.description=Grace AI System Backend API" \
        --label "org.opencontainers.image.version=${VERSION}" \
        --label "org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --label "org.opencontainers.image.source=https://github.com/grace-ai/grace" \
        .

    log_success "Backend image built: $backend_tag"
    echo "$backend_tag" >> .build_tags
}

# Build frontend image
build_frontend() {
    log_info "Building Grace frontend image..."

    local frontend_tag="${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION}"

    cd frontend

    docker build \
        --tag "$frontend_tag" \
        --label "org.opencontainers.image.title=Grace Frontend" \
        --label "org.opencontainers.image.description=Grace AI System Frontend UI" \
        --label "org.opencontainers.image.version=${VERSION}" \
        --label "org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --label "org.opencontainers.image.source=https://github.com/grace-ai/grace" \
        .

    cd ..
    log_success "Frontend image built: $frontend_tag"
    echo "$frontend_tag" >> .build_tags
}

# Build all images
build_all() {
    log_info "Starting Grace system build..."

    # Clean previous build tags
    rm -f .build_tags

    # Build images
    build_backend
    build_frontend

    log_success "All images built successfully"

    # Show build summary
    echo
    log_info "Build Summary:"
    if [ -f .build_tags ]; then
        cat .build_tags
    fi
}

# Multi-platform build (requires Docker Buildx)
build_multiplatform() {
    log_info "Building multi-platform images..."

    if ! docker buildx ls | grep -q "grace-builder"; then
        log_info "Creating buildx builder..."
        docker buildx create --name grace-builder --use
    fi

    local backend_tag="${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:${VERSION}"
    local frontend_tag="${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION}"

    # Build backend for multiple platforms
    log_info "Building backend for platforms: $BUILD_PLATFORMS"
    docker buildx build \
        --target production \
        --platform "$BUILD_PLATFORMS" \
        --tag "$backend_tag" \
        --push \
        --label "org.opencontainers.image.title=Grace Backend" \
        --label "org.opencontainers.image.description=Grace AI System Backend API" \
        --label "org.opencontainers.image.version=${VERSION}" \
        --label "org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        .

    # Build frontend for multiple platforms
    log_info "Building frontend for platforms: $BUILD_PLATFORMS"
    cd frontend
    docker buildx build \
        --platform "$BUILD_PLATFORMS" \
        --tag "$frontend_tag" \
        --push \
        --label "org.opencontainers.image.title=Grace Frontend" \
        --label "org.opencontainers.image.description=Grace AI System Frontend UI" \
        --label "org.opencontainers.image.version=${VERSION}" \
        --label "org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        .
    cd ..

    log_success "Multi-platform images built and pushed"
}

# Show usage
usage() {
    cat << EOF
Grace Docker Build Script

Usage: $0 [OPTIONS] [COMMAND]

Commands:
    all             Build all images (default)
    backend         Build only backend image
    frontend        Build only frontend image
    multiplatform   Build multi-platform images and push to registry

Options:
    -r, --registry REGISTRY    Docker registry (default: graceai)
    -n, --name NAME           Image name (default: grace)
    -v, --version VERSION     Image version tag (default: latest)
    -p, --platforms PLATFORMS Comma-separated platforms for multiplatform build
    -h, --help               Show this help

Environment Variables:
    DOCKER_REGISTRY    Docker registry
    IMAGE_NAME        Image name
    VERSION           Image version
    BUILD_PLATFORMS   Platforms for multiplatform build

Examples:
    $0                          # Build all images locally
    $0 backend                  # Build only backend
    $0 -v v2.0.0 all           # Build all with specific version
    $0 multiplatform           # Build multi-platform and push
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--registry)
                DOCKER_REGISTRY="$2"
                shift 2
                ;;
            -n|--name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            -p|--platforms)
                BUILD_PLATFORMS="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            all|backend|frontend|multiplatform)
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
    local COMMAND="${1:-all}"

    parse_args "$@"

    check_docker

    case $COMMAND in
        all)
            build_all
            ;;
        backend)
            build_backend
            ;;
        frontend)
            build_frontend
            ;;
        multiplatform)
            build_multiplatform
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"