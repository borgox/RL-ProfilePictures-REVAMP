#!/usr/bin/env python3
"""
Database migration script to add new columns to existing tables.
Run this script to update your existing database with the new tracking columns.
"""
import asyncio
import aiosqlite
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_database(db_path: str = "avatar_cache.db"):
    """Migrate the database to add new tracking columns."""
    db_file = Path(db_path)
    
    if not db_file.exists():
        logger.error(f"Database file {db_path} not found!")
        return False
    
    logger.info(f"Starting migration of database: {db_path}")
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # Check current schema
            cursor = await db.execute("PRAGMA table_info(avatar_requests)")
            columns = await cursor.fetchall()
            current_columns = [col[1] for col in columns]
            logger.info(f"Current avatar_requests columns: {current_columns}")
            
            # Add new columns if they don't exist
            new_columns = [
                ("user_agent", "TEXT"),
                ("response_time_ms", "INTEGER"),
                ("referer", "TEXT")
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in current_columns:
                    logger.info(f"Adding column: {column_name}")
                    await db.execute(f"ALTER TABLE avatar_requests ADD COLUMN {column_name} {column_type}")
                else:
                    logger.info(f"Column {column_name} already exists")
            
            # Check rate_limit_tracking table
            cursor = await db.execute("PRAGMA table_info(rate_limit_tracking)")
            columns = await cursor.fetchall()
            current_columns = [col[1] for col in columns]
            logger.info(f"Current rate_limit_tracking columns: {current_columns}")
            
            if "user_agent" not in current_columns:
                logger.info("Adding user_agent column to rate_limit_tracking")
                await db.execute("ALTER TABLE rate_limit_tracking ADD COLUMN user_agent TEXT")
            else:
                logger.info("user_agent column already exists in rate_limit_tracking")
            
            # Create new tables if they don't exist
            new_tables = [
                """
                CREATE TABLE IF NOT EXISTS user_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_requests INTEGER DEFAULT 1,
                    unique_platforms INTEGER DEFAULT 1,
                    platforms_used TEXT,
                    user_agent TEXT,
                    country TEXT,
                    city TEXT,
                    is_bot BOOLEAN DEFAULT FALSE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    total_requests INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    steam_requests INTEGER DEFAULT 0,
                    xbox_requests INTEGER DEFAULT 0,
                    psn_requests INTEGER DEFAULT 0,
                    switch_requests INTEGER DEFAULT 0,
                    epic_requests INTEGER DEFAULT 0,
                    total_bandwidth_mb REAL DEFAULT 0,
                    avg_response_time_ms REAL DEFAULT 0
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS hourly_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime TEXT NOT NULL UNIQUE,
                    requests INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    bandwidth_mb REAL DEFAULT 0
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    platform TEXT,
                    user_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    stack_trace TEXT
                )
                """
            ]
            
            for table_sql in new_tables:
                await db.execute(table_sql)
                logger.info("Created/verified new table")
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_avatar_requests_timestamp ON avatar_requests(request_timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_avatar_requests_ip ON avatar_requests(ip_address)",
                "CREATE INDEX IF NOT EXISTS idx_user_analytics_ip ON user_analytics(ip_address)",
                "CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)",
                "CREATE INDEX IF NOT EXISTS idx_hourly_stats_datetime ON hourly_stats(datetime)",
                "CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp)"
            ]
            
            for index_sql in indexes:
                await db.execute(index_sql)
                logger.info("Created/verified index")
            
            await db.commit()
            logger.info("Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

async def main():
    """Main migration function."""
    import sys
    
    db_path = "avatar_cache.db"
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    success = await migrate_database(db_path)
    if success:
        print("✅ Database migration completed successfully!")
        print("You can now restart your server with the updated tracking features.")
    else:
        print("❌ Database migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
