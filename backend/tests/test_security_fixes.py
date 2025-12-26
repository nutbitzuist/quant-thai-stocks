"""
Security Fixes Tests
Verifies authentication, user isolation, input validation, and destructive actions
"""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
import os

# Set environment variables for testing
os.environ["API_SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "false"

from app.main import app

@pytest.fixture
async def client_auth():
    """Client with valid auth headers"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        ac.headers = {
            "X-API-Key": "test-secret-key",
            "X-User-ID": "test_user_1"
        }
        yield ac

@pytest.fixture
async def client_no_auth():
    """Client without auth headers"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_auth_enforcement(client_no_auth):
    """Test that protected endpoints require auth"""
    # Try to create custom universe without auth
    response = await client_no_auth.post(
        "/api/custom-universe/",
        json={"name": "Hacker Universe", "tickers": ["AAPL"]}
    )
    assert response.status_code == 401
    assert "Missing API key" in response.json()['detail']

@pytest.mark.anyio
async def test_user_isolation(client_auth):
    """Test that users cannot see others' data"""
    # 1. Create universe as User 1
    create_resp = await client_auth.post(
        "/api/custom-universe/",
        json={"name": "User1 Universe", "tickers": ["AAPL"]}
    )
    assert create_resp.status_code == 200
    universe_id = create_resp.json()['universe']['id']
    
    # 2. Try to get it as User 2
    async with AsyncClient(app=app, base_url="http://test") as ac2:
        ac2.headers = {
            "X-API-Key": "test-secret-key",
            "X-User-ID": "test_user_2"
        }
        get_resp = await ac2.get(f"/api/custom-universe/{universe_id}")
        assert get_resp.status_code == 404 or "not found" in str(get_resp.json()).lower()

@pytest.mark.anyio
async def test_input_validation(client_auth):
    """Test data validation prevents bad inputs"""
    # Invalid ticker
    response = await client_auth.post(
        "/api/custom-universe/",
        json={"name": "Bad Ticker", "tickers": ["INVALID$TICKER"]}
    )
    assert response.status_code == 400
    assert "Invalid ticker format" in response.json()['detail']
    
    # Empty name
    response = await client_auth.post(
        "/api/custom-universe/",
        json={"name": "", "tickers": ["AAPL"]}
    )
    assert response.status_code == 400

@pytest.mark.anyio
async def test_destructive_confirmation(client_auth):
    """Test delete requires confirmation"""
    # Create universe
    create_resp = await client_auth.post(
        "/api/custom-universe/",
        json={"name": "Delete Me", "tickers": ["AAPL"]}
    )
    universe_id = create_resp.json()['universe']['id']
    
    # Try delete without confirm
    del_resp = await client_auth.delete(f"/api/custom-universe/{universe_id}")
    assert del_resp.status_code == 400
    assert "confirm=true" in del_resp.json()['detail']
    
    # Delete with confirm
    del_resp_ok = await client_auth.delete(f"/api/custom-universe/{universe_id}?confirm=true")
    assert del_resp_ok.status_code == 200

@pytest.mark.anyio
async def test_debug_hidden(client_no_auth):
    """Test debug endpoints are hidden in production"""
    # app/config.py check env var at import time, so might need reload or mock
    # Assuming DEBUG=false set at start of this file works for app re-import/usage
    response = await client_no_auth.get("/debug/errors")
    assert response.status_code == 404
