import logging
import os
import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request, Response
from fastapi.responses import FileResponse
from middleware.rate_limiter import rate_limit_middleware

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/update", tags=["Update"])


@router.get("/version")
async def get_current_plugin_version(
    request: Request
):
    """Check the current plugin version"""
    await rate_limit_middleware.check_rate_limit(request)
    
    # Get the root directory path
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dll_path = os.path.join(root, "files", "RLProfilePicturesREVAMP.dll")
    
    # Check if the file exists and get its info
    file_exists = os.path.exists(dll_path)
    file_size = None
    file_modified = None
    
    if file_exists:
        stat = os.stat(dll_path)
        file_size = stat.st_size
        file_modified = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
    
    return {
        "version": "1.1.2",
        "current_date": str(datetime.date.today()),
        "download_info": {
            #"file_path": dll_path,
            "file_exists": file_exists,
            "file_size_bytes": file_size,
            "last_modified": file_modified,
            "download_url": "/update/latest"
        }
    }


@router.get("/latest")
async def get_latest_plugin_file(
    request: Request
):
    """Download the latest plugin version"""
    await rate_limit_middleware.check_rate_limit(request)
    
    # Get the root directory path
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dll_path = os.path.join(root, "files", "RLProfilePicturesREVAMP.dll")
    
    # Check if the file exists
    if not os.path.exists(dll_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    # Use FileResponse for better file serving
    return FileResponse(
        path=dll_path,
        media_type="application/octet-stream",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": "attachment; filename=RLProfilePicturesREVAMP.dll"
        }
    )
