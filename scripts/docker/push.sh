#!/bin/bash

# Grace Docker Push Script
# Pushes Docker images to Docker Hub with proper tagging

set -e

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-graceai}"
IMAGE_NAME="${IMAGE_NAME:-grace}"
VERSION="${VERSION:-latest}"
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
DOCKER_PASSWORD="${DOCKER_PASSWORD:-}"

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
}

# Login to Docker Hub
docker_login() {
    if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_PASSWORD" ]; then
        log_warning "DOCKER_USERNAME and/or DOCKER_PASSWORD not set"
        log_info "Attempting to login interactively..."
        echo "Please login to Docker Hub:"
        docker login
    else
        log_info "Logging in to Docker Hub..."
        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
        log_success "Logged in to Docker Hub"
    fi
}

# Push single image with retries
push_image() {
    local image_tag="$1"
    local max_retries=3
    local retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        log_info "Pushing $image_tag (attempt $((retry_count + 1))/$max_retries)..."

        if docker push "$image_tag"; then
            log_success "Successfully pushed $image_tag"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                log_warning "Push failed, retrying in 5 seconds..."
                sleep 5
            fi
        fi
    done

    log_error "Failed to push $image_tag after $max_retries attempts"
    return 1
}

# Tag and push images with multiple tags
push_with_tags() {
    local source_tag="$1"
    local base_name="$2"
    local tags=("${@:3}")

    # Check if source image exists
    if ! docker image inspect "$source_tag" &> /dev/null; then
        log_error "Source image $source_tag does not exist locally"
        return 1
    fi

    # Push with each tag
    for tag in "${tags[@]}"; do
        local full_tag="${DOCKER_REGISTRY}/${base_name}:${tag}"
        log_info "Tagging $source_tag as $full_tag"

        docker tag "$source_tag" "$full_tag"
        push_image "$full_tag"
    done
}

# Push backend images
push_backend() {
    local source_tag="${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:${VERSION}"
    local tags=("latest")

    if [ "$VERSION" != "latest" ]; then
        tags=("$VERSION" "latest")
    fi

    log_info "Pushing backend images..."
    push_with_tags "$source_tag" "${IMAGE_NAME}-backend" "${tags[@]}"
}

# Push frontend images
push_frontend() {
    local source_tag="${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION}"
    local tags=("latest")

    if [ "$VERSION" != "latest" ]; then
        tags=("$VERSION" "latest")
    fi

    log_info "Pushing frontend images..."
    push_with_tags "$source_tag" "${IMAGE_NAME}-frontend" "${tags[@]}"
}

# Push all images
push_all() {
    log_info "Starting Grace system push to Docker Hub..."

    push_backend
    push_frontend

    log_success "All images pushed successfully"
}

# Create and push manifest for multi-arch images
push_manifest() {
    log_info "Creating and pushing multi-arch manifests..."

    local backend_tags=()
    local frontend_tags=()

    # Collect tags for manifest
    if [ "$VERSION" != "latest" ]; then
        backend_tags=(
            "${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:${VERSION}"
            "${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:latest"
        )
        frontend_tags=(
            "${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION}"
            "${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:latest"
        )
    else
        backend_tags=("${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:latest")
        frontend_tags=("${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:latest")
    fi

    # Create manifests
    log_info "Creating backend manifest..."
    docker manifest create "${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:${VERSION}" "${backend_tags[@]}"
    docker manifest push "${DOCKER_REGISTRY}/${IMAGE_NAME}-backend:${VERSION}"

    log_info "Creating frontend manifest..."
    docker manifest create "${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION}" "${frontend_tags[@]}"
    docker manifest push "${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION}"

    log_success "Multi-arch manifests created and pushed"
}

# Show usage
usage() {
    cat << EOF
Grace Docker Push Script

Usage: $0 [OPTIONS] [COMMAND]

Commands:
    all             Push all images (default)
    backend         Push only backend images
    frontend        Push only frontend images
    manifest        Create and push multi-arch manifests

Options:
    -r, --registry REGISTRY      Docker registry (default: graceai)
    -n, --name NAME             Image name (default: grace)
    -v, --version VERSION       Image version tag (default: latest)
    -u, --username USERNAME     Docker Hub username
    -p, --password PASSWORD     Docker Hub password
    -h, --help                  Show this help

Environment Variables:
    DOCKER_REGISTRY     Docker registry
    IMAGE_NAME         Image name
    VERSION            Image version
    DOCKER_USERNAME    Docker Hub username
    DOCKER_PASSWORD    Docker Hub password/token

Examples:
    $0                          # Push all images
    $0 -v v2.0.0 all           # Push with specific version
    $0 backend                 # Push only backend
    $0 manifest                # Create multi-arch manifests

Note: Make sure to run build.sh first to create the images locally.
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
            -u|--username)
                DOCKER_USERNAME="$2"
                shift 2
                ;;
            -p|--password)
                DOCKER_PASSWORD="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            all|backend|frontend|manifest)
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
    docker_login

    case $COMMAND in
        all)
            push_all
            ;;
        backend)
            push_backend
            ;;
        frontend)
            push_frontend
            ;;
        manifest)
            push_manifest
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