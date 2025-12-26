"""
 Global Error Handlers
 Centralized error handling to prevent sensitive info leakage
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.validation import sanitize_error_message

logger = logging.getLogger(__name__)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors"""
    logger.warning(f"Rate limit exceeded: {request.client.host} - {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": "60s"
        }
    )


from app.middleware.request_id import get_request_id

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    Logs full error but returns sanitized message to client.
    """
    # Log full details including stack trace and request ID
    req_id = get_request_id() or "unknown"
    logger.error(f"[{req_id}] Unhandled exception: {str(exc)}", exc_info=True)
    
    # Sanitize for client
    sanitized_msg = sanitize_error_message(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            # Only include sanitized message in development/debug mode if needed
            "debug_message": sanitized_msg
        }
    )


async def validation_exception_handler(request: Request, exc: ValueError):
    """Handle standard ValueError as 400 Bad Request"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "detail": str(exc)
        }
    )
