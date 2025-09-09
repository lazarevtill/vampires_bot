# Docker Setup Guide

This guide covers the complete Docker setup for the Vampires Bot, including database migrations and production deployment.

## 🏗️ Architecture

The Docker setup consists of:

- **Bot Container** - Python application with aiogram
- **PostgreSQL Database** - Production-ready database with persistent storage
- **Automatic Migrations** - Alembic migrations run on startup
- **Health Checks** - Ensures services are running properly
- **Logging** - Centralized logging with volume mounts

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## 🚀 Quick Start

1. **Clone and configure:**
   ```bash
   git clone <repository>
   cd vampires_bot
   cp .env.docker .env
   ```

2. **Update bot token:**
   ```bash
   # Edit .env file
   nano .env
   # Replace 'your_bot_token_here' with your actual token
   ```

3. **Start services:**
   ```bash
   ./start-docker.sh
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | Required |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEFAULT_LOCALIZATION` | Bot language | `ru` |
| `BOT_NAME` | Bot display name | `Vampires Bot` |
| `DATABASE_URL` | Database connection string | Auto-configured |

### Database Configuration

The Docker setup automatically configures:
- **Database**: `vampires_bot`
- **User**: `bot_user`
- **Password**: `bot_password`
- **Host**: `postgres` (internal Docker network)
- **Port**: `5432`

## 🗄️ Database Migrations

### Automatic Migrations

Migrations run automatically when the bot container starts:
1. Wait for database to be ready
2. Run `alembic upgrade head`
3. Start the bot application

### Manual Migration Commands

```bash
# Check current migration status
docker-compose exec bot alembic current

# View migration history
docker-compose exec bot alembic history

# Create new migration
docker-compose exec bot alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec bot alembic upgrade head

# Rollback migration
docker-compose exec bot alembic downgrade -1
```

## 📊 Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Bot only
docker-compose logs -f bot

# Database only
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 bot
```

### Health Checks

```bash
# Check service status
docker-compose ps

# Check bot health
docker-compose exec bot python -c "import sys; sys.exit(0)"

# Check database connection
docker-compose exec postgres pg_isready -U bot_user -d vampires_bot
```

## 🔄 Development Workflow

### Making Changes

1. **Code changes:**
   ```bash
   # Make your changes to the code
   # Rebuild and restart
   docker-compose up --build -d
   ```

2. **Database changes:**
   ```bash
   # Create migration
   docker-compose exec bot alembic revision --autogenerate -m "Add new feature"
   
   # Apply migration
   docker-compose exec bot alembic upgrade head
   ```

### Debugging

```bash
# Access bot container shell
docker-compose exec bot bash

# Access database
docker-compose exec postgres psql -U bot_user -d vampires_bot

# Check environment variables
docker-compose exec bot env
```

## 🚀 Production Deployment

### Security Considerations

1. **Change default passwords:**
   ```yaml
   # In docker-compose.yml
   environment:
     POSTGRES_PASSWORD: your_secure_password
   ```

2. **Use secrets management:**
   ```yaml
   # Use Docker secrets or external secret management
   environment:
     BOT_TOKEN_FILE: /run/secrets/bot_token
   ```

3. **Network security:**
   ```yaml
   # Don't expose database port in production
   postgres:
     ports: []  # Remove port mapping
   ```

### Performance Optimization

1. **Resource limits:**
   ```yaml
   services:
     bot:
       deploy:
         resources:
           limits:
             memory: 512M
             cpus: '0.5'
   ```

2. **Database optimization:**
   ```yaml
   postgres:
     environment:
       POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
   ```

## 🛠️ Troubleshooting

### Common Issues

1. **Bot token invalid:**
   ```
   TokenValidationError: Token is invalid!
   ```
   **Solution:** Check your bot token in `.env` file

2. **Database connection failed:**
   ```
   Connection refused to postgres:5432
   ```
   **Solution:** Ensure postgres service is healthy: `docker-compose ps`

3. **Migration failed:**
   ```
   alembic.util.exc.CommandError: Can't locate revision
   ```
   **Solution:** Check migration files exist in `alembic/versions/`

### Reset Everything

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
./start-docker.sh
```

## 📁 File Structure

```
vampires_bot/
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Bot container definition
├── docker-entrypoint.sh    # Container startup script
├── .env.docker            # Docker environment template
├── init-db.sql            # Database initialization
├── alembic/               # Database migrations
│   ├── versions/          # Migration files
│   ├── env.py            # Alembic environment
│   └── script.py.mako    # Migration template
└── logs/                  # Application logs (mounted volume)
```

## 🔗 Useful Commands

```bash
# Quick start
./start-docker.sh

# View logs
docker-compose logs -f bot

# Restart bot
docker-compose restart bot

# Stop everything
docker-compose down

# Clean restart
docker-compose down && docker-compose up -d

# Check status
docker-compose ps

# Access database
docker-compose exec postgres psql -U bot_user -d vampires_bot
```
