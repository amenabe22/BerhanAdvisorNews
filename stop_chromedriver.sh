#!/bin/bash

echo "🛑 Stopping ChromeDriver Docker container..."

# Check if container is running
if docker ps | grep -q "berhan-news-chromedriver"; then
    echo "🛑 Stopping ChromeDriver container..."
    docker-compose -f docker-compose.selenium.yml down
    echo "✅ ChromeDriver container stopped"
else
    echo "ℹ️  ChromeDriver container is not running"
fi 