#!/bin/bash

# Vampires Bot Startup Script
echo "🤖 Starting Vampires Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your bot token."
    exit 1
fi

# Check if bot token is set
if grep -q "your_bot_token_here" .env; then
    echo "⚠️  Please update your bot token in .env file before running the bot."
    echo "   Get your token from @BotFather on Telegram"
    exit 1
fi

# Start the bot
echo "🚀 Starting bot..."
python app.py
