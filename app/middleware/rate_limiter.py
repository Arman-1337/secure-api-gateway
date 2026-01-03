"""
Rate limiting middleware using Redis
"""
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from redis import Redis
from redis.exceptions import RedisError
from ..core.config import settings

class RateLimiter:
    """Token bucket rate limiter using Redis."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.redis.ping()
            self.redis_available = True
        except (RedisError, Exception) as e:
            print(f"⚠️  Redis not available: {e}")
            print("⚠️  Rate limiting disabled - running in fallback mode")
            self.redis_available = False
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting."""
        # Try to get user from token, otherwise use IP
        if hasattr(request.state, 'user_id'):
            return f"user:{request.state.user_id}"
        
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        return f"ip:{request.client.host}"
    
    async def check_rate_limit(self, request: Request) -> None:
        """
        Check if request is within rate limit.
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        if not settings.RATE_LIMIT_ENABLED or not self.redis_available:
            return
        
        identifier = self._get_identifier(request)
        key = f"rate_limit:{identifier}"
        
        try:
            # Get current count
            current = self.redis.get(key)
            
            if current is None:
                # First request in window
                self.redis.setex(
                    key,
                    settings.RATE_LIMIT_WINDOW,
                    1
                )
            else:
                if int(current) >= settings.RATE_LIMIT_REQUESTS:
                    # Rate limit exceeded
                    ttl = self.redis.ttl(key)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {ttl} seconds",
                        headers={"Retry-After": str(ttl)}
                    )
                
                # Increment counter
                self.redis.incr(key)
        
        except RedisError as e:
            # If Redis fails, allow request (fail open)
            print(f"Redis error in rate limiter: {e}")
            pass
    
    def get_usage(self, request: Request) -> dict:
        """Get current rate limit usage for identifier."""
        if not self.redis_available:
            return {
                "limit": settings.RATE_LIMIT_REQUESTS,
                "remaining": settings.RATE_LIMIT_REQUESTS,
                "reset": 0
            }
        
        identifier = self._get_identifier(request)
        key = f"rate_limit:{identifier}"
        
        try:
            current = self.redis.get(key)
            ttl = self.redis.ttl(key)
            
            if current is None:
                remaining = settings.RATE_LIMIT_REQUESTS
            else:
                remaining = max(0, settings.RATE_LIMIT_REQUESTS - int(current))
            
            return {
                "limit": settings.RATE_LIMIT_REQUESTS,
                "remaining": remaining,
                "reset": ttl if ttl > 0 else settings.RATE_LIMIT_WINDOW
            }
        except RedisError:
            return {
                "limit": settings.RATE_LIMIT_REQUESTS,
                "remaining": settings.RATE_LIMIT_REQUESTS,
                "reset": 0
            }

rate_limiter = RateLimiter()