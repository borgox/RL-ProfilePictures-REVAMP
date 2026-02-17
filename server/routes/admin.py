import logging
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from typing import Optional
from cache.cache_manager import CacheManager
from database.models import Database
from middleware.rate_limiter import rate_limit_middleware
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Admin"])


async def get_cache_manager() -> CacheManager:
    """Dependency to get cache manager."""
    return cache_manager


async def get_database() -> Database:
    """Dependency to get database."""
    return database


def verify_admin_secret(authorization: Optional[str] = Header(None)):
    """Verify admin secret from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    # Support both "Bearer <secret>" and just "<secret>" formats
    secret = authorization
    if authorization.startswith("Bearer "):
        secret = authorization[7:]
    
    if secret != settings.admin_secret:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin secret"
        )
    
    return True


# Global instances (will be initialized in main.py)
cache_manager: Optional[CacheManager] = None
database: Optional[Database] = None


@router.delete("/epic/delete/{epic_user_id}")
async def delete_epic_avatar(
    epic_user_id: str,
    request: Request,
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database),
    _: bool = Depends(verify_admin_secret)
):
    """Delete an Epic Games user avatar (Admin only)."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        success = await cache.delete("epic", epic_user_id)
        
        if success:
            await db.delete_cache_metadata("epic", epic_user_id)
            logger.info(f"Admin deleted Epic avatar for user {epic_user_id}")
            return {"success": True, "message": f"Avatar deleted for Epic user {epic_user_id}"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Avatar not found for Epic user {epic_user_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Epic avatar for {epic_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/steam/delete/{steam_user_id}")
async def delete_steam_avatar(
    steam_user_id: str,
    request: Request,
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database),
    _: bool = Depends(verify_admin_secret)
):
    """Delete a Steam user avatar (Admin only)."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        success = await cache.delete("steam", steam_user_id)
        
        if success:
            await db.delete_cache_metadata("steam", steam_user_id)
            logger.info(f"Admin deleted Steam avatar for user {steam_user_id}")
            return {"success": True, "message": f"Avatar deleted for Steam user {steam_user_id}"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Avatar not found for Steam user {steam_user_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Steam avatar for {steam_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/xbox/delete/{xbox_gamertag}")
async def delete_xbox_avatar(
    xbox_gamertag: str,
    request: Request,
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database),
    _: bool = Depends(verify_admin_secret)
):
    """Delete an Xbox user avatar (Admin only)."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        success = await cache.delete("xbox", xbox_gamertag)
        
        if success:
            await db.delete_cache_metadata("xbox", xbox_gamertag)
            logger.info(f"Admin deleted Xbox avatar for user {xbox_gamertag}")
            return {"success": True, "message": f"Avatar deleted for Xbox user {xbox_gamertag}"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Avatar not found for Xbox user {xbox_gamertag}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Xbox avatar for {xbox_gamertag}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/psn/delete/{psn_user_id}")
async def delete_psn_avatar(
    psn_user_id: str,
    request: Request,
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database),
    _: bool = Depends(verify_admin_secret)
):
    """Delete a PSN user avatar (Admin only)."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        success = await cache.delete("psn", psn_user_id)
        
        if success:
            await db.delete_cache_metadata("psn", psn_user_id)
            logger.info(f"Admin deleted PSN avatar for user {psn_user_id}")
            return {"success": True, "message": f"Avatar deleted for PSN user {psn_user_id}"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Avatar not found for PSN user {psn_user_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PSN avatar for {psn_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/admin/stats")
async def get_admin_stats(
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database),
    _: bool = Depends(verify_admin_secret)
):
    """Get admin statistics (Admin only)."""
    try:
        cache_stats = cache.get_cache_stats()
        db_stats = await db.get_statistics()
        
        return {
            "cache": cache_stats,
            "database": db_stats,
            "system": {
                "rate_limit_requests": settings.rate_limit_requests,
                "rate_limit_window": settings.rate_limit_window,
                "target_image_size": settings.target_image_size,
                "cache_directory": settings.cache_dir
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/admin/cleanup")
async def cleanup_old_data(
    hours: int = 24,
    db: Database = Depends(get_database),
    _: bool = Depends(verify_admin_secret)
):
    """Clean up old rate limit tracking data (Admin only)."""
    try:
        await db.cleanup_old_rate_limit_data(hours)
        logger.info(f"Admin cleaned up rate limit data older than {hours} hours")
        return {"success": True, "message": f"Cleaned up data older than {hours} hours"}
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



