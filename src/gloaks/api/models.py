from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class ScanRequest(BaseModel):
    target: str
    config: Optional[Dict[str, Any]] = None

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    target: str
    results: Optional[Dict[str, Any]] = None
