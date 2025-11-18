from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./grace_memory.db")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Export async_session for imports
async_session = async_session_maker

class MemoryArtifact(Base):
    __tablename__ = "memory_artifacts"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    trust_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)

class TrustEvent(Base):
    __tablename__ = "trust_events"
    
    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, nullable=False)
    old_score = Column(Float, nullable=False)
    new_score = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MemoryIndex(Base):
    __tablename__ = "memory_index"
    
    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, nullable=False)
    symbol = Column(String(255), nullable=False)
    symbol_type = Column(String(50), nullable=False)
    context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class GarbageCollectionLog(Base):
    __tablename__ = "gc_log"
    
    id = Column(Integer, primary_key=True)
    operation = Column(String(100), nullable=False)
    artifacts_affected = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default=dict)

