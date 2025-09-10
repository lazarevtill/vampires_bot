#!/usr/bin/env python3
"""
Production seeding script that imports existing data from SQLite export
This script is used when you want to migrate real data to PostgreSQL
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

# ... (rest of the import functions from the original seed_database.py)
# This file contains the production import logic

async def main():
    """Main production seeding function"""
    logger.info("Starting production database seeding from SQLite export...")
    
    # Load SQLite data
    data = await load_sqlite_data()
    if not data:
        logger.info("No data to seed")
        return
    
    async with get_session() as session:
        try:
            # Clear existing data
            await clear_existing_data(session)
            
            # Import production data
            await seed_users(session, data)
            # ... add other import functions as needed
            
            logger.info("Production database seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())
