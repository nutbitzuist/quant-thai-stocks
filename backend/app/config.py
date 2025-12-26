"""
Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    app_name: str = "Quant Stock Analysis"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"  # Default to false for security
    
    # Security
    api_secret_key: str = os.getenv("API_SECRET_KEY", "")
    rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")

    # Payments (Stripe)
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_id_pro: str = os.getenv("STRIPE_PRICE_ID_PRO", "")
    
    # CORS - Allow frontend connections
    # Can be set via CORS_ORIGINS environment variable (JSON array or comma-separated)
    # Default includes localhost for development
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]
    
    # Data settings
    data_cache_minutes: int = 30
    max_workers: int = 10  # For parallel data fetching
    data_providers: List[str] = []  # Empty = use all available providers
    data_fallback_enabled: bool = True  # Try next provider if one fails
    
    # Default universe
    default_universe: str = "sp500"  # Start with S&P 500 for reliability
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override CORS origins from environment if provided
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env and cors_env.strip():
            try:
                import json
                # Try to parse as JSON first
                parsed = json.loads(cors_env)
                if isinstance(parsed, list):
                    self.cors_origins = parsed
                else:
                    # If it's a string, treat as comma-separated
                    self.cors_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
            except (json.JSONDecodeError, ValueError, TypeError):
                # If not valid JSON, treat as comma-separated
                self.cors_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
        
        # Override other settings from environment
        if os.getenv("DATA_CACHE_MINUTES"):
            self.data_cache_minutes = int(os.getenv("DATA_CACHE_MINUTES"))
        if os.getenv("MAX_WORKERS"):
            self.max_workers = int(os.getenv("MAX_WORKERS"))
        if os.getenv("DEFAULT_UNIVERSE"):
            self.default_universe = os.getenv("DEFAULT_UNIVERSE")
        if os.getenv("DATA_PROVIDERS"):
            # Comma-separated list of provider names
            self.data_providers = [p.strip() for p in os.getenv("DATA_PROVIDERS").split(",") if p.strip()]
        if os.getenv("DATA_FALLBACK_ENABLED"):
            self.data_fallback_enabled = os.getenv("DATA_FALLBACK_ENABLED").lower() == "true"
    
    class Config:
        env_file = ".env"


settings = Settings()
