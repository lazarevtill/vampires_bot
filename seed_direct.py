#!/usr/bin/env python3
"""
Direct database seeding script that reads from SQLite and writes to PostgreSQL
using SQLAlchemy models to ensure proper data type handling
"""
import asyncio
import logging
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from db.session import get_session
from db.models import User, District, Action, News, Politician, ControlLevel, ActionStatus, ActionType
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_sqlite_database():
    """Find the SQLite database file"""
    possible_paths = [
        'bot.db',
        r'C:\Users\lazarev\Documents\bot.db',
        r'C:\Users\lazarev\Documents\GitHub\vampires_bot\bot.db'
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            logger.info(f"Found database at: {path}")
            return path
    
    logger.warning("SQLite database not found in expected locations")
    return None

async def clear_existing_data(session):
    """Clear existing data from all tables"""
    logger.info("Clearing existing data...")
    
    # Check if tables exist first
    tables_to_clear = ['news', 'politicians', 'districts']
    
    for table in tables_to_clear:
        try:
            # Check if table exists
            result = await session.execute(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"))
            table_exists = result.scalar()
            
            if table_exists:
                await session.execute(text(f"DELETE FROM {table}"))
                logger.info(f"Cleared table: {table}")
            else:
                logger.info(f"Table {table} does not exist yet, skipping clear")
        except Exception as e:
            logger.warning(f"Could not clear table {table}: {e}")
    
    try:
        await session.commit()
    except Exception as e:
        logger.warning(f"Could not commit clear operation: {e}")
        await session.rollback()

async def migrate_users(session, sqlite_conn):
    """Migrate users from SQLite to PostgreSQL"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    logger.info(f"Migrating {len(rows)} users...")
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime strings
        for date_field in ['actions_refresh_at', 'created_at', 'updated_at']:
            if date_field in row_dict and row_dict[date_field]:
                if isinstance(row_dict[date_field], str):
                    try:
                        row_dict[date_field] = datetime.fromisoformat(row_dict[date_field].replace('Z', '+00:00'))
                    except:
                        row_dict[date_field] = None
        
        user = User(
            tg_id=row_dict['tg_id'],
            username=row_dict.get('username'),
            first_name=row_dict.get('first_name'),
            last_name=row_dict.get('last_name'),
            in_game_name=row_dict.get('in_game_name'),
            language_code=row_dict.get('language_code'),
            money=row_dict.get('money', 0),
            influence=row_dict.get('influence', 0),
            information=row_dict.get('information', 0),
            force=row_dict.get('force', 0),
            base_money=row_dict.get('base_money', 0),
            base_influence=row_dict.get('base_influence', 0),
            base_information=row_dict.get('base_information', 0),
            base_force=row_dict.get('base_force', 0),
            ideology=row_dict.get('ideology', 0),
            faction=row_dict.get('faction'),
            available_actions=row_dict.get('available_actions', 0),
            max_available_actions=row_dict.get('max_available_actions', 5),
            actions_refresh_at=row_dict.get('actions_refresh_at'),
            is_admin=bool(row_dict.get('is_admin', False)),
            created_at=row_dict.get('created_at') or datetime.utcnow(),
            updated_at=row_dict.get('updated_at') or datetime.utcnow()
        )
        
        session.add(user)
    
    await session.commit()
    logger.info(f"Successfully migrated {len(rows)} users")

async def migrate_districts(session, sqlite_conn):
    """Migrate districts from SQLite to PostgreSQL"""
    # Check if districts table exists
    try:
        result = await session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'districts')"))
        table_exists = result.scalar()
        if not table_exists:
            logger.error("Districts table does not exist! Make sure migrations ran successfully.")
            return
    except Exception as e:
        logger.error(f"Could not check if districts table exists: {e}")
        return
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM districts")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute("PRAGMA table_info(districts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    logger.info(f"Migrating {len(rows)} districts...")
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime
        if 'created_at' in row_dict and row_dict['created_at']:
            if isinstance(row_dict['created_at'], str):
                try:
                    row_dict['created_at'] = datetime.fromisoformat(row_dict['created_at'].replace('Z', '+00:00'))
                except:
                    row_dict['created_at'] = datetime.utcnow()
        
        # Handle control_level enum
        control_level = ControlLevel.MINIMAL
        if 'control_level' in row_dict and row_dict['control_level']:
            try:
                control_level = ControlLevel(row_dict['control_level'])
            except:
                logger.warning(f"Unknown control level: {row_dict['control_level']}, using MINIMAL")
        
        district = District(
            name=row_dict['name'],
            owner_id=None,  # Remove user references
            control_points=row_dict.get('control_points', 0),
            control_level=control_level,
            resource_multiplier=row_dict.get('resource_multiplier', 0.4),
            base_money=row_dict.get('base_money', 100),
            base_influence=row_dict.get('base_influence', 10),
            base_information=row_dict.get('base_information', 5),
            base_force=row_dict.get('base_force', 0),
            created_at=row_dict.get('created_at') or datetime.utcnow()
        )
        
        session.add(district)
    
    await session.commit()
    logger.info(f"Successfully migrated {len(rows)} districts")

async def migrate_politicians(session, sqlite_conn):
    """Migrate politicians from SQLite to PostgreSQL"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM politicians")
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No politicians to migrate")
        return
    
    # Get column names
    cursor.execute("PRAGMA table_info(politicians)")
    columns = [col[1] for col in cursor.fetchall()]
    
    logger.info(f"Migrating {len(rows)} politicians...")
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime fields
        for date_field in ['created_at', 'updated_at']:
            if date_field in row_dict and row_dict[date_field]:
                if isinstance(row_dict[date_field], str):
                    try:
                        row_dict[date_field] = datetime.fromisoformat(row_dict[date_field].replace('Z', '+00:00'))
                    except:
                        row_dict[date_field] = datetime.utcnow()
        
        politician = Politician(
            name=row_dict['name'],
            role_and_influence=row_dict['role_and_influence'],
            district_id=row_dict.get('district_id'),
            ideology=row_dict.get('ideology', 0),
            influence=row_dict.get('influence', 0),
            bonuses_penalties=row_dict.get('bonuses_penalties'),
            created_at=row_dict.get('created_at') or datetime.utcnow(),
            updated_at=row_dict.get('updated_at') or datetime.utcnow()
        )
        
        session.add(politician)
    
    await session.commit()
    logger.info(f"Successfully migrated {len(rows)} politicians")

async def migrate_actions(session, sqlite_conn):
    """Migrate actions from SQLite to PostgreSQL"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM actions")
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No actions to migrate")
        return
    
    # Get column names
    cursor.execute("PRAGMA table_info(actions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    logger.info(f"Migrating {len(rows)} actions...")
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime fields
        for date_field in ['created_at', 'updated_at']:
            if date_field in row_dict and row_dict[date_field]:
                if isinstance(row_dict[date_field], str):
                    try:
                        row_dict[date_field] = datetime.fromisoformat(row_dict[date_field].replace('Z', '+00:00'))
                    except:
                        row_dict[date_field] = datetime.utcnow()
        
        # Handle status enum
        status = ActionStatus.DRAFT
        if 'status' in row_dict and row_dict['status']:
            try:
                status = ActionStatus(row_dict['status'])
            except:
                logger.warning(f"Unknown action status: {row_dict['status']}, using DRAFT")
        
        # Handle type enum
        action_type = ActionType.INDIVIDUAL
        if 'type' in row_dict and row_dict['type']:
            try:
                action_type = ActionType(row_dict['type'])
            except:
                logger.warning(f"Unknown action type: {row_dict['type']}, using INDIVIDUAL")
        
        action = Action(
            kind=row_dict.get('kind', 'unknown'),
            title=row_dict.get('title'),
            status=status,
            owner_id=row_dict['owner_id'],
            district_id=row_dict.get('district_id'),
            type=action_type,
            parent_action_id=row_dict.get('parent_action_id'),
            force=row_dict.get('force', 0),
            money=row_dict.get('money', 0),
            influence=row_dict.get('influence', 0),
            information=row_dict.get('information', 0),
            estimated_power=row_dict.get('estimated_power', 0),
            on_point=bool(row_dict.get('on_point', False)),
            text=row_dict.get('text'),
            created_at=row_dict.get('created_at') or datetime.utcnow(),
            updated_at=row_dict.get('updated_at') or datetime.utcnow()
        )
        
        session.add(action)
    
    await session.commit()
    logger.info(f"Successfully migrated {len(rows)} actions")

async def migrate_news(session, sqlite_conn):
    """Migrate news from SQLite to PostgreSQL"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM news")
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No news to migrate")
        return
    
    # Get column names
    cursor.execute("PRAGMA table_info(news)")
    columns = [col[1] for col in cursor.fetchall()]
    
    logger.info(f"Migrating {len(rows)} news items...")
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime fields
        for date_field in ['created_at', 'updated_at']:
            if date_field in row_dict and row_dict[date_field]:
                if isinstance(row_dict[date_field], str):
                    try:
                        row_dict[date_field] = datetime.fromisoformat(row_dict[date_field].replace('Z', '+00:00'))
                    except:
                        row_dict[date_field] = datetime.utcnow()
        
        # Handle media_urls
        media_urls = row_dict.get('media_urls', [])
        if isinstance(media_urls, str):
            try:
                import json
                media_urls = json.loads(media_urls)
            except:
                media_urls = []
        
        news = News(
            title=row_dict['title'],
            body=row_dict['body'],
            media_urls=media_urls,
            action_id=None,  # Remove action references
            created_at=row_dict.get('created_at') or datetime.utcnow(),
            updated_at=row_dict.get('updated_at') or datetime.utcnow()
        )
        
        session.add(news)
    
    await session.commit()
    logger.info(f"Successfully migrated {len(rows)} news items")

async def migrate_user_scouts_districts(session, sqlite_conn):
    """Migrate user scouts districts from SQLite to PostgreSQL"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_scouts_districts")
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No user scout relationships to migrate")
        return
    
    logger.info(f"Migrating {len(rows)} user scout relationships...")
    
    for row in rows:
        await session.execute(
            text("INSERT INTO user_scouts_districts (user_id, district_id) VALUES (:user_id, :district_id)"),
            {
                'user_id': row[0],
                'district_id': row[1]
            }
        )
    
    await session.commit()
    logger.info(f"Successfully migrated {len(rows)} user scout relationships")

async def main():
    """Main migration function"""
    logger.info("Starting direct SQLite to PostgreSQL migration...")
    
    # Find SQLite database
    sqlite_path = find_sqlite_database()
    if not sqlite_path:
        logger.error("SQLite database not found!")
        return
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    
    try:
        async with get_session() as session:
            # Clear existing data
            await clear_existing_data(session)
            
            # Migrate data in dependency order (excluding users and actions)
            await migrate_districts(session, sqlite_conn)
            await migrate_politicians(session, sqlite_conn)
            await migrate_news(session, sqlite_conn)
            
            logger.info("Migration completed successfully!")
            
            # Get final counts
            tables = ['districts', 'politicians', 'news']
            logger.info("Final data counts:")
            
            for table in tables:
                try:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"  {table}: {count} rows")
                except Exception as e:
                    logger.warning(f"  {table}: Could not get count - {e}")
                    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        sqlite_conn.close()

if __name__ == "__main__":
    asyncio.run(main())
