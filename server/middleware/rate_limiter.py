import time
import logging
from typing import Dict, List
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config import settings

logger = logging.getLogger(__name__)

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


class RateLimitMiddleware:
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.cleanup_interval = 300  # Clean up old entries every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove old entries from the requests tracking."""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - settings.rate_limit_window
        for ip in list(self.requests.keys()):
            self.requests[ip] = [req_time for req_time in self.requests[ip] if req_time > cutoff_time]
            if not self.requests[ip]:
                del self.requests[ip]
        
        self.last_cleanup = current_time
    
    def is_rate_limited(self, ip_address: str) -> bool:
        """Check if an IP address is rate limited."""
        self._cleanup_old_entries()
        
        current_time = time.time()
        cutoff_time = current_time - settings.rate_limit_window
        
        # Get recent requests for this IP
        if ip_address not in self.requests:
            self.requests[ip_address] = []
        
        # Filter to only recent requests
        recent_requests = [req_time for req_time in self.requests[ip_address] if req_time > cutoff_time]
        self.requests[ip_address] = recent_requests
        
        # Check if over limit
        if len(recent_requests) >= settings.rate_limit_requests:
            logger.warning(f"Rate limit exceeded for IP {ip_address}: {len(recent_requests)} requests in {settings.rate_limit_window} seconds")
            return True
        
        return False
    
    def record_request(self, ip_address: str):
        """Record a request from an IP address."""
        current_time = time.time()
        if ip_address not in self.requests:
            self.requests[ip_address] = []
        
        self.requests[ip_address].append(current_time)
        
        # Keep only recent requests to prevent memory bloat
        cutoff_time = current_time - settings.rate_limit_window
        self.requests[ip_address] = [req_time for req_time in self.requests[ip_address] if req_time > cutoff_time]
    
    async def check_rate_limit(self, request: Request):
        """Check and enforce rate limiting."""
        ip_address = get_remote_address(request)
        
        if self.is_rate_limited(ip_address):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {settings.rate_limit_requests} requests per {settings.rate_limit_window} seconds allowed",
                    "retry_after": settings.rate_limit_window
                }
            )
        
        self.record_request(ip_address)


# Global rate limiter instance
rate_limit_middleware = RateLimitMiddleware()


def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exception handler."""
    response = _rate_limit_exceeded_handler(request, exc)
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {exc.detail}")
    return response



