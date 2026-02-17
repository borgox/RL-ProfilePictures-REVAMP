import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class DefaultAvatarService:
    """Service for handling default platform avatars."""
    
    def __init__(self, default_dir: str = "files/default"):
        self.default_dir = Path(default_dir)
        self.default_avatars = {
            "steam": "steam_default.png",
            "xbox": "xbox_default.png", 
            "psn": "psn_default.png",
            "switch": "switch_default.png",
            "epic": "epic_default.png"
        }
    
    async def get_default_avatar(self, platform: str) -> Optional[bytes]:
        """Get default avatar for a platform."""
        try:
            if platform not in self.default_avatars:
                logger.warning(f"No default avatar configured for platform: {platform}")
                return None
                
            avatar_path = self.default_dir / self.default_avatars[platform]
            
            if not avatar_path.exists():
                logger.warning(f"Default avatar file not found: {avatar_path}")
                return None
                
            with open(avatar_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error loading default avatar for {platform}: {e}")
            return None
    
    def has_default_avatar(self, platform: str) -> bool:
        """Check if a default avatar exists for a platform."""
        if platform not in self.default_avatars:
            return False
        avatar_path = self.default_dir / self.default_avatars[platform]
        return avatar_path.exists()

# Global instance
default_service = DefaultAvatarService()