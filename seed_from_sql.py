#!/usr/bin/env python3
"""
Database seeding script that uses actual SQL dump from SQLite database
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from db.session import get_session
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

async def execute_sql_dump(session, sql_file='seed_data.sql'):
    """Execute SQL dump file"""
    if not Path(sql_file).exists():
        logger.error(f"SQL dump file not found: {sql_file}")
        logger.info("Please run 'python extract_sql_dump.py' first to generate the SQL dump.")
        return False
    
    logger.info(f"Executing SQL dump from: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split into individual statements, handling multi-line statements
    statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if line.startswith('--') or not line:
            continue
            
        current_statement += line + " "
        
        # If line ends with semicolon, it's the end of a statement
        if line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    executed_count = 0
    insert_count = 0
    failed_count = 0
    
    for statement in statements:
        if not statement:
            continue
            
        try:
            await session.execute(text(statement))
            executed_count += 1
            
            if statement.upper().startswith('INSERT'):
                insert_count += 1
                if insert_count % 20 == 0:
                    logger.info(f"Executed {insert_count} INSERT statements...")
                    
        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed statement #{failed_count}: {statement[:100]}...")
            logger.warning(f"Error: {e}")
            
            # If too many failures, abort
            if failed_count > 10:
                logger.error("Too many failed statements, aborting...")
                await session.rollback()
                return False
    
    await session.commit()
    logger.info(f"Successfully executed {executed_count} SQL statements ({insert_count} INSERTs, {failed_count} failed)")
    return True

async def main():
    """Main seeding function"""
    logger.info("Starting database seeding from SQL dump...")
    
    async with get_session() as session:
        try:
            # Clear existing data
            await clear_existing_data(session)
            
            # Execute SQL dump
            success = await execute_sql_dump(session)
            
            if success:
                logger.info("Database seeding completed successfully!")
                
                # Get counts for verification
                tables = ['users', 'districts', 'politicians', 'actions', 'news', 'user_scouts_districts']
                logger.info("Final data counts:")
                
                for table in tables:
                    try:
                        result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        logger.info(f"  {table}: {count} rows")
                    except Exception as e:
                        logger.warning(f"  {table}: Could not get count - {e}")
            else:
                logger.error("Database seeding failed!")
                
        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())
