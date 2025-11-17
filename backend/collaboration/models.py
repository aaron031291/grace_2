"""
Collaboration System Database Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from backend.base_models import Base


class UserPresence(Base):
    __tablename__ = "user_presence"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False, index=True)
    user_name = Column(String(256), nullable=False)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    
    current_view = Column(String(64))
    current_file = Column(Text)
    current_table = Column(String(128))
    current_row_id = Column(String(128))
    
    user_metadata = Column(JSON, default={})
    
    is_active = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))


class CollaborationWorkflow(Base):
    __tablename__ = "collaboration_workflows"
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(128), unique=True, nullable=False, index=True)
    workflow_type = Column(String(64), nullable=False)
    
    title = Column(String(512), nullable=False)
    description = Column(Text)
    
    created_by = Column(String(128), nullable=False)
    created_by_name = Column(String(256))
    
    status = Column(String(64), default="pending")
    
    reviewers = Column(JSON, default=[])
    checklist = Column(JSON, default=[])
    checklist_completed = Column(JSON, default=[])
    
    approvals = Column(JSON, default={})
    rejections = Column(JSON, default={})
    comments = Column(JSON, default=[])
    
    workflow_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    notification_id = Column(String(128), unique=True, nullable=False, index=True)
    
    user_id = Column(String(128), nullable=False, index=True)
    
    notification_type = Column(String(64), nullable=False)
    title = Column(String(512), nullable=False)
    message = Column(Text)
    
    priority = Column(String(32), default="normal")
    
    action_url = Column(Text)
    action_label = Column(String(128))
    
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    
    notification_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    dismissed_at = Column(DateTime(timezone=True))


class ActivityFeed(Base):
    __tablename__ = "activity_feed"
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(String(128), unique=True, nullable=False, index=True)
    
    user_id = Column(String(128), nullable=False, index=True)
    user_name = Column(String(256))
    
    activity_type = Column(String(64), nullable=False)
    action = Column(String(256), nullable=False)
    
    resource_type = Column(String(64))
    resource_id = Column(String(128))
    resource_name = Column(String(512))
    
    details = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
