import time
import asyncio
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
import os

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.max_requests = int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000"))
        self.window_size = 60  # 1 minute window
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        client_requests[:] = [req_time for req_time in client_requests 
                            if now - req_time < self.window_size]
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests
        client_requests[:] = [req_time for req_time in client_requests 
                            if now - req_time < self.window_size]
        
        return max(0, self.max_requests - len(client_requests))

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_id(request: Request) -> str:
    """Get client identifier for rate limiting"""
    # Use API key if available, otherwise use IP
    api_key = request.headers.get("app_api_key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Use X-Forwarded-For if behind proxy, otherwise use client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0].strip()}"
    
    return f"ip:{request.client.host}"

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_id = get_client_id(request)
    
    # Skip rate limiting for health checks and metrics
    if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Check rate limit
    if not rate_limiter.is_allowed(client_id):
        remaining = rate_limiter.get_remaining_requests(client_id)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded",
                "retry_after": 60,
                "remaining_requests": remaining
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + 60))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    remaining = rate_limiter.get_remaining_requests(client_id)
    
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
    
    return response 