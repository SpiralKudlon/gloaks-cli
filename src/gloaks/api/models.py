from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, Column
from pydantic import validator
from gloaks.utils.validators import InputValidator

class ScanBase(SQLModel):
    target: str
    config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    @validator("target")
    def validate_target(cls, v):
        is_valid, error = InputValidator.validate_target(v)
        if not is_valid:
            raise ValueError(error)
        return v

class Scan(ScanBase, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    status: str = Field(default="pending")
    results: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ScanRequest(ScanBase):
    pass

class ScanResponse(ScanBase):
    id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
