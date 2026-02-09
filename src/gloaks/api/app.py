from fastapi import FastAPI, BackgroundTasks
from gloaks.api.models import ScanRequest, ScanResponse
from gloaks.core.engine import GloaksEngine
from gloaks.core.config import load_config
import uuid
import structlog

logger = structlog.get_logger()
app = FastAPI(title="Gloaks API", version="3.0.0")

# In-memory storage for demo purposes
# In production, this should be a database (PostgreSQL)
scans = {}

@app.post("/scans", response_model=ScanResponse)
async def create_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    scan_id = str(uuid.uuid4())
    config = load_config()
    
    # Update config with request overrides if needed
    # (Simplified for now)
    
    scans[scan_id] = {
        "scan_id": scan_id,
        "status": "running",
        "target": request.target,
        "results": None
    }
    
    background_tasks.add_task(run_scan_task, scan_id, request.target, config)
    
    return ScanResponse(
        scan_id=scan_id,
        status="running",
        target=request.target
    )

@app.get("/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str):
    scan = scans.get(scan_id)
    if not scan:
        return {"error": "Scan not found"} # Should retry 404
        
    return ScanResponse(**scan)

async def run_scan_task(scan_id: str, target: str, config):
    try:
        engine = GloaksEngine(config)
        results = await engine.run(target)
        scans[scan_id]["status"] = "completed"
        scans[scan_id]["results"] = results
        logger.info("API Scan completed", scan_id=scan_id)
    except Exception as e:
        scans[scan_id]["status"] = "failed"
        scans[scan_id]["results"] = {"error": str(e)}
        logger.error("API Scan failed", scan_id=scan_id, error=str(e))
