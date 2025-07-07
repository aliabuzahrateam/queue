from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class LogBase(BaseModel):
    event_type: str
    message: str
    details: Optional[str]
    application_id: Optional[UUID]
    queue_id: Optional[UUID]
    queue_user_id: Optional[UUID]

class LogCreate(LogBase):
    pass

class LogResponse(LogBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True 