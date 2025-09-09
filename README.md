# Vampires Bot

A sophisticated Telegram bot built with aiogram 3.x for managing political districts and actions. Features a modular architecture with PostgreSQL database, Docker deployment, and comprehensive Russian localization.

## ✨ Features

- **Political District Management** - Create and manage political districts
- **Action Tracking** - Track political actions and activities with ideology shifts
- **User Registration** - Comprehensive user management system with profiles
- **News System** - Distribute news and updates to districts
- **Scouting System** - User-district scouting relationships
- **Multi-language Support** - Russian localization with Jinja2 templates
- **Database Migrations** - Automatic schema management with Alembic
- **Docker Deployment** - Production-ready containerized setup
- **Health Monitoring** - Built-in health checks and logging
- **Excel Integration** - Import/export functionality for data management

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
│   ├── start.py          # Start command and main menu
│   ├── options.py        # Options and settings
│   ├── universal.py      # Universal handlers
│   └── start_support.py  # Support functionality
├── middlewares/           # Middleware components
│   ├── timing.py         # Request timing middleware
│   └── user_registration.py # User registration middleware
├── screens/               # UI screen components and templates
│   ├── base.py           # Base screen class
│   ├── main_menu.py      # Main menu screen
│   ├── profile.py        # User profile screen
│   ├── actions.py        # Actions management
│   ├── district_list.py  # District listing
│   ├── news_list.py      # News management
│   ├── communicate_screen.py # Communication features
│   ├── registration_screen.py # User registration
│   ├── scout_action.py   # Scouting actions
│   ├── settings_action.py # Action settings
│   └── notify_screen.py  # Notifications
├── templates/             # Jinja2 message templates (Russian localization)
├── db/                    # Database models and operations
│   ├── models.py         # SQLAlchemy database models
│   ├── session.py        # Database session management
│   └── config.py         # Database configuration
├── services/              # Business logic services
│   ├── message_store.py  # Message storage service
│   └── notify.py         # Notification service
├── keyboards/             # Inline keyboard components
│   ├── renderer.py       # Keyboard rendering
│   ├── presets.py        # Keyboard presets
│   ├── spec.py           # Keyboard specifications
│   └── presets_actions_stats.py # Action stats keyboards
├── states/                # FSM (Finite State Machine) states
│   ├── registration.py   # Registration states
│   ├── communicate.py    # Communication states
│   └── scout.py          # Scouting states
├── text_handlers/         # Text message handlers
│   ├── register_name.py  # Name registration
│   ├── communicate.py    # Communication handling
│   └── scout_info.py     # Scouting information
├── options/               # Configuration options system
│   ├── registry.py       # Options registry
│   ├── main_menu.py      # Main menu options
│   ├── actions_menu.py   # Actions menu options
│   ├── district_list_menu.py # District list options
│   ├── news_list.py      # News list options
│   ├── scout_menu.py     # Scout menu options
│   ├── communicate.py    # Communication options
│   ├── actions_stats.py  # Action statistics
│   └── action_setup_menu.py # Action setup options
├── utils/                 # Utility functions
│   ├── callback.py       # Callback utilities
│   └── render.py         # Rendering utilities
├── alembic/               # Database migrations
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Bot container definition
├── docker-entrypoint.sh   # Container startup script
├── start-docker.sh        # Easy Docker startup
├── test-docker.sh         # Docker testing suite
├── setup.sh               # Local setup script
├── start.sh               # Local startup script
├── excel_import.py        # Excel import functionality
├── excel_templates.py     # Excel template management
├── commands.py            # Bot commands
└── docs/                  # Comprehensive documentation
```

## 🗄️ Database Schema

The bot uses PostgreSQL with the following main entities:

### Core Models

- **User** - User registration and profile information
  - Telegram ID, username, names
  - Game stats: money, influence, information, force
  - Ideology and faction
  - Action limits and refresh timers
  - Admin status

- **District** - Political districts management
  - Name and description
  - Creation and update timestamps

- **Action** - Political actions and activities
  - Action type, title, status
  - Owner and district relationships
  - Resource costs: force, money, influence, information
  - Ideology shift functionality
  - Parent-child action relationships

- **Politician** - Politician data and information
  - Name and district association

- **News** - News articles and updates
  - Title, content, district association
  - Creation and update timestamps

- **UserScoutsDistrict** - Many-to-many relationships between users and districts
  - Scouting relationships and permissions

## 🛠️ Technology Stack

- **Framework**: aiogram 3.x (Async Telegram Bot API)
- **Database**: PostgreSQL with SQLAlchemy 2.x
- **Migrations**: Alembic
- **Templates**: Jinja2 with Russian localization
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.10+
- **Architecture**: Modular with clear separation of concerns
- **Excel Support**: openpyxl for data import/export

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
- [ ] Advanced scouting features
- [ ] Political simulation enhancements