from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import enum
from datetime import datetime, timedelta
import uuid

class QueueUserStatus(enum.Enum):
    waiting = 'waiting'
    ready = 'ready'
    expired = 'expired'
    rejected = 'rejected'

class QueueUser(Base):
    __tablename__ = 'queue_users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    queue_id = Column(UUID(as_uuid=True), ForeignKey('queues.id'), nullable=False)
    visitor_id = Column(String(64), nullable=False, index=True)
    status = Column(Enum(QueueUserStatus), default=QueueUserStatus.waiting, nullable=False)
    token = Column(String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    redirect_url = Column(String(255), nullable=True)
    wait_time = Column(Integer, nullable=True)
    expires_at = Column(DateTime, nullable=True) 