from fastapi import FastAPI, BackgroundTasks, HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Optional
import asyncio
import uuid
import structlog
import os
import httpx
import time
import secrets
from datetime import datetime
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

from gloaks.api.models import Scan, ScanRequest, ScanResponse
from gloaks.core.engine import GloaksEngine
from gloaks.core.config import load_config
from gloaks.core.database import create_db_and_tables, get_session

logger = structlog.get_logger()

# Global state for job management
running_tasks: Dict[str, asyncio.Task] = {}
cancellation_tokens: Dict[str, asyncio.Event] = {}
jobs_lock = asyncio.Lock()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            "Request processed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=process_time
        )
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Gloaks API...")
    await create_db_and_tables()
    app.state.http_client = httpx.AsyncClient(verify=True)
    
    # Generate API key if not set
    # Using 'environ' allows us to set it dynamically if missing
    if not os.environ.get("GLOAKS_API_KEY"):
        generated_key = secrets.token_urlsafe(32)
        os.environ["GLOAKS_API_KEY"] = generated_key
        logger.critical("No API key configured. Generated secure key", api_key=generated_key)
        # Note: In production logs, this might be risky, but essential for first run CLI usage without env
    
    yield
    
    # Shutdown
    logger.info("Shutting down Gloaks API...")
    logger.info("Shutting down Gloaks API...")
    # Cancel all running tasks
    async with jobs_lock:
        for scan_id, task in running_tasks.items():
            if not task.done():
                logger.info("Cancelling active scan", scan_id=scan_id)
                task.cancel()
    
    await app.state.http_client.aclose()

app = FastAPI(title="Gloaks API", version="3.0.0", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Rate Limiting (Simple Token Bucket per Key)
RATE_LIMIT_CALLS = 10
RATE_LIMIT_PERIOD = 60  # seconds
from collections import defaultdict
request_history = defaultdict(list)

def check_rate_limit(api_key: str):
    now = time.time()
    request_history[api_key] = [t for t in request_history[api_key] if now - t < RATE_LIMIT_PERIOD]
    if len(request_history[api_key]) >= RATE_LIMIT_CALLS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    request_history[api_key].append(now)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # Fetch from environment variable which might be set during startup
    expected_key = os.environ.get("GLOAKS_API_KEY")
    if not expected_key:
         # Should not happen given lifespan logic, but fail safe
         raise HTTPException(status_code=500, detail="Server misconfiguration: API Key not set")
         
    if api_key_header == expected_key:
        check_rate_limit(api_key_header)
        return api_key_header
    
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

async def run_scan_task(scan_id: str, target: str, config, http_client, session_factory):
    # Create cancellation token for this task
    token = asyncio.Event()
    async with jobs_lock:
        cancellation_tokens[scan_id] = token
    
    # Create new session
    async with session_factory() as session:
        try:
            # Update status to running
            scan = await session.get(Scan, scan_id)
            if scan:
                scan.status = "running"
                session.add(scan)
                await session.commit()

            engine = GloaksEngine(config, http_client=http_client)
            
            # Check if cancelled before starting (race condition check)
            if token.is_set():
                 raise asyncio.CancelledError()

            results = await engine.run(target, cancellation_token=token)
            
            scan = await session.get(Scan, scan_id)
            if scan:
                if token.is_set() or results.get("status") == "cancelled":
                    scan.status = "cancelled"
                else:
                    scan.status = "completed"
                    scan.results = results
                scan.updated_at = datetime.utcnow()
                session.add(scan)
                await session.commit()
                
            logger.info("API Scan completed", scan_id=scan_id)
            
        except (asyncio.CancelledError, Exception) as e:
            is_cancelled = isinstance(e, asyncio.CancelledError) or token.is_set()
            status = "cancelled" if is_cancelled else "failed"
            error_msg = str(e) if not is_cancelled else "Scan cancelled by user"
            
            logger.error(f"API Scan {status}", scan_id=scan_id, error=error_msg)
            
            try:
                # Need fresh transaction/session? We are in one.
                # If commit failed above, session might be rollback state.
                # Safe practice: await session.rollback()
                await session.rollback()
                
                scan = await session.get(Scan, scan_id)
                if scan:
                    scan.status = status
                    if not is_cancelled:
                         scan.results = {"error": error_msg}
                    scan.updated_at = datetime.utcnow()
                    session.add(scan)
                    await session.commit()
            except Exception as db_e:
                logger.error("Failed to update scan status", error=str(db_e))
                
        finally:
            # Cleanup global dictionaries
            async with jobs_lock:
                running_tasks.pop(scan_id, None)
                cancellation_tokens.pop(scan_id, None)

@app.post("/scans", response_model=ScanResponse)
async def create_scan(
    request: ScanRequest, 
    session: AsyncSession = Depends(get_session),
    api_key: APIKey = Depends(get_api_key)
):
    scan_id = str(uuid.uuid4())
    config = load_config()
    
    new_scan = Scan(
        id=scan_id,
        target=request.target,
        status="pending",
        config=request.config
    )
    session.add(new_scan)
    await session.commit()
    await session.refresh(new_scan)
    
    # We must create a task manually to track it.
    # We pass session_factory (get_session used as generator, need callable)
    # The 'get_session' logic assumes 'sessionmaker' logic inside.
    # We need access to the sessionmaker or similar factory.
    # Or we can just import it.
    from gloaks.core.database import engine
    from sqlalchemy.orm import sessionmaker
    
    # Create a factory for the background task
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    task = asyncio.create_task(
        run_scan_task(scan_id, request.target, config, app.state.http_client, async_session_factory)
    )
    async with jobs_lock:
        running_tasks[scan_id] = task
    
    return new_scan

@app.get("/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str, 
    session: AsyncSession = Depends(get_session),
    api_key: APIKey = Depends(get_api_key)
):
    scan = await session.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@app.post("/scans/{scan_id}/cancel", response_model=ScanResponse)
async def cancel_scan(
    scan_id: str,
    session: AsyncSession = Depends(get_session),
    api_key: APIKey = Depends(get_api_key)
):
    scan = await session.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    async with jobs_lock:
        if scan_id in cancellation_tokens:
            cancellation_tokens[scan_id].set()
        
        if scan_id in running_tasks:
            running_tasks[scan_id].cancel()
        
    scan.status = "cancelling"
    session.add(scan)
    await session.commit()
    await session.refresh(scan)
    return scan

@app.get("/health")
async def health_check():
    async with jobs_lock:
        count = len(running_tasks)
    return {"status": "ok", "version": "3.0.0", "active_scans": count}
