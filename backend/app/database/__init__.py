"""
Database Configuration and Session Management
Uses SQLAlchemy 2.0 async for PostgreSQL
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment (Railway provides this automatically)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Convert postgres:// to postgresql+asyncpg:// for async driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
engine = None
async_session_maker = None

if DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        echo=os.getenv("DEBUG", "false").lower() == "true",
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    async_session_maker = async_sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    logger.info("Database engine configured for PostgreSQL")
else:
    logger.warning("DATABASE_URL not set - running without database persistence")


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    if async_session_maker is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL environment variable.")
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables"""
    if engine is None:
        logger.warning("Skipping database initialization - no database configured")
        return
    
    async with engine.begin() as conn:
        # Import models to register them
        from app.database.models import User, UsageLog, CustomUniverse
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def check_db_connection() -> bool:
    """Check if database is connected"""
    if engine is None:
        return False
    
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
