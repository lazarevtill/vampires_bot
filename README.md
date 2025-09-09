# Vampires Bot

A Telegram bot built with aiogram for managing political districts and actions.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Get your bot token:**
   - Go to [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot or use existing one
   - Copy the bot token

2. **Configure environment:**
   ```bash
   cp .env.docker .env
   # Edit .env and replace 'your_bot_token_here' with your actual token
   ```

3. **Start with Docker:**
   ```bash
   ./start-docker.sh
   ```

### Option 2: Local Development

1. **Setup:**
   ```bash
   ./setup.sh
   ```

2. **Configure Bot Token:**
   - Edit `.env` file and replace `your_bot_token_here` with your actual token

3. **Run the Bot:**
   ```bash
   ./start.sh
   ```

## 🐳 Docker Setup

The Docker setup includes:
- **PostgreSQL Database** - Production-ready database
- **Automatic Migrations** - Database schema is automatically applied
- **Health Checks** - Ensures services are running properly
- **Logging** - Centralized logging with volume mounts

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bot
docker-compose logs -f postgres

# Stop services
docker-compose down

# Restart bot only
docker-compose restart bot

# Check service status
docker-compose ps
```

### Database Management

```bash
# Access PostgreSQL directly
docker-compose exec postgres psql -U bot_user -d vampires_bot

# Run migrations manually
docker-compose exec bot alembic upgrade head

# Create new migration
docker-compose exec bot alembic revision --autogenerate -m "Description"
```

## Project Structure

- `app.py` - Main bot application
- `config.py` - Configuration management
- `routes/` - Bot command handlers
- `middlewares/` - Middleware components
- `templates/` - Message templates
- `db/` - Database models and operations
- `services/` - Business logic services
- `keyboards/` - Inline keyboards
- `states/` - FSM states
- `text_handlers/` - Text message handlers

## Features

- User registration and management
- District management
- Political actions tracking
- News system
- Excel import/export functionality
- Multi-language support

## Database

The bot uses SQLite database (`bot.db`) with the following tables:
- `users` - User information
- `districts` - Political districts
- `actions` - Political actions
- `politicians` - Politician data
- `news` - News articles
- `user_scouts_districts` - User-district relationships

## Requirements

- Python 3.10+
- Telegram Bot Token
- All dependencies listed in `pyproject.toml`
