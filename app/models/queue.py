from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class Queue(Base):
    __tablename__ = 'queues'
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    name = Column(String(100), nullable=False)
    max_users_per_minute = Column(Integer, nullable=False, default=10)
    priority = Column(Integer, nullable=False, default=1) 