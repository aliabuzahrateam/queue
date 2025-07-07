from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ApplicationBase(BaseModel):
    name: str
    domain: str
    callback_url: str

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    name: Optional[str]
    domain: Optional[str]
    callback_url: Optional[str]
    is_active: Optional[bool]

class ApplicationResponse(ApplicationBase):
    id: UUID
    api_key: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True 