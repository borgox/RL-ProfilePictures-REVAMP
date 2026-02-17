#!/usr/bin/env python3
"""
Quick migration runner script.
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_mig import migrate_database

async def main():
    print("🔄 Starting database migration...")
    print("This will add new tracking columns to your existing database.")
    print()
    
    # Check if database exists
    if not os.path.exists("avatar_cache.db"):
        print("❌ Database file 'avatar_cache.db' not found!")
        print("Please make sure you're running this from the correct directory.")
        return
    
    success = await migrate_database("avatar_cache.db")
    
    if success:
        print()
        print("✅ Migration completed successfully!")
        print("Your database now supports the enhanced tracking features.")
        print("You can restart your server and the new tracking will work.")
    else:
        print()
        print("❌ Migration failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
