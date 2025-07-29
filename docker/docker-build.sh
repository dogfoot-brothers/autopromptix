#!/bin/bash
set -e

# AutoPromptix Docker Build Script

echo "🔨 Building AutoPromptix Docker Images..."

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build base image
print_status "Building base image..."
docker build --target base -t autopromptix:base .

if [ $? -eq 0 ]; then
    print_success "Base image built successfully"
else
    print_error "Failed to build base image"
    exit 1
fi

# Build development image
print_status "Building development image..."
docker build --target development -t autopromptix:dev .

if [ $? -eq 0 ]; then
    print_success "Development image built successfully"
else
    print_error "Failed to build development image"
    exit 1
fi

# Build production image
print_status "Building production image..."
docker build --target production -t autopromptix:prod .

if [ $? -eq 0 ]; then
    print_success "Production image built successfully"
else
    print_error "Failed to build production image"
    exit 1
fi

# Build dashboard image
print_status "Building dashboard image..."
docker build --target dashboard -t autopromptix:dashboard .

if [ $? -eq 0 ]; then
    print_success "Dashboard image built successfully"
else
    print_error "Failed to build dashboard image"
    exit 1
fi

# Create latest tag
print_status "Creating latest tag..."
docker tag autopromptix:prod autopromptix:latest

print_success "All Docker images built successfully!"
echo ""
echo "Available images:"
echo "  - autopromptix:base     (Base image)"
echo "  - autopromptix:dev      (Development environment)"
echo "  - autopromptix:prod     (Production environment)"
echo "  - autopromptix:dashboard (Dashboard with frontend)"
echo "  - autopromptix:latest   (Latest production image)"
echo ""
echo "To run a specific image:"
echo "  docker run -p 8001:8001 autopromptix:prod"
echo "  docker run -p 8002:8001 autopromptix:dashboard"
echo ""
echo "To run with Docker Compose:"
echo "  docker-compose --profile enhanced up"
echo "  docker-compose --profile dashboard up"
echo "  docker-compose --profile development up" 