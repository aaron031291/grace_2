"""Create missing critical tables for production"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from backend.models import Base, engine


# Define missing tables
class Message(Base):
    """Chat messages table"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(32), nullable=False)  # user, assistant, system
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, default=dict)  # Renamed from metadata (reserved)


class HunterRule(Base):
    """Hunter security rules"""
    __tablename__ = "hunter_rules"

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(128), nullable=False, unique=True)
    rule_type = Column(String(64), nullable=False)  # pattern, behavior, anomaly
    pattern = Column(Text, nullable=True)
    severity = Column(String(32), nullable=False)  # low, medium, high, critical
    enabled = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_data = Column(JSON, default=dict)  # Renamed from metadata (reserved)


async def create_missing_tables():
    """Create all missing tables"""
    print("Creating missing critical tables...")
    
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ All tables created")
    
    # Seed default hunter rules
    from backend.models import async_session
    
    async with async_session() as session:
        # Check if rules exist
        from sqlalchemy import select
        result = await session.execute(select(HunterRule))
        existing = result.scalars().all()
        
        if not existing:
            print("Seeding default hunter rules...")
            
            default_rules = [
                HunterRule(
                    rule_name="sql_injection_detection",
                    rule_type="pattern",
                    pattern=r"(union|select|insert|update|delete|drop|exec|script)",
                    severity="critical",
                    description="Detect SQL injection attempts"
                ),
                HunterRule(
                    rule_name="xss_detection",
                    rule_type="pattern",
                    pattern=r"(<script|javascript:|onerror=|onload=)",
                    severity="high",
                    description="Detect XSS attempts"
                ),
                HunterRule(
                    rule_name="path_traversal",
                    rule_type="pattern",
                    pattern=r"(\.\./|\.\.\\|/etc/|c:\\)",
                    severity="high",
                    description="Detect path traversal attempts"
                ),
                HunterRule(
                    rule_name="command_injection",
                    rule_type="pattern",
                    pattern=r"(;|\||&|`|\$\()",
                    severity="critical",
                    description="Detect command injection attempts"
                ),
                HunterRule(
                    rule_name="excessive_requests",
                    rule_type="behavior",
                    severity="medium",
                    description="Detect rate limit violations"
                ),
            ]
            
            session.add_all(default_rules)
            await session.commit()
            
            print(f"✓ Seeded {len(default_rules)} hunter rules")
        else:
            print(f"✓ Hunter rules already exist ({len(existing)} rules)")


if __name__ == '__main__':
    asyncio.run(create_missing_tables())

