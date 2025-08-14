# Docker Setup for Telegram Scraper

This guide shows how to run the Telegram Scraper with PostgreSQL using Docker.

## Quick Start

1. **Build and run the services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the API:**
   - API: http://localhost:8003
   - Health check: http://localhost:8003/api/v1/health

3. **Database:**
   - PostgreSQL: localhost:5432
   - Database: `telegram_news`
   - User: `telegram_user`
   - Password: `telegram_password`

## Services

- **postgres**: PostgreSQL 15 database
- **telegram-scraper**: Main application API

## Environment Variables

The main configuration is in `docker-compose.yml`. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `API_HOST`: API host (0.0.0.0 for Docker)
- `API_PORT`: API port (8000 internally)

## Database Migrations

Database migrations run automatically on startup using Alembic.

## Volumes

- `postgres_data`: PostgreSQL data persistence
- `./data`: Application data
- `./logs`: Application logs
- `./images`: Downloaded images

## Troubleshooting

1. **Database connection issues:**
   - Check if PostgreSQL container is running: `docker-compose ps`
   - Check logs: `docker-compose logs postgres`

2. **Application issues:**
   - Check logs: `docker-compose logs telegram-scraper`
   - Ensure database is ready before app starts

3. **Port conflicts:**
   - Change port mapping in `docker-compose.yml` if 8003 is in use
