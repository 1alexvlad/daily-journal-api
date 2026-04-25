from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import UTC, datetime

from app.database import Base

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    is_done = Column(Boolean, default=False, nullable=False)
