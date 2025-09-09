#!/bin/bash

# Vampires Bot Setup Script
echo "🔧 Setting up Vampires Bot..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install aiogram jinja2 sqlalchemy alembic aiosqlite asyncpg pydantic python-dotenv openpyxl

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Logging Configuration
LOG_LEVEL=INFO

# Localization
DEFAULT_LOCALIZATION=en

# Template Configuration
TEMPLATE_ROOT=templates

# Bot Name (optional)
BOT_NAME=Vampires Bot
EOF
    echo "⚠️  Please update your bot token in .env file"
fi

echo "✅ Setup completed!"
echo "📋 Next steps:"
echo "   1. Get your bot token from @BotFather on Telegram"
echo "   2. Update BOT_TOKEN in .env file"
echo "   3. Run ./start.sh to start the bot"
