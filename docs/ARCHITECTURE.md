# Vampires Bot Architecture

## Overview

Vampires Bot is a Telegram bot built with aiogram 3.x for managing political districts and actions. The bot uses a modular architecture with clear separation of concerns, PostgreSQL database, and comprehensive Russian localization.

## Core Components

### 1. Application Layer
- **Entry Point**: `app.py` - Main application startup and configuration
- **Configuration**: `config.py` - Environment-based configuration management
- **Logging**: `logging_config.py` - Centralized logging configuration

### 2. Bot Framework Layer
- **Routes**: `routes/` - Command handlers and message routing
  - `start.py` - Start command and main menu
  - `options.py` - Options and settings
  - `universal.py` - Universal handlers
  - `start_support.py` - Support functionality
- **Middlewares**: `middlewares/` - Request processing middleware
  - `timing.py` - Request timing and performance monitoring
  - `user_registration.py` - Automatic user registration
- **States**: `states/` - FSM (Finite State Machine) state management
  - `registration.py` - Registration states
  - `communicate.py` - Communication states
  - `scout.py` - Scouting states
- **Keyboards**: `keyboards/` - Inline keyboard components
  - `renderer.py` - Keyboard rendering engine
  - `presets.py` - Predefined keyboard layouts
  - `spec.py` - Keyboard specifications
  - `presets_actions_stats.py` - Action statistics keyboards

### 3. Business Logic Layer
- **Screens**: `screens/` - UI screen components and templates
  - `base.py` - Base screen class with common functionality
  - `main_menu.py` - Main menu screen
  - `profile.py` - User profile and status screen
  - `actions.py` - Actions management screen
  - `district_list.py` - District listing and management
  - `news_list.py` - News management screen
  - `communicate_screen.py` - Communication features
  - `registration_screen.py` - User registration screen
  - `scout_action.py` - Scouting action interface
  - `settings_action.py` - Action settings and configuration
  - `notify_screen.py` - Notification interface
- **Services**: `services/` - Business logic and data processing
  - `message_store.py` - Message storage and retrieval
  - `notify.py` - Notification service
- **Text Handlers**: `text_handlers/` - Text message processing
  - `register_name.py` - Name registration handling
  - `communicate.py` - Communication message handling
  - `scout_info.py` - Scouting information processing
- **Options**: `options/` - Configuration options and feature flags
  - `registry.py` - Options registry and management
  - `main_menu.py` - Main menu options
  - `actions_menu.py` - Actions menu options
  - `district_list_menu.py` - District list options
  - `news_list.py` - News list options
  - `scout_menu.py` - Scout menu options
  - `communicate.py` - Communication options
  - `actions_stats.py` - Action statistics options
  - `action_setup_menu.py` - Action setup options

### 4. Data Layer
- **Models**: `db/models.py` - SQLAlchemy database models
- **Session**: `db/session.py` - Database session management
- **Config**: `db/config.py` - Database configuration
- **Migrations**: `alembic/` - Database schema migrations

### 5. Presentation Layer
- **Templates**: `templates/` - Jinja2 message templates
- **Localization**: Russian language support with template system

### 6. Utility Layer
- **Utils**: `utils/` - Utility functions
  - `callback.py` - Callback data utilities
  - `render.py` - Rendering utilities

## Data Flow

```
User Message → Middleware → Router → Handler → Screen/Service → Database
                ↓
            Logging & Timing
```

### Detailed Flow

1. **User Input**: Telegram message or callback
2. **Middleware Processing**: 
   - Timing middleware records request start time
   - User registration middleware ensures user exists in database
3. **Routing**: Message routed to appropriate handler
4. **Handler Processing**: 
   - Command handlers for `/start`, etc.
   - Callback handlers for inline keyboards
   - Text handlers for FSM states
5. **Screen Rendering**: UI components render responses
6. **Database Operations**: CRUD operations via SQLAlchemy
7. **Response**: Formatted message sent back to user
8. **Logging**: Request completion and timing logged

## Key Design Patterns

### 1. Screen Pattern
Screens encapsulate UI logic and template rendering:
```python
class BaseScreen:
    async def run(self, message, actor, state, force_new=False):
        # Main execution method
        result = await self._render(message, actor, state)
        return result
    
    async def _render(self, message, actor, state):
        # UI logic here
        return await self._send_message(message, text, keyboard)
```

### 2. Middleware Pattern
Middlewares handle cross-cutting concerns:
- **TimingMiddleware**: Request timing and performance monitoring
- **UserRegistrationMiddleware**: Automatic user registration and validation

### 3. Service Pattern
Services contain business logic:
- Data processing and validation
- External API integration
- Complex business rules
- Message storage and retrieval

### 4. Options Pattern
Flexible configuration system:
- Options are defined with decorators
- Can be toggled at runtime
- Support for different value types
- Centralized registry management

### 5. Repository Pattern
Database models act as repositories:
- Encapsulate data access logic
- Provide clean interfaces for data operations
- Handle relationships and constraints

## Database Schema

### Core Entities

1. **Users** - Bot users and their profiles
   - Telegram ID, username, names
   - Game stats: money, influence, information, force
   - Ideology and faction
   - Action limits and refresh timers
   - Admin status

2. **Districts** - Political districts
   - Name and description
   - Creation and update timestamps

3. **Actions** - Political actions and activities
   - Action type, title, status
   - Owner and district relationships
   - Resource costs: force, money, influence, information
   - Ideology shift functionality
   - Parent-child action relationships

4. **Politicians** - Politician data
   - Name and district association
   - Creation and update timestamps

5. **News** - News articles and updates
   - Title, content, district association
   - Creation and update timestamps

6. **UserScoutsDistrict** - User-district relationships
   - Many-to-many scouting relationships
   - Permissions and access control

### Relationships

- Users can be associated with multiple districts (scouting)
- Actions belong to users and optionally to districts
- Politicians can be associated with districts
- News can be related to districts or actions
- Actions can have parent-child relationships

## Configuration Management

### Environment Variables
- `BOT_TOKEN` - Telegram bot token
- `LOG_LEVEL` - Logging level
- `DEFAULT_LOCALIZATION` - Default language
- `DATABASE_URL` - Database connection string
- `TEMPLATE_ROOT` - Template directory
- `BOT_NAME` - Bot display name

### Options System
The bot uses a flexible options system for feature flags and configuration:
- Options are defined with decorators
- Can be toggled at runtime
- Support for different value types
- Centralized registry for management

## Error Handling

### Global Error Handling
- All unhandled exceptions are caught and logged
- User-friendly error messages are sent to users
- Detailed error information is logged for debugging
- Graceful degradation for non-critical errors

### Database Error Handling
- Connection errors are handled gracefully
- Transaction rollbacks on errors
- Proper error propagation
- Retry mechanisms for transient failures

## Security Considerations

### Input Validation
- All user inputs are validated
- SQL injection prevention through ORM
- XSS prevention in templates
- Rate limiting for user actions

### Authentication
- Telegram user ID validation
- Session management
- Access control for sensitive operations
- Admin role verification

### Data Protection
- Sensitive data encryption
- Secure database connections
- Environment variable protection
- Audit logging for sensitive operations

## Performance Considerations

### Database Optimization
- Proper indexing on frequently queried fields
- Connection pooling
- Query optimization
- Lazy loading for relationships

### Caching
- Template caching
- Database query result caching
- Session data caching
- Keyboard layout caching

### Monitoring
- Request timing middleware
- Database query monitoring
- Error rate tracking
- Performance metrics collection

## Deployment Architecture

### Docker Setup
- Multi-container setup with PostgreSQL
- Automatic database migrations
- Health checks and monitoring
- Persistent data storage
- Network isolation

### Scaling Considerations
- Stateless application design
- Database connection pooling
- Horizontal scaling support
- Load balancing ready
- Microservices architecture potential

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

## Technology Stack

### Core Technologies
- **Framework**: aiogram 3.x (Async Telegram Bot API)
- **Database**: PostgreSQL with SQLAlchemy 2.x
- **Migrations**: Alembic
- **Templates**: Jinja2 with Russian localization
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.10+

### Supporting Technologies
- **Excel Integration**: openpyxl for data import/export
- **Async Support**: asyncio and asyncpg
- **Configuration**: python-dotenv
- **Validation**: Pydantic
- **Logging**: Python logging module

## Future Architecture Considerations

### Microservices Potential
- Separate services for different domains
- API gateway for external access
- Event-driven architecture
- Service mesh for communication

### Advanced Features
- Real-time notifications
- Web interface for administration
- Advanced analytics and reporting
- Multi-language support expansion
- API endpoints for external integrations

### Performance Improvements
- Redis caching layer
- Database read replicas
- CDN for static assets
- Advanced monitoring and alerting
- Automated scaling