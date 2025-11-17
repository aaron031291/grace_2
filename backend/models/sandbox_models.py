from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .base_models import Base

class SandboxRun(Base):
    __tablename__ = "sandbox_runs"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    command = Column(Text, nullable=False)
    file_name = Column(String(256))
    stdout = Column(Text)
    stderr = Column(Text)
    exit_code = Column(Integer)
    duration_ms = Column(Integer)
    success = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SandboxFile(Base):
    __tablename__ = "sandbox_files"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    file_path = Column(String(512), nullable=False)
    content = Column(Text)
    size_bytes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
