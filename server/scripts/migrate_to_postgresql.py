#!/usr/bin/env python3
"""
Enhanced migration script to move data from SQLite to PostgreSQL
Run this script after setting up PostgreSQL and updating your .env file
"""

import asyncio
import sqlite3
import asyncpg
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import os
import sys

# Import config
try:
    from config import settings
except ImportError:
    print("❌ Could not import settings from config. Please ensure config.py exists with database_url.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProgressBar:
    """Simple progress bar for terminal output."""
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1, detail: str = ""):
        """Update progress bar."""
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        
        # Calculate ETA
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if self.current > 0:
            eta_seconds = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {int(eta_seconds)}s" if eta_seconds > 0 else "ETA: --"
        else:
            eta_str = "ETA: --"
        
        # Create progress bar
        bar_length = 40
        filled_length = int(bar_length * self.current // self.total) if self.total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # Print progress
        print(f'\r{self.description}: |{bar}| {self.current}/{self.total} ({percentage:.1f}%) {eta_str} {detail}', end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete
    
    def finish(self, message: str = "Complete!"):
        """Finish the progress bar."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f'\r{self.description}: Complete! ({self.current}/{self.total}) in {elapsed:.1f}s - {message}')
        print()

class SQLiteToPostgreSQLMigrator:
    def __init__(self, sqlite_path: str = "avatar_cache.db", batch_size: int = 1000):
        self.sqlite_path = sqlite_path
        self.batch_size = batch_size
        self.pg_connection = None
        
    async def connect_postgresql(self):
        """Connect to PostgreSQL database with improved URL parsing."""
        try:
            # Parse database URL properly
            parsed = urlparse(settings.database_url)
            
            # Handle different URL formats
            if parsed.scheme in ['postgresql+asyncpg', 'postgresql', 'postgres']:
                self.pg_connection = await asyncpg.connect(
                    host=parsed.hostname,
                    port=parsed.port or 5432,
                    user=parsed.username,
                    password=parsed.password,
                    database=parsed.path[1:] if parsed.path else None  # Remove leading slash
                )
            else:
                raise ValueError(f"Unsupported database URL scheme: {parsed.scheme}")
            
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def create_tables(self):
        """Create all necessary tables in PostgreSQL."""
        try:
            # Create avatar_requests table
            await self.pg_connection.execute("""
                CREATE TABLE IF NOT EXISTS avatar_requests (
                    id SERIAL PRIMARY KEY,
                    platform VARCHAR(50) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cache_hit BOOLEAN DEFAULT FALSE,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    response_time_ms INTEGER,
                    referer TEXT
                )
            """)
            
            # Create rate_limit_tracking table
            await self.pg_connection.execute("""
                CREATE TABLE IF NOT EXISTS rate_limit_tracking (
                    id SERIAL PRIMARY KEY,
                    ip_address VARCHAR(45) NOT NULL,
                    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    endpoint VARCHAR(255) NOT NULL,
                    user_agent TEXT
                )
            """)
            
            # Create cache_metadata table
            await self.pg_connection.execute("""
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    id SERIAL PRIMARY KEY,
                    platform VARCHAR(50) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size_bytes INTEGER,
                    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    UNIQUE(platform, user_id)
                )
            """)
            
            # Create user_analytics table
            await self.pg_connection.execute("""
                CREATE TABLE IF NOT EXISTS user_analytics (
                    id SERIAL PRIMARY KEY,
                    ip_address VARCHAR(45) NOT NULL UNIQUE,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_requests INTEGER DEFAULT 1,
                    unique_platforms INTEGER DEFAULT 1,
                    platforms_used TEXT,
                    user_agent TEXT,
                    country VARCHAR(100),
                    city VARCHAR(100),
                    is_bot BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create daily_stats table
            await self.pg_connection.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id SERIAL PRIMARY KEY,
                    date VARCHAR(10) NOT NULL UNIQUE,
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
            """)
            
            # Create hourly_stats table
            await self.pg_connection.execute("""
                CREATE TABLE IF NOT EXISTS hourly_stats (
                    id SERIAL PRIMARY KEY,
                    datetime VARCHAR(19) NOT NULL UNIQUE,
                    requests INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    bandwidth_mb REAL DEFAULT 0
                )
            """)
            
            # Create error_logs table
            await self.pg_connection.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error_type VARCHAR(100) NOT NULL,
                    error_message TEXT NOT NULL,
                    platform VARCHAR(50),
                    user_id VARCHAR(255),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    stack_trace TEXT
                )
            """)
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_avatar_requests_platform_user ON avatar_requests(platform, user_id)",
                "CREATE INDEX IF NOT EXISTS idx_avatar_requests_timestamp ON avatar_requests(request_timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_avatar_requests_ip ON avatar_requests(ip_address)",
                "CREATE INDEX IF NOT EXISTS idx_rate_limit_ip_timestamp ON rate_limit_tracking(ip_address, request_timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_cache_metadata_platform_user ON cache_metadata(platform, user_id)",
                "CREATE INDEX IF NOT EXISTS idx_user_analytics_ip ON user_analytics(ip_address)",
                "CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)",
                "CREATE INDEX IF NOT EXISTS idx_hourly_stats_datetime ON hourly_stats(datetime)",
                "CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp)"
            ]
            
            for index_sql in indexes:
                await self.pg_connection.execute(index_sql)
            
            logger.info("Database tables and indexes created successfully!")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    async def validate_schema_compatibility(self, table_name: str, sqlite_columns: List[str]) -> List[str]:
        """Check if SQLite columns are compatible with PostgreSQL schema."""
        try:
            # Get PostgreSQL table columns
            pg_columns = await self.pg_connection.fetch(
                "SELECT column_name FROM information_schema.columns WHERE table_name = $1",
                table_name
            )
            pg_column_names = {row['column_name'] for row in pg_columns}
            
            # Check for missing columns
            missing_columns = set(sqlite_columns) - pg_column_names
            if missing_columns:
                print(f"⚠️  Warning: {table_name} has columns not in PostgreSQL schema: {missing_columns}")
                # Filter out missing columns
                compatible_columns = [col for col in sqlite_columns if col in pg_column_names]
                print(f"  └─ Using compatible columns: {compatible_columns}")
                return compatible_columns
            
            return sqlite_columns
        except Exception as e:
            print(f"⚠️  Could not validate schema for {table_name}: {e}")
            return sqlite_columns
    
    def convert_datetime_string(self, datetime_str):
        """Convert datetime string to datetime object."""
        if datetime_str is None:
            return None
        
        try:
            # Try different datetime formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            # If no format works, return the string as-is
            print(f"⚠️  Warning: Could not parse datetime '{datetime_str}', using as string")
            return datetime_str
            
        except Exception as e:
            print(f"⚠️  Warning: Error parsing datetime '{datetime_str}': {e}")
            return datetime_str

    def convert_boolean_value(self, value):
        """Convert SQLite boolean (int) to Python boolean."""
        if value is None:
            return None
        
        # SQLite stores booleans as 0/1, PostgreSQL expects True/False
        if isinstance(value, int):
            return bool(value)
        elif isinstance(value, str):
            # Handle string representations
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
            else:
                return bool(int(value)) if value.isdigit() else False
        else:
            return bool(value)

    def process_row_data(self, row_data: List, columns: List[str], table_name: str) -> List:
        """Process row data with appropriate type conversions."""
        for i, val in enumerate(row_data):
            if i >= len(columns):
                break
                
            column_name = columns[i]
            
            # Handle None values
            if val is None:
                if column_name in ['cache_hit', 'success', 'is_bot']:
                    row_data[i] = False
                elif column_name in ['response_time_ms', 'access_count', 'total_requests', 'unique_platforms']:
                    row_data[i] = 0
                else:
                    row_data[i] = None
            # Handle datetime conversions
            elif column_name in ['request_timestamp', 'created_timestamp', 'last_accessed', 'first_seen', 'last_seen', 'timestamp'] and isinstance(val, str):
                row_data[i] = self.convert_datetime_string(val)
            # Handle boolean conversions
            elif column_name in ['cache_hit', 'success', 'is_bot']:
                row_data[i] = self.convert_boolean_value(val)
        
        return row_data

    async def migrate_table_in_batches(self, table_name: str):
        """Migrate a table in batches to handle large datasets efficiently."""
        with sqlite3.connect(self.sqlite_path) as db:
            # Get total count
            cursor = db.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]
            
            if total_rows == 0:
                print(f"📋 {table_name}: No data to migrate")
                return
            
            # Get column info
            cursor = db.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            sqlite_columns = [col[1] for col in columns_info]
            
            # Validate schema compatibility
            compatible_columns = await self.validate_schema_compatibility(table_name, sqlite_columns)
            
            print(f"📋 {table_name}: Migrating {total_rows:,} rows in batches of {self.batch_size:,}...")
            
            # Create progress bar for large datasets
            progress = ProgressBar(total_rows, f"  └─ {table_name}")
            
            # Use transaction for the entire table migration
            async with self.pg_connection.transaction():
                try:
                    offset = 0
                    total_migrated = 0
                    
                    while offset < total_rows:
                        # Fetch batch from SQLite
                        cursor = db.execute(f"SELECT * FROM {table_name} LIMIT {self.batch_size} OFFSET {offset}")
                        batch_rows = cursor.fetchall()
                        
                        if not batch_rows:
                            break
                        
                        # Process batch data
                        processed_data = []
                        for row in batch_rows:
                            row_data = self.process_row_data(list(row), sqlite_columns, table_name)
                            # Only include data for compatible columns
                            if len(compatible_columns) != len(sqlite_columns):
                                # Map to compatible columns only
                                compatible_row = []
                                for col in compatible_columns:
                                    col_index = sqlite_columns.index(col)
                                    compatible_row.append(row_data[col_index])
                                processed_data.append(tuple(compatible_row))
                            else:
                                processed_data.append(tuple(row_data))
                        
                        # Insert batch into PostgreSQL
                        if processed_data:
                            placeholders = ", ".join([f"${i+1}" for i in range(len(compatible_columns))])
                            column_names = ", ".join(compatible_columns)
                            
                            query = f"""
                                INSERT INTO {table_name} ({column_names}) 
                                VALUES ({placeholders})
                                ON CONFLICT DO NOTHING
                            """
                            
                            await self.pg_connection.executemany(query, processed_data)
                            total_migrated += len(processed_data)
                        
                        offset += len(batch_rows)
                        progress.update(len(batch_rows), f"({len(batch_rows)} rows)")
                    
                    progress.finish(f"✅ {total_migrated:,} rows migrated successfully")
                    
                except Exception as e:
                    print(f"\n  └─ ❌ Error migrating {table_name}: {e}")
                    logger.error(f"Error migrating table {table_name}: {e}")
                    raise

    async def run_pre_migration_checks(self) -> bool:
        """Run checks before starting migration."""
        print("🔍 Running pre-migration checks...")
        
        # Check PostgreSQL connection
        try:
            await self.pg_connection.fetch("SELECT 1")
            print("✅ PostgreSQL connection working")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return False
        
        # Check SQLite database
        if not os.path.exists(self.sqlite_path):
            print(f"❌ SQLite database not found: {self.sqlite_path}")
            return False
        
        print(f"✅ SQLite database found: {self.sqlite_path}")
        
        # Check if tables already have data
        tables_to_check = ["avatar_requests", "rate_limit_tracking", "cache_metadata", 
                          "user_analytics", "daily_stats", "hourly_stats", "error_logs"]
        
        existing_data = {}
        for table in tables_to_check:
            try:
                count = await self.pg_connection.fetchval(f"SELECT COUNT(*) FROM {table}")
                existing_data[table] = count
                if count > 0:
                    print(f"⚠️  {table} already contains {count:,} rows")
            except:
                # Table might not exist yet, which is fine
                existing_data[table] = 0
        
        if any(count > 0 for count in existing_data.values()):
            try:
                response = input("Some tables already contain data. Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("Migration cancelled by user")
                    return False
            except (EOFError, KeyboardInterrupt):
                print("\nMigration cancelled by user")
                return False
        
        print("✅ Pre-migration checks passed")
        return True

    async def verify_migration(self):
        """Verify that migration completed successfully."""
        print("\n🔍 Verifying migration integrity...")
        
        tables_to_verify = ["avatar_requests", "rate_limit_tracking", "cache_metadata", 
                           "user_analytics", "daily_stats", "hourly_stats", "error_logs"]
        
        with sqlite3.connect(self.sqlite_path) as db:
            verification_results = []
            
            for table in tables_to_verify:
                try:
                    # Count rows in SQLite
                    sqlite_cursor = db.execute(f"SELECT COUNT(*) FROM {table}")
                    sqlite_count = sqlite_cursor.fetchone()[0]
                    
                    # Count rows in PostgreSQL
                    pg_count = await self.pg_connection.fetchval(f"SELECT COUNT(*) FROM {table}")
                    
                    if sqlite_count == pg_count:
                        print(f"✅ {table}: {sqlite_count:,} rows (perfect match)")
                        verification_results.append(True)
                    else:
                        print(f"⚠️  {table}: SQLite={sqlite_count:,}, PostgreSQL={pg_count:,} (mismatch)")
                        verification_results.append(False)
                
                except Exception as e:
                    print(f"❌ Could not verify {table}: {e}")
                    verification_results.append(False)
        
        success_rate = sum(verification_results) / len(verification_results) * 100
        print(f"\n📊 Verification success rate: {success_rate:.1f}% ({sum(verification_results)}/{len(verification_results)} tables)")
        
        if all(verification_results):
            print("✅ All tables verified successfully!")
        else:
            print("⚠️  Some tables had verification issues - please review the results above")
        
        return all(verification_results)

    async def run_migration(self):
        """Run the complete migration with enhanced error handling and verification."""
        start_time = datetime.now()
        
        try:
            print("🚀 Starting enhanced migration from SQLite to PostgreSQL...")
            print("=" * 70)
            
            # Connect to PostgreSQL
            print("🔌 Connecting to PostgreSQL database...")
            await self.connect_postgresql()
            print("✅ Connected to PostgreSQL successfully!")
            
            # Run pre-migration checks
            if not await self.run_pre_migration_checks():
                print("❌ Pre-migration checks failed. Aborting migration.")
                return False
            
            # Get SQLite database info
            with sqlite3.connect(self.sqlite_path) as db:
                cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"📊 Found {len(tables)} tables in SQLite: {', '.join(tables)}")
            
            # Create database tables first
            print("\n🏗️  Creating PostgreSQL database tables and indexes...")
            await self.create_tables()
            print("✅ Database schema created successfully!")
            
            # Define migration order (order matters for referential integrity)
            migration_tables = [
                "user_analytics",      # Independent table
                "avatar_requests",     # Main requests table
                "rate_limit_tracking", # Rate limiting data
                "cache_metadata",      # Cache information
                "daily_stats",         # Aggregated daily stats
                "hourly_stats",        # Aggregated hourly stats
                "error_logs"           # Error information
            ]
            
            # Filter to only include tables that exist in SQLite
            existing_tables = [table for table in migration_tables if table in tables]
            
            print(f"\n📦 Starting data migration for {len(existing_tables)} tables...")
            print("-" * 70)
            
            # Create overall progress tracker
            overall_progress = ProgressBar(len(existing_tables), "Migration Progress")
            total_rows_migrated = 0
            migration_success = True
            
            for i, table_name in enumerate(existing_tables):
                try:
                    await self.migrate_table_in_batches(table_name)
                    overall_progress.update(1, f"✅ {table_name}")
                    
                    # Count migrated rows
                    with sqlite3.connect(self.sqlite_path) as db:
                        cursor = db.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = cursor.fetchone()[0]
                        total_rows_migrated += row_count
                        
                except Exception as e:
                    print(f"\n❌ Failed to migrate {table_name}: {e}")
                    overall_progress.update(1, f"❌ {table_name}")
                    migration_success = False
                    # Continue with other tables instead of failing completely
                    continue
            
            overall_progress.finish("Migration phase completed!")
            
            # Verify migration integrity
            verification_success = await self.verify_migration()
            
            # Final summary
            elapsed_time = (datetime.now() - start_time).total_seconds()
            print("\n" + "=" * 70)
            
            if migration_success and verification_success:
                print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            else:
                print("⚠️  MIGRATION COMPLETED WITH ISSUES")
            
            print("=" * 70)
            print(f"📊 Total rows processed: {total_rows_migrated:,}")
            print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
            if total_rows_migrated > 0:
                print(f"📈 Average speed: {total_rows_migrated/elapsed_time:.1f} rows/second")
            print(f"🗃️  Batch size used: {self.batch_size:,} rows")
            
            if migration_success and verification_success:
                print("✅ Your data is now ready in PostgreSQL!")
                print("\n💡 Next steps:")
                print("   • Update your application configuration to use PostgreSQL")
                print("   • Test your application with the new database")
                print("   • Consider backing up the SQLite file before removing it")
            else:
                print("⚠️  Please review any errors above and consider re-running for failed tables")
            
            print("=" * 70)
            return migration_success and verification_success
            
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            print(f"\n❌ Migration failed after {elapsed_time:.1f} seconds: {e}")
            logger.error(f"Migration failed: {e}", exc_info=True)
            return False
        finally:
            if self.pg_connection:
                await self.pg_connection.close()
                print("🔌 PostgreSQL connection closed")

async def main():
    """Main function to run the migration with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL")
    parser.add_argument("--sqlite-path", default="avatar_cache.db", 
                       help="Path to SQLite database file (default: avatar_cache.db)")
    parser.add_argument("--batch-size", type=int, default=1000,
                       help="Number of rows to process in each batch (default: 1000)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print(f"Configuration:")
    print(f"  SQLite database: {args.sqlite_path}")
    print(f"  Batch size: {args.batch_size:,}")
    print(f"  Verbose logging: {args.verbose}")
    print()
    
    migrator = SQLiteToPostgreSQLMigrator(
        sqlite_path=args.sqlite_path,
        batch_size=args.batch_size
    )
    
    success = await migrator.run_migration()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
