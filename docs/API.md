# Vampires Bot API Documentation

## Overview

This document describes the internal API and interfaces of the Vampires Bot application.

## Core Interfaces

### Configuration API

#### `config.py`
```python
@dataclass
class Config:
    bot_token: str
    log_level: str = "INFO"
    default_localization: str = "en"
    template_root: str = "templates"
    bot_name: str = ""

def load_config() -> Config
```

### Database API

#### `db/session.py`
```python
class Base(DeclarativeBase):
    pass

engine = create_async_engine(url, echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session
```

#### `db/config.py`
```python
@dataclass
class DBConfig:
    url: str

def load_db_config() -> DBConfig
```

### Screen API

#### `screens/base.py`
```python
class BaseScreen:
    async def run(self, message, actor, state, force_new=False):
        """Main screen execution method"""
    
    async def _render(self, message, actor, state):
        """Render screen content"""
    
    async def _send_message(self, message, text, keyboard=None):
        """Send message to user"""
```

### Middleware API

#### `middlewares/timing.py`
```python
class TimingMW:
    async def __call__(self, handler, event, data):
        """Measure request processing time"""
```

#### `middlewares/user_registration.py`
```python
class UserRegistrationMiddleware:
    async def __call__(self, handler, event, data):
        """Ensure user is registered in database"""
```

## Database Models API

### User Model
```python
class User(Base):
    id: int
    tg_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    in_game_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    async def get_by_tg_id(cls, session: AsyncSession, tg_id: int) -> Optional['User']
    @classmethod
    async def create(cls, session: AsyncSession, tg_id: int, **kwargs) -> 'User'
```

### District Model
```python
class District(Base):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Action Model
```python
class Action(Base):
    id: int
    kind: str
    title: Optional[str]
    status: str
    owner_id: int
    district_id: Optional[int]
    type: str
    parent_action_id: Optional[int]
    force: int
    money: int
    influence: int
    information: int
    estimated_power: int
    on_point: bool
    ideology_shift: Optional[int]
    created_at: datetime
    updated_at: datetime
    text: Optional[str]
```

### Politician Model
```python
class Politician(Base):
    id: int
    name: str
    district_id: Optional[int]
    created_at: datetime
    updated_at: datetime
```

### News Model
```python
class News(Base):
    id: int
    title: str
    content: str
    district_id: Optional[int]
    created_at: datetime
    updated_at: datetime
```

## Route Handlers API

### Start Handler
```python
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command"""
```

### Main Menu Handler
```python
@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
    """Handle main menu navigation"""
```

## Service Layer API

### User Service
```python
class UserService:
    @staticmethod
    async def get_or_create_user(session: AsyncSession, tg_id: int) -> User:
        """Get existing user or create new one"""
    
    @staticmethod
    async def update_user_profile(session: AsyncSession, user: User, **kwargs) -> User:
        """Update user profile information"""
```

### District Service
```python
class DistrictService:
    @staticmethod
    async def get_all_districts(session: AsyncSession) -> List[District]:
        """Get all available districts"""
    
    @staticmethod
    async def get_district_by_id(session: AsyncSession, district_id: int) -> Optional[District]:
        """Get district by ID"""
```

### Action Service
```python
class ActionService:
    @staticmethod
    async def create_action(session: AsyncSession, user_id: int, **kwargs) -> Action:
        """Create new action"""
    
    @staticmethod
    async def get_user_actions(session: AsyncSession, user_id: int) -> List[Action]:
        """Get all actions for user"""
```

## Template API

### Template Rendering
```python
class TemplateRenderer:
    def __init__(self, template_root: str, default_locale: str):
        self.template_root = template_root
        self.default_locale = default_locale
    
    async def render(self, template_name: str, context: dict, locale: str = None) -> str:
        """Render template with context"""
```

### Template Context
Templates receive the following context variables:
- `user` - Current user object
- `districts` - Available districts
- `actions` - User actions
- `news` - Recent news
- `_` - Translation function

## State Management API

### FSM States
```python
class RegistrationStates(StatesGroup):
    waiting_name = State()
    waiting_confirmation = State()

class ScoutStates(StatesGroup):
    waiting_question = State()
    waiting_answer = State()

class CommunicateStates(StatesGroup):
    waiting_news = State()
    waiting_response = State()
```

### State Transitions
```python
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_name)
    # Send registration form

async def process_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await state.set_state(RegistrationStates.waiting_confirmation)
    # Send confirmation
```

## Error Handling API

### Custom Exceptions
```python
class BotError(Exception):
    """Base exception for bot errors"""
    pass

class ValidationError(BotError):
    """Input validation error"""
    pass

class DatabaseError(BotError):
    """Database operation error"""
    pass
```

### Error Handlers
```python
async def error_handler(event, exception):
    """Global error handler"""
    logger.exception(f"Unhandled error: {exception}")
    # Send user-friendly error message
```

## Logging API

### Logging Configuration
```python
def setup_logging(level: str = "INFO"):
    """Setup application logging"""
```

### Logging Usage
```python
import logging
logger = logging.getLogger(__name__)

logger.info("User action completed")
logger.error("Database connection failed", exc_info=True)
logger.debug("Debug information")
```

## Utility Functions

### Text Processing
```python
def sanitize_text(text: str) -> str:
    """Sanitize user input text"""
    
def format_number(number: int) -> str:
    """Format number for display"""
```

### Validation
```python
def validate_username(username: str) -> bool:
    """Validate username format"""
    
def validate_action_data(data: dict) -> bool:
    """Validate action data"""
```

## External Integrations

### Telegram API
- Bot token configuration
- Webhook or polling setup
- Message and callback handling
- File upload/download

### Database Integration
- PostgreSQL connection
- Async SQLAlchemy operations
- Migration management
- Connection pooling

## Performance Monitoring

### Metrics Collection
```python
class MetricsCollector:
    def record_request_time(self, duration: float):
        """Record request processing time"""
    
    def record_database_query(self, query: str, duration: float):
        """Record database query performance"""
    
    def record_error(self, error: Exception):
        """Record error occurrence"""
```
