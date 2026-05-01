"""
Pydantic schemas for request/response validation.

NodeCreate: for POST body (name, host, port — all required)
NodeUpdate: for PUT body (host, port — optional)
NodeResponse: for API responses (includes id, status, timestamps)
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class NodeBase(BaseModel):
    host: str
    port: int = Field(..., ge=1, le=65535)

class NodeCreate(NodeBase):
    name: str

class NodeUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)

class NodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    host: str
    port: int
    status: str
    created_at: datetime
    updated_at: datetime
