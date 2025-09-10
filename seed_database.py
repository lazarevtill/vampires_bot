#!/usr/bin/env python3
"""
Database seeding script that imports data from SQLite export to PostgreSQL
"""
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from db.session import get_session
from db.models import User, District, Action, News, Politician
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_sqlite_data():
    """Load data from SQLite export JSON"""
    try:
        with open('sqlite_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded data for tables: {list(data.keys())}")
        for table, info in data.items():
            logger.info(f"  {table}: {len(info['rows'])} rows")
        
        return data
    except FileNotFoundError:
        logger.warning("sqlite_data.json not found, skipping data import")
        return None
    except Exception as e:
        logger.error(f"Error loading SQLite data: {e}")
        return None

async def clear_existing_data(session):
    """Clear existing data from all tables"""
    logger.info("Clearing existing data...")
    
    # Clear in reverse dependency order
    tables = ['news', 'actions', 'politicians', 'user_scouts_districts', 'districts', 'users']
    
    for table in tables:
        try:
            await session.execute(text(f"DELETE FROM {table}"))
            logger.info(f"Cleared table: {table}")
        except Exception as e:
            logger.warning(f"Could not clear table {table}: {e}")
    
    await session.commit()

async def seed_users(session, data):
    """Seed users table"""
    if 'users' not in data:
        logger.info("No users data to seed")
        return
    
    logger.info("Seeding users...")
    users_data = data['users']
    columns = users_data['columns']
    
    for row in users_data['rows']:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime strings if needed
        for date_field in ['actions_refresh_at', 'created_at', 'updated_at']:
            if date_field in row_dict and row_dict[date_field]:
                if isinstance(row_dict[date_field], str):
                    try:
                        row_dict[date_field] = datetime.fromisoformat(row_dict[date_field].replace('Z', '+00:00'))
                    except:
                        row_dict[date_field] = None
        
        # Create user
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
    logger.info(f"Seeded {len(users_data['rows'])} users")

async def seed_districts(session, data):
    """Seed districts table"""
    if 'districts' not in data:
        logger.info("No districts data to seed")
        return
    
    logger.info("Seeding districts...")
    districts_data = data['districts']
    columns = districts_data['columns']
    
    for row in districts_data['rows']:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime
        if 'created_at' in row_dict and row_dict['created_at']:
            if isinstance(row_dict['created_at'], str):
                try:
                    row_dict['created_at'] = datetime.fromisoformat(row_dict['created_at'].replace('Z', '+00:00'))
                except:
                    row_dict['created_at'] = datetime.utcnow()
        
        # Import control_level enum
        from db.models import ControlLevel
        control_level = ControlLevel.MINIMAL
        if 'control_level' in row_dict and row_dict['control_level']:
            try:
                control_level = ControlLevel(row_dict['control_level'])
            except:
                pass
        
        district = District(
            name=row_dict['name'],
            owner_id=row_dict['owner_id'],
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
    logger.info(f"Seeded {len(districts_data['rows'])} districts")

async def seed_actions(session, data):
    """Seed actions table"""
    if 'actions' not in data:
        logger.info("No actions data to seed")
        return
    
    logger.info("Seeding actions...")
    actions_data = data['actions']
    columns = actions_data['columns']
    
    for row in actions_data['rows']:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime fields
        for date_field in ['created_at', 'updated_at']:
            if date_field in row_dict and row_dict[date_field]:
                if isinstance(row_dict[date_field], str):
                    try:
                        row_dict[date_field] = datetime.fromisoformat(row_dict[date_field].replace('Z', '+00:00'))
                    except:
                        row_dict[date_field] = datetime.utcnow()
        
        # Import enums
        from db.models import ActionStatus, ActionType
        
        status = ActionStatus.DRAFT
        if 'status' in row_dict and row_dict['status']:
            try:
                status = ActionStatus(row_dict['status'])
            except:
                pass
        
        action_type = ActionType.INDIVIDUAL
        if 'type' in row_dict and row_dict['type']:
            try:
                action_type = ActionType(row_dict['type'])
            except:
                pass
        
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
    logger.info(f"Seeded {len(actions_data['rows'])} actions")

async def seed_news(session, data):
    """Seed news table"""
    if 'news' not in data:
        logger.info("No news data to seed")
        return
    
    logger.info("Seeding news...")
    news_data = data['news']
    columns = news_data['columns']
    
    for row in news_data['rows']:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime fields
        for date_field in ['created_at', 'updated_at']:
            if date_field in row_dict and row_dict[date_field]:
                if isinstance(row_dict[date_field], str):
                    try:
                        row_dict[date_field] = datetime.fromisoformat(row_dict[date_field].replace('Z', '+00:00'))
                    except:
                        row_dict[date_field] = datetime.utcnow()
        
        # Handle media_urls - it might be JSON string or list
        media_urls = row_dict.get('media_urls', [])
        if isinstance(media_urls, str):
            try:
                media_urls = json.loads(media_urls)
            except:
                media_urls = []
        
        news = News(
            title=row_dict['title'],
            body=row_dict['body'],
            media_urls=media_urls,
            action_id=row_dict.get('action_id'),
            created_at=row_dict.get('created_at') or datetime.utcnow(),
            updated_at=row_dict.get('updated_at') or datetime.utcnow()
        )
        
        session.add(news)
    
    await session.commit()
    logger.info(f"Seeded {len(news_data['rows'])} news items")

async def seed_politicians(session, data):
    """Seed politicians table"""
    if 'politicians' not in data:
        logger.info("No politicians data to seed")
        return
    
    logger.info("Seeding politicians...")
    politicians_data = data['politicians']
    columns = politicians_data['columns']
    
    for row in politicians_data['rows']:
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
    logger.info(f"Seeded {len(politicians_data['rows'])} politicians")

async def seed_user_scouts_districts(session, data):
    """Seed user_scouts_districts many-to-many table"""
    if 'user_scouts_districts' not in data:
        logger.info("No user scouts districts data to seed")
        return
    
    logger.info("Seeding user scouts districts...")
    scouts_data = data['user_scouts_districts']
    columns = scouts_data['columns']
    
    for row in scouts_data['rows']:
        row_dict = dict(zip(columns, row))
        
        # Insert directly into the association table
        await session.execute(
            text("INSERT INTO user_scouts_districts (user_id, district_id) VALUES (:user_id, :district_id)"),
            {
                'user_id': row_dict['user_id'],
                'district_id': row_dict['district_id']
            }
        )
    
    await session.commit()
    logger.info(f"Seeded {len(scouts_data['rows'])} user scout relationships")

async def main():
    """Main seeding function"""
    logger.info("Starting database seeding...")
    
    # Load SQLite data
    data = await load_sqlite_data()
    if not data:
        logger.info("No data to seed")
        return
    
    async with get_session() as session:
        try:
            # Clear existing data
            await clear_existing_data(session)
            
            # Seed tables in dependency order
            await seed_users(session, data)
            await seed_districts(session, data)
            await seed_actions(session, data)
            await seed_news(session, data)
            await seed_politicians(session, data)
            await seed_user_scouts_districts(session, data)
            
            logger.info("Database seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())
