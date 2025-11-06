from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from .models import Base

class GoalDependency(Base):
    __tablename__ = "goal_dependencies"
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"))
    depends_on_goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"))
    type = Column(String(16), nullable=False, default="blocks")  # blocks | enables
    note = Column(Text, nullable=True)

class GoalEvaluation(Base):
    __tablename__ = "goal_evaluations"
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"))
    status = Column(String(16), nullable=False)  # on_track | at_risk | off_track | met
    explanation = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
