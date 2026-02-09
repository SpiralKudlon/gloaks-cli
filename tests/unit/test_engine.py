import pytest
from gloaks.core.engine import GloaksEngine
from gloaks.core.config import GloaksConfig

@pytest.mark.asyncio
async def test_engine_initialization():
    config = GloaksConfig()
    engine = GloaksEngine(config)
    assert len(engine.modules) == 4
    assert engine.modules[0].name == "geolocation"

@pytest.mark.asyncio
async def test_engine_run_modules():
    config = GloaksConfig()
    engine = GloaksEngine(config)
    
    # Mocking modules would be ideal here, but for now we test integration 
    # with the real modules (they handle errors gracefully)
    # We use a dummy target that won't resolve to avoid external network calls holding up tests if possible
    # But some modules might try.
    
    # For unit test, we should mock.
    # But let's verify invalid target handling.
    results = await engine.run("invalid-target-12345.local")
    
    assert results["target"] == "invalid-target-12345.local"
    assert "geolocation" in results["modules"]
    assert "port_scan" in results["modules"]
