#!/usr/bin/env python3
"""
Fix PostgreSQL sequences after migration to prevent primary key conflicts
"""

import asyncio
import asyncpg
import logging
from config import settings
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_sequences():
    """Fix PostgreSQL sequences to match existing data."""
    try:
        # Parse database URL
        parsed = urlparse(settings.database_url)
        
        # Connect to PostgreSQL
        connection = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else None
        )
        
        print("🔧 Fixing PostgreSQL sequences...")
        
        # Tables with SERIAL primary keys that need sequence fixes
        tables_to_fix = [
            "avatar_requests",
            "rate_limit_tracking", 
            "cache_metadata",
            "user_analytics",
            "daily_stats",
            "hourly_stats",
            "error_logs"
        ]
        
        for table in tables_to_fix:
            try:
                # Get the current maximum ID from the table
                max_id = await connection.fetchval(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
                
                if max_id > 0:
                    # Get the sequence name (PostgreSQL convention: tablename_columnname_seq)
                    sequence_name = f"{table}_id_seq"
                    
                    # Reset the sequence to start from max_id + 1
                    await connection.execute(f"SELECT setval('{sequence_name}', {max_id}, true)")
                    
                    print(f"✅ Fixed {table}: sequence set to {max_id + 1}")
                else:
                    print(f"📋 {table}: No data, skipping sequence fix")
                    
            except Exception as e:
                print(f"⚠️  Could not fix sequence for {table}: {e}")
                continue
        
        print("🎉 All sequences fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing sequences: {e}")
        raise
    finally:
        if 'connection' in locals():
            await connection.close()

if __name__ == "__main__":
    asyncio.run(fix_sequences())

