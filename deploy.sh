#!/bin/bash

# BerhanAdvisor News API Deployment Script

set -e

echo "🚀 Deploying BerhanAdvisor News API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip first."
    exit 1
fi

print_status "pip3 found: $(pip3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_status "Creating directories..."
mkdir -p images logs

# Run tests
print_status "Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    print_status "All tests passed!"
else
    print_error "Tests failed. Please check the errors above."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating default configuration..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./news.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Scraping Configuration
SCRAPING_INTERVAL=3600
RATE_LIMIT_DELAY=2

# Storage Configuration
IMAGE_STORAGE_PATH=./images

# Logging Configuration
LOG_LEVEL=INFO
EOF
    print_status "Created default .env file"
fi

# Initialize database
print_status "Initializing database..."
python -c "from database import db_manager; db_manager.create_tables()"

print_status "Deployment completed successfully!"
echo ""
echo "🌐 To start the API server, run:"
echo "   source venv/bin/activate"
echo "   python start.py"
echo ""
echo "📚 API documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔍 To test the system, run:"
echo "   python test_system.py"
echo ""
echo "🐳 To deploy with Docker, run:"
echo "   docker-compose up -d" 