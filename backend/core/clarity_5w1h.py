"""
5W1H Clarity Logging for Layer 2 Orchestration
Every major dispatch gets audited with full narrative

5W1H Framework:
- Who: Actor/component making the decision
- What: Action being taken
- When: Timestamp and context
- Where: Resource/target
- Why: Reasoning chain
- How: Method/mechanism used
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Clarity5W1H:
    """
    5W1H narrative logger for orchestration decisions
    Integrates with Clarity Framework for full transparency
    """
    
    def __init__(self):
        self.narrative_log: List[Dict] = []
        logger.info("[5W1H] Clarity narrative logger initialized")
    
    async def log_dispatch(
        self,
        who: str,
        what: str,
        when: datetime,
        where: str,
        why: List[str],
        how: str,
        context: Optional[Dict] = None
    ):
        """
        Log a dispatch decision with full 5W1H narrative
        
        Args:
            who: Actor making the dispatch
            what: Action being taken (e.g., "dispatch_intent_to_htm")
            when: Timestamp (with context about trigger)
            where: Resource/target (e.g., "htm_worker_3", "task_queue")
            why: List of reasoning steps
            how: Mechanism (e.g., "priority_queue_selection", "round_robin")
        """
        
        narrative = {
            'who': who,
            'what': what,
            'when': when.isoformat(),
            'where': where,
            'why': why,
            'how': how,
            'context': context or {},
            'logged_at': datetime.utcnow().isoformat()
        }
        
        self.narrative_log.append(narrative)
        
        # Publish to Clarity Framework
        try:
            from backend.core.clarity_framework import clarity_framework, DecisionType, ClarityLevel
            
            await clarity_framework.record_decision(
                actor=who,
                action_type=what,
                resource=where,
                decision={
                    'action': what,
                    'target': where,
                    'method': how,
                    'context': context
                },
                reasoning_chain=why,
                confidence=0.9,  # High confidence for automated decisions
                risk_assessment=0.1,
                evidence=context or {},
                transparency_level=ClarityLevel.COMPLETE,
                decision_type=DecisionType.OPERATIONAL
            )
        
        except Exception as e:
            logger.error(f"[5W1H] Clarity logging failed: {e}")
        
        # Log summary
        logger.info(f"[5W1H] {who} → {what} on {where}")
        logger.debug(f"[5W1H] Why: {' | '.join(why)}")
        logger.debug(f"[5W1H] How: {how}")
    
    async def log_task_dispatch(
        self,
        dispatcher: str,
        task_id: str,
        task_type: str,
        target_worker: str,
        queue_depth: int,
        selection_method: str,
        reasons: List[str]
    ):
        """Convenience method for task dispatch logging"""
        
        await self.log_dispatch(
            who=dispatcher,
            what=f"dispatch_task_{task_type}",
            when=datetime.utcnow(),
            where=target_worker,
            why=reasons,
            how=selection_method,
            context={
                'task_id': task_id,
                'task_type': task_type,
                'queue_depth': queue_depth
            }
        )
    
    async def log_load_shedding(
        self,
        shedder: str,
        shed_count: int,
        total_load: int,
        shed_criteria: str,
        reasons: List[str]
    ):
        """Log load shedding decisions"""
        
        await self.log_dispatch(
            who=shedder,
            what="shed_load",
            when=datetime.utcnow(),
            where="task_queue",
            why=reasons,
            how=shed_criteria,
            context={
                'shed_count': shed_count,
                'total_load': total_load,
                'shed_percentage': (shed_count / max(total_load, 1)) * 100
            }
        )
    
    async def log_reroute(
        self,
        router: str,
        task_id: str,
        from_target: str,
        to_target: str,
        reroute_reason: List[str],
        method: str
    ):
        """Log task rerouting decisions"""
        
        await self.log_dispatch(
            who=router,
            what="reroute_task",
            when=datetime.utcnow(),
            where=to_target,
            why=reroute_reason,
            how=method,
            context={
                'task_id': task_id,
                'from': from_target,
                'to': to_target
            }
        )
    
    def get_narratives(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Query narratives with filters"""
        
        results = self.narrative_log
        
        if actor:
            results = [n for n in results if n['who'] == actor]
        
        if action:
            results = [n for n in results if n['what'] == action]
        
        if since:
            since_iso = since.isoformat()
            results = [n for n in results if n['when'] >= since_iso]
        
        return results[-limit:]


# Global instance
clarity_5w1h = Clarity5W1H()
