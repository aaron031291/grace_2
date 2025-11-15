"""
Database models for the Remote Access API.
"""

from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base_models import Base

class RemoteSession(Base):
    __tablename__ = "remote_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, nullable=False)
    target_system = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String, default="active") # active, expired, stopped

    command_history = relationship("CommandHistory", back_populates="session")

class CommandHistory(Base):
    __tablename__ = "command_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("remote_sessions.session_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    command = Column(String, nullable=False)
    output = Column(String)
    success = Column(String, nullable=False)

    session = relationship("RemoteSession", back_populates="command_history")