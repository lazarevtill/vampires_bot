# Contributing to Vampires Bot

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Telegram Bot Token (for testing)
- Git

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/vampires_bot.git
   cd vampires_bot
   ```

2. **Switch to the Docker branch**:
   ```bash
   git checkout feature/docker-postgresql-setup
   ```

3. **Setup development environment**:
   ```bash
   cp .env.docker .env
   # Edit .env with your bot token
   ./start-docker.sh
   ```

4. **Verify setup**:
   ```bash
   ./test-docker.sh
   ```

## Development Workflow

### Branch Strategy

- `feature/docker-postgresql-setup` - Main development branch with Docker setup
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical fixes

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**:
   ```bash
   # Run Docker tests
   ./test-docker.sh
   
   # Run specific tests
   docker-compose exec bot python -m pytest tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

## Coding Standards

### Python Code Style

- Follow PEP 8
- Use type hints for all functions
- Add docstrings for public functions
- Use descriptive variable names
- Maximum line length: 88 characters (Black formatter)

### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check code style
flake8 .
```

### Type Hints

```python
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    pass
```

### Docstrings

```python
async def create_action(
    session: AsyncSession, 
    user_id: int, 
    action_data: Dict[str, Any]
) -> Action:
    """
    Create a new action for a user.
    
    Args:
        session: Database session
        user_id: ID of the user creating the action
        action_data: Action data dictionary
        
    Returns:
        Created Action object
        
    Raises:
        ValidationError: If action data is invalid
        DatabaseError: If database operation fails
    """
    pass
```

## Database Development

### Model Development

1. **Define models in `db/models.py`**:
   ```python
   class NewModel(Base):
       __tablename__ = "new_table"
       
       id = Column(Integer, primary_key=True)
       name = Column(String(255), nullable=False)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

2. **Create migration**:
   ```bash
   docker-compose exec bot alembic revision --autogenerate -m "Add new model"
   ```

3. **Review migration file**:
   ```bash
   # Check generated migration
   cat alembic/versions/latest_migration.py
   ```

4. **Apply migration**:
   ```bash
   docker-compose exec bot alembic upgrade head
   ```

### Database Best Practices

- Use proper foreign key relationships
- Add indexes for frequently queried fields
- Use appropriate data types
- Add constraints for data validation
- Use nullable=False for required fields

## Bot Development

### Adding New Commands

1. **Create handler in `routes/`**:
   ```python
   from aiogram import Router, F
   from aiogram.types import Message
   
   router = Router()
   
   @router.message(F.text == "/newcommand")
   async def new_command_handler(message: Message):
       """Handle new command."""
       await message.answer("New command response")
   ```

2. **Register router in `app.py`**:
   ```python
   from routes.new_module import router as new_router
   dp.include_router(new_router)
   ```

### Adding New Screens

1. **Create screen class**:
   ```python
   from screens.base import BaseScreen
   
   class NewScreen(BaseScreen):
       async def _render(self, message, actor, state):
           text = "Screen content"
           keyboard = self._create_keyboard()
           return await self._send_message(message, text, keyboard)
       
       def _create_keyboard(self):
           # Create inline keyboard
           pass
   ```

2. **Use screen in handlers**:
   ```python
   @router.callback_query(F.data == "new_screen")
   async def show_new_screen(callback: CallbackQuery, state: FSMContext):
       await NewScreen().run(
           message=callback.message,
           actor=callback.from_user,
           state=state
       )
   ```

### Adding New Middleware

1. **Create middleware class**:
   ```python
   from aiogram import BaseMiddleware
   from aiogram.types import TelegramObject
   
   class NewMiddleware(BaseMiddleware):
       async def __call__(self, handler, event: TelegramObject, data: dict):
           # Pre-processing
           result = await handler(event, data)
           # Post-processing
           return result
   ```

2. **Register middleware in `app.py`**:
   ```python
   from middlewares.new_middleware import NewMiddleware
   dp.update.middleware(NewMiddleware())
   ```

### Adding New Options

1. **Create option class**:
   ```python
   from options.registry import BaseOption
   
   class NewOption(BaseOption):
       name = "new_option"
       title = "New Option"
       description = "Description of the new option"
       
       async def render(self, user: User) -> str:
           return "Option content"
       
       async def handle_callback(self, callback: CallbackQuery, user: User):
           # Handle option callback
           pass
   ```

2. **Register option**:
   ```python
   from options.registry import registry
   
   registry.register("new_option", NewOption())
   ```

## Testing

### Test Structure

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_database.py
│   └── test_api.py
└── e2e/
    └── test_bot_flow.py
```

### Writing Tests

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from services.user_service import UserService

@pytest.mark.asyncio
async def test_create_user(session: AsyncSession):
    """Test user creation."""
    user = await UserService.create_user(
        session=session,
        tg_id=12345,
        username="testuser"
    )
    
    assert user.tg_id == 12345
    assert user.username == "testuser"
    assert user.id is not None
```

### Running Tests

```bash
# Run all tests
docker-compose exec bot python -m pytest

# Run specific test file
docker-compose exec bot python -m pytest tests/unit/test_models.py

# Run with coverage
docker-compose exec bot python -m pytest --cov=. --cov-report=html
```

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Use type hints for better IDE support
- Add inline comments for complex logic
- Update README.md for new features

### API Documentation

- Update `docs/API.md` for new interfaces
- Document all public methods
- Include examples for complex operations
- Update architecture docs for structural changes

### User Documentation

- Update `README.md` for new features
- Add usage examples
- Document configuration options
- Update deployment guides

## Pull Request Process

### Before Submitting

1. **Run tests**:
   ```bash
   ./test-docker.sh
   docker-compose exec bot python -m pytest
   ```

2. **Check code style**:
   ```bash
   black --check .
   isort --check-only .
   flake8 .
   ```

3. **Update documentation**:
   - Update README.md if needed
   - Add docstrings for new functions
   - Update API documentation

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

### Review Process

1. **Automated checks**:
   - Code style validation
   - Test execution
   - Docker build verification

2. **Manual review**:
   - Code quality review
   - Architecture review
   - Security review
   - Performance review

3. **Approval**:
   - At least one approval required
   - All checks must pass
   - No merge conflicts

## Release Process

### Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Steps

1. **Update version**:
   ```bash
   # Update version in pyproject.toml
   # Create release branch
   git checkout -b release/v1.0.0
   ```

2. **Create release notes**:
   ```markdown
   # Release Notes v1.0.0
   
   ## New Features
   - Feature 1
   - Feature 2
   
   ## Bug Fixes
   - Fix 1
   - Fix 2
   
   ## Breaking Changes
   - Change 1
   ```

3. **Create release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   # Create release on GitHub
   ```

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code reviews and collaboration

### Resources

- [aiogram Documentation](https://docs.aiogram.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards
- Respect different opinions and approaches

## License

This project is licensed under the MIT License - see the LICENSE file for details.