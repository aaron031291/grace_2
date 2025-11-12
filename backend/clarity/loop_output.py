# -*- coding: utf-8 -*-
"""
Loop Output - Clarity Framework Class 3
Standardized output format for all cognitive loops
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


@dataclass
class GraceLoopOutput:
    """
    Standardized output from any Grace cognitive loop.
    Makes loop execution traceable and results consistent.
    """
    
    # Identity
    loop_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    loop_type: str = ""  # e.g., "reasoning", "planning", "execution"
    
    # Reasoning chain tracking
    reasoning_chain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_loop_id: Optional[str] = None
    
    # Results
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "completed"  # completed, failed, partial
    confidence: float = 1.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Traceability
    component_id: Optional[str] = None
    trace_context: Dict[str, Any] = field(default_factory=dict)
    
    def mark_completed(self, results: Dict[str, Any], confidence: float = 1.0):
        """Mark loop as completed with results"""
        self.results = results
        self.confidence = confidence
        self.status = "completed"
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        """Mark loop as failed"""
        self.status = "failed"
        self.metadata["error"] = error
        self.completed_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "loop_id": self.loop_id,
            "loop_type": self.loop_type,
            "reasoning_chain_id": self.reasoning_chain_id,
            "parent_loop_id": self.parent_loop_id,
            "results": self.results,
            "status": self.status,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "component_id": self.component_id,
            "trace_context": self.trace_context
        }
    
    def get_duration_ms(self) -> Optional[float]:
        """Get loop execution duration in milliseconds"""
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None
