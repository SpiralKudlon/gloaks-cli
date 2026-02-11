import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from gloaks.api.app import app, get_session
from gloaks.api.models import Scan
import pytest_asyncio
import os

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

app.dependency_overrides[get_session] = get_test_session

app.dependency_overrides[get_session] = get_test_session

# Set API Key for tests
os.environ["GLOAKS_API_KEY"] = "gloaks-secret-123"

# Define async fixture properly
@pytest_asyncio.fixture(name="client")
async def client_fixture():
    # Override dependency for this test context
    app.dependency_overrides[get_session] = get_test_session
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    with TestClient(app) as client:
        yield client
        
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        
    # Cleanup dependency override
    app.dependency_overrides.pop(get_session, None)

@patch("gloaks.api.app.run_scan_task")
@pytest.mark.asyncio
async def test_create_and_get_scan_happy_path(mock_task, client):
    # 1. Create Scan
    response = client.post("/scans", 
                          json={"target": "example.com"}, 
                          headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 200
    data = response.json()
    scan_id = data["id"]
    assert data["status"] == "pending"

    # 2. Get Scan Status
    response = client.get(f"/scans/{scan_id}", headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 200

    # 3. Simulate completion (Update DB)
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        scan = await session.get(Scan, scan_id)
        if scan:
            scan.status = "completed"
            scan.results = {"open_ports": [80]}
            session.add(scan)
            await session.commit()

    # 4. Get Scan Results
    response = client.get(f"/scans/{scan_id}", headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["results"]["open_ports"] == [80]

@pytest.mark.asyncio
async def test_get_nonexistent_scan(client):
    response = client.get("/scans/non-existent-id", headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 404

@patch("gloaks.api.app.GloaksEngine")
@pytest.mark.asyncio
async def test_scan_task_failure(MockEngine):
    # Test the background task logic directly
    from gloaks.api.app import run_scan_task
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    try:
        # Create session factory
        async_session_factory = sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session_factory() as session:
            # Create a scan in DB
            scan = Scan(id="test-fail-id", target="example.com", status="pending")
            session.add(scan)
            await session.commit()
            
        # Mock Engine failures
        engine_instance = MockEngine.return_value
        engine_instance.run.side_effect = Exception("Engine Failure")
        
        # Run task
        await run_scan_task("test-fail-id", "example.com", {}, None, async_session_factory)
        
        # Verify DB state
        async with async_session_factory() as session:
            scan = await session.get(Scan, "test-fail-id")
            assert scan.status == "failed"
            assert "Engine Failure" in scan.results.get("error", "")
            
    finally:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
