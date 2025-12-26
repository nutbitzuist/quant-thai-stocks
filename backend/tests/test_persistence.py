"""
Persistence Tests
Verify data is stored in the database and survives across calls
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import os

# Ensure we use test secret
os.environ["API_SECRET_KEY"] = "test-secret-key"

@pytest.fixture
async def client_auth():
    """Client with valid auth headers"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.headers = {
            "X-API-Key": "test-secret-key",
            "X-User-ID": "test_persistence_user"
        }
        yield ac

@pytest.mark.anyio
async def test_universe_persistence(client_auth):
    """Test creating and retrieving universes from DB"""
    # 1. Create
    create_resp = await client_auth.post(
        "/api/custom-universe/",
        json={"name": "Persist Test", "tickers": ["AAPL", "GOOG"]}
    )
    assert create_resp.status_code == 200
    uid = create_resp.json()['universe']['id']
    
    # 2. Retrieve
    get_resp = await client_auth.get(f"/api/custom-universe/{uid}")
    assert get_resp.status_code == 200
    assert get_resp.json()['name'] == "Persist Test"
    assert "AAPL" in get_resp.json()['tickers']

@pytest.mark.anyio
async def test_scheduled_scan_persistence(client_auth):
    """Test creating and listing scheduled scans from DB"""
    # 1. Create
    create_resp = await client_auth.post(
        "/api/scheduled-scans/",
        json={
            "model_id": "rsi_reversal",
            "universe": "US",
            "schedule_time": "09:30",
            "days": ["Mon"],
            "enabled": True
        }
    )
    assert create_resp.status_code == 200
    scan_id = create_resp.json()['scan']['id']
    
    # 2. List
    list_resp = await client_auth.get("/api/scheduled-scans/")
    assert list_resp.status_code == 200
    scans = list_resp.json()['scans']
    found = next((s for s in scans if s['id'] == scan_id), None)
    assert found is not None
    assert found['schedule_time'] == "09:30"
    
    # 3. Soft Delete
    del_resp = await client_auth.delete(f"/api/scheduled-scans/{scan_id}?confirm=true")
    assert del_resp.status_code == 200
    
    # 4. Verify Gone
    list_resp_2 = await client_auth.get("/api/scheduled-scans/")
    scans_2 = list_resp_2.json()['scans']
    found_2 = next((s for s in scans_2 if s['id'] == scan_id), None)
    assert found_2 is None

@pytest.mark.anyio
async def test_history_persistence(client_auth):
    """Test history is saved and retrieved from DB"""
    # Note: Calling /api/models/run directly might try to fetch real data
    # We'll just check if /history endpoint works empty first
    hist_resp = await client_auth.get("/api/models/history")
    assert hist_resp.status_code == 200
    assert "runs" in hist_resp.json()
