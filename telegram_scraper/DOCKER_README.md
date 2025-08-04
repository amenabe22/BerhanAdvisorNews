# Telegram Scraper - Docker Deployment

This guide explains how to deploy the Telegram Scraper using Docker.

## Prerequisites

1. **Docker and Docker Compose** installed on your system
2. **Telegram API credentials** from https://my.telegram.org/apps
3. **Google Cloud Storage credentials** (optional, for image storage)

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to the telegram_scraper directory
cd telegram_scraper

# Copy environment file
cp env.example .env

# Edit the environment file with your credentials
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:

```env
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here

# Google Cloud Storage (Optional)
GCS_BUCKET_NAME=your_bucket_name
GCS_CREDENTIALS_PATH=/app/credentials/your-service-account.json
```

### 3. Setup Credentials (Optional)

If using Google Cloud Storage:

```bash
# Create credentials directory
mkdir -p credentials

# Copy your GCS service account JSON file
cp path/to/your/service-account.json credentials/
```

### 4. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f
```

### 5. Access the Application

- **API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs
- **News Feed**: http://localhost:8003/news_feed.html

## Docker Commands

### Basic Operations

```bash
# Start the service
docker-compose up -d

# Stop the service
docker-compose down

# View logs
docker-compose logs -f

# Restart the service
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```

### Database Operations

```bash
# Clear database
docker-compose exec telegram-scraper python3 main.py clear

# Initialize database
docker-compose exec telegram-scraper python3 main.py init

# Scrape posts
docker-compose exec telegram-scraper python3 main.py scrape
```

### Container Management

```bash
# Enter the container
docker-compose exec telegram-scraper bash

# View container status
docker-compose ps

# View resource usage
docker stats telegram-scraper
```

## Volume Mounts

The following directories are mounted as volumes:

- `./data` → Database files
- `./logs` → Application logs
- `./images` → Downloaded images
- `./telegram_session` → Telegram session files
- `./credentials` → GCS credentials (read-only)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_API_ID` | Telegram API ID | Required |
| `TELEGRAM_API_HASH` | Telegram API Hash | Required |
| `TELEGRAM_PHONE` | Phone number | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./telegram_news.db` |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket | Optional |
| `GCS_CREDENTIALS_PATH` | Path to GCS credentials | Optional |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `RATE_LIMIT_DELAY` | Delay between requests | `2` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs telegram-scraper
   
   # Check environment variables
   docker-compose exec telegram-scraper env
   ```

2. **Database issues**
   ```bash
   # Reinitialize database
   docker-compose exec telegram-scraper python3 main.py init --force
   ```

3. **Telegram authentication issues**
   ```bash
   # Check session files
   ls -la telegram_session/
   
   # Remove session and restart
   rm telegram_session/*
   docker-compose restart
   ```

4. **Permission issues**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER data logs images telegram_session
   ```

### Health Check

The container includes a health check that monitors the API:

```bash
# Check health status
docker-compose ps

# Manual health check
curl http://localhost:8003/api/v1/health
```

## Production Deployment

For production deployment, consider:

1. **Use PostgreSQL** instead of SQLite
2. **Set up proper logging** with log rotation
3. **Configure reverse proxy** (nginx)
4. **Set up monitoring** (Prometheus/Grafana)
5. **Use secrets management** for credentials

### Example Production docker-compose.yml

```yaml
version: '3.8'

services:
  telegram-scraper:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/telegram_news
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=telegram_news
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Security Notes

- The container runs as a non-root user
- Credentials are mounted as read-only
- Health checks monitor application status
- Restart policy prevents crashes 