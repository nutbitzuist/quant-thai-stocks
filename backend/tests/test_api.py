"""
API Tests
Tests for main API endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint returns API info"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "status" in data


@pytest.mark.anyio
async def test_models_list(client: AsyncClient):
    """Test models list endpoint"""
    response = await client.get("/api/models/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check model structure
    if len(data) > 0:
        model = data[0]
        assert "id" in model
        assert "name" in model
        assert "category" in model


@pytest.mark.anyio
async def test_universe_list(client: AsyncClient):
    """Test universe list endpoint"""
    response = await client.get("/api/universe/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.anyio
async def test_status_endpoint(client: AsyncClient):
    """Test status endpoint"""
    response = await client.get("/api/status/")
    assert response.status_code == 200


class TestModelRun:
    """Tests for model run functionality"""

    @pytest.mark.anyio
    async def test_run_invalid_model(self, client: AsyncClient):
        """Test running with invalid model ID"""
        response = await client.post(
            "/api/models/run",
            json={
                "model_id": "invalid_model_123",
                "universe": "sp50",
                "top_n": 10
            }
        )
        # Should return 404 or 400 for invalid model
        assert response.status_code in [400, 404, 422]

    @pytest.mark.anyio
    async def test_run_model_missing_params(self, client: AsyncClient):
        """Test running without required parameters"""
        response = await client.post(
            "/api/models/run",
            json={}
        )
        # Should return validation error
        assert response.status_code == 422


class TestDatabaseModels:
    """Tests for database models"""

    def test_user_model_import(self):
        """Test User model can be imported"""
        from app.database.models import User
        assert User is not None
        assert hasattr(User, 'email')
        assert hasattr(User, 'plan')

    def test_usage_log_model_import(self):
        """Test UsageLog model can be imported"""
        from app.database.models import UsageLog
        assert UsageLog is not None
        assert hasattr(UsageLog, 'model_id')
        assert hasattr(UsageLog, 'user_id')

    def test_custom_universe_model_import(self):
        """Test CustomUniverse model can be imported"""
        from app.database.models import CustomUniverse
        assert CustomUniverse is not None
        assert hasattr(CustomUniverse, 'name')
        assert hasattr(CustomUniverse, 'symbols')

    def test_backtest_result_model_import(self):
        """Test BacktestResult model can be imported"""
        from app.database.models import BacktestResult
        assert BacktestResult is not None
        assert hasattr(BacktestResult, 'model_id')
        assert hasattr(BacktestResult, 'metrics')
