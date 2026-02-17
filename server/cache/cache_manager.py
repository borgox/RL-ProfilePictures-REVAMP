import os
import logging
import asyncio
from typing import Optional, Dict, List
import aiofiles
from pathlib import Path
import time
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, cache_dir: str = "cache", max_memory_cache_size: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.memory_cache: Dict[str, bytes] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_access_count: Dict[str, int] = {}
        self.max_memory_cache_size = max_memory_cache_size
        
        # Ensure cache directories exist
        self.platforms = ["epic", "steam", "xbox", "psn", "switch"]
        for platform in self.platforms:
            platform_dir = self.cache_dir / platform
            platform_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize cache manager (lazy loading for large caches)."""
        logger.info("Initializing cache manager...")
        
        # Count existing cache files without loading into memory
        total_files = 0
        for platform in self.platforms:
            platform_dir = self.cache_dir / platform
            if platform_dir.exists():
                file_count = len(list(platform_dir.glob("*.png")))
                total_files += file_count
                logger.info(f"Found {file_count} cached {platform} avatars")
        
        logger.info(f"Cache manager initialized. {total_files} avatars available on filesystem (lazy loading enabled)")
    
    def get_cache_key(self, platform: str, user_id: str) -> str:
        """Generate cache key for platform and user ID."""
        # Sanitize user_id to prevent path traversal
        safe_user_id = hashlib.md5(user_id.encode()).hexdigest()[:16]
        return f"{platform}/{safe_user_id}"
    
    def get_file_path(self, platform: str, user_id: str) -> Path:
        """Get file path for platform and user ID."""
        # Use the same sanitized user_id as cache key
        safe_user_id = hashlib.md5(user_id.encode()).hexdigest()[:16]
        return self.cache_dir / platform / f"{safe_user_id}.png"
    
    async def get(self, platform: str, user_id: str) -> Optional[bytes]:
        """Get image from cache."""
        cache_key = self.get_cache_key(platform, user_id)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            logger.debug(f"Cache hit for {cache_key}")
            # Update access count and timestamp
            self.cache_access_count[cache_key] = self.cache_access_count.get(cache_key, 0) + 1
            self.cache_timestamps[cache_key] = time.time()
            return self.memory_cache[cache_key]
        
        # Check filesystem cache
        file_path = self.get_file_path(platform, user_id)
        if file_path.exists():
            try:
                async with aiofiles.open(file_path, 'rb') as f:
                    image_data = await f.read()
                
                # Load into memory cache (with size management)
                await self._manage_memory_cache_size()
                self.memory_cache[cache_key] = image_data
                self.cache_timestamps[cache_key] = file_path.stat().st_mtime
                self.cache_access_count[cache_key] = 1
                
                logger.debug(f"Loaded {cache_key} from filesystem to memory")
                return image_data
            except Exception as e:
                logger.error(f"Error reading cache file {file_path}: {e}")
        
        logger.debug(f"Cache miss for {cache_key}")
        return None
    
    async def set(self, platform: str, user_id: str, image_data: bytes) -> bool:
        """Set image in cache (both memory and filesystem)."""
        cache_key = self.get_cache_key(platform, user_id)
        file_path = self.get_file_path(platform, user_id)
        
        try:
            # Save to filesystem
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_data)
            
            # Save to memory cache (with size management)
            await self._manage_memory_cache_size()
            self.memory_cache[cache_key] = image_data
            self.cache_timestamps[cache_key] = time.time()
            self.cache_access_count[cache_key] = 1
            
            logger.debug(f"Cached {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Error caching {cache_key}: {e}")
            return False
    
    async def delete(self, platform: str, user_id: str) -> bool:
        """Delete image from cache (both memory and filesystem)."""
        cache_key = self.get_cache_key(platform, user_id)
        file_path = self.get_file_path(platform, user_id)
        
        try:
            # Remove from memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            if cache_key in self.cache_timestamps:
                del self.cache_timestamps[cache_key]
            
            # Remove from filesystem
            if file_path.exists():
                file_path.unlink()
            
            logger.info(f"Deleted {cache_key} from cache")
            return True
        except Exception as e:
            logger.error(f"Error deleting {cache_key}: {e}")
            return False
    
    def exists(self, platform: str, user_id: str) -> bool:
        """Check if image exists in cache."""
        cache_key = self.get_cache_key(platform, user_id)
        return cache_key in self.memory_cache
    
    async def _manage_memory_cache_size(self):
        """Manage memory cache size by removing least recently used items."""
        if len(self.memory_cache) >= self.max_memory_cache_size:
            # Remove least recently used items (LRU eviction)
            sorted_items = sorted(
                self.cache_timestamps.items(),
                key=lambda x: x[1]
            )
            
            # Remove oldest 20% of items
            items_to_remove = int(self.max_memory_cache_size * 0.2)
            for cache_key, _ in sorted_items[:items_to_remove]:
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                if cache_key in self.cache_timestamps:
                    del self.cache_timestamps[cache_key]
                if cache_key in self.cache_access_count:
                    del self.cache_access_count[cache_key]
            
            logger.debug(f"Evicted {items_to_remove} items from memory cache")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total_size = sum(len(data) for data in self.memory_cache.values())
        total_access_count = sum(self.cache_access_count.values())
        
        # Get filesystem cache stats
        filesystem_stats = {}
        total_filesystem_files = 0
        total_filesystem_size = 0
        
        for platform in self.platforms:
            platform_dir = self.cache_dir / platform
            if platform_dir.exists():
                files = list(platform_dir.glob("*.png"))
                filesystem_files = len(files)
                filesystem_size = sum(f.stat().st_size for f in files if f.exists())
                
                filesystem_stats[platform] = {
                    "files": filesystem_files,
                    "size_bytes": filesystem_size,
                    "size_mb": round(filesystem_size / (1024 * 1024), 2)
                }
                
                total_filesystem_files += filesystem_files
                total_filesystem_size += filesystem_size
        
        return {
            "memory_cache": {
                "total_items": len(self.memory_cache),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_access_count": total_access_count,
                "max_size": self.max_memory_cache_size,
                "platforms": {
                    platform: len([k for k in self.memory_cache.keys() if k.startswith(f"{platform}/")])
                    for platform in self.platforms
                }
            },
            "filesystem_cache": {
                "total_files": total_filesystem_files,
                "total_size_bytes": total_filesystem_size,
                "total_size_mb": round(total_filesystem_size / (1024 * 1024), 2),
                "platforms": filesystem_stats
            },
            "combined": {
                "total_items": len(self.memory_cache) + total_filesystem_files,
                "total_size_bytes": total_size + total_filesystem_size,
                "total_size_mb": round((total_size + total_filesystem_size) / (1024 * 1024), 2)
            }
        }
    
    async def cleanup_old_files(self, days: int = 30):
        """Clean up old cache files from filesystem."""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned_files = 0
        
        for platform in self.platforms:
            platform_dir = self.cache_dir / platform
            if platform_dir.exists():
                for file_path in platform_dir.glob("*.png"):
                    try:
                        if file_path.stat().st_mtime < cutoff_time:
                            file_path.unlink()
                            cleaned_files += 1
                            
                            # Also remove from memory cache if present
                            cache_key = self.get_cache_key(platform, file_path.stem)
                            if cache_key in self.memory_cache:
                                del self.memory_cache[cache_key]
                            if cache_key in self.cache_timestamps:
                                del self.cache_timestamps[cache_key]
                            if cache_key in self.cache_access_count:
                                del self.cache_access_count[cache_key]
                    except Exception as e:
                        logger.error(f"Error cleaning up file {file_path}: {e}")
        
        logger.info(f"Cleaned up {cleaned_files} old cache files")
        return cleaned_files
    




