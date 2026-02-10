import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from gloaks.api.app import app

# Happy Path Test
@patch("gloaks.api.app.run_scan_task")
def test_create_and_get_scan_happy_path(mock_task):
    with TestClient(app) as client:
        # 1. Create Scan
        response = client.post("/scans", 
                              json={"target": "example.com"}, 
                              headers={"X-API-Key": "gloaks-secret-123"})
        assert response.status_code == 200
        data = response.json()
        scan_id = data["scan_id"]
        assert data["status"] == "running"
        
        # 2. Get Scan Status (Running)
        response = client.get(f"/scans/{scan_id}", headers={"X-API-Key": "gloaks-secret-123"})
        assert response.status_code == 200
        assert response.json()["status"] == "running"

        # 3. Simulate completion (Manually update in-memory dict for the test)
        # We need to access the 'scans' dict in app.py. 
        from gloaks.api.app import scans
        scans[scan_id]["status"] = "completed"
        scans[scan_id]["results"] = {"open_ports": [80]}

        # 4. Get Scan Results
        response = client.get(f"/scans/{scan_id}", headers={"X-API-Key": "gloaks-secret-123"})
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert response.json()["results"]["open_ports"] == [80]

# Error Handling Test
def test_get_nonexistent_scan():
    with TestClient(app) as client:
        response = client.get("/scans/non-existent-id", headers={"X-API-Key": "gloaks-secret-123"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Scan not found"

@patch("gloaks.api.app.GloaksEngine")
@pytest.mark.asyncio
async def test_scan_task_failure(MockEngine):
    # Test the background task directly to ensure it handles errors
    from gloaks.api.app import run_scan_task, scans
    
    # Use patch.dict context manager to isolate state for this test, targeting the imported 'scans' or the module's 'scans'
    # Since 'scans' is imported from app, we should patch 'gloaks.api.app.scans'
    with patch.dict("gloaks.api.app.scans", {}, clear=True):
        # Mock Engine failures
        engine_instance = MockEngine.return_value
        engine_instance.run.side_effect = Exception("Engine Failure")
        
        scan_id = "test-fail-id"
        # Access the dictionary through the module path or the imported name if it reflects changes? 
        # Imported name `scans` refers to the object. `patch.dict` modifies the object in place.
        scans[scan_id] = {"scan_id": scan_id, "status": "running"}
        
        await run_scan_task(scan_id, "example.com", {}, None)
        
        assert scans[scan_id]["status"] == "failed"
        assert "Engine Failure" in scans[scan_id]["results"]["error"]
    
    scan_id = "test-fail-id"
    # We need to make sure 'scans' we import IS the patched one or mutable. 
    # Since we patched the symbol in app.py, importing it inside might get the patched one IF patch is active.
    # But patch works on where it is looked up.
    
    # Safest way to patch a dict is patch.dict.
    pass
    
    scan_id = "test-fail-id"
    scans[scan_id] = {"scan_id": scan_id, "status": "running"}
    
    await run_scan_task(scan_id, "example.com", {}, None)
    
    assert scans[scan_id]["status"] == "failed"
    assert "Engine Failure" in scans[scan_id]["results"]["error"]
