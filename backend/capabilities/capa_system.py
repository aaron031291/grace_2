"""
CAPA System - Corrective and Preventive Action
ISO 9001 requirement for handling nonconformities
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class CAPAType(str, Enum):
    CORRECTIVE = "corrective"  # Fix existing problem
    PREVENTIVE = "preventive"  # Prevent future problem


class CAPAStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    ACTION_PLANNED = "action_planned"
    IMPLEMENTING = "implementing"
    VERIFYING = "verifying"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class CAPASeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CAPASystem:
    """
    Corrective and Preventive Action management
    
    Workflow:
    1. Issue detected (anomaly, customer feedback, audit finding)
    2. CAPA record created
    3. Root cause analysis
    4. Corrective action planned
    5. Action implemented
    6. Effectiveness verified
    7. Record closed with evidence
    8. Learning fed to governance/ML
    """
    
    def __init__(self):
        # Active CAPA records
        self.capa_records: Dict[str, Dict[str, Any]] = {}
        
        # Lazy dependencies
        self._immutable_log = None
        self._governance = None
        self._unified_logic_hub = None
        self._trigger_mesh = None
    
    async def create_capa(
        self,
        title: str,
        description: str,
        capa_type: CAPAType,
        severity: CAPASeverity,
        source: str,  # anomaly, customer, audit, internal
        related_update_id: Optional[str] = None,
        detected_by: str = "system",
        evidence: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new CAPA record
        
        Args:
            title: Brief description
            description: Detailed description
            capa_type: Corrective or Preventive
            severity: Critical/High/Medium/Low
            source: Where issue originated
            related_update_id: If tied to logic update
            detected_by: Who/what detected the issue
            evidence: Supporting evidence
            
        Returns:
            capa_id for tracking
        """
        
        capa_id = f"capa_{uuid.uuid4().hex[:12]}"
        
        record = {
            "capa_id": capa_id,
            "title": title,
            "description": description,
            "capa_type": capa_type.value,
            "severity": severity.value,
            "source": source,
            "related_update_id": related_update_id,
            "detected_by": detected_by,
            "evidence": evidence or {},
            
            # Workflow tracking
            "status": CAPAStatus.OPEN.value,
            "created_at": datetime.now(timezone.utc),
            "status_history": [
                {
                    "status": CAPAStatus.OPEN.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "actor": detected_by
                }
            ],
            
            # Analysis
            "root_cause": None,
            "root_cause_analysis": {},
            
            # Actions
            "corrective_actions": [],
            "preventive_actions": [],
            
            # Implementation
            "implementation_plan": None,
            "implemented_at": None,
            "implemented_by": None,
            
            # Verification
            "verification_method": None,
            "verification_results": None,
            "verified_at": None,
            "verified_by": None,
            
            # Closure
            "closed_at": None,
            "closed_by": None,
            "closure_evidence": {},
            
            # Learning
            "lessons_learned": [],
            "governance_updates": [],
            "playbook_updates": []
        }
        
        self.capa_records[capa_id] = record
        
        # Log creation
        await self._log_capa_event(
            capa_id=capa_id,
            action="capa_created",
            payload=record,
            result="created"
        )
        
        # Publish event
        await self._publish_capa_event(
            capa_id=capa_id,
            event_type="capa.created",
            payload={
                "capa_id": capa_id,
                "severity": severity.value,
                "source": source,
                "related_update_id": related_update_id
            }
        )
        
        logger.info(f"[CAPA] Created {capa_id}: {title} ({severity.value})")
        
        return capa_id
    
    async def conduct_root_cause_analysis(
        self,
        capa_id: str,
        root_cause: str,
        analysis: Dict[str, Any],
        analyst: str = "system"
    ):
        """
        Document root cause analysis
        
        Args:
            capa_id: CAPA record ID
            root_cause: Identified root cause
            analysis: Analysis details (5 Whys, fishbone, etc.)
            analyst: Who conducted analysis
        """
        
        record = self.capa_records.get(capa_id)
        if not record:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Update record
        record["root_cause"] = root_cause
        record["root_cause_analysis"] = {
            **analysis,
            "analyst": analyst,
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update status
        await self._update_status(capa_id, CAPAStatus.INVESTIGATING, analyst)
        
        # Log analysis
        await self._log_capa_event(
            capa_id=capa_id,
            action="root_cause_identified",
            payload={
                "root_cause": root_cause,
                "analysis": analysis
            },
            result="analyzed"
        )
        
        logger.info(f"[CAPA] Root cause for {capa_id}: {root_cause}")
    
    async def plan_actions(
        self,
        capa_id: str,
        corrective_actions: List[Dict[str, Any]],
        preventive_actions: Optional[List[Dict[str, Any]]] = None,
        implementation_plan: Dict[str, Any] = None,
        planner: str = "system"
    ):
        """
        Plan corrective and preventive actions
        
        Args:
            capa_id: CAPA record ID
            corrective_actions: List of corrective actions
            preventive_actions: List of preventive actions
            implementation_plan: How actions will be implemented
            planner: Who planned actions
        """
        
        record = self.capa_records.get(capa_id)
        if not record:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Update record
        record["corrective_actions"] = corrective_actions
        record["preventive_actions"] = preventive_actions or []
        record["implementation_plan"] = {
            **(implementation_plan or {}),
            "planner": planner,
            "planned_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update status
        await self._update_status(capa_id, CAPAStatus.ACTION_PLANNED, planner)
        
        # Log planning
        await self._log_capa_event(
            capa_id=capa_id,
            action="actions_planned",
            payload={
                "corrective_count": len(corrective_actions),
                "preventive_count": len(preventive_actions or []),
                "plan": implementation_plan
            },
            result="planned"
        )
        
        logger.info(f"[CAPA] Actions planned for {capa_id}: {len(corrective_actions)} corrective, {len(preventive_actions or [])} preventive")
    
    async def implement_actions(
        self,
        capa_id: str,
        implementation_results: Dict[str, Any],
        implementer: str = "system"
    ):
        """
        Mark actions as implemented
        
        Args:
            capa_id: CAPA record ID
            implementation_results: Results of implementation
            implementer: Who implemented
        """
        
        record = self.capa_records.get(capa_id)
        if not record:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Update record
        record["implemented_at"] = datetime.now(timezone.utc)
        record["implemented_by"] = implementer
        record["implementation_results"] = implementation_results
        
        # Update status
        await self._update_status(capa_id, CAPAStatus.IMPLEMENTING, implementer)
        
        # Trigger governance/playbook updates if needed
        await self._apply_systemic_changes(capa_id, record)
        
        # Log implementation
        await self._log_capa_event(
            capa_id=capa_id,
            action="actions_implemented",
            payload=implementation_results,
            result="implemented"
        )
        
        logger.info(f"[CAPA] Actions implemented for {capa_id}")
    
    async def verify_effectiveness(
        self,
        capa_id: str,
        verification_method: str,
        verification_results: Dict[str, Any],
        effective: bool,
        verifier: str = "system"
    ):
        """
        Verify effectiveness of actions
        
        Args:
            capa_id: CAPA record ID
            verification_method: How effectiveness was verified
            verification_results: Results of verification
            effective: Whether actions were effective
            verifier: Who verified
        """
        
        record = self.capa_records.get(capa_id)
        if not record:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Update record
        record["verification_method"] = verification_method
        record["verification_results"] = verification_results
        record["verified_at"] = datetime.now(timezone.utc)
        record["verified_by"] = verifier
        record["effective"] = effective
        
        # Update status
        await self._update_status(capa_id, CAPAStatus.VERIFYING, verifier)
        
        # Log verification
        await self._log_capa_event(
            capa_id=capa_id,
            action="effectiveness_verified",
            payload={
                "method": verification_method,
                "effective": effective,
                "results": verification_results
            },
            result="verified" if effective else "ineffective"
        )
        
        logger.info(f"[CAPA] Effectiveness verified for {capa_id}: {'Effective' if effective else 'Ineffective'}")
        
        # Auto-close if effective
        if effective:
            await self.close_capa(
                capa_id=capa_id,
                closure_notes="Automatically closed - effectiveness verified",
                closer=verifier
            )
    
    async def close_capa(
        self,
        capa_id: str,
        closure_notes: str,
        lessons_learned: Optional[List[str]] = None,
        closer: str = "system",
        closure_evidence: Optional[Dict[str, Any]] = None
    ):
        """
        Close CAPA record
        
        Args:
            capa_id: CAPA record ID
            closure_notes: Notes explaining closure
            lessons_learned: Lessons from this CAPA
            closer: Who closed
            closure_evidence: Evidence supporting closure
        """
        
        record = self.capa_records.get(capa_id)
        if not record:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Update record
        record["closed_at"] = datetime.now(timezone.utc)
        record["closed_by"] = closer
        record["closure_notes"] = closure_notes
        record["closure_evidence"] = closure_evidence or {}
        record["lessons_learned"] = lessons_learned or []
        
        # Update status
        await self._update_status(capa_id, CAPAStatus.CLOSED, closer)
        
        # Feed learning to ML models
        await self._feed_learning(capa_id, record)
        
        # Log closure
        await self._log_capa_event(
            capa_id=capa_id,
            action="capa_closed",
            payload={
                "closure_notes": closure_notes,
                "lessons_learned": lessons_learned,
                "duration_days": (record["closed_at"] - record["created_at"]).days
            },
            result="closed"
        )
        
        # Publish closure event
        await self._publish_capa_event(
            capa_id=capa_id,
            event_type="capa.closed",
            payload={
                "capa_id": capa_id,
                "effective": record.get("effective", False),
                "lessons_learned": lessons_learned
            }
        )
        
        logger.info(f"[CAPA] Closed {capa_id}")
    
    async def _apply_systemic_changes(
        self,
        capa_id: str,
        record: Dict[str, Any]
    ):
        """Apply changes to governance/playbooks based on CAPA"""
        
        # Governance policy updates
        if record.get("preventive_actions"):
            for action in record["preventive_actions"]:
                if action.get("type") == "governance_policy":
                    try:
                        
                        # Create new policy based on CAPA learning
                        # (In production, this would create actual policy)
                        
                        record.setdefault("governance_updates", []).append({
                            "policy": action.get("policy_name"),
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "capa_id": capa_id
                        })
                        
                        logger.info(f"[CAPA] Created governance policy from {capa_id}")
                    except Exception as e:
                        logger.debug(f"Could not create governance policy: {e}")
        
        # Playbook updates
        for action in record.get("corrective_actions", []):
            if action.get("type") == "playbook_update":
                try:
                    # Update playbook
                    # (In production, this would modify actual playbook)
                    
                    record.setdefault("playbook_updates", []).append({
                        "playbook": action.get("playbook_name"),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "capa_id": capa_id
                    })
                    
                    logger.info(f"[CAPA] Updated playbook from {capa_id}")
                except Exception as e:
                    logger.debug(f"Could not update playbook: {e}")
    
    async def _feed_learning(
        self,
        capa_id: str,
        record: Dict[str, Any]
    ):
        """Feed CAPA learnings to ML models"""
        
        try:
            from backend.ml_update_integration import ml_update_integration
            
            # If related to update, correlate
            if record.get("related_update_id"):
                # This CAPA represents a regression
                regression_data = {
                    "detected_at": record["created_at"].isoformat(),
                    "components": [],  # Extract from evidence
                    "metrics": [],  # Extract from evidence
                    "severity": record["severity"]
                }
                
                correlation = await ml_update_integration.correlate_regression_with_rollout(
                    regression_data=regression_data,
                    time_window_hours=48
                )
                
                if correlation:
                    record["ml_correlation"] = correlation
            
            # Feed as training data
            # (Helps models predict issues)
            
            logger.info(f"[CAPA] Fed learning to ML from {capa_id}")
        
        except Exception as e:
            logger.debug(f"Could not feed learning: {e}")
    
    async def _update_status(
        self,
        capa_id: str,
        status: CAPAStatus,
        actor: str
    ):
        """Update CAPA status"""
        
        record = self.capa_records[capa_id]
        record["status"] = status.value
        record["status_history"].append({
            "status": status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor
        })
    
    async def _log_capa_event(
        self,
        capa_id: str,
        action: str,
        payload: Dict[str, Any],
        result: str
    ):
        """Log CAPA event to immutable log"""
        
        try:
            from backend.immutable_log import immutable_log
            self._immutable_log = immutable_log
            
            await self._immutable_log.append(
                actor="capa_system",
                action=action,
                resource=capa_id,
                subsystem="capa",
                payload=payload,
                result=result
            )
        except Exception as e:
            logger.debug(f"Could not log CAPA event: {e}")
    
    async def _publish_capa_event(
        self,
        capa_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Publish CAPA event to trigger mesh"""
        
        try:
            from backend.trigger_mesh import trigger_mesh, TriggerEvent
            self._trigger_mesh = trigger_mesh
            
            await self._trigger_mesh.publish(TriggerEvent(
                event_type=event_type,
                source="capa_system",
                actor="capa_system",
                resource=capa_id,
                payload=payload,
                timestamp=datetime.now(timezone.utc)
            ))
        except Exception as e:
            logger.debug(f"Could not publish CAPA event: {e}")
    
    def get_capa(self, capa_id: str) -> Optional[Dict[str, Any]]:
        """Get CAPA record"""
        return self.capa_records.get(capa_id)
    
    def list_open_capas(self, severity: Optional[CAPASeverity] = None) -> List[Dict[str, Any]]:
        """List open CAPA records"""
        records = [
            r for r in self.capa_records.values()
            if r["status"] != CAPAStatus.CLOSED.value
        ]
        
        if severity:
            records = [r for r in records if r["severity"] == severity.value]
        
        return sorted(records, key=lambda r: r["created_at"], reverse=True)
    
    def get_capa_metrics(self) -> Dict[str, Any]:
        """Get CAPA system metrics"""
        
        all_records = list(self.capa_records.values())
        open_records = [r for r in all_records if r["status"] != CAPAStatus.CLOSED.value]
        closed_records = [r for r in all_records if r["status"] == CAPAStatus.CLOSED.value]
        
        # Calculate average closure time
        closure_times = [
            (r["closed_at"] - r["created_at"]).days
            for r in closed_records
            if r.get("closed_at")
        ]
        avg_closure_days = sum(closure_times) / len(closure_times) if closure_times else 0
        
        return {
            "total_capas": len(all_records),
            "open_capas": len(open_records),
            "closed_capas": len(closed_records),
            "critical_open": len([r for r in open_records if r["severity"] == "critical"]),
            "high_open": len([r for r in open_records if r["severity"] == "high"]),
            "average_closure_days": avg_closure_days,
            "effectiveness_rate": len([r for r in closed_records if r.get("effective")]) / len(closed_records) if closed_records else 0.0
        }


# Global instance
capa_system = CAPASystem()
