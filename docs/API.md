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
    language_code: Optional[str]
    money: int
    influence: int
    information: int
    force: int
    base_money: int
    base_influence: int
    base_information: int
    base_force: int
    ideology: int  # -5 to 5 range
    faction: Optional[str]
    available_actions: int
    max_available_actions: Optional[int]
    actions_refresh_at: Optional[datetime]
    is_admin: bool
    created_at: datetime
    updated_at: datetime
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
    ideology_shift: Optional[int]  # NEW: Ideology shift functionality
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

### UserScoutsDistrict Model
```python
# Association table for many-to-many relationship
user_scouts_districts = Table(
    "user_scouts_districts",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("district_id", ForeignKey("districts.id", ondelete="CASCADE"), primary_key=True),
)
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

### Options Handler
```python
@router.callback_query(F.data.startswith("options_"))
async def options_handler(callback: CallbackQuery, state: FSMContext):
    """Handle options and settings"""
```

### Universal Handler
```python
@router.callback_query()
async def universal_handler(callback: CallbackQuery, state: FSMContext):
    """Handle universal callbacks"""
```

## Screen Components API

### Main Menu Screen
```python
class MainMenuScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render main menu with user stats and options"""
```

### Profile Screen
```python
class StatusScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render user profile with stats and information"""
```

### Actions Screen
```python
class ActionsScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render actions list and management"""
```

### District List Screen
```python
class DistrictListScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render district list with scouting options"""
```

### News List Screen
```python
class NewsListScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render news list and management"""
```

### Communication Screen
```python
class CommunicateScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render communication features"""
```

### Registration Screen
```python
class RegistrationScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render user registration form"""
```

### Scout Action Screen
```python
class ScoutActionScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render scouting action interface"""
```

### Settings Action Screen
```python
class SettingsActionScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render action settings and configuration"""
```

### Notify Screen
```python
class NotifyScreen(BaseScreen):
    async def _render(self, message, actor, state):
        """Render notification interface"""
```

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

## Text Handlers API

### Registration Handler
```python
@router.message(RegistrationStates.waiting_name)
async def register_name_handler(message: Message, state: FSMContext):
    """Handle name registration input"""
```

### Communication Handler
```python
@router.message(CommunicateStates.waiting_news)
async def communicate_handler(message: Message, state: FSMContext):
    """Handle communication input"""
```

### Scout Info Handler
```python
@router.message(ScoutStates.waiting_question)
async def scout_info_handler(message: Message, state: FSMContext):
    """Handle scouting information input"""
```

## Keyboard API

### Keyboard Renderer
```python
class KeyboardRenderer:
    def render(self, spec: KeyboardSpec) -> InlineKeyboardMarkup:
        """Render keyboard from specification"""
```

### Keyboard Presets
```python
class KeyboardPresets:
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard"""
    
    @staticmethod
    def actions_menu() -> InlineKeyboardMarkup:
        """Actions menu keyboard"""
    
    @staticmethod
    def district_list() -> InlineKeyboardMarkup:
        """District list keyboard"""
```

### Keyboard Specifications
```python
class KeyboardSpec:
    buttons: List[ButtonSpec]
    layout: List[List[str]]
    
class ButtonSpec:
    text: str
    callback_data: str
    url: Optional[str] = None
```

## Options System API

### Options Registry
```python
class OptionsRegistry:
    def register(self, name: str, option: BaseOption):
        """Register an option"""
    
    def get(self, name: str) -> BaseOption:
        """Get an option by name"""
    
    def list_all(self) -> List[BaseOption]:
        """List all registered options"""
```

### Base Option
```python
class BaseOption:
    name: str
    title: str
    description: str
    
    async def render(self, user: User) -> str:
        """Render option content"""
    
    async def handle_callback(self, callback: CallbackQuery, user: User):
        """Handle option callback"""
```

### Specific Options
```python
class MainMenuOption(BaseOption):
    """Main menu option handler"""

class ActionsMenuOption(BaseOption):
    """Actions menu option handler"""

class DistrictListMenuOption(BaseOption):
    """District list menu option handler"""

class NewsListOption(BaseOption):
    """News list option handler"""

class ScoutMenuOption(BaseOption):
    """Scout menu option handler"""

class CommunicateOption(BaseOption):
    """Communication option handler"""

class ActionsStatsOption(BaseOption):
    """Action statistics option handler"""

class ActionSetupMenuOption(BaseOption):
    """Action setup menu option handler"""
```

## Service Layer API

### Message Store Service
```python
class MessageStoreService:
    @staticmethod
    async def store_message(user_id: int, message_data: dict):
        """Store message data"""
    
    @staticmethod
    async def get_messages(user_id: int) -> List[dict]:
        """Get stored messages for user"""
```

### Notification Service
```python
class NotificationService:
    @staticmethod
    async def send_notification(user_id: int, message: str):
        """Send notification to user"""
    
    @staticmethod
    async def broadcast_to_district(district_id: int, message: str):
        """Broadcast message to district users"""
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

## Utility Functions

### Callback Utilities
```python
def parse_callback_data(data: str) -> dict:
    """Parse callback data string"""
    
def build_callback_data(**kwargs) -> str:
    """Build callback data string"""
```

### Render Utilities
```python
def format_number(number: int) -> str:
    """Format number for display"""
    
def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
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

## Excel Integration API

### Excel Import
```python
class ExcelImporter:
    def import_users(self, file_path: str) -> List[User]:
        """Import users from Excel file"""
    
    def import_districts(self, file_path: str) -> List[District]:
        """Import districts from Excel file"""
    
    def import_actions(self, file_path: str) -> List[Action]:
        """Import actions from Excel file"""
```

### Excel Templates
```python
class ExcelTemplates:
    def create_user_template(self) -> str:
        """Create user import template"""
    
    def create_district_template(self) -> str:
        """Create district import template"""
    
    def create_action_template(self) -> str:
        """Create action import template"""
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