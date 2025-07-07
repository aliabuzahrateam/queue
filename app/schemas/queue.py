from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class QueueBase(BaseModel):
    application_id: UUID
    name: str
    max_users_per_minute: int = 10
    priority: int = 1

class QueueCreate(QueueBase):
    pass

class QueueUpdate(BaseModel):
    name: Optional[str]
    max_users_per_minute: Optional[int]
    priority: Optional[int]
    is_active: Optional[bool]

class QueueResponse(QueueBase):
    id: UUID
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True 