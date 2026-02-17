import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from cache.cache_manager import CacheManager
from database.models import Database
from services.avatar_services import SteamAvatarService, XboxAvatarService, PSNAvatarService, SwitchAvatarService
from middleware.rate_limiter import rate_limit_middleware
from slowapi.util import get_remote_address
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bulk", tags=["Bulk Avatar Operations"])


class BulkAvatarRequest(BaseModel):
    """Request model for bulk avatar retrieval."""
    user_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of user IDs (max 100)")
    platform: str = Field(..., description="Platform name (steam, xbox, psn, switch, epic)")


class AvatarResult(BaseModel):
    """Result model for individual avatar."""
    user_id: str
    found: bool
    cached: bool
    avatar_data: Optional[str] = None  # Base64 encoded image data
    error: Optional[str] = None


class BulkAvatarResponse(BaseModel):
    """Response model for bulk avatar retrieval."""
    success: bool
    total_requested: int
    total_found: int
    total_cached: int
    total_fetched: int
    results: List[AvatarResult]
    processing_time_ms: int


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


async def get_avatar_service(platform: str):
    """Get the appropriate avatar service for the platform."""
    services = {
        "steam": steam_service,
        "xbox": xbox_service,
        "psn": get_psn_service(),
        "switch": switch_service,
        "epic": None  # Epic doesn't have a service, only cache
    }
    
    if platform not in services:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    return services[platform]


async def process_single_avatar(platform: str, user_id: str, cache: CacheManager, db: Database) -> AvatarResult:
    """Process a single avatar request."""
    try:
        # Check cache first
        image_data = await cache.get(platform, user_id)
        cache_hit = image_data is not None
        
        if image_data is None and platform != "epic":
            # Fetch from platform API (Epic doesn't have API, only cache)
            logger.info(f"Fetching {platform} avatar for {user_id}")
            service = await get_avatar_service(platform)
            
            if service:
                try:
                    image_data = await asyncio.wait_for(service.get_processed_avatar(user_id), timeout=20.0)
                except asyncio.TimeoutError:
                    logger.warning(f"{platform} avatar fetch timed out for {user_id}")
                    return AvatarResult(
                        user_id=user_id,
                        found=False,
                        cached=False,
                        error="Fetch timed out"
                    )
                except Exception as e:
                    logger.error(f"Error fetching {platform} avatar for {user_id}: {e}")
                    return AvatarResult(
                        user_id=user_id,
                        found=False,
                        cached=False,
                        error=str(e)
                    )
                
                if image_data:
                    # Save to cache
                    await cache.set(platform, user_id, image_data)
                    await db.update_cache_metadata(platform, user_id, 
                                                  str(cache.get_file_path(platform, user_id)), 
                                                  len(image_data))
                else:
                    return AvatarResult(
                        user_id=user_id,
                        found=False,
                        cached=False,
                        error="Avatar not found"
                    )
            else:
                return AvatarResult(
                    user_id=user_id,
                    found=False,
                    cached=False,
                    error="Platform service unavailable"
                )
        
        if image_data:
            # Convert to base64 for JSON response
            import base64
            avatar_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Update cache access if it was a cache hit
            if cache_hit:
                await db.update_cache_access(platform, user_id)
            
            return AvatarResult(
                user_id=user_id,
                found=True,
                cached=cache_hit,
                avatar_data=avatar_b64
            )
        else:
            return AvatarResult(
                user_id=user_id,
                found=False,
                cached=False,
                error="Avatar not found"
            )
            
    except Exception as e:
        logger.error(f"Error processing {platform} avatar for {user_id}: {e}")
        return AvatarResult(
            user_id=user_id,
            found=False,
            cached=False,
            error=str(e)
        )


@router.post("/avatars", response_model=BulkAvatarResponse)
async def get_bulk_avatars(
    request_data: BulkAvatarRequest,
    request: Request,
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """
    Retrieve multiple avatars in a single request.
    
    This endpoint accepts an array of user IDs and a platform, then returns:
    - Users found in cache (with their avatars)
    - Users not in cache but found via platform API (fetched and cached)
    - Users not found (with error messages)
    
    Epic platform only returns cached avatars (no API fetching).
    Other platforms will fetch from their respective APIs if not cached.
    """
    start_time = datetime.utcnow()
    
    # Apply rate limiting (more lenient for bulk requests)
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        platform = request_data.platform.lower()
        user_ids = request_data.user_ids
        
        # Validate platform
        valid_platforms = ["steam", "xbox", "psn", "switch", "epic"]
        if platform not in valid_platforms:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
            )
        
        # Process avatars concurrently (but limit concurrency to avoid overwhelming APIs)
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
        async def process_with_semaphore(user_id: str):
            async with semaphore:
                return await process_single_avatar(platform, user_id, cache, db)
        
        # Process all avatars concurrently
        results = await asyncio.gather(*[process_with_semaphore(user_id) for user_id in user_ids])
        
        # Calculate statistics
        total_requested = len(user_ids)
        total_found = sum(1 for r in results if r.found)
        total_cached = sum(1 for r in results if r.cached)
        total_fetched = total_found - total_cached
        
        # Log bulk request
        ip_address = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "")
        referer = request.headers.get("referer", "")
        
        # Log each individual request for analytics
        for result in results:
            await db.log_avatar_request(
                platform, 
                result.user_id, 
                result.cached, 
                result.found, 
                result.error, 
                ip_address, 
                user_agent, 
                None, 
                referer
            )
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info(f"Bulk avatar request completed: {total_found}/{total_requested} found, "
                   f"{total_cached} cached, {total_fetched} fetched, {processing_time}ms")
        
        return BulkAvatarResponse(
            success=True,
            total_requested=total_requested,
            total_found=total_found,
            total_cached=total_cached,
            total_fetched=total_fetched,
            results=results,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk avatar request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/avatars/{platform}")
async def get_bulk_avatars_get(
    platform: str,
    user_ids: str,  # Comma-separated list
    request: Request,
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """
    GET version of bulk avatar retrieval.
    
    Usage: /api/v1/bulk/avatars/steam?user_ids=123,456,789
    """
    try:
        # Parse user IDs
        user_id_list = [uid.strip() for uid in user_ids.split(",") if uid.strip()]
        
        if not user_id_list:
            raise HTTPException(status_code=400, detail="No user IDs provided")
        
        if len(user_id_list) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 user IDs allowed")
        
        # Create request data and use POST endpoint logic
        request_data = BulkAvatarRequest(user_ids=user_id_list, platform=platform)
        return await get_bulk_avatars(request_data, request, cache, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in GET bulk avatar request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/cache-status/{platform}")
async def get_cache_status(
    platform: str,
    user_ids: str,  # Comma-separated list
    request: Request,
    cache: CacheManager = Depends(get_cache_manager)
):
    """
    Check cache status for multiple users without fetching avatars.
    
    Usage: /api/v1/bulk/cache-status/steam?user_ids=123,456,789
    """
    try:
        # Parse user IDs
        user_id_list = [uid.strip() for uid in user_ids.split(",") if uid.strip()]
        
        if not user_id_list:
            raise HTTPException(status_code=400, detail="No user IDs provided")
        
        if len(user_id_list) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 user IDs allowed")
        
        # Check cache status for each user
        cache_status = {}
        for user_id in user_id_list:
            exists = cache.exists(platform, user_id)
            cache_status[user_id] = {
                "cached": exists,
                "file_path": str(cache.get_file_path(platform, user_id)) if exists else None
            }
        
        return {
            "platform": platform,
            "total_checked": len(user_id_list),
            "total_cached": sum(1 for status in cache_status.values() if status["cached"]),
            "cache_status": cache_status
        }
        
    except Exception as e:
        logger.error(f"Error checking cache status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


class BulkPersonasCheckRequest(BaseModel):
    """Request model for bulk personas check."""
    epic: Optional[List[str]] = Field(default_factory=list, max_items=100)
    steam: Optional[List[str]] = Field(default_factory=list, max_items=100)
    psn: Optional[List[str]] = Field(default_factory=list, max_items=100)
    xbox: Optional[List[str]] = Field(default_factory=list, max_items=100)
    switch: Optional[List[str]] = Field(default_factory=list, max_items=100)


class BulkPersonasCheckResponse(BaseModel):
    """Response model for bulk personas check."""
    epic: Dict[str, str] = Field(default_factory=dict)
    steam: Dict[str, str] = Field(default_factory=dict)
    psn: Dict[str, str] = Field(default_factory=dict)
    xbox: Dict[str, str] = Field(default_factory=dict)
    switch: Dict[str, str] = Field(default_factory=dict)


router_personas = APIRouter(prefix="/api/v1/personas", tags=["Personas"])


@router_personas.post("/bulk-check", response_model=BulkPersonasCheckResponse)
async def bulk_check_personas(
    request_data: BulkPersonasCheckRequest,
    request: Request,
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """
    Check which users have avatars available (bulk check for personas feature).
    
    Returns API endpoint URLs for avatars that exist in cache.
    This endpoint is optimized for checking many users at once.
    """
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        from sqlalchemy import select
        
        result = BulkPersonasCheckResponse()
        
        # Check each platform
        platforms_data = {
            "epic": request_data.epic or [],
            "steam": request_data.steam or [],
            "psn": request_data.psn or [],
            "xbox": request_data.xbox or [],
            "switch": request_data.switch or []
        }
        
        # For each platform, check cache metadata to see which users have avatars
        from database.models import CacheMetadata
        from sqlalchemy import select
        
        async with db.get_session() as session:
            for platform, user_ids in platforms_data.items():
                if not user_ids:
                    continue
                
                # Query cache_metadata to find which users have avatars
                cache_result = await session.execute(
                    select(CacheMetadata.user_id)
                    .where(
                        CacheMetadata.platform == platform,
                        CacheMetadata.user_id.in_(user_ids)
                    )
                )
                cached_user_ids = {row[0] for row in cache_result.fetchall()}
                
                # Also check filesystem cache for users not in database
                for user_id in user_ids:
                    avatar_url = None
                    if user_id in cached_user_ids:
                        # Construct API endpoint URL (relative path)
                        avatar_url = f"/api/v1/{platform}/retrieve/{user_id}"
                    else:
                        # Check filesystem cache as fallback
                        file_path = cache.get_file_path(platform, user_id)
                        if file_path.exists():
                            avatar_url = f"/api/v1/{platform}/retrieve/{user_id}"
                    
                    if avatar_url:
                        if platform == "epic":
                            result.epic[user_id] = avatar_url
                        elif platform == "steam":
                            result.steam[user_id] = avatar_url
                        elif platform == "psn":
                            result.psn[user_id] = avatar_url
                        elif platform == "xbox":
                            result.xbox[user_id] = avatar_url
                        elif platform == "switch":
                            result.switch[user_id] = avatar_url
        
        logger.info(f"Bulk personas check completed: {sum(len(v) for v in [result.epic, result.steam, result.psn, result.xbox, result.switch])} avatars found")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk personas check: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")