from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .models import Base

class IssueReport(Base):
    __tablename__ = "issue_reports"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    source = Column(String(64), nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(Text)
    explanation = Column(Text)
    likely_cause = Column(Text)
    suggested_fix = Column(Text)
    action_label = Column(String(256))
    action_payload = Column(Text)
    status = Column(String(32), default="pending")
    applied_fix = Column(Text)
    fix_result = Column(String(32))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
