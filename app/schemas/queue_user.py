from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class QueueUserStatus(str, Enum):
    waiting = 'waiting'
    ready = 'ready'
    expired = 'expired'
    rejected = 'rejected'

class QueueUserJoin(BaseModel):
    queue_id: UUID
    visitor_id: str

class QueueUserBase(BaseModel):
    queue_id: UUID
    visitor_id: str
    status: QueueUserStatus = QueueUserStatus.waiting
    redirect_url: Optional[str] = None
    wait_time: Optional[int] = None
    expires_at: Optional[datetime] = None

class QueueUserCreate(QueueUserBase):
    pass

class QueueUserUpdate(BaseModel):
    status: Optional[QueueUserStatus] = None
    redirect_url: Optional[str] = None
    wait_time: Optional[int] = None
    expires_at: Optional[datetime] = None

class QueueUserResponse(QueueUserBase):
    id: UUID
    token: str
    created_at: datetime

    class Config:
        from_attributes = True 