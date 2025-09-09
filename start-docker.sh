#!/bin/bash

# Docker Startup Script for Vampires Bot
echo "🐳 Starting Vampires Bot with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.docker .env
    echo "⚠️  Please update your bot token in .env file before running the bot."
    echo "   Get your token from @BotFather on Telegram"
    exit 1
fi

# Check if bot token is set
if grep -q "your_bot_token_here" .env; then
    echo "⚠️  Please update your bot token in .env file before running the bot."
    echo "   Get your token from @BotFather on Telegram"
    exit 1
fi

# Build and start the services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "✅ Bot is starting up!"
echo "📋 Useful commands:"
echo "   docker-compose logs -f bot    # View bot logs"
echo "   docker-compose logs -f postgres  # View database logs"
echo "   docker-compose down           # Stop all services"
echo "   docker-compose restart bot    # Restart bot only"
echo ""
echo "🔍 To view logs: docker-compose logs -f bot"
