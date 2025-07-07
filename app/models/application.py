from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid

class Application(Base):
    __tablename__ = 'applications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    domain = Column(String(255), nullable=False)
    callback_url = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex) 