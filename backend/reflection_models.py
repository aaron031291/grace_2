"""
Reflection Models - Database models for SelfReflectionLoop
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, CheckConstraint, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Reflection(Base):
    """Reflections table for storing SelfReflectionLoop insights and metadata"""
    __tablename__ = 'reflections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(255), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    agent = Column(String(100), nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Performance metrics
    execution_time_ms = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    trust_score_before = Column(Float, nullable=True)
    trust_score_after = Column(Float, nullable=True)
    
    # Structured reflection data
    performance_analysis = Column(JSONB, nullable=True)  # Analysis of what went well/poorly
    identified_improvements = Column(JSONB, nullable=True)  # Specific improvement suggestions
    generated_insights = Column(JSONB, nullable=True)  # Key learnings and patterns
    strategy_updates = Column(JSONB, nullable=True)  # Recommended strategy changes
    
    # Context and metadata
    context = Column(JSONB, nullable=True)  # Additional context about the action
    error_details = Column(JSONB, nullable=True)  # Error information if applicable
    tags = Column(JSONB, nullable=True)  # Categorization tags
    
    # Learning metadata
    learned_patterns = Column(JSONB, nullable=True)  # Patterns extracted for future learning
    confidence_in_insights = Column(Float, nullable=True)  # How confident we are in our analysis
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name='check_confidence_score'),
        CheckConstraint("trust_score_before >= 0.0 AND trust_score_before <= 1.0", name='check_trust_score_before'),
        CheckConstraint("trust_score_after >= 0.0 AND trust_score_after <= 1.0", name='check_trust_score_after'),
        CheckConstraint("confidence_in_insights >= 0.0 AND confidence_in_insights <= 1.0", name='check_confidence_in_insights'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'trace_id': self.trace_id,
            'action_type': self.action_type,
            'agent': self.agent,
            'success': self.success,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'execution_time_ms': self.execution_time_ms,
            'confidence_score': self.confidence_score,
            'trust_score_before': self.trust_score_before,
            'trust_score_after': self.trust_score_after,
            'performance_analysis': self.performance_analysis,
            'identified_improvements': self.identified_improvements,
            'generated_insights': self.generated_insights,
            'strategy_updates': self.strategy_updates,
            'context': self.context,
            'error_details': self.error_details,
            'tags': self.tags,
            'learned_patterns': self.learned_patterns,
            'confidence_in_insights': self.confidence_in_insights,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
