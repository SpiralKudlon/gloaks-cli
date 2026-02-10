from fastapi.testclient import TestClient
from gloaks.api.app import app
import os

client = TestClient(app)

def test_api_auth_missing():
    response = client.post("/scans", json={"target": "example.com"})
    assert response.status_code == 403

def test_api_auth_invalid():
    response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403

def test_api_auth_valid():
    # Set env var mock if needed, but app uses default if not set
    # Default is "gloaks-secret-123"
    response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 200
    assert "scan_id" in response.json()

def test_input_validation_invalid_target():
    response = client.post("/scans", 
                          json={"target": "invalid_target_!@#"}, 
                          headers={"X-API-Key": "gloaks-secret-123"})
    assert response.status_code == 422 # Validation error

def test_rate_limiting():
    # Reset limit for this test (mocking would be better but simple iteration works for now)
    # We need to hit it > 10 times
    for _ in range(12):
        response = client.post("/scans", json={"target": "example.com"}, headers={"X-API-Key": "gloaks-secret-123"})
        if response.status_code == 429:
            break
    else:
        assert False, "Rate limit not triggered"
    
    assert response.status_code == 429
