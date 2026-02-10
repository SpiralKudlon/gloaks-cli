import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from gloaks.modules.http_analysis import HttpAnalysisModule
import httpx

@pytest.mark.asyncio
async def test_http_analysis_secure_headers():
    # Mock response with all security headers
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.url = "https://example.com"
    mock_response.headers = httpx.Headers({
        "Strict-Transport-Security": "max-age=31536000",
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Server": "nginx",
        "X-Powered-By": "PHP/7.4"
    })

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    module = HttpAnalysisModule(http_client=mock_client)
    results = await module.run("example.com", {})

    assert results["status_code"] == 200
    assert results["security_headers"]["strict_transport_security"] is True
    assert results["security_headers"]["content_security_policy"] is True
    assert results["security_headers"]["x_frame_options"] is True
    assert results["security_headers"]["x_content_type_options"] is True
    assert results["security_headers"]["referrer_policy"] is True
    assert len(results["missing_headers"]) == 0
    assert "Server: nginx" in results["technologies"]

@pytest.mark.asyncio
async def test_http_analysis_missing_headers():
    # Mock response with NO security headers
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.url = "http://example.com"
    mock_response.headers = httpx.Headers({}) # Empty

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    # Simulate HTTPS failure then HTTP success if logic dictates, 
    # but here we inject client so logic uses it.
    # The module tries HTTPS first. We can mock that.
    
    mock_client.get.return_value = mock_response

    module = HttpAnalysisModule(http_client=mock_client)
    results = await module.run("example.com", {})

    assert results["security_headers"]["strict_transport_security"] is False
    assert "Strict-Transport-Security" in results["missing_headers"]

@pytest.mark.asyncio
async def test_http_analysis_https_fallback():
    # Mock first call raises error, second call succeeds
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    
    secure_response = MagicMock()
    secure_response.status_code = 200
    secure_response.headers = httpx.Headers({})
    secure_response.url = "http://example.com"

    # side_effect: first call raises ConnectError, second returns response
    mock_client.get.side_effect = [httpx.ConnectError("Connection refused"), secure_response]

    module = HttpAnalysisModule(http_client=mock_client)
    results = await module.run("example.com", {})

    assert results["status_code"] == 200
    assert str(results["url"]) == "http://example.com"
    # Verify two calls were made
    assert mock_client.get.call_count == 2
