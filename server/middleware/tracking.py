import time
import logging
import uuid
import traceback
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


class TrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request tracking and analytics (Reverted to lightweight version)."""
    
    def __init__(self, app, database=None):
        super().__init__(app)
        self.database = database
    
    async def dispatch(self, request: Request, call_next):
        """Process each request with lightweight tracking."""
        start_time = time.time()
        
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Extract request information
        ip_address = get_remote_address(request)
        path = request.url.path
        
        # Skip tracking for certain paths
        if self._should_skip_tracking(path):
            return await call_next(request)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # NOTE: Database logging is now handled directly by routes for better accuracy.
            # We don't log to DB here anymore to avoid performance bottlenecks.
            
            # Add tracking headers
            response.headers["X-Response-Time"] = str(response_time_ms)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log errors
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Request failed: {request.method} {path} - {e}")
            
            # Database error logging (optional, could also be moved to routes/global handler)
            # if self.database:
            #     import asyncio
            #     asyncio.create_task(self._log_error_to_db(request, e, response_time_ms, ip_address))
                
            raise
    
    def _should_skip_tracking(self, path: str) -> bool:
        """Determine if we should skip tracking for this path."""
        skip_paths = ["/health", "/favicon.ico", "/stats", "/docs", "/redoc", "/openapi.json", "/update"]
        return any(path.startswith(skip) for skip in skip_paths)
    
    def _is_avatar_request(self, path: str) -> bool:
        """Check if this is an avatar request."""
        return "/retrieve/" in path or "/upload/" in path

    async def _log_error_to_db(self, request: Request, error: Exception, 
                               response_time_ms: int, ip_address: str):
        """Log error details to database (Backup)."""
        if not self.database:
            return
        
        try:
            # Extract platform and user_id if possible
            path_parts = request.url.path.split("/")
            platform = path_parts[2] if len(path_parts) >= 3 else None
            user_id = path_parts[3] if len(path_parts) >= 4 else None
            
            await self.database.log_error(
                error_type=type(error).__name__,
                error_message=str(error),
                platform=platform,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=request.headers.get("user-agent", ""),
                stack_trace=traceback.format_exc()
            )
        except Exception as e:
            logger.error(f"Failed to log error to database: {e}")
