#!/usr/bin/env python3
"""
Standalone Bulk Avatar Import Script
===================================

This script imports avatars directly to the filesystem and database
without going through the web API, avoiding memory issues and timeouts.

Usage:
    python bulk_import_standalone.py /path/to/source/avatars [--batch-size 1000] [--skip-existing]

Features:
- Direct filesystem operations (no memory cache loading)
- Efficient database batch operations
- Progress tracking and resumability
- Memory efficient for large datasets
- Checks existing files to avoid duplicates

Requirements:
- Run from the same directory as run.py
- Database and cache directories must be accessible
"""

import asyncio
import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
import aiofiles
import aiosqlite

# Import your existing modules
sys.path.append('.')
from database.models import Database
from config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StandaloneBulkImporter:
    def __init__(self, cache_dir: str = None, db_path: str = None):
        self.cache_dir = Path(cache_dir or settings.cache_dir)
        self.db_path = db_path or "avatar_cache.db"
        self.platforms = ["epic", "steam", "xbox", "psn", "switch"]
        self.db = Database(self.db_path)
        
        # Ensure cache directories exist
        for platform in self.platforms:
            platform_dir = self.cache_dir / platform
            platform_dir.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self, platform: str, user_id: str) -> Path:
        """Get file path for platform and user ID."""
        return self.cache_dir / platform / f"{user_id}.png"
    
    def parse_filename(self, filename: str) -> Tuple[str, str]:
        """Parse filename to extract platform and user_id."""
        if '-' not in filename:
            raise ValueError(f"Invalid filename format: {filename} (expected: platform-uid)")
        
        # Split on the first dash to separate platform from uid
        platform, user_id = filename.split('-', 1)
        
        if platform not in self.platforms:
            raise ValueError(f"Unknown platform: {platform}")
        
        return platform, user_id
    
    async def file_exists_in_cache(self, platform: str, user_id: str) -> bool:
        """Check if file already exists in cache."""
        cache_file = self.get_file_path(platform, user_id)
        return cache_file.exists()
    
    async def copy_avatar_file(self, source_path: Path, platform: str, user_id: str) -> bool:
        """Copy avatar file to cache directory."""
        try:
            cache_file = self.get_file_path(platform, user_id)
            
            # Read source file
            async with aiofiles.open(source_path, 'rb') as src:
                image_data = await src.read()
            
            # Write to cache
            async with aiofiles.open(cache_file, 'wb') as dst:
                await dst.write(image_data)
            
            return True
        except Exception as e:
            logger.error(f"Error copying {source_path} to cache: {e}")
            return False
    
    async def process_batch(self, files: List[Path], skip_existing: bool = True) -> Dict:
        """Process a batch of files."""
        batch_stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "metadata": [],
            "errors": []
        }
        
        for file_path in files:
            batch_stats["processed"] += 1
            
            try:
                # Parse filename
                filename = file_path.stem
                platform, user_id = self.parse_filename(filename)
                
                # Check if already exists
                if skip_existing and await self.file_exists_in_cache(platform, user_id):
                    batch_stats["skipped"] += 1
                    logger.debug(f"Skipping existing {platform}/{user_id}")
                    continue
                
                # Copy file to cache
                success = await self.copy_avatar_file(file_path, platform, user_id)
                
                if success:
                    batch_stats["successful"] += 1
                    
                    # Prepare metadata for database
                    cache_file = self.get_file_path(platform, user_id)
                    file_size = file_path.stat().st_size
                    batch_stats["metadata"].append((
                        platform, user_id, str(cache_file), file_size
                    ))
                    
                    logger.debug(f"Imported {platform}/{user_id}")
                else:
                    batch_stats["failed"] += 1
                    batch_stats["errors"].append(f"Failed to copy {filename}")
                
            except ValueError as e:
                batch_stats["failed"] += 1
                batch_stats["errors"].append(str(e))
                logger.debug(f"Skipping invalid file: {e}")
            except Exception as e:
                batch_stats["failed"] += 1
                batch_stats["errors"].append(f"Error processing {file_path.name}: {str(e)}")
                logger.error(f"Error processing {file_path}: {e}")
        
        return batch_stats
    
    async def bulk_import(self, source_dir: Path, batch_size: int = 1000, skip_existing: bool = True) -> Dict:
        """Perform bulk import from source directory."""
        logger.info(f"Starting bulk import from: {source_dir}")
        logger.info(f"Batch size: {batch_size}, Skip existing: {skip_existing}")
        
        # Initialize database
        await self.db.initialize()
        
        # Find all PNG files
        png_files = list(source_dir.rglob("*.png"))
        total_files = len(png_files)
        
        if total_files == 0:
            logger.error("No PNG files found in source directory")
            return {"error": "No PNG files found"}
        
        logger.info(f"Found {total_files} PNG files to process")
        
        # Initialize statistics
        total_stats = {
            "total_files": total_files,
            "total_processed": 0,
            "total_successful": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "platforms": {},
            "errors": [],
            "start_time": time.time()
        }
        
        # Process in batches
        batch_count = 0
        total_batches = (total_files + batch_size - 1) // batch_size
        
        for i in range(0, total_files, batch_size):
            batch_files = png_files[i:i + batch_size]
            batch_count += 1
            
            logger.info(f"Processing batch {batch_count}/{total_batches} ({len(batch_files)} files)")
            
            # Process the batch
            batch_stats = await self.process_batch(batch_files, skip_existing)
            
            # Update total statistics
            total_stats["total_processed"] += batch_stats["processed"]
            total_stats["total_successful"] += batch_stats["successful"]
            total_stats["total_failed"] += batch_stats["failed"]
            total_stats["total_skipped"] += batch_stats["skipped"]
            total_stats["errors"].extend(batch_stats["errors"])
            
            # Track platform statistics
            for platform, user_id, _, _ in batch_stats["metadata"]:
                if platform not in total_stats["platforms"]:
                    total_stats["platforms"][platform] = 0
                total_stats["platforms"][platform] += 1
            
            # Bulk insert database metadata
            if batch_stats["metadata"]:
                try:
                    await self.db.bulk_insert_cache_metadata(batch_stats["metadata"])
                    logger.debug(f"Inserted {len(batch_stats['metadata'])} metadata entries")
                except Exception as e:
                    logger.error(f"Error inserting metadata batch: {e}")
            
            # Progress report
            elapsed = time.time() - total_stats["start_time"]
            progress = (total_stats["total_processed"] / total_files) * 100
            rate = total_stats["total_processed"] / elapsed if elapsed > 0 else 0
            eta = (total_files - total_stats["total_processed"]) / rate if rate > 0 else 0
            
            logger.info(f"Progress: {progress:.1f}% ({total_stats['total_processed']}/{total_files}) "
                       f"- {rate:.1f} files/sec - ETA: {eta/60:.1f} min")
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.05)
        
        # Final statistics
        total_stats["elapsed_time"] = time.time() - total_stats["start_time"]
        
        # Log completion summary
        asyncio.create_task(
                self.db.log_avatar_request(
                "bulk_import", "standalone_script", False, True,
                f"Bulk imported {total_stats['total_successful']} avatars in {total_stats['elapsed_time']:.1f}s",
                "localhost"
            )
        )
        logger.info(f"Bulk import completed in {total_stats['elapsed_time']:.1f} seconds")
        logger.info(f"Results: {total_stats['total_successful']} successful, "
                   f"{total_stats['total_failed']} failed, {total_stats['total_skipped']} skipped")
        
        return total_stats


async def main():
    parser = argparse.ArgumentParser(description="Standalone Avatar Bulk Import")
    parser.add_argument("source_dir", help="Source directory containing avatar files")
    parser.add_argument("--batch-size", type=int, default=1000, 
                       help="Number of files to process per batch (default: 1000)")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                       help="Skip files that already exist in cache (default: True)")
    parser.add_argument("--cache-dir", help="Cache directory path (default: from config)")
    parser.add_argument("--db-path", help="Database path (default: avatar_cache.db)")
    
    args = parser.parse_args()
    
    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    # Create importer
    importer = StandaloneBulkImporter(args.cache_dir, args.db_path)
    
    try:
        # Run the import
        results = await importer.bulk_import(
            source_dir, 
            args.batch_size, 
            args.skip_existing
        )
        
        if "error" in results:
            logger.error(f"Import failed: {results['error']}")
            sys.exit(1)
        
        # Print final results
        print("\n" + "="*60)
        print("🎉 BULK IMPORT COMPLETED!")
        print("="*60)
        print(f"📁 Total files found: {results['total_files']:,}")
        print(f"✅ Successfully imported: {results['total_successful']:,}")
        print(f"⏭️  Skipped (existing): {results['total_skipped']:,}")
        print(f"❌ Failed: {results['total_failed']:,}")
        print(f"⏱️  Total time: {results['elapsed_time']:.1f} seconds")
        print(f"🚀 Average rate: {results['total_successful']/results['elapsed_time']:.1f} files/sec")
        
        if results['platforms']:
            print(f"\n📊 Platform breakdown:")
            for platform, count in results['platforms'].items():
                print(f"   {platform}: {count:,} avatars")
        
        if results['errors'] and len(results['errors']) > 0:
            print(f"\n⚠️  First 10 errors:")
            for error in results['errors'][:10]:
                print(f"   - {error}")
        
        print("\n🎮 Import complete! Your avatar cache is ready!")
        
    except KeyboardInterrupt:
        logger.info("Import interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Import failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
