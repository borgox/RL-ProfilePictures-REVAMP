import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request, Query
from fastapi.responses import Response
from typing import Optional
from PIL import Image
import io
from cache.cache_manager import CacheManager
from database.models import Database
from utils.image_processor import ImageProcessor
from middleware.rate_limiter import rate_limit_middleware
from services.default_service import default_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/epic", tags=["Epic Games"])


async def get_cache_manager() -> CacheManager:
    """Dependency to get cache manager."""
    return cache_manager


async def get_database() -> Database:
    """Dependency to get database."""
    return database


async def get_image_processor() -> ImageProcessor:
    """Dependency to get image processor."""
    return ImageProcessor(settings.target_image_size, settings.image_quality)


# Global instances (will be initialized in main.py)
cache_manager: Optional[CacheManager] = None
database: Optional[Database] = None


@router.post("/upload/{epic_user_id}")
async def upload_epic_avatar(
    epic_user_id: str,
    request: Request,
    file: UploadFile = File(...),
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database),
    image_processor: ImageProcessor = Depends(get_image_processor)
):
    """Upload or update an Epic Games user avatar."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        # Validate file type - now accepting both PNG and JPG
        if not file.content_type or file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(
                status_code=400,
                detail="Only PNG and JPG files are allowed"
            )
        
        # Read the uploaded file
        file_content = await file.read()
        
        # Convert JPG to PNG if necessary
        if file.content_type in ["image/jpeg", "image/jpg"]:
            # Convert JPG to PNG
            pil_image = Image.open(io.BytesIO(file_content))
            # Convert to RGBA if not already
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')
            
            # Save as PNG
            png_buffer = io.BytesIO()
            pil_image.save(png_buffer, format='PNG')
            file_content = png_buffer.getvalue()
        
        # Process the image (now always PNG)
        processed_image = await image_processor.process_image_bytes(file_content)
        
        if not processed_image:
            raise HTTPException(
                status_code=400,
                detail="Failed to process image. Please ensure it's a valid image file."
            )
        
        # Save to cache
        success = await cache.set("epic", epic_user_id, processed_image)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save avatar to cache."
            )
        
        # Log to database
        ip_address = request.client.host if request.client else None
        await db.log_avatar_request("epic", epic_user_id, False, True, None, ip_address)
        await db.update_cache_metadata("epic", epic_user_id, 
                                      str(cache.get_file_path("epic", epic_user_id)), 
                                      len(processed_image))
        
        logger.info(f"Successfully uploaded avatar for Epic user {epic_user_id}")
        
        return {
            "success": True,
            "message": "Avatar uploaded successfully",
            "user_id": epic_user_id,
            "file_size_bytes": len(processed_image)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar for Epic user {epic_user_id}: {e}")
        
        # Log error to database
        ip_address = request.client.host if request.client else None
        await db.log_avatar_request("epic", epic_user_id, False, False, str(e), ip_address)
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing avatar upload."
        )


@router.get("/retrieve/{epic_user_id}")
async def retrieve_epic_avatar(
    epic_user_id: str,
    request: Request,
    default_enabled: bool = Query(False, description="Use default avatar if user avatar not found"),
    cache: CacheManager = Depends(get_cache_manager),
    db: Database = Depends(get_database)
):
    """Retrieve an Epic Games user avatar."""
    await rate_limit_middleware.check_rate_limit(request)
    
    try:
        # Try to get from cache
        image_data = await cache.get("epic", epic_user_id)
        
        if image_data is None:
            # Try default avatar if enabled
            if default_enabled:
                logger.info(f"Avatar not found for Epic user {epic_user_id}, using default avatar")
                image_data = await default_service.get_default_avatar("epic")
                
                if image_data is not None:
                    # Log successful default avatar usage
                    ip_address = request.client.host if request.client else None
                    await db.log_avatar_request("epic", epic_user_id, False, True, "Default avatar used", ip_address)
                    
                    return Response(
                        content=image_data,
                        media_type="image/png",
                        headers={
                            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                            "Pragma": "no-cache",
                            "Expires": "0",
                            "Content-Length": str(len(image_data))
                        }
                    )
            
            # Log cache miss
            ip_address = request.client.host if request.client else None
            await db.log_avatar_request("epic", epic_user_id, False, False, "Avatar not found", ip_address)
            
            raise HTTPException(
                status_code=404,
                detail=f"Avatar not found for Epic user {epic_user_id}"
            )
        
        # Update access tracking
        await db.update_cache_access("epic", epic_user_id)
        
        # Log successful cache hit
        ip_address = request.client.host if request.client else None
        await db.log_avatar_request("epic", epic_user_id, True, True, None, ip_address)
        
        logger.debug(f"Retrieved avatar for Epic user {epic_user_id}")
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
                "Content-Length": str(len(image_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving avatar for Epic user {epic_user_id}: {e}")
        
        # Log error to database
        ip_address = request.client.host if request.client else None
        await db.log_avatar_request("epic", epic_user_id, False, False, str(e), ip_address)
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving avatar."
        )


