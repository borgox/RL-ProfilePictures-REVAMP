import logging
import httpx
import hashlib
import base64
import random
import asyncio
import os
from typing import Optional, List
from psnawp_api import PSNAWP
from config import settings
from utils.http_client import HttpClient
from utils.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class AvatarService:
    def __init__(self):
        self.image_processor = ImageProcessor(settings.target_image_size, settings.image_quality)

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        return await HttpClient.get_client()

    @classmethod
    async def close_client(cls):
        await HttpClient.close_client()


class SteamAvatarService(AvatarService):
    async def get_avatar_url(self, steam_id: str) -> Optional[str]:
        """Get Steam avatar URL using Steam Web API."""
        if not settings.steam_api_key:
            logger.error("Steam API key not configured")
            return None
        
        try:
            url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            params = {
                "key": settings.steam_api_key,
                "steamids": steam_id
            }
            
            client = await self.get_client()
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                players = data.get("response", {}).get("players", [])
                if players:
                    # Return the full-size avatar (avatarfull)
                    avatar_url = players[0].get("avatarfull") or players[0].get("avatarmedium") or players[0].get("avatar")
                    logger.info(f"Found Steam avatar for {steam_id}: {avatar_url}")
                    return avatar_url
                else:
                    logger.warning(f"No player data found for Steam ID {steam_id}")
            else:
                logger.warning(f"Steam API returned status {response.status_code} for {steam_id}")
        except Exception as e:
            logger.error(f"Error fetching Steam avatar for {steam_id}: {e}")
        
        return None
    
    async def get_processed_avatar(self, steam_id: str) -> Optional[bytes]:
        """Get and process Steam avatar."""
        avatar_url = await self.get_avatar_url(steam_id)
        if avatar_url:
            return await self.image_processor.download_and_process_image(avatar_url)
        return None


class XboxAvatarService(AvatarService):
    async def get_avatar_url(self, gamertag: str) -> Optional[str]:
        """Get Xbox avatar URL using Xbox Live API or fallback to xbl.io."""
        
        # 1. Try public API first
        try:
            url = f"https://peoplehub-public.xboxlive.com/people/gt({gamertag})"
            
            headers = {
                "X-Xbl-Contract-Version": "3",
                "Accept-Language": "*",
                "Accept": "application/json",
                "User-Agent": "RLProfilePicturesREVAMP/1.0.0"
            }
            
            client = await self.get_client()
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                people = data.get("people", [])
                if people and len(people) > 0:
                    person = people[0]
                    # Get the display picture URL
                    display_pic_raw = person.get("displayPicRaw")
                    if display_pic_raw:
                        logger.info(f"Found Xbox avatar for {gamertag} (Public API): {display_pic_raw}")
                        return display_pic_raw
            elif response.status_code == 429:
                logger.warning(f"Xbox Public API Rate Limit hit for {gamertag}")
            else:
                logger.warning(f"Xbox Public API returned status {response.status_code} for {gamertag}")
        except Exception as e:
            logger.error(f"Error fetching Xbox avatar from Public API for {gamertag}: {e}")
        
        # 2. Fallback to xbl.io if public API failed
        if settings.xbl_io_api_key:
            return await self._get_avatar_from_xbl_io(gamertag)
        
        return None

    async def _get_avatar_from_xbl_io(self, gamertag: str) -> Optional[str]:
        """Fallback: Get Xbox avatar using xbl.io API."""
        try:
            logger.info(f"Attempting xbl.io fallback for {gamertag}")
            # xbl.io search endpoint: https://xbl.io/api/v2/search/{gamertag}
            url = f"https://xbl.io/api/v2/search/{gamertag}"
            
            headers = {
                "X-Authorization": settings.xbl_io_api_key,
                "Accept": "application/json",
                "User-Agent": "RLProfilePicturesREVAMP/1.0.0"
            }
            
            client = await self.get_client()
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # xbl.io returns a list of people found
                people = data.get("people", [])
                if people:
                    # Find exact match if multiple returned
                    # (API usually returns best matches first, but let's be safe)
                    target_person = None
                    for person in people:
                        if person.get("gamertag", "").lower() == gamertag.lower():
                            target_person = person
                            break
                    
                    if not target_person and people:
                         # Fallback to first result if exact match not found but results exist
                         target_person = people[0]

                    if target_person:
                         display_pic_raw = target_person.get("displayPicRaw")
                         if display_pic_raw:
                             logger.info(f"Found Xbox avatar for {gamertag} (xbl.io): {display_pic_raw}")
                             return display_pic_raw
                else:
                    logger.warning(f"No people found in xbl.io response for {gamertag}")
            else:
                logger.warning(f"xbl.io API returned status {response.status_code} for {gamertag}: {response.text}")

        except Exception as e:
            logger.error(f"Error fetching Xbox avatar from xbl.io for {gamertag}: {e}")
        
        return None
    
    async def get_processed_avatar(self, gamertag: str) -> Optional[bytes]:
        """Get and process Xbox avatar."""
        avatar_url = await self.get_avatar_url(gamertag)
        if avatar_url:
            return await self.image_processor.download_and_process_image(avatar_url)
        return None


class PSNAvatarService(AvatarService):
    def __init__(self):
        super().__init__()
        if not settings.psn_npsso_token:
            raise ValueError("PSN NPSSO token not configured")
        self.psnawp = PSNAWP(settings.psn_npsso_token)
        self.PREFERRED_ORDER = ["xl", "l", "m", "s"]
    async def get_avatar_url(self, account_id: str) -> Optional[str]:
        """Get PSN avatar URL using psnawp_api."""
        try:
            # Determine if we have an Account ID (numeric) or Online ID (username)
            psn_user = None
            if account_id.isdigit():
                 psn_user = await asyncio.to_thread(self.psnawp.user, account_id=account_id)
            else:
                 # Assume it's an Online ID
                 logger.debug(f"Treating {account_id} as PSN Online ID")
                 psn_user = await asyncio.to_thread(self.psnawp.user, online_id=account_id)
            
            profile = await asyncio.to_thread(psn_user.profile)
            avatars = profile.get("avatars", [])
            
            if not avatars:
                logger.warning(f"No avatars found for {account_id}")
                return None
            
            for size in self.PREFERRED_ORDER:
                avatar = next((a for a in avatars if a.get("size") == size), None)
                if avatar and avatar.get("url"):
                    url = avatar["url"]
                    logger.info(f"Selected {size} avatar for {account_id}: {url}")
                    return url
            
            logger.warning(f"No preferred avatar size found for {account_id}")
            return None

        except Exception as e:
            logger.error(f"Error fetching PSN avatar for {account_id}: {e}")
            return None
    
    async def get_processed_avatar(self, account_id: str) -> Optional[bytes]:
        """Get and process PSN avatar."""
        avatar_url = await self.get_avatar_url(account_id)
        if avatar_url:
            return await self.image_processor.download_and_process_image(avatar_url)
        return None


class SwitchAvatarService(AvatarService):
    def __init__(self):
        super().__init__()
        # Use absolute path relative to this file to locate presets
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.presets_dir = os.path.join(base_dir, "cache", "switch", "presets")
        # Nintendo Switch has icons numbered from 000 to 230 (231 total icons)
        self.total_icons = 231
    
    def _get_deterministic_icon_number(self, switch_user_id: str) -> int:
        """Get a deterministic icon number based on the Switch user ID."""
        # Create a deterministic seed from the user ID
        user_id_bytes = switch_user_id.encode('utf-8')
        
        # Use MD5 hash to create a deterministic index
        hash_obj = hashlib.md5(user_id_bytes)
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Use the hash to select an icon (0-230)
        icon_number = hash_int % self.total_icons
        return icon_number
    
    def _get_icon_path(self, icon_number: int) -> str:
        """Get the file path for the given icon number."""
        icon_filename = f"icon_{icon_number:03d}.png"
        return os.path.join(self.presets_dir, icon_filename)
    
    async def get_processed_avatar(self, switch_user_id: str) -> Optional[bytes]:
        """Get a deterministic Nintendo Switch avatar from preset icons."""
        try:
            # Get deterministic icon number
            icon_number = self._get_deterministic_icon_number(switch_user_id)
            icon_path = self._get_icon_path(icon_number)
            
            # Check if the icon file exists
            if not os.path.exists(icon_path):
                logger.error(f"Switch icon file not found: {icon_path}")
                return None
            
            # Read the icon file
            with open(icon_path, 'rb') as f:
                icon_data = f.read()
            
            # Process the image to ensure it matches target size and quality
            processed_image = await self.image_processor.process_image_bytes(icon_data)
            
            if processed_image:
                logger.info(f"Selected Switch icon {icon_number:03d} for user {switch_user_id}")
                return processed_image
            else:
                logger.error(f"Failed to process Switch icon {icon_number:03d} for user {switch_user_id}")
                return None
            
        except Exception as e:
            logger.error(f"Error getting Switch avatar for {switch_user_id}: {e}")
            return None


