from fastapi.testclient import TestClient
from gloaks.api.app import app
from unittest.mock import patch
import os

client = TestClient(app)

# Mock the background task to prevent real scanning during auth tests
@patch("gloaks.api.app.run_scan_task")
def test_api_auth_missing(mock_task):
    response = client.post("/scans", json={"target": "example.com"})
    assert response.status_code == 403

@patch("gloaks.api.app.run_scan_task")
def test_api_auth_invalid(mock_task):
    response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403

@patch("gloaks.api.app.run_scan_task")
def test_api_auth_valid(mock_task):
    # Set env var mock if needed, but app uses default if not set
    # Default is "gloaks-secret-123"
    response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 200
    assert "scan_id" in response.json()

@patch("gloaks.api.app.run_scan_task")
def test_input_validation_invalid_target(mock_task):
    response = client.post("/scans", 
                          json={"target": "invalid_target_!@#"}, 
                          headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 422 # Validation error

@patch("gloaks.api.app.run_scan_task")
def test_rate_limiting(mock_task):
    # Reset limit for this test (mocking would be better but simple iteration works for now)
    # We need to hit it > 10 times
    # Note: request_history is global in app.py, so it might persist across tests if not cleared.
    # In a real test suite we would reset dependency or app state.
    from gloaks.api.app import request_history
    request_history.clear()
    
    for _ in range(12):
        response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "gloaks-secret-123"})
        if response.status_code == 429:
            break
    else:
        assert False, "Rate limit not triggered"
    
    assert response.status_code == 429
