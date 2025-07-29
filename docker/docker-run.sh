#!/bin/bash
set -e

# AutoPromptix Docker Run Script

echo "🚀 AutoPromptix Docker Runner"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  basic       - Run basic AutoPromptix server (port 8000)"
    echo "  enhanced    - Run enhanced AutoPromptix server (port 8001)"
    echo "  dashboard   - Run dashboard with frontend (port 8002)"
    echo "  dev         - Run development environment (port 8003)"
    echo "  full        - Run full setup with Docker Compose"
    echo "  build       - Build all Docker images"
    echo "  stop        - Stop all AutoPromptix containers"
    echo "  logs        - Show logs for running containers"
    echo "  clean       - Remove all AutoPromptix containers and images"
    echo ""
    echo "Examples:"
    echo "  $0 enhanced"
    echo "  $0 dashboard"
    echo "  $0 full"
}

# Function to check if container is running
is_container_running() {
    local container_name=$1
    docker ps --format "table {{.Names}}" | grep -q "^$container_name$"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping AutoPromptix containers..."
    
    # Stop containers by name pattern
    docker ps --format "table {{.Names}}" | grep "autopromptix" | while read container; do
        if [ -n "$container" ]; then
            print_status "Stopping $container..."
            docker stop "$container" 2>/dev/null || true
        fi
    done
    
    print_success "All AutoPromptix containers stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing logs for AutoPromptix containers..."
    
    # Show logs for containers by name pattern
    docker ps --format "table {{.Names}}" | grep "autopromptix" | while read container; do
        if [ -n "$container" ]; then
            echo ""
            print_status "Logs for $container:"
            docker logs --tail=50 "$container" 2>/dev/null || echo "No logs available"
        fi
    done
}

# Function to clean up
clean_up() {
    print_warning "This will remove all AutoPromptix containers and images!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing AutoPromptix containers..."
        docker ps -a --format "table {{.Names}}" | grep "autopromptix" | while read container; do
            if [ -n "$container" ]; then
                docker rm -f "$container" 2>/dev/null || true
            fi
        done
        
        print_status "Removing AutoPromptix images..."
        docker images --format "table {{.Repository}}:{{.Tag}}" | grep "autopromptix" | while read image; do
            if [ -n "$image" ]; then
                docker rmi "$image" 2>/dev/null || true
            fi
        done
        
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main script logic
case "${1:-}" in
    "basic")
        print_status "Starting basic AutoPromptix server..."
        docker run -d --name autopromptix-basic \
            -p 8000:8000 \
            -e AUTOPROMPTIX_MODE=basic \
            -e OPENAI_API_KEY=${OPENAI_API_KEY:-} \
            autopromptix:prod
        print_success "Basic server started at http://localhost:8000"
        ;;
    
    "enhanced")
        print_status "Starting enhanced AutoPromptix server..."
        docker run -d --name autopromptix-enhanced \
            -p 8001:8001 \
            -e AUTOPROMPTIX_MODE=enhanced \
            -e OPENAI_API_KEY=${OPENAI_API_KEY:-} \
            autopromptix:prod
        print_success "Enhanced server started at http://localhost:8001"
        ;;
    
    "dashboard")
        print_status "Starting dashboard with frontend..."
        docker run -d --name autopromptix-dashboard \
            -p 8002:8001 \
            -e OPENAI_API_KEY=${OPENAI_API_KEY:-} \
            autopromptix:dashboard
        print_success "Dashboard started at http://localhost:8002"
        ;;
    
    "dev")
        print_status "Starting development environment..."
        docker run -d --name autopromptix-dev \
            -p 8003:8001 \
            -p 8004:8000 \
            -e FLASK_ENV=development \
            -e FLASK_DEBUG=1 \
            -e OPENAI_API_KEY=${OPENAI_API_KEY:-} \
            -v "$(pwd):/app" \
            autopromptix:dev
        print_success "Development environment started"
        print_success "Enhanced server: http://localhost:8003"
        print_success "Basic server: http://localhost:8004"
        ;;
    
    "full")
        print_status "Starting full setup with Docker Compose..."
        docker-compose --profile enhanced up -d
        print_success "Full setup started"
        print_success "Enhanced server: http://localhost:8001"
        ;;
    
    "build")
        print_status "Building Docker images..."
        ./docker-build.sh
        ;;
    
    "stop")
        stop_containers
        ;;
    
    "logs")
        show_logs
        ;;
    
    "clean")
        clean_up
        ;;
    
    *)
        show_usage
        exit 1
        ;;
esac

# Show running containers
if [ "$1" != "stop" ] && [ "$1" != "clean" ] && [ "$1" != "build" ]; then
    echo ""
    print_status "Running AutoPromptix containers:"
    docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" | grep "autopromptix" || echo "No containers running"
fi 