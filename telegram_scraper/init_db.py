#!/usr/bin/env python3
"""
Database initialization script for Telegram Scraper
This script creates the database tables and can be used for development/testing
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.database import db_manager
from models.database import Base
from config.settings import Config

def init_database():
    """Initialize the database with all tables"""
    try:
        print(f"Connecting to database: {Config.DATABASE_URL}")
        
        # Create all tables
        db_manager.create_tables()
        print("✅ Database tables created successfully!")
        
        # Test connection
        with db_manager.get_session() as session:
            result = session.execute("SELECT 1")
            print("✅ Database connection test successful!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

def drop_database():
    """Drop all tables (use with caution!)"""
    try:
        print("⚠️  Dropping all database tables...")
        db_manager.drop_tables()
        print("✅ All tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument("--drop", action="store_true", help="Drop all tables before creating")
    parser.add_argument("--init", action="store_true", help="Initialize database tables")
    
    args = parser.parse_args()
    
    if args.drop:
        drop_database()
    
    if args.init or not (args.drop):
        init_database()
