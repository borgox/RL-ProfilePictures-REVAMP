import logging
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import Response
from typing import Optional
from cache.cache_manager import CacheManager
from database.models import Database
from services.avatar_services import SteamAvatarService, XboxAvatarService, PSNAvatarService, SwitchAvatarService
from services.default_service import default_service
from middleware.rate_limiter import rate_limit_middleware
from slowapi.util import get_remote_address
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Platform Avatars"])


async def get_cache_manager() -> CacheManager:
    """Dependency to get cache manager."""
    return cache_manager


async def get_database() -> Database:
    """Dependency to get database."""
    return database


# Global instances (will be initialized in main.py)
cache_manager: Optional[CacheManager] = None
database: Optional[Database] = None

# Service instances
steam_service = SteamAvatarService()
xbox_service = XboxAvatarService()
psn_service = None  # Will be initialized when needed
switch_service = SwitchAvatarService()

def get_psn_service():
    """Get or create PSN service instance."""
    global psn_service
    if psn_service is None:
        try:
            psn_service = PSNAvatarService()
        except Exception as e:
            logger.error(f"Failed to initialize PSN service: {e}")
            raise HTTPException(status_code=500, detail="PSN service unavailable")
    return psn_service


@router.get("/steam/retrieve/{steam_user_id}")
async def retrieve_steam_avatar(
    steam_user_id: str,
    request: Request,
    default_enabled: bool = Query(False, description="Use default avatar if user avatar not found"),
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """Retrieve a Steam user avatar."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        # Check cache first
        image_data = await cache.get("steam", steam_user_id)
        cache_hit = image_data is not None
        
        if image_data is None:
            # Fetch from Steam API (bounded by timeout)
            logger.info(f"Fetching Steam avatar for {steam_user_id}")
            try:
                image_data = await asyncio.wait_for(steam_service.get_processed_avatar(steam_user_id), timeout=20.0)
            except asyncio.TimeoutError:
                logger.warning(f"Steam avatar fetch timed out for {steam_user_id}; using fallback or returning not found")
                image_data = None
            except Exception as e:
                logger.error(f"Error fetching Steam avatar for {steam_user_id}: {e}")
                image_data = None
            
            if image_data is None:
                # Try default avatar if enabled
                if default_enabled:
                    logger.info(f"Avatar not found for Steam user {steam_user_id}, using default avatar")
                    default_image = await default_service.get_default_avatar("steam")
                    
                    if default_image is not None:
                        # Log successful default avatar usage
                        ip_address = get_remote_address(request)
                        user_agent = request.headers.get("user-agent", "")
                        referer = request.headers.get("referer", "")
                        await db.log_avatar_request("steam", steam_user_id, False, True, "Default avatar used", ip_address, user_agent, None, referer)
                        
                        return Response(
                            content=default_image,
                            media_type="image/png",
                            headers={
                                "Cache-Control": "public, max-age=86400",  # Cache default for 24 hours
                                "Content-Length": str(len(default_image))
                            }
                        )
                
                ip_address = get_remote_address(request)
                await db.log_avatar_request("steam", steam_user_id, False, False, "Avatar not found", ip_address)
                raise HTTPException(
                    status_code=404,
                    detail=f"Avatar not found for Steam user {steam_user_id}"
                )
            
            # Save to cache
            await cache.set("steam", steam_user_id, image_data)
            await db.update_cache_metadata("steam", steam_user_id, 
                                          str(cache.get_file_path("steam", steam_user_id)), 
                                          len(image_data))
        else:
            await db.update_cache_access("steam", steam_user_id)
        
        # Log request
        ip_address = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "")
        referer = request.headers.get("referer", "")
        asyncio.create_task(
            db.log_avatar_request("steam", steam_user_id, cache_hit, True, None, ip_address, user_agent, None, referer)
        )
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Length": str(len(image_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Steam avatar for {steam_user_id}: {e}")
        ip_address = get_remote_address(request)
        asyncio.create_task(
            db.log_avatar_request("steam", steam_user_id, False, False, str(e), ip_address)
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/xbox/retrieve/{xbox_gamertag}")
async def retrieve_xbox_avatar(
    xbox_gamertag: str,
    request: Request,
    default_enabled: bool = Query(False, description="Use default avatar if user avatar not found"),
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """Retrieve an Xbox user avatar."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        # Check cache first
        image_data = await cache.get("xbox", xbox_gamertag)
        cache_hit = image_data is not None
        
        if image_data is None:
            # Fetch from Xbox API (bounded by timeout)
            logger.info(f"Fetching Xbox avatar for {xbox_gamertag}")
            try:
                image_data = await asyncio.wait_for(xbox_service.get_processed_avatar(xbox_gamertag), timeout=20.0)
            except asyncio.TimeoutError:
                logger.warning(f"Xbox avatar fetch timed out for {xbox_gamertag}; using fallback or returning not found")
                image_data = None
            except Exception as e:
                logger.error(f"Error fetching Xbox avatar for {xbox_gamertag}: {e}")
                image_data = None
            
            if image_data is None:
                # Try default avatar if enabled
                if default_enabled:
                    logger.info(f"Avatar not found for Xbox user {xbox_gamertag}, using default avatar")
                    default_image = await default_service.get_default_avatar("xbox")
                    
                    if default_image is not None:
                        # Log successful default avatar usage
                        ip_address = get_remote_address(request)
                        user_agent = request.headers.get("user-agent", "")
                        referer = request.headers.get("referer", "")
                        await db.log_avatar_request("xbox", xbox_gamertag, False, True, "Default avatar used", ip_address, user_agent, None, referer)
                        
                        return Response(
                            content=default_image,
                            media_type="image/png",
                            headers={
                                "Cache-Control": "public, max-age=86400",  # Cache default for 24 hours
                                "Content-Length": str(len(default_image))
                            }
                        )
                
                ip_address = get_remote_address(request)
                await db.log_avatar_request("xbox", xbox_gamertag, False, False, "Avatar not found", ip_address)
                raise HTTPException(
                    status_code=404,
                    detail=f"Avatar not found for Xbox user {xbox_gamertag}"
                )
            
            # Save to cache
            await cache.set("xbox", xbox_gamertag, image_data)
            await db.update_cache_metadata("xbox", xbox_gamertag, 
                                          str(cache.get_file_path("xbox", xbox_gamertag)), 
                                          len(image_data))
        else:
            await db.update_cache_access("xbox", xbox_gamertag)
        
        # Log request
        ip_address = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "")
        referer = request.headers.get("referer", "")
        asyncio.create_task(
            db.log_avatar_request("xbox", xbox_gamertag, cache_hit, True, None, ip_address, user_agent, None, referer)
        )
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Length": str(len(image_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Xbox avatar for {xbox_gamertag}: {e}")
        ip_address = get_remote_address(request)
        asyncio.create_task(
            db.log_avatar_request("xbox", xbox_gamertag, False, False, str(e), ip_address)
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/psn/retrieve/{psn_user_id}")
async def retrieve_psn_avatar(
    psn_user_id: str,
    request: Request,
    default_enabled: bool = Query(False, description="Use default avatar if user avatar not found"),
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """Retrieve a PSN user avatar."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        # Check cache first
        image_data = await cache.get("psn", psn_user_id)
        cache_hit = image_data is not None
        
        if image_data is None:
            # Fetch from PSN API (bounded by timeout)
            logger.info(f"Fetching PSN avatar for {psn_user_id}")
            psn_svc = get_psn_service()
            try:
                image_data = await asyncio.wait_for(psn_svc.get_processed_avatar(psn_user_id), timeout=20.0)
            except asyncio.TimeoutError:
                logger.warning(f"PSN avatar fetch timed out for {psn_user_id}; using fallback or returning not found")
                image_data = None
            except Exception as e:
                logger.error(f"Error fetching PSN avatar for {psn_user_id}: {e}")
                image_data = None
            
            if image_data is None:
                # Try default avatar if enabled
                if default_enabled:
                    logger.info(f"Avatar not found for PSN user {psn_user_id}, using default avatar")
                    default_image = await default_service.get_default_avatar("psn")
                    
                    if default_image is not None:
                        # Log successful default avatar usage
                        ip_address = get_remote_address(request)
                        user_agent = request.headers.get("user-agent", "")
                        referer = request.headers.get("referer", "")
                        await db.log_avatar_request("psn", psn_user_id, False, True, "Default avatar used", ip_address, user_agent, None, referer)
                        
                        return Response(
                            content=default_image,
                            media_type="image/png",
                            headers={
                                "Cache-Control": "public, max-age=86400",  # Cache default for 24 hours
                                "Content-Length": str(len(default_image))
                            }
                        )
                
                ip_address = get_remote_address(request)
                await db.log_avatar_request("psn", psn_user_id, False, False, "Avatar not found", ip_address)
                raise HTTPException(
                    status_code=404,
                    detail=f"Avatar not found for PSN user {psn_user_id}"
                )
            
            # Save to cache
            await cache.set("psn", psn_user_id, image_data)
            await db.update_cache_metadata("psn", psn_user_id, 
                                          str(cache.get_file_path("psn", psn_user_id)), 
                                          len(image_data))
        else:
            await db.update_cache_access("psn", psn_user_id)
        
        # Log request
        ip_address = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "")
        referer = request.headers.get("referer", "")
        asyncio.create_task(
            db.log_avatar_request("psn", psn_user_id, cache_hit, True, None, ip_address, user_agent, None, referer)
        )
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Length": str(len(image_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving PSN avatar for {psn_user_id}: {e}")
        ip_address = get_remote_address(request)
        asyncio.create_task(
            db.log_avatar_request("psn", psn_user_id, False, False, str(e), ip_address)
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/switch/retrieve/{switch_user_id}")
async def retrieve_switch_avatar(
    switch_user_id: str,
    request: Request,
    default_enabled: bool = Query(False, description="Use default avatar if user avatar not found"),
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """Retrieve a Nintendo Switch user avatar."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        # Check cache first
        image_data = await cache.get("switch", switch_user_id)
        cache_hit = image_data is not None
        
        if image_data is None:
            # Generate deterministic Switch avatar (bounded by timeout)
            logger.info(f"Generating Switch avatar for {switch_user_id}")
            try:
                image_data = await asyncio.wait_for(switch_service.get_processed_avatar(switch_user_id), timeout=20.0)
            except asyncio.TimeoutError:
                logger.warning(f"Switch avatar generation timed out for {switch_user_id}; using fallback default")
                image_data = None
            except Exception as e:
                logger.error(f"Error generating Switch avatar for {switch_user_id}: {e}")
                image_data = None
            
            if image_data is None:
                # Try default avatar as fallback for Switch (always enabled for Switch)
                logger.info(f"Avatar generation failed for Switch user {switch_user_id}, using default avatar")
                image_data = await default_service.get_default_avatar("switch")
                
                if image_data is None:
                    ip_address = get_remote_address(request)
                    await db.log_avatar_request("switch", switch_user_id, False, False, "Avatar generation and default fallback failed", ip_address)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate avatar for Switch user {switch_user_id}"
                    )
            
            # Save to cache
            await cache.set("switch", switch_user_id, image_data)
            await db.update_cache_metadata("switch", switch_user_id, 
                                          str(cache.get_file_path("switch", switch_user_id)), 
                                          len(image_data))
        else:
            await db.update_cache_access("switch", switch_user_id)
        
        # Log request
        ip_address = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "")
        referer = request.headers.get("referer", "")
        asyncio.create_task(
            db.log_avatar_request("switch", switch_user_id, cache_hit, True, None, ip_address, user_agent, None, referer)
        )
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache Switch avatars for 24 hours
                "Content-Length": str(len(image_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Switch avatar for {switch_user_id}: {e}")
        ip_address = get_remote_address(request)
        asyncio.create_task(
            db.log_avatar_request("switch", switch_user_id, False, False, str(e), ip_address)
        )
        raise HTTPException(status_code=500, detail="Internal server error")


