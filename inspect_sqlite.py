#!/usr/bin/env python3
"""
Script to inspect SQLite database and extract data for seeding PostgreSQL
"""
import sqlite3
import json
import os
from pathlib import Path

def inspect_sqlite_db(db_path):
    """Inspect SQLite database and return structure and data"""
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found tables: {tables}")
    
    data = {}
    
    for table in tables:
        print(f"\n=== Table: {table} ===")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        print(f"Columns: {[(col[1], col[2]) for col in columns]}")
        
        # Get table data
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        print(f"Row count: {len(rows)}")
        
        if rows:
            print("Sample data (first 3 rows):")
            column_names = [col[1] for col in columns]
            for i, row in enumerate(rows[:3]):
                row_dict = dict(zip(column_names, row))
                print(f"  {i+1}: {row_dict}")
        
        # Store data for seeding
        data[table] = {
            'columns': [col[1] for col in columns],
            'rows': rows
        }
    
    conn.close()
    return data

def main():
    # Check both possible locations
    db_paths = [
        'bot.db',
        r'C:\Users\lazarev\Documents\bot.db'
    ]
    
    for db_path in db_paths:
        print(f"\nChecking {db_path}...")
        if os.path.exists(db_path):
            print(f"Found database at: {db_path}")
            data = inspect_sqlite_db(db_path)
            
            if data:
                # Save data to JSON for seeding
                with open('sqlite_data.json', 'w', encoding='utf-8') as f:
                    # Convert rows to lists for JSON serialization
                    json_data = {}
                    for table, info in data.items():
                        json_data[table] = {
                            'columns': info['columns'],
                            'rows': [list(row) for row in info['rows']]
                        }
                    json.dump(json_data, f, indent=2, default=str)
                print(f"\nData exported to sqlite_data.json")
            return
    
    print("No SQLite database found in expected locations!")

if __name__ == "__main__":
    main()
