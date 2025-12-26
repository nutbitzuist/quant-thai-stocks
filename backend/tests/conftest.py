"""
Test Configuration
Pytest fixtures for API testing
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db

@pytest.fixture(scope="function", autouse=True)
async def db_session():
    """Create in-memory SQLite database and override get_db dependency"""
    # Create engine
    engine = create_async_engine(
        "sqlite+aiosqlite://", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Create session
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        # Override dependency
        async def override():
            yield session
            
        app.dependency_overrides[get_db] = override
        yield session
        app.dependency_overrides.clear()
        
    await engine.dispose()



@pytest.fixture
async def client():
    """Create test client for async API testing"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
