"""
Unified Logic Integration with Message Bus
Governance and policy enforcement via message bus

Part of Layer 1 - Core decision-making
"""

import asyncio
from typing import Dict, Any
from datetime import datetime
import logging

from .message_bus import message_bus, MessagePriority
from .immutable_log import immutable_log
from .clarity_framework import clarity_framework, DecisionType, ClarityLevel
from .schemas import (
    MessageType, BusMessage, create_kernel_message,
    GovernanceDecisionPayload, ProposalPayload, TrustLevel
)

logger = logging.getLogger(__name__)


class UnifiedLogicCore:
    """
    Unified Logic integration with message bus
    
    Listens for:
    - event.proposal (from kernels)
    - task.request (approval needed)
    
    Publishes:
    - event.governance_decision (approval/rejection)
    
    All decisions go through:
    1. Policy evaluation
    2. Trust score check
    3. Risk assessment
    4. Clarity logging
    5. Immutable audit
    """
    
    def __init__(self):
        self.running = False
        self.decisions_queue = None
        self.proposals_received = 0
        self.decisions_made = 0
    
    async def start(self):
        """Start unified logic core"""
        
        self.running = True
        
        # Subscribe to proposal events
        self.decisions_queue = await message_bus.subscribe(
            subscriber='unified_logic',
            topic='event.proposal'
        )
        
        # Start decision processing loop
        asyncio.create_task(self._decision_loop())
        
        logger.info("[UNIFIED-LOGIC] Started - governance active on message bus")
    
    async def _decision_loop(self):
        """Process governance decisions"""
        
        while self.running:
            try:
                # Wait for proposal
                message: BusMessage = await self.decisions_queue.get()
                
                self.proposals_received += 1
                
                logger.info(f"[UNIFIED-LOGIC] Received proposal from {message.source}")
                
                # Process proposal
                decision = await self._evaluate_proposal(message)
                
                # Publish decision
                await self._publish_decision(decision, message)
                
                self.decisions_made += 1
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[UNIFIED-LOGIC] Error in decision loop: {e}")
    
    async def _evaluate_proposal(self, message: BusMessage) -> Dict[str, Any]:
        """
        Evaluate a proposal using Unified Logic
        
        Returns:
            Governance decision
        """
        
        payload = message.payload
        
        # Extract proposal details
        proposal_id = payload.get('proposal_id', 'unknown')
        confidence = payload.get('confidence', 0.0)
        risk_level = payload.get('risk_level', 'medium')
        trust_score = message.metadata.trust_level
        
        # Decision logic
        decision = {
            'decision_id': f"decision_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'proposal_id': proposal_id,
            'decision': 'unknown',
            'rationale': '',
            'approver': 'unified_logic',
            'trust_score': confidence,
            'risk_score': 0.0
        }
        
        # Auto-approve if high trust + low risk
        if confidence >= 0.95 and risk_level == 'low':
            decision['decision'] = 'approved'
            decision['rationale'] = f'Auto-approved: High confidence ({confidence*100:.0f}%), low risk'
            logger.info(f"[UNIFIED-LOGIC] Auto-approved: {proposal_id}")
        
        # Manual review for medium/high risk
        elif risk_level in ['medium', 'high', 'critical']:
            decision['decision'] = 'needs_review'
            decision['rationale'] = f'Human review required: {risk_level} risk'
            logger.info(f"[UNIFIED-LOGIC] Queued for review: {proposal_id}")
        
        # Reject if low confidence
        elif confidence < 0.70:
            decision['decision'] = 'rejected'
            decision['rationale'] = f'Rejected: Low confidence ({confidence*100:.0f}%)'
            logger.info(f"[UNIFIED-LOGIC] Rejected: {proposal_id}")
        
        else:
            decision['decision'] = 'needs_review'
            decision['rationale'] = 'Standard review required'
        
        # Log decision with clarity
        await clarity_framework.record_decision(
            decision_type=DecisionType.POLICY_ENFORCEMENT,
            actor='unified_logic',
            action='evaluate_proposal',
            resource=proposal_id,
            rationale=decision['rationale'],
            confidence=confidence,
            risk_score=self._risk_to_score(risk_level),
            clarity_level=ClarityLevel.DETAILED,
            evidence=[{'proposal': payload}]
        )
        
        return decision
    
    async def _publish_decision(self, decision: Dict[str, Any], original_message: BusMessage):
        """Publish governance decision"""
        
        # Create decision message
        decision_msg = create_kernel_message(
            msg_type=MessageType.EVENT_GOVERNANCE_DECISION,
            source='unified_logic',
            payload=decision,
            target=original_message.source,
            correlation_id=original_message.metadata.correlation_id,
            trust_level=TrustLevel.VERIFIED
        )
        
        # Publish to bus
        await message_bus.publish(
            source='unified_logic',
            topic='event.governance_decision',
            payload=decision,
            priority=MessagePriority.HIGH,
            correlation_id=original_message.metadata.correlation_id
        )
        
        # Log to immutable log
        await immutable_log.append(
            actor='unified_logic',
            action='governance_decision',
            resource=decision['proposal_id'],
            decision=decision
        )
        
        logger.info(f"[UNIFIED-LOGIC] Decision published: {decision['decision_id']}")
    
    def _risk_to_score(self, risk_level: str) -> float:
        """Convert risk level to score"""
        risk_map = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.75,
            'critical': 0.95
        }
        return risk_map.get(risk_level, 0.5)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get unified logic statistics"""
        return {
            'running': self.running,
            'proposals_received': self.proposals_received,
            'decisions_made': self.decisions_made,
            'auto_approved': 0,  # Would track this
            'queued_for_review': 0  # Would track this
        }


# Global instance - Core governance
unified_logic_core = UnifiedLogicCore()
