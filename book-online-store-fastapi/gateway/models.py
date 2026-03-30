# gateway/models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLog(BaseModel):
    """Model for API audit logging"""
    service: str
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime
    user_id: Optional[str] = None
    request_body: Optional[dict] = None
    response_body: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "service": "book",
                "endpoint": "/api/books",
                "method": "GET",
                "status_code": 200,
                "timestamp": "2026-03-24T10:30:00",
                "user_id": "user123"
            }
        }
