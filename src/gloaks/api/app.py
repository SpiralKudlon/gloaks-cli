from fastapi import FastAPI, BackgroundTasks, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN
from gloaks.api.models import ScanRequest, ScanResponse
from gloaks.core.engine import GloaksEngine
from gloaks.core.config import load_config
import uuid
import structlog
import os
import httpx
from collections import defaultdict
import time
from contextlib import asynccontextmanager

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create shared HTTP client
    app.state.http_client = httpx.AsyncClient(verify=True)
    yield
    # Shutdown: Close client
    await app.state.http_client.aclose()

app = FastAPI(title="Gloaks API", version="3.0.0", lifespan=lifespan)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Rate Limiting (Simple Token Bucket per Key)
RATE_LIMIT_CALLS = 10
RATE_LIMIT_PERIOD = 60  # seconds
request_history = defaultdict(list)

def check_rate_limit(api_key: str):
    now = time.time()
    # Clean up old requests
    request_history[api_key] = [t for t in request_history[api_key] if now - t < RATE_LIMIT_PERIOD]
    
    if len(request_history[api_key]) >= RATE_LIMIT_CALLS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_history[api_key].append(now)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # In production, fetch from DB or Secrets Manager
    expected_key = os.getenv("GLOAKS_API_KEY", "gloaks-secret-123")
    if api_key_header == expected_key:
        check_rate_limit(api_key_header)
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

# In-memory storage with simple cleanup mechanism
scans = {}
MAX_HISTORY = 100

def cleanup_old_scans():
    """Remove old scans to prevent memory leaks."""
    if len(scans) > MAX_HISTORY:
        # Simple FIFO removal
        sorted_keys = sorted(scans.keys())
        excess = len(scans) - MAX_HISTORY
        for k in sorted_keys[:excess]:
            del scans[k]

async def run_scan_task(scan_id: str, target: str, config, http_client):
    try:
        engine = GloaksEngine(config, http_client=http_client)
        results = await engine.run(target)
        scans[scan_id]["status"] = "completed"
        scans[scan_id]["results"] = results
        logger.info("API Scan completed", scan_id=scan_id)
    except Exception as e:
        scans[scan_id]["status"] = "failed"
        scans[scan_id]["results"] = {"error": str(e)}
        logger.error("API Scan failed", scan_id=scan_id, error=str(e))

@app.post("/scans", response_model=ScanResponse)
async def create_scan(request: ScanRequest, background_tasks: BackgroundTasks, api_key: APIKey = Depends(get_api_key)):
    cleanup_old_scans()
    
    scan_id = str(uuid.uuid4())
    config = load_config()
    
    # Update config with request overrides if needed
    
    scans[scan_id] = {
        "scan_id": scan_id,
        "status": "running",
        "target": request.target,
        "results": None
    }
    
    background_tasks.add_task(run_scan_task, scan_id, request.target, config, app.state.http_client)
    
    return ScanResponse(
        scan_id=scan_id,
        status="running",
        target=request.target
    )

@app.get("/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str, api_key: APIKey = Depends(get_api_key)):
    scan = scans.get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return ScanResponse(**scan)
