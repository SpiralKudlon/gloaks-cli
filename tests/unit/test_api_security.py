import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from gloaks.api.app import app, get_session

# Setup Test Database (Async)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

async def get_test_session():
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# Global override removed to avoid pollution
# app.dependency_overrides[get_session] = get_test_session

# Force a known key for testing
os.environ["GLOAKS_API_KEY"] = "gloaks-secret-123"

@pytest.fixture(autouse=True)
def dependency_override():
    app.dependency_overrides[get_session] = get_test_session
    yield
    app.dependency_overrides.pop(get_session, None)

@pytest.mark.asyncio
@patch("gloaks.api.app.run_scan_task")
async def test_api_auth_missing(mock_task):
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    with TestClient(app) as client:
        response = client.post("/scans", json={"target": "example.com"})
        assert response.status_code == 403

@pytest.mark.asyncio
@patch("gloaks.api.app.run_scan_task")
async def test_api_auth_invalid(mock_task):
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    with TestClient(app) as client:
        # Note: TestClient methods are sync (blocking), but fine here.
        response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 403

@pytest.mark.asyncio
@patch("gloaks.api.app.run_scan_task")
async def test_api_auth_valid(mock_task):
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    # Mock the background task creation? 
    # run_scan_task is patched.
    
    with TestClient(app) as client:
        response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "gloaks-secret-123"})
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
@patch("gloaks.api.app.run_scan_task")
async def test_input_validation_invalid_target(mock_task):
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    with TestClient(app) as client:
        response = client.post("/scans", 
                              json={"target": "invalid_target_!@#"}, 
                              headers={"X-API-Key": "gloaks-secret-123"})
        assert response.status_code == 422 # Validation error

@pytest.mark.asyncio
@patch("gloaks.api.app.run_scan_task")
async def test_rate_limiting(mock_task):
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    # Reset limit for this test
    from gloaks.api.app import request_history
    request_history.clear()
    
    with TestClient(app) as client:
        for _ in range(12):
            response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "gloaks-secret-123"})
            if response.status_code == 429:
                break
        else:
            assert False, "Rate limit not triggered"
        
        assert response.status_code == 429
