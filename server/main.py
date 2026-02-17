import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import configuration and components
from config import settings
from cache.cache_manager import CacheManager
from database.models import Database
from middleware.rate_limiter import limiter, rate_limit_handler
from middleware.tracking import TrackingMiddleware

# Import routes
from routes import epic, platforms, admin, stats, tos, update, bulk

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rlprofilepicturesrevamp.log')
    ]
)
logger = logging.getLogger(__name__)

# Global instances
cache_manager: CacheManager = None
database: Database = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting RLProfilePicturesREVAMP Server...")
    
    global cache_manager, database
    
    # Initialize database
    database = Database()
    await database.initialize()
    logger.info("Database initialized")
    
    # Initialize cache manager
    cache_manager = CacheManager(settings.cache_dir)
    await cache_manager.initialize()
    logger.info("Cache manager initialized")
    
    # Set global instances in route modules
    epic.cache_manager = cache_manager
    epic.database = database
    platforms.cache_manager = cache_manager
    platforms.database = database
    admin.cache_manager = cache_manager
    admin.database = database
    stats.database = database
    bulk.cache_manager = cache_manager
    bulk.database = database
    
    logger.info(f"Server starting on {settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RLProfilePicturesREVAMP Server...")
    
    # Cleanup old rate limit data on shutdown
    if database:
        await database.cleanup_old_rate_limit_data(24)
    
    # Close shared HTTP client
    from services.avatar_services import AvatarService
    await AvatarService.close_client()
    
    logger.info("Server shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="RLProfilePicturesREVAMP API",
    description="Backend API for fetching and caching user avatars from various gaming platforms",
    version="1.0.0",
    docs_url=None,  # Disable public docs
    redoc_url=None,  # Disable public docs
    openapi_url=None,  # Disable public docs
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add tracking middleware
app.add_middleware(TrackingMiddleware, database=database)

# Include routers
app.include_router(epic.router)
app.include_router(platforms.router)
app.include_router(admin.router)
app.include_router(stats.router)
app.include_router(tos.router)
app.include_router(update.router)
app.include_router(bulk.router)
app.include_router(bulk.router_personas)


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "RLProfilePicturesREVAMP API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "epic_upload": "/api/v1/epic/upload/{epic_user_id}",
            "epic_retrieve": "/api/v1/epic/retrieve/{epic_user_id}",
            "steam_retrieve": "/api/v1/steam/retrieve/{steam_user_id}",
            "xbox_retrieve": "/api/v1/xbox/retrieve/{xbox_gamertag}",
            "psn_retrieve": "/api/v1/psn/retrieve/{psn_user_id}",
            "switch_retrieve": "/api/v1/switch/retrieve/{switch_user_id}",
            "bulk_avatars": "/api/v1/bulk/avatars",
            "bulk_avatars_get": "/api/v1/bulk/avatars/{platform}?user_ids=id1,id2,id3",
            "cache_status": "/api/v1/bulk/cache-status/{platform}?user_ids=id1,id2,id3",
            "bulk_personas_check": "/api/v1/personas/bulk-check",
            "admin_delete": "/api/v1/{platform}/delete/{user_id}",
            "admin_stats": "/api/v1/admin/stats",
            "analytics_dashboard": "/api/v1/stats?secret=YOUR_ADMIN_SECRET",
            "terms_of_service": "/tos",
            "privacy_policy": "/privacy"
        },
        "tracking": {
            "note": "This service collects usage analytics for optimization and debugging purposes",
            "privacy_policy": "/privacy",
            "terms_of_service": "/tos"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check cache manager
        cache_stats = cache_manager.get_cache_stats() if cache_manager else {}
        
        # Check database
        db_stats = await database.get_statistics() if database else {}
        
        return {
            "status": "healthy",
            "cache": {
                "available": cache_manager is not None,
                "items": cache_stats.get("total_items", 0)
            },
            "database": {
                "available": database is not None,
                "total_requests": db_stats.get("total_requests", 0)
            },
            "rate_limiting": {
                "requests_per_minute": settings.rate_limit_requests,
                "window_seconds": settings.rate_limit_window
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception in {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True
    )
