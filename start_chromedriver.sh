#!/bin/bash

echo "🚀 Starting ChromeDriver Docker container..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if container is already running
if docker ps | grep -q "berhan-news-chromedriver"; then
    echo "✅ ChromeDriver container is already running"
    exit 0
fi

# Build and start the container
echo "🔨 Building ChromeDriver container..."
docker-compose -f docker-compose.selenium.yml build

echo "🚀 Starting ChromeDriver container..."
docker-compose -f docker-compose.selenium.yml up -d

# Wait for container to be ready
echo "⏳ Waiting for ChromeDriver to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:4444/status > /dev/null 2>&1; then
        echo "✅ ChromeDriver is ready!"
        echo "🌐 ChromeDriver URL: http://localhost:4444"
        echo "🔍 VNC URL (for debugging): http://localhost:7900"
        exit 0
    fi
    echo "⏳ Waiting... ($i/30)"
    sleep 2
done

echo "❌ ChromeDriver failed to start within 60 seconds"
exit 1 