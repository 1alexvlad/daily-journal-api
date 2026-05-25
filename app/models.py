from enum import Enum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import UTC, datetime
from app.database import Base

class Role(Enum):
    USER = 'user'
    STAFF = 'staff'
    ADMIN = 'admin'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(Role), default=Role.USER, nullable=False)  
    is_active = Column(Boolean, default=True, nullable=False)

    notes = relationship('Note', back_populates='user', cascade='all, delete-orphan')
    sessions = relationship('UserSession', back_populates="user", cascade="all, delete-orphan")

    def __str__(self):
        return f"User #{self.email}"

class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    user = relationship("User", back_populates="sessions")


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    is_done = Column(Boolean, default=False, nullable=False)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='notes')

    def __str__(self):
        return f"Note #{self.id}"