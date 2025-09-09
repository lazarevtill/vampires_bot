# Vampires Bot

A sophisticated Telegram bot built with aiogram 3.x for managing political districts and actions. Features a modular architecture with PostgreSQL database, Docker deployment, and comprehensive Russian localization.

## ✨ Features

- **Political District Management** - Create and manage political districts
- **Action Tracking** - Track political actions and activities
- **User Registration** - Comprehensive user management system
- **News System** - Distribute news and updates
- **Multi-language Support** - Russian localization with template system
- **Database Migrations** - Automatic schema management with Alembic
- **Docker Deployment** - Production-ready containerized setup
- **Health Monitoring** - Built-in health checks and logging

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
- **PostgreSQL Database** - Production-ready database with persistent storage
- **Automatic Migrations** - Database schema is automatically applied on startup
- **Health Checks** - Ensures services are running properly
- **Logging** - Centralized logging with volume mounts
- **Security** - Non-root containers and network isolation

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

# Test Docker setup
./test-docker.sh
```

### Database Management

```bash
# Access PostgreSQL directly
docker-compose exec postgres psql -U bot_user -d vampires_bot

# Run migrations manually
docker-compose exec bot alembic upgrade head

# Create new migration
docker-compose exec bot alembic revision --autogenerate -m "Description"

# Check migration status
docker-compose exec bot alembic current
```

## 📁 Project Structure

```
vampires_bot/
├── app.py                 # Main bot application entry point
├── config.py              # Configuration management
├── logging_config.py      # Logging configuration
├── routes/                # Bot command handlers and routing
├── middlewares/           # Middleware components (timing, user registration)
├── screens/               # UI screen components and templates
├── templates/             # Jinja2 message templates (Russian localization)
├── db/                    # Database models and operations
│   ├── models.py          # SQLAlchemy database models
│   ├── session.py         # Database session management
│   └── config.py          # Database configuration
├── services/              # Business logic services
├── keyboards/             # Inline keyboard components
├── states/                # FSM (Finite State Machine) states
├── text_handlers/         # Text message handlers
├── options/               # Configuration options system
├── utils/                 # Utility functions
├── alembic/               # Database migrations
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Bot container definition
├── docker-entrypoint.sh   # Container startup script
├── start-docker.sh        # Easy Docker startup
├── test-docker.sh         # Docker testing suite
└── docs/                  # Comprehensive documentation
```

## 🗄️ Database Schema

The bot uses PostgreSQL with the following main entities:

- **Users** - User registration and profile information
- **Districts** - Political districts management
- **Actions** - Political actions and activities
- **Politicians** - Politician data and information
- **News** - News articles and updates
- **UserScoutsDistrict** - Many-to-many relationships between users and districts

## 🛠️ Technology Stack

- **Framework**: aiogram 3.x (Async Telegram Bot API)
- **Database**: PostgreSQL with SQLAlchemy 2.x
- **Migrations**: Alembic
- **Templates**: Jinja2 with Russian localization
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.10+
- **Architecture**: Modular with clear separation of concerns

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed system architecture
- **[API Documentation](docs/API.md)** - Internal API and interfaces
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development and contribution guidelines
- **[Docker Guide](DOCKER.md)** - Complete Docker setup documentation

## 🔧 Development

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Git

### Development Workflow

1. **Fork and clone the repository**
2. **Switch to Docker branch**: `git checkout feature/docker-postgresql-setup`
3. **Setup environment**: `cp .env.docker .env` and configure your bot token
4. **Start development**: `./start-docker.sh`
5. **Make changes and test**: `./test-docker.sh`

### Code Quality

- Type hints for all functions
- PEP 8 style guidelines
- Comprehensive error handling
- Async/await patterns
- Database transaction management

## 🚀 Deployment

### Production Deployment

1. **Server Setup**: Install Docker and Docker Compose
2. **Configuration**: Set up environment variables and secrets
3. **Deploy**: Use Docker Compose with production configuration
4. **Monitor**: Use built-in health checks and logging

### Scaling

- Horizontal scaling with multiple bot instances
- Database read replicas for high availability
- Load balancing with nginx or traefik
- Connection pooling for database optimization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details on:

- Development setup
- Coding standards
- Testing procedures
- Pull request process
- Code of conduct

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/vampires_bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/vampires_bot/discussions)
- **Documentation**: Check the `docs/` directory for comprehensive guides

## 🎯 Roadmap

- [ ] Web interface for administration
- [ ] Advanced analytics and reporting
- [ ] Multi-language support expansion
- [ ] API endpoints for external integrations
- [ ] Advanced user role management
- [ ] Real-time notifications system
