#!/bin/bash

echo "========================================"
echo "CCCD Scanner - Docker Build Script"
echo "========================================"
echo

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "ERROR: Docker is not running!"
        echo "Please start Docker and try again."
        exit 1
    fi
}

# Function to build and run
build_and_run() {
    echo "[1/3] Building Docker image..."
    if ! docker build -t cccd-scanner:latest .; then
        echo "ERROR: Failed to build Docker image!"
        exit 1
    fi

    echo
    echo "[2/3] Stopping existing container (if any)..."
    docker stop cccd-scanner-app 2>/dev/null || true
    docker rm cccd-scanner-app 2>/dev/null || true

    echo
    echo "[3/3] Starting new container..."
    if ! docker run -d \
        --name cccd-scanner-app \
        -p 8501:8501 \
        --restart unless-stopped \
        cccd-scanner:latest; then
        echo "ERROR: Failed to start container!"
        exit 1
    fi
}

# Function to use docker-compose
use_compose() {
    echo "Using Docker Compose..."
    if ! docker-compose up --build -d; then
        echo "ERROR: Failed to start with docker-compose!"
        exit 1
    fi
}

# Main script
check_docker

echo "Choose deployment method:"
echo "1) Docker command"
echo "2) Docker Compose"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        build_and_run
        ;;
    2)
        use_compose
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo
echo "========================================"
echo "SUCCESS! CCCD Scanner is running!"
echo "========================================"
echo
echo "Access the application at: http://localhost:8501"
echo
echo "Useful commands:"
echo "  View logs:    docker logs cccd-scanner-app"
echo "  Stop app:     docker stop cccd-scanner-app"
echo "  Remove app:   docker rm cccd-scanner-app"
echo
echo "Or with docker-compose:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Rebuild:      docker-compose up --build -d"