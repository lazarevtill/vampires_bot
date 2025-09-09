# Docker Setup Guide

This guide covers the complete Docker setup for the Vampires Bot, including PostgreSQL database, automatic migrations, and production-ready configuration.

## 🐳 Overview

The Docker setup provides:
- **PostgreSQL Database** - Production-ready database with persistent storage
- **Automatic Migrations** - Database schema applied automatically on startup
- **Health Checks** - Ensures all services are running properly
- **Centralized Logging** - All logs accessible via Docker
- **Security** - Non-root containers and network isolation
- **Easy Management** - Simple commands for all operations

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## 🚀 Quick Start

### 1. Configure Environment

```bash
# Copy the Docker environment template
cp .env.docker .env

# Edit .env with your bot token
nano .env
```

Update the following variables in `.env`:
```bash
BOT_TOKEN=your_actual_bot_token_here
BOT_NAME=Your Bot Name
```

### 2. Start Services

```bash
# Start all services
./start-docker.sh

# Or manually
docker-compose up -d
```

### 3. Verify Setup

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f bot
```

## 🏗️ Architecture

### Services

#### PostgreSQL Database (`postgres`)
- **Image**: `postgres:15-alpine`
- **Port**: 5432
- **Database**: `vampires_bot`
- **User**: `bot_user`
- **Password**: `bot_password`
- **Health Check**: Built-in PostgreSQL health check
- **Volumes**: Persistent data storage

#### Bot Application (`bot`)
- **Build**: Custom Dockerfile
- **Dependencies**: Waits for PostgreSQL to be healthy
- **Environment**: All configuration via environment variables
- **Volumes**: Logs directory mounted
- **Restart Policy**: `unless-stopped`

### Network

- **Network**: `bot_network` (bridge driver)
- **Isolation**: Services communicate internally
- **Security**: No external database access by default

## 📁 File Structure

```
vampires_bot/
├── docker-compose.yml     # Multi-service configuration
├── Dockerfile             # Bot container definition
├── docker-entrypoint.sh   # Startup script with migrations
├── init-db.sql           # PostgreSQL initialization
├── start-docker.sh       # Easy startup script
├── test-docker.sh        # Comprehensive testing
├── .env.docker           # Environment template
└── .dockerignore         # Docker build exclusions
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Telegram bot token | - | ✅ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `DEFAULT_LOCALIZATION` | Default language | `ru` | ❌ |
| `TEMPLATE_ROOT` | Template directory | `templates` | ❌ |
| `BOT_NAME` | Bot display name | `Vampires Bot` | ❌ |
| `DATABASE_URL` | Database connection | Auto-configured | ❌ |

### Docker Compose Configuration

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: vampires_bot
      POSTGRES_USER: bot_user
      POSTGRES_PASSWORD: bot_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bot_user -d vampires_bot"]
      interval: 10s
      timeout: 5s
      retries: 5

  bot:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=postgresql+asyncpg://bot_user:bot_password@postgres:5432/vampires_bot
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## 🛠️ Management Commands

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart bot only
docker-compose restart bot

# View logs
docker-compose logs -f bot
docker-compose logs -f postgres

# Check status
docker-compose ps
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U bot_user -d vampires_bot

# Run migrations manually
docker-compose exec bot alembic upgrade head

# Create new migration
docker-compose exec bot alembic revision --autogenerate -m "Description"

# Check migration status
docker-compose exec bot alembic current

# Backup database
docker-compose exec postgres pg_dump -U bot_user vampires_bot > backup.sql

# Restore database
docker-compose exec -T postgres psql -U bot_user vampires_bot < backup.sql
```

### Development Operations

```bash
# Rebuild bot container
docker-compose build --no-cache bot

# View container logs
docker-compose logs bot --tail=50

# Execute commands in bot container
docker-compose exec bot python -c "print('Hello from container')"

# Access bot container shell
docker-compose exec bot bash
```

## 🧪 Testing

### Automated Testing

```bash
# Run comprehensive Docker tests
./test-docker.sh
```

The test script checks:
- Docker and Docker Compose installation
- Configuration files validity
- Environment setup
- Docker build process
- Database startup and health
- Bot container startup

### Manual Testing

```bash
# Test database connection
docker-compose exec postgres psql -U bot_user -d vampires_bot -c "SELECT 1;"

# Test bot functionality
docker-compose exec bot python -c "
import asyncio
from aiogram import Bot
import os

async def test_bot():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    me = await bot.get_me()
    print(f'Bot: {me.first_name} (@{me.username})')
    await bot.session.close()

asyncio.run(test_bot())
"
```

## 📊 Monitoring

### Health Checks

```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect vampires_bot_db --format='{{.State.Health.Status}}'
docker inspect vampires_bot_app --format='{{.State.Health.Status}}'
```

### Logging

```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f bot
docker-compose logs -f postgres

# View logs with timestamps
docker-compose logs -f -t bot
```

### Performance Monitoring

```bash
# Container resource usage
docker stats

# Database performance
docker-compose exec postgres psql -U bot_user -d vampires_bot -c "
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database WHERE datname = 'vampires_bot';
"
```

## 🔒 Security

### Container Security

- **Non-root user**: Bot runs as `appuser`
- **Network isolation**: Services communicate via internal network
- **Read-only filesystem**: Where possible
- **Minimal base image**: Alpine Linux for PostgreSQL

### Database Security

- **Internal network**: Database not exposed externally
- **Strong passwords**: Use environment variables for credentials
- **Connection limits**: Configured in PostgreSQL
- **Backup encryption**: Use encrypted backups for sensitive data

### Production Security

```bash
# Use Docker secrets for production
echo "your_secure_password" | docker secret create db_password -

# Update docker-compose.yml for production
services:
  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
```

## 🚀 Production Deployment

### Environment Setup

```bash
# Create production environment
cp .env.docker .env.prod

# Set production values
BOT_TOKEN=your_production_token
LOG_LEVEL=WARNING
BOT_NAME=Production Bot Name
```

### Deployment Commands

```bash
# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor deployment
docker-compose logs -f bot

# Verify deployment
docker-compose ps
```

### Scaling

```bash
# Scale bot instances
docker-compose up -d --scale bot=3

# Use load balancer (nginx/traefik)
# Configure reverse proxy for multiple instances
```

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Starting
```bash
# Check logs
docker-compose logs bot

# Common causes:
# - Invalid bot token
# - Database connection issues
# - Missing environment variables
```

#### Database Connection Failed
```bash
# Check database status
docker-compose ps postgres

# Test connection
docker-compose exec postgres pg_isready -U bot_user -d vampires_bot

# Check database logs
docker-compose logs postgres
```

#### Migration Issues
```bash
# Check migration status
docker-compose exec bot alembic current

# Reset migrations (if needed)
docker-compose exec postgres psql -U bot_user -d vampires_bot -c "DELETE FROM alembic_version;"
docker-compose exec bot alembic stamp head
```

### Performance Issues

#### High Memory Usage
```bash
# Check container stats
docker stats

# Optimize memory limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 512M
```

#### Slow Database Queries
```bash
# Check database performance
docker-compose exec postgres psql -U bot_user -d vampires_bot -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [aiogram Documentation](https://docs.aiogram.dev/)

## 🤝 Support

For issues with the Docker setup:
1. Check the logs: `docker-compose logs`
2. Run the test script: `./test-docker.sh`
3. Check the troubleshooting section above
4. Create an issue on GitHub with logs and configuration details