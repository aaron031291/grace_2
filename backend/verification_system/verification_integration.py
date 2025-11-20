"""
Verification Integration - Connects verification engine to event bus and memory
Handles VERIFICATION_REQUESTED events and publishes VERIFICATION_COMPLETED events
"""

import json
from typing import Dict, Any
from datetime import datetime

from backend.clarity import BaseComponent, ComponentStatus, Event, TrustLevel, get_event_bus
from backend.database import get_db
from .code_verification_engine import (
    verification_engine,
    Hypothesis,
    VerificationStatus
)


class VerificationIntegration(BaseComponent):
    """
    Integrates verification engine with Grace's event system
    
    Listens for:
    - verification.requested
    - code.verification.requested
    
    Publishes:
    - verification.completed
    - verification.failed
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "verification_integration"
        self.event_bus = get_event_bus()
        self.engine = verification_engine
    
    async def activate(self) -> bool:
        """Activate and subscribe to verification events"""
        
        await self.event_bus.subscribe(
            "verification.requested",
            self._handle_verification_request
        )
        
        await self.event_bus.subscribe(
            "code.verification.requested",
            self._handle_code_verification_request
        )
        
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        return True
    
    async def _handle_verification_request(self, event: Event):
        """Handle general verification requests"""
        
        try:
            payload = event.payload
            
            hypothesis = Hypothesis(
                id=payload.get('hypothesis_id', f"hyp_{datetime.utcnow().timestamp()}"),
                description=payload.get('description', ''),
                code_snippet=payload.get('code_snippet'),
                expected_behavior=payload.get('expected_behavior'),
                context=payload.get('context', {}),
                metadata=payload.get('metadata', {})
            )
            
            result = await self.engine.verify_claim(hypothesis)
            
            await self._store_verification_result(result)
            
            trust_level = self._map_confidence_to_trust(result.confidence)
            
            await self.event_bus.publish(Event(
                event_type="verification.completed",
                source=self.component_id,
                payload=result.to_dict(),
                trust_level=trust_level
            ))
            
        except Exception as e:
            await self.event_bus.publish(Event(
                event_type="verification.failed",
                source=self.component_id,
                payload={
                    'error': str(e),
                    'original_event': event.to_dict()
                },
                trust_level=TrustLevel.LOW
            ))
    
    async def _handle_code_verification_request(self, event: Event):
        """Handle code-specific verification requests"""
        
        try:
            payload = event.payload
            
            hypothesis = Hypothesis(
                id=payload.get('hypothesis_id', f"code_{datetime.utcnow().timestamp()}"),
                description=payload.get('description', 'Code verification'),
                code_snippet=payload['code'],
                expected_behavior=payload.get('expected_behavior'),
                context=payload.get('context', {})
            )
            
            run_tests = payload.get('run_tests', True)
            
            result = await self.engine.verify_code_snippet(
                hypothesis,
                payload['code'],
                run_tests=run_tests
            )
            
            await self._store_verification_result(result)
            
            trust_level = self._map_confidence_to_trust(result.confidence)
            
            await self.event_bus.publish(Event(
                event_type="verification.completed",
                source=self.component_id,
                payload=result.to_dict(),
                trust_level=trust_level
            ))
            
        except Exception as e:
            await self.event_bus.publish(Event(
                event_type="verification.failed",
                source=self.component_id,
                payload={
                    'error': str(e),
                    'original_event': event.to_dict()
                },
                trust_level=TrustLevel.LOW
            ))
    
    async def _store_verification_result(self, result):
        """Store verification result in memory (Fusion + Vector)"""
        
        db = await get_db()
        
        result_json = json.dumps(result.to_dict())
        
        await db.execute(
            """INSERT INTO memory_verification_results
               (hypothesis_id, status, confidence, result_data, timestamp)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                result.hypothesis_id,
                result.status.value,
                result.confidence,
                result_json
            )
        )
        
        await db.commit()
        
        await self._store_in_vector_memory(result)
    
    async def _store_in_vector_memory(self, result):
        """Store verification insights in vector memory for retrieval"""
        
        db = await get_db()
        
        summary_text = (
            f"Verification {result.status.value} with {result.confidence:.2f} confidence. "
            f"{len(result.issues)} issues found. "
        )
        
        if result.recommended_actions:
            summary_text += f"Actions: {', '.join(result.recommended_actions[:3])}. "
        
        await db.execute(
            """INSERT INTO memory_insights
               (document_id, insight_type, content, metadata, timestamp)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                result.hypothesis_id,
                "verification_result",
                summary_text,
                json.dumps({
                    'status': result.status.value,
                    'confidence': result.confidence,
                    'issue_count': len(result.issues)
                })
            )
        )
        
        await db.commit()
    
    def _map_confidence_to_trust(self, confidence: float) -> TrustLevel:
        """Map verification confidence to TrustLevel"""
        if confidence >= 0.9:
            return TrustLevel.HIGH
        elif confidence >= 0.7:
            return TrustLevel.MEDIUM
        elif confidence >= 0.5:
            return TrustLevel.LOW
        else:
            return TrustLevel.CRITICAL


_integration = None

def get_verification_integration() -> VerificationIntegration:
    """Get singleton verification integration instance"""
    global _integration
    if _integration is None:
        _integration = VerificationIntegration()
    return _integration
