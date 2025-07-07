from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class Log(Base):
    __tablename__ = 'logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=True)
    queue_id = Column(UUID(as_uuid=True), ForeignKey('queues.id'), nullable=True)
    queue_user_id = Column(UUID(as_uuid=True), ForeignKey('queue_users.id'), nullable=True) 