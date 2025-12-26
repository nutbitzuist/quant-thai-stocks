"""
Rate Limiting Configuration
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
import os

from app.config import settings

# Create limiter instance
# Uses remote address (IP) as the key
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"] if settings.rate_limit_enabled else ["100000/minute"],
    enabled=settings.rate_limit_enabled,
    storage_uri="memory://"
)

def get_limiter():
    return limiter
