#!/usr/bin/env python3
"""
Extract SQL INSERT statements from SQLite database for PostgreSQL seeding
"""
import sqlite3
import os
import sys
from pathlib import Path

def find_sqlite_database():
    """Find the SQLite database file"""
    possible_paths = [
        'bot.db',
        r'C:\Users\lazarev\Documents\bot.db',
        r'C:\Users\lazarev\Documents\GitHub\vampires_bot\bot.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found database at: {path}")
            return path
    
    print("SQLite database not found in expected locations:")
    for path in possible_paths:
        print(f"  - {path}")
    return None

def get_table_schema(cursor, table_name):
    """Get table schema for reference"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return [(col[1], col[2]) for col in columns]  # (name, type)

def escape_sql_value(value):
    """Escape SQL values for PostgreSQL"""
    if value is None:
        return 'NULL'
    elif isinstance(value, str):
        # Use dollar-quoted strings for PostgreSQL to handle complex text
        # This avoids issues with quotes and special characters
        if "'" in value or '"' in value or '\n' in value or '\\' in value:
            # Use dollar quoting for complex strings
            return f"$${value}$$"
        else:
            # Simple strings can use regular quoting
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    else:
        return str(value)

def generate_insert_statements(cursor, table_name, schema):
    """Generate INSERT statements for a table"""
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        return []
    
    column_names = [col[0] for col in schema]
    statements = []
    
    # Add comment header
    statements.append(f"-- Data for table: {table_name}")
    statements.append(f"-- Columns: {', '.join(column_names)}")
    statements.append("")
    
    for row in rows:
        values = [escape_sql_value(value) for value in row]
        values_str = ', '.join(values)
        
        insert_stmt = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({values_str});"
        statements.append(insert_stmt)
    
    statements.append("")
    return statements

def create_sql_dump(db_path, output_file='seed_data.sql'):
    """Create SQL dump from SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables except system tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found tables: {tables}")
    
    # Define table order for proper foreign key constraints
    # Users first, then districts, then everything else
    table_order = []
    
    # Add users first
    if 'users' in tables:
        table_order.append('users')
        tables.remove('users')
    
    # Add districts second
    if 'districts' in tables:
        table_order.append('districts')
        tables.remove('districts')
    
    # Add politicians
    if 'politicians' in tables:
        table_order.append('politicians')
        tables.remove('politicians')
    
    # Add actions
    if 'actions' in tables:
        table_order.append('actions')
        tables.remove('actions')
    
    # Add news
    if 'news' in tables:
        table_order.append('news')
        tables.remove('news')
    
    # Add many-to-many tables last
    if 'user_scouts_districts' in tables:
        table_order.append('user_scouts_districts')
        tables.remove('user_scouts_districts')
    
    # Add any remaining tables
    table_order.extend(tables)
    
    # Generate SQL dump
    sql_statements = []
    sql_statements.append("-- PostgreSQL seed data dump")
    sql_statements.append("-- Generated from SQLite database")
    sql_statements.append("-- ")
    sql_statements.append("")
    
    # Disable foreign key checks during seeding
    sql_statements.append("-- Disable triggers and constraints during seeding")
    sql_statements.append("SET session_replication_role = 'replica';")
    sql_statements.append("")
    
    for table_name in table_order:
        print(f"Processing table: {table_name}")
        
        schema = get_table_schema(cursor, table_name)
        print(f"  Columns: {[col[0] for col in schema]}")
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"  Rows: {row_count}")
        
        if row_count > 0:
            statements = generate_insert_statements(cursor, table_name, schema)
            sql_statements.extend(statements)
    
    # Re-enable foreign key checks
    sql_statements.append("-- Re-enable triggers and constraints")
    sql_statements.append("SET session_replication_role = 'origin';")
    sql_statements.append("")
    
    # Reset sequences for auto-increment columns
    sql_statements.append("-- Reset sequences to correct values")
    for table_name in table_order:
        if table_name in ['users', 'districts', 'actions', 'news', 'politicians']:
            sql_statements.append(f"SELECT setval('{table_name}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {table_name}));")
    sql_statements.append("")
    
    conn.close()
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"\nSQL dump created: {output_file}")
    print(f"Total statements: {len([s for s in sql_statements if s.startswith('INSERT')])}")
    
    return output_file

def main():
    print("SQLite to PostgreSQL SQL Dump Generator")
    print("=" * 50)
    
    # Find SQLite database
    db_path = find_sqlite_database()
    if not db_path:
        print("\nPlease ensure your SQLite database file exists and try again.")
        sys.exit(1)
    
    # Create SQL dump
    try:
        output_file = create_sql_dump(db_path)
        print(f"\n✅ Success! SQL dump created: {output_file}")
        print("\nYou can now use this file to seed your PostgreSQL database.")
        
    except Exception as e:
        print(f"\n❌ Error creating SQL dump: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
