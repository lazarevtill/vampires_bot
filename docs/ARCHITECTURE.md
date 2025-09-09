# Vampires Bot Architecture

## Overview

Vampires Bot is a Telegram bot built with aiogram 3.x for managing political districts and actions. The bot uses a modular architecture with clear separation of concerns.

## Core Components

### 1. Application Layer
- **Entry Point**: `app.py` - Main application startup and configuration
- **Configuration**: `config.py` - Environment-based configuration management
- **Logging**: `logging_config.py` - Centralized logging configuration

### 2. Bot Framework Layer
- **Routes**: `routes/` - Command handlers and message routing
- **Middlewares**: `middlewares/` - Request processing middleware
- **States**: `states/` - FSM (Finite State Machine) state management
- **Keyboards**: `keyboards/` - Inline keyboard components

### 3. Business Logic Layer
- **Screens**: `screens/` - UI screen components and templates
- **Services**: `services/` - Business logic and data processing
- **Text Handlers**: `text_handlers/` - Text message processing
- **Options**: `options/` - Configuration options and feature flags

### 4. Data Layer
- **Models**: `db/models.py` - SQLAlchemy database models
- **Session**: `db/session.py` - Database session management
- **Migrations**: `alembic/` - Database schema migrations

### 5. Presentation Layer
- **Templates**: `templates/` - Jinja2 message templates
- **Localization**: Russian language support

## Data Flow

```
User Message → Middleware → Router → Handler → Screen/Service → Database
                ↓
            Logging & Timing
```

## Key Design Patterns

### 1. Screen Pattern
Screens encapsulate UI logic and template rendering:
```python
class MainMenuScreen(BaseScreen):
    async def _render(self, message, actor, state):
        # UI logic here
        return await self._send_message(message, text, keyboard)
```

### 2. Middleware Pattern
Middlewares handle cross-cutting concerns:
- **TimingMiddleware**: Request timing and performance monitoring
- **UserRegistrationMiddleware**: Automatic user registration

### 3. Service Pattern
Services contain business logic:
- Data processing
- External API integration
- Complex business rules

### 4. Repository Pattern
Database models act as repositories:
- Encapsulate data access logic
- Provide clean interfaces for data operations

## Database Schema

### Core Entities

1. **Users** - Bot users and their profiles
2. **Districts** - Political districts
3. **Actions** - Political actions and activities
4. **Politicians** - Politician information
5. **News** - News articles and updates
6. **UserScoutsDistrict** - User-district relationships

### Relationships

- Users can be associated with multiple districts
- Actions belong to users and districts
- Politicians can be associated with districts
- News can be related to districts or actions

## Configuration Management

### Environment Variables
- `BOT_TOKEN` - Telegram bot token
- `LOG_LEVEL` - Logging level
- `DEFAULT_LOCALIZATION` - Default language
- `DATABASE_URL` - Database connection string

### Options System
The bot uses a flexible options system for feature flags and configuration:
- Options are defined with decorators
- Can be toggled at runtime
- Support for different value types

## Error Handling

### Global Error Handling
- All unhandled exceptions are caught and logged
- User-friendly error messages are sent to users
- Detailed error information is logged for debugging

### Database Error Handling
- Connection errors are handled gracefully
- Transaction rollbacks on errors
- Proper error propagation

## Security Considerations

### Input Validation
- All user inputs are validated
- SQL injection prevention through ORM
- XSS prevention in templates

### Authentication
- Telegram user ID validation
- Session management
- Access control for sensitive operations

## Performance Considerations

### Database Optimization
- Proper indexing on frequently queried fields
- Connection pooling
- Query optimization

### Caching
- Template caching
- Database query result caching
- Session data caching

### Monitoring
- Request timing middleware
- Database query monitoring
- Error rate tracking

## Deployment Architecture

### Docker Setup
- Multi-container setup with PostgreSQL
- Automatic database migrations
- Health checks and monitoring
- Persistent data storage

### Scaling Considerations
- Stateless application design
- Database connection pooling
- Horizontal scaling support
- Load balancing ready

## Development Workflow

### Local Development
1. Use Docker Compose for consistent environment
2. Automatic database migrations on startup
3. Hot reloading for development
4. Comprehensive logging

### Testing
- Unit tests for business logic
- Integration tests for database operations
- End-to-end tests for bot functionality
- Docker-based testing environment

### Deployment
- Docker-based deployment
- Environment-specific configurations
- Database migration automation
- Health monitoring and alerting
