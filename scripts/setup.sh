#!/bin/bash

# Smart Research Hub - Setup Script

echo "==================================="
echo "Smart Research Hub - Setup"
echo "==================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/uploads backend/logs backend/models
echo "✅ Directories created"

# Build and start containers
echo "🐳 Building and starting Docker containers..."
docker compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo "✅ All services are running!"
    echo ""
    echo "==================================="
    echo "Access the application:"
    echo "- API: http://localhost:8000"
    echo "- API Docs: http://localhost:8000/api/v1/docs"
    echo "- Health Check: http://localhost:8000/health"
    echo "==================================="
    echo ""
    echo "View logs: docker compose logs -f"
    echo "Stop services: docker compose down"
else
    echo "❌ Some services failed to start. Check logs with: docker compose logs"
    exit 1
fi
