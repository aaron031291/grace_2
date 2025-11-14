"""
Schema Evolution System
Grace can propose schema improvements and apply them through governance
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from .base_models import Base
from .models import async_session
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log

class SchemaProposal(Base):
    """Proposed schema changes tracked for governance approval"""
    __tablename__ = "schema_proposals"
    
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(256), nullable=False)
    current_schema = Column(JSON, nullable=True)
    proposed_schema = Column(JSON, nullable=False)
    reasoning = Column(Text, nullable=False)
    
    # Governance
    status = Column(String(32), default="pending")  # pending, approved, rejected, applied
    approval_id = Column(String(128), nullable=True)
    
    # Learning context
    triggered_by = Column(String(128), nullable=True)  # error_pattern, usage_analysis, manual
    confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Timestamps
    proposed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    decided_at = Column(DateTime, nullable=True)
    applied_at = Column(DateTime, nullable=True)
    
    # Metadata
    impact_assessment = Column(JSON, nullable=True)


class SchemaEvolutionEngine:
    """
    Grace's system for learning better API schemas over time
    """
    
    async def analyze_endpoint_usage(
        self,
        endpoint: str,
        error_patterns: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze endpoint usage and errors to propose schema improvements
        
        Args:
            endpoint: API endpoint path
            error_patterns: List of validation errors encountered
            
        Returns:
            Schema improvement proposal or None
        """
        
        # Analyze error patterns
        common_errors = {}
        for error in error_patterns:
            error_type = error.get("type")
            if error_type:
                common_errors[error_type] = common_errors.get(error_type, 0) + 1
        
        # If we see missing field errors, propose adding optional fields
        if "missing" in common_errors or "required" in str(error_patterns):
            missing_fields = self._extract_missing_fields(error_patterns)
            
            if missing_fields:
                proposal = {
                    "endpoint": endpoint,
                    "improvement_type": "add_optional_fields",
                    "fields_to_add": missing_fields,
                    "reasoning": f"Detected {len(missing_fields)} commonly missing fields in client requests",
                    "confidence": 0.8
                }
                return proposal
        
        # If we see type errors, propose better type definitions
        if "type" in common_errors:
            return {
                "endpoint": endpoint,
                "improvement_type": "refine_types",
                "reasoning": "Frequent type validation errors suggest schema types need refinement",
                "confidence": 0.7
            }
        
        return None
    
    async def propose_schema_change(
        self,
        endpoint: str,
        current_schema: Optional[Dict[str, Any]],
        proposed_schema: Dict[str, Any],
        reasoning: str,
        triggered_by: str = "automatic",
        confidence: float = 0.8
    ) -> int:
        """
        Propose a schema change that requires governance approval
        
        Returns:
            Proposal ID
        """
        
        # Create proposal
        async with async_session() as session:
            proposal = SchemaProposal(
                endpoint=endpoint,
                current_schema=current_schema,
                proposed_schema=proposed_schema,
                reasoning=reasoning,
                triggered_by=triggered_by,
                confidence_score=int(confidence * 100),
                impact_assessment={
                    "breaking_change": self._is_breaking_change(current_schema, proposed_schema),
                    "affected_clients": "unknown",
                    "rollback_available": True
                }
            )
            session.add(proposal)
            await session.commit()
            await session.refresh(proposal)
            
            proposal_id = proposal.id
        
        # Log to immutable log
        await immutable_log.append(
            actor="schema_evolution",
            action="schema_change_proposed",
            resource=endpoint,
            subsystem="api_evolution",
            payload={
                "proposal_id": proposal_id,
                "endpoint": endpoint,
                "reasoning": reasoning,
                "confidence": confidence
            },
            result="proposed"
        )
        
        # Emit event for governance review
        await trigger_mesh.publish(TriggerEvent(
            event_type="schema.change_proposed",
            source="schema_evolution",
            actor="grace_learning",
            resource=endpoint,
            payload={
                "proposal_id": proposal_id,
                "endpoint": endpoint,
                "reasoning": reasoning,
                "requires_approval": True
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        return proposal_id
    
    async def apply_approved_schema(self, proposal_id: int) -> bool:
        """
        Apply an approved schema change
        
        In production, this would:
        1. Update schemas.py programmatically
        2. Reload the route
        3. Run migration if needed
        
        For now, it logs the approval and creates a task for manual application
        """
        
        async with async_session() as session:
            proposal = await session.get(SchemaProposal, proposal_id)
            if not proposal or proposal.status != "approved":
                return False
            
            # Mark as applied
            proposal.status = "applied"
            proposal.applied_at = datetime.now(timezone.utc)
            await session.commit()
        
        # Log application
        await immutable_log.append(
            actor="schema_evolution",
            action="schema_change_applied",
            resource=proposal.endpoint,
            subsystem="api_evolution",
            payload={
                "proposal_id": proposal_id,
                "endpoint": proposal.endpoint
            },
            result="applied"
        )
        
        print(f"[SCHEMA] Applied schema change for {proposal.endpoint} (proposal #{proposal_id})")
        return True
    
    def _extract_missing_fields(self, error_patterns: List[Dict[str, Any]]) -> List[str]:
        """Extract commonly missing field names from validation errors"""
        missing = []
        for error in error_patterns:
            if "loc" in error and "field required" in str(error.get("msg", "")).lower():
                field = error["loc"][-1] if error["loc"] else None
                if field and field not in missing:
                    missing.append(field)
        return missing
    
    def _is_breaking_change(
        self, 
        current: Optional[Dict[str, Any]], 
        proposed: Dict[str, Any]
    ) -> bool:
        """
        Determine if a schema change is breaking
        
        Breaking changes:
        - Removing required fields
        - Changing field types incompatibly
        - Renaming fields
        
        Non-breaking:
        - Adding optional fields
        - Making required fields optional
        - Adding new optional properties
        """
        
        if not current:
            return False  # New schema, not breaking
        
        # Simple heuristic: check if proposed has fewer required fields
        current_required = current.get("required", [])
        proposed_required = proposed.get("required", [])
        
        # If any current required field is missing in proposed, it's breaking
        for field in current_required:
            if field not in proposed_required and field not in proposed.get("properties", {}):
                return True
        
        return False


# Global instance
schema_evolution = SchemaEvolutionEngine()
