# Vampires Bot

A Telegram bot built with aiogram for managing political districts and actions.

## Quick Start

### 1. Setup
```bash
./setup.sh
```

### 2. Configure Bot Token
1. Go to [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot or use existing one
3. Copy the bot token
4. Edit `.env` file and replace `your_bot_token_here` with your actual token

### 3. Run the Bot
```bash
./start.sh
```

## Manual Setup

If you prefer manual setup:

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install aiogram jinja2 sqlalchemy alembic aiosqlite asyncpg pydantic python-dotenv openpyxl
   ```

3. **Configure environment:**
   - Copy `.env` file and update `BOT_TOKEN` with your bot token

4. **Run the bot:**
   ```bash
   python app.py
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
