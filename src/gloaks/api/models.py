from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional, Dict, Any
from gloaks.utils.validators import InputValidator

class ScanRequest(BaseModel):
    target: str
    config: Optional[Dict[str, Any]] = None

    @validator("target")
    def validate_target(cls, v):
        is_valid, error = InputValidator.validate_target(v)
        if not is_valid:
            raise ValueError(error)
        return v

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    target: str
    results: Optional[Dict[str, Any]] = None
