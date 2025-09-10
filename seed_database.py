#!/usr/bin/env python3
"""
Database seeding script that creates sample data for development and testing
"""
import asyncio
import logging
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from db.session import get_session
from db.models import User, District, Action, News, Politician, ControlLevel, ActionStatus, ActionType
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data for seeding
SAMPLE_DISTRICTS = [
    {"name": "Central District", "base_money": 150, "base_influence": 20, "base_information": 10, "base_force": 5},
    {"name": "Industrial Quarter", "base_money": 200, "base_influence": 15, "base_information": 8, "base_force": 12},
    {"name": "Old Town", "base_money": 120, "base_influence": 25, "base_information": 15, "base_force": 3},
    {"name": "Harbor District", "base_money": 180, "base_influence": 18, "base_information": 12, "base_force": 8},
    {"name": "University Quarter", "base_money": 100, "base_influence": 30, "base_information": 25, "base_force": 2},
    {"name": "Financial District", "base_money": 250, "base_influence": 22, "base_information": 18, "base_force": 6},
    {"name": "Residential Area", "base_money": 130, "base_influence": 12, "base_information": 8, "base_force": 4},
    {"name": "Entertainment District", "base_money": 160, "base_influence": 28, "base_information": 20, "base_force": 7}
]

SAMPLE_POLITICIANS = [
    {"name": "Mayor Victoria Sterling", "role": "City Mayor - Controls municipal policies and has significant influence over all districts", "ideology": 2, "influence": 50},
    {"name": "Councilman Marcus Webb", "role": "District Council Leader - Manages local governance and resource allocation", "ideology": -1, "influence": 35},
    {"name": "Senator Elena Rodriguez", "role": "State Senator - Influences regional politics and funding", "ideology": 3, "influence": 45},
    {"name": "Judge Harrison Clarke", "role": "District Court Judge - Controls legal proceedings and justice system", "ideology": 0, "influence": 40},
    {"name": "Commissioner Sarah Chen", "role": "Police Commissioner - Oversees law enforcement and security", "ideology": -2, "influence": 38},
    {"name": "Director James Morrison", "role": "Economic Development Director - Manages business licenses and development", "ideology": 1, "influence": 32},
    {"name": "Professor Angela Thompson", "role": "University Chancellor - Controls education and research funding", "ideology": 2, "influence": 28},
    {"name": "Captain Robert Hayes", "role": "Harbor Master - Controls shipping and trade regulations", "ideology": -1, "influence": 25}
]

SAMPLE_NEWS_ITEMS = [
    {
        "title": "Welcome to the Vampire Chronicles",
        "body": "The eternal struggle for power begins. Multiple factions vie for control over the city's districts, each with their own agenda and methods. Choose your allies wisely, for the night is dark and full of intrigue."
    },
    {
        "title": "District Control Mechanics Updated",
        "body": "New resource management systems have been implemented. Districts now generate resources based on control level and multipliers. Plan your actions carefully to maximize your influence."
    },
    {
        "title": "Political Influence System Active",
        "body": "Politicians across the city are now actively influencing district affairs. Building relationships with key figures can provide significant advantages in your quest for dominance."
    }
]

SAMPLE_FACTIONS = [
    "The Crimson Court", "Shadow Syndicate", "Iron Brotherhood", 
    "Midnight Council", "Blood Aristocracy", "The Dark Parliament"
]

ACTION_TYPES_SAMPLE = [
    "infiltrate", "negotiate", "sabotage", "gather_intel", 
    "establish_presence", "form_alliance", "eliminate_threat"
]

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

async def seed_sample_users(session):
    """Create sample users for development/testing"""
    logger.info("Creating sample users...")
    
    sample_users = []
    
    # Create admin user
    admin_user = User(
        tg_id=999999999,  # Fake telegram ID
        username="admin_vampire",
        first_name="Admin",
        last_name="Vampire",
        in_game_name="The Elder",
        language_code="en",
        money=1000,
        influence=500,
        information=300,
        force=200,
        base_money=1000,
        base_influence=500,
        base_information=300,
        base_force=200,
        ideology=0,
        faction="The Council of Elders",
        available_actions=10,
        max_available_actions=10,
        is_admin=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(admin_user)
    sample_users.append(admin_user)
    
    # Create sample players
    for i in range(1, 11):  # 10 sample players
        faction = random.choice(SAMPLE_FACTIONS)
        ideology = random.randint(-5, 5)
        
        user = User(
            tg_id=100000000 + i,  # Fake telegram IDs
            username=f"player_{i}",
            first_name=f"Player",
            last_name=f"{i}",
            in_game_name=f"Vampire Lord {chr(64 + i)}",  # A, B, C, etc.
            language_code="en",
            money=random.randint(50, 200),
            influence=random.randint(20, 100),
            information=random.randint(10, 80),
            force=random.randint(5, 60),
            base_money=random.randint(50, 150),
            base_influence=random.randint(20, 80),
            base_information=random.randint(10, 60),
            base_force=random.randint(5, 40),
            ideology=ideology,
            faction=faction,
            available_actions=random.randint(3, 8),
            max_available_actions=random.randint(5, 10),
            is_admin=False,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow()
        )
        session.add(user)
        sample_users.append(user)
    
    await session.commit()
    await session.refresh(admin_user)  # Get the ID
    
    logger.info(f"Created {len(sample_users)} sample users")
    return sample_users

async def seed_sample_districts(session, users):
    """Create sample districts"""
    logger.info("Creating sample districts...")
    
    districts = []
    
    for i, district_data in enumerate(SAMPLE_DISTRICTS):
        # Assign districts to random users (excluding admin)
        owner = random.choice(users[1:])  # Skip admin user
        
        control_levels = list(ControlLevel)
        control_level = random.choice(control_levels)
        
        district = District(
            name=district_data["name"],
            owner_id=owner.id,
            control_points=random.randint(0, 100),
            control_level=control_level,
            resource_multiplier=random.uniform(0.3, 0.8),
            base_money=district_data["base_money"],
            base_influence=district_data["base_influence"],
            base_information=district_data["base_information"],
            base_force=district_data["base_force"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
        )
        session.add(district)
        districts.append(district)
    
    await session.commit()
    logger.info(f"Created {len(districts)} sample districts")
    return districts

async def seed_sample_politicians(session, districts):
    """Create sample politicians"""
    logger.info("Creating sample politicians...")
    
    politicians = []
    
    for i, politician_data in enumerate(SAMPLE_POLITICIANS):
        # Some politicians are assigned to specific districts, others are city-wide
        district = random.choice(districts) if i > 2 else None  # First 3 are city-wide
        
        politician = Politician(
            name=politician_data["name"],
            role_and_influence=politician_data["role"],
            district_id=district.id if district else None,
            ideology=politician_data["ideology"],
            influence=politician_data["influence"],
            bonuses_penalties=f"Provides {politician_data['influence']} influence points when aligned",
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15)),
            updated_at=datetime.utcnow()
        )
        session.add(politician)
        politicians.append(politician)
    
    await session.commit()
    logger.info(f"Created {len(politicians)} sample politicians")
    return politicians

async def seed_sample_actions(session, users, districts):
    """Create sample actions"""
    logger.info("Creating sample actions...")
    
    actions = []
    action_statuses = list(ActionStatus)
    action_types = list(ActionType)
    
    # Create various types of actions
    for i in range(50):  # 50 sample actions
        owner = random.choice(users)
        district = random.choice(districts) if random.random() > 0.3 else None
        action_type = random.choice(action_types)
        status = random.choice(action_statuses)
        kind = random.choice(ACTION_TYPES_SAMPLE)
        
        # Create some support actions (child actions)
        parent_action = None
        if i > 10 and random.random() > 0.8:  # 20% chance for support action
            parent_action = random.choice(actions[:i])
            action_type = ActionType.SUPPORT
        
        action = Action(
            kind=kind,
            title=f"{kind.replace('_', ' ').title()} in {district.name if district else 'City'}" if district else f"City-wide {kind.replace('_', ' ').title()}",
            status=status,
            owner_id=owner.id,
            district_id=district.id if district else None,
            type=action_type,
            parent_action_id=parent_action.id if parent_action else None,
            force=random.randint(0, 50),
            money=random.randint(0, 100),
            influence=random.randint(0, 80),
            information=random.randint(0, 60),
            estimated_power=random.randint(10, 200),
            on_point=random.random() > 0.7,  # 30% chance
            text=f"Sample action description for {kind}. This is a test action created during database seeding.",
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 168)),  # Last week
            updated_at=datetime.utcnow()
        )
        session.add(action)
        actions.append(action)
    
    await session.commit()
    logger.info(f"Created {len(actions)} sample actions")
    return actions

async def seed_sample_news(session, actions):
    """Create sample news items"""
    logger.info("Creating sample news...")
    
    news_items = []
    
    # Create general news
    for news_data in SAMPLE_NEWS_ITEMS:
        news = News(
            title=news_data["title"],
            body=news_data["body"],
            media_urls=[],
            action_id=None,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
            updated_at=datetime.utcnow()
        )
        session.add(news)
        news_items.append(news)
    
    # Create some action-related news
    for i in range(5):
        action = random.choice(actions)
        news = News(
            title=f"Action Report: {action.title}",
            body=f"Recent activity detected in relation to {action.title}. Status: {action.status.value}. Resources allocated: Money {action.money}, Influence {action.influence}.",
            media_urls=[],
            action_id=action.id,
            created_at=action.created_at + timedelta(hours=random.randint(1, 24)),
            updated_at=datetime.utcnow()
        )
        session.add(news)
        news_items.append(news)
    
    await session.commit()
    logger.info(f"Created {len(news_items)} sample news items")
    return news_items

async def seed_scout_relationships(session, users, districts):
    """Create sample scouting relationships"""
    logger.info("Creating sample scout relationships...")
    
    relationships = 0
    
    # Create some scouting relationships
    for user in users[:5]:  # First 5 users scout districts
        num_scouts = random.randint(1, 3)
        scouted_districts = random.sample(districts, min(num_scouts, len(districts)))
        
        for district in scouted_districts:
            # Don't scout your own district
            if district.owner_id != user.id:
                await session.execute(
                    text("INSERT INTO user_scouts_districts (user_id, district_id) VALUES (:user_id, :district_id)"),
                    {'user_id': user.id, 'district_id': district.id}
                )
                relationships += 1
    
    await session.commit()
    logger.info(f"Created {relationships} scout relationships")

async def main():
    """Main seeding function"""
    logger.info("Starting database seeding with sample data...")
    
    async with get_session() as session:
        try:
            # Clear existing data
            await clear_existing_data(session)
            
            # Create sample data in dependency order
            users = await seed_sample_users(session)
            districts = await seed_sample_districts(session, users)
            politicians = await seed_sample_politicians(session, districts)
            actions = await seed_sample_actions(session, users, districts)
            news_items = await seed_sample_news(session, actions)
            await seed_scout_relationships(session, users, districts)
            
            logger.info("Database seeding completed successfully!")
            logger.info("Sample data created:")
            logger.info(f"  - {len(users)} users (including 1 admin)")
            logger.info(f"  - {len(districts)} districts")
            logger.info(f"  - {len(politicians)} politicians")
            logger.info(f"  - {len(actions)} actions")
            logger.info(f"  - {len(news_items)} news items")
            logger.info("")
            logger.info("Admin credentials for testing:")
            logger.info("  Telegram ID: 999999999")
            logger.info("  Username: admin_vampire")
            logger.info("  In-game name: The Elder")
            
        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())