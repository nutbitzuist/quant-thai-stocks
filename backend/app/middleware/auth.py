"""
Authentication Middleware
Simple API key + user ID based authentication
"""

import os
import logging
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader

logger = logging.getLogger(__name__)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# User ID header (passed from frontend after Clerk auth)
USER_ID_HEADER = "X-User-ID"

# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS = {
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}

# Endpoints that are public by prefix
PUBLIC_PREFIXES = [
    "/api/models",  # Model listing is public
    "/api/universe",  # Universe listing is public
    "/api/status",  # Status is public
]


def get_api_key() -> Optional[str]:
    """Get API key from environment"""
    return os.getenv("API_SECRET_KEY")


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header)
) -> bool:
    """
    Verify API key for protected endpoints.
    Returns True if authenticated, raises HTTPException if not.
    """
    # Check if endpoint is public
    path = request.url.path
    
    # Exact match public endpoints
    if path in PUBLIC_ENDPOINTS:
        return True
    
    # Prefix match public endpoints (read-only)
    if request.method == "GET":
        for prefix in PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
    
    # Check API key
    expected_key = get_api_key()
    
    # If no API key configured, allow all (dev mode)
    if not expected_key:
        logger.warning("API_SECRET_KEY not set - authentication disabled")
        return True
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide X-API-Key header."
        )
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True


async def get_current_user_id(request: Request) -> Optional[str]:
    """
    Extract user ID from request headers.
    Returns None for unauthenticated requests (public endpoints).
    """
    user_id = request.headers.get(USER_ID_HEADER)
    return user_id


async def require_user_id(request: Request) -> str:
    """
    Require user ID for protected endpoints.
    Raises HTTPException if not provided.
    """
    user_id = request.headers.get(USER_ID_HEADER)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Missing user ID. Provide X-User-ID header."
        )
    
    return user_id


class AuthMiddleware:
    """
    Authentication middleware for FastAPI.
    Checks API key for all non-public endpoints.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            method = scope["method"]
            
            # Check if public endpoint
            is_public = path in PUBLIC_ENDPOINTS
            
            if not is_public and method == "GET":
                for prefix in PUBLIC_PREFIXES:
                    if path.startswith(prefix):
                        is_public = True
                        break
            
            # For non-public endpoints, middleware will be enforced via Depends
            # This middleware is optional - main auth is via Depends(verify_api_key)
        
        await self.app(scope, receive, send)
