#!/usr/bin/env python3
"""
Database initialization script.
This script runs Alembic migrations to set up the database schema.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from alembic import command
from alembic.config import Config
from db.config import load_db_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations to create/update database schema."""
    try:
        # Load database configuration
        db_config = load_db_config()

        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_config.url)

        # Always create a fresh migration for PostgreSQL setup
        versions_dir = Path("alembic/versions")
        
        # Clean up any existing migration files to avoid conflicts
        if versions_dir.exists():
            for migration_file in versions_dir.glob("*.py"):
                migration_file.unlink()
                logger.info(f"Removed old migration: {migration_file}")
        
        logger.info("Creating fresh initial migration...")
        # Create initial migration based on current models
        command.revision(alembic_cfg, message="Initial migration", autogenerate=True)
        logger.info("Initial migration created.")

        # Run all pending migrations
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")

    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
