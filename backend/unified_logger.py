"""
Unified Logger
Logs all activities to appropriate tables + data cube with cryptographic signing
"""

import hashlib
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .models import async_session
from .healing_models import (
    HealingAttempt, AgenticSpineLog, MetaLoopLog,
    MLLearningLog, TriggerMeshLog, DataCubeEntry
)
from .immutable_log import ImmutableLog

logger = logging.getLogger(__name__)


class UnifiedLogger:
    """
    Central logging system that routes events to:
    1. Appropriate subsystem table
    2. Data cube for analytics
    3. Immutable log for audit
    
    All with cryptographic signing
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.chain_hashes = {}  # Track last hash per table for chaining
    
    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _sign_entry(self, data: Dict[str, Any]) -> str:
        """Sign entry with cryptographic signature"""
        # Simplified - would use proper signing with private key
        return hashlib.sha256(
            (str(data) + "grace_private_key").encode()
        ).hexdigest()
    
    async def log_healing_attempt(
        self,
        attempt_id: str,
        error_type: str,
        error_message: str,
        detected_by: str,
        severity: str,
        error_file: Optional[str] = None,
        error_line: Optional[int] = None,
        stack_trace: Optional[str] = None,
        fix_type: Optional[str] = None,
        fix_description: Optional[str] = None,
        fix_code: Optional[str] = None,
        original_code: Optional[str] = None,
        confidence: float = 0.0,
        ml_recommendation: Optional[Dict] = None,
        requires_approval: bool = False,
        **kwargs
    ):
        """Log healing attempt to table + data cube"""
        
        async with async_session() as session:
            # Prepare data for hashing
            data_for_hash = {
                'attempt_id': attempt_id,
                'error_type': error_type,
                'error_message': error_message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Compute hash and signature
            entry_hash = self._compute_hash(data_for_hash)
            signature = self._sign_entry(data_for_hash)
            
            # Get previous hash for chaining
            previous_hash = self.chain_hashes.get('healing_attempts')
            
            # Create healing attempt entry
            attempt = HealingAttempt(
                attempt_id=attempt_id,
                error_type=error_type,
                error_message=error_message,
                error_file=error_file,
                error_line=error_line,
                stack_trace=stack_trace,
                fix_type=fix_type,
                fix_description=fix_description,
                fix_code=fix_code,
                original_code=original_code,
                detected_by=detected_by,
                severity=severity,
                confidence=confidence,
                ml_recommendation=ml_recommendation,
                requires_approval=requires_approval,
                status=kwargs.get('status', 'pending'),
                success=kwargs.get('success'),
                signature=signature,
                hash=entry_hash,
                previous_hash=previous_hash
            )
            
            session.add(attempt)
            
            # Update chain hash
            self.chain_hashes['healing_attempts'] = entry_hash
            
            # Also log to data cube
            await self._log_to_data_cube(
                session=session,
                subsystem='healing',
                actor=detected_by,
                action=error_type,
                resource=error_file or 'unknown',
                success=kwargs.get('success'),
                duration=None,
                confidence=confidence,
                severity=severity,
                context={'attempt_id': attempt_id}
            )
            
            await session.commit()
            
            logger.debug(f"[UNIFIED_LOG] Logged healing attempt: {attempt_id}")
    
    async def log_agentic_spine_decision(
        self,
        decision_type: str,
        decision_context: Dict[str, Any],
        chosen_action: str,
        rationale: str,
        actor: str,
        confidence: float = 0.0,
        risk_score: float = 0.0,
        **kwargs
    ):
        """Log agentic spine decision"""
        
        async with async_session() as session:
            log_id = f"spine_{uuid.uuid4()}"
            
            # Hash and sign
            data_for_hash = {
                'log_id': log_id,
                'decision_type': decision_type,
                'chosen_action': chosen_action,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            entry_hash = self._compute_hash(data_for_hash)
            signature = self._sign_entry(data_for_hash)
            previous_hash = self.chain_hashes.get('agentic_spine_logs')
            
            # Create entry
            spine_log = AgenticSpineLog(
                log_id=log_id,
                decision_type=decision_type,
                decision_context=decision_context,
                options_considered=kwargs.get('options_considered'),
                chosen_action=chosen_action,
                rationale=rationale,
                confidence=confidence,
                risk_score=risk_score,
                actor=actor,
                resource=kwargs.get('resource'),
                status=kwargs.get('status', 'proposed'),
                outcome=kwargs.get('outcome'),
                impact=kwargs.get('impact'),
                signature=signature,
                hash=entry_hash,
                previous_hash=previous_hash
            )
            
            session.add(spine_log)
            self.chain_hashes['agentic_spine_logs'] = entry_hash
            
            # Log to data cube
            await self._log_to_data_cube(
                session=session,
                subsystem='agentic_spine',
                actor=actor,
                action=decision_type,
                resource=kwargs.get('resource', 'unknown'),
                success=kwargs.get('outcome') == 'success',
                duration=None,
                confidence=confidence,
                severity=None,
                context={'decision_type': decision_type}
            )
            
            await session.commit()
            
            logger.debug(f"[UNIFIED_LOG] Logged agentic spine decision: {log_id}")
    
    async def log_meta_loop_cycle(
        self,
        cycle_number: int,
        focus_area: Optional[str] = None,
        guardrails_mode: Optional[str] = None,
        ml_root_causes: Optional[list] = None,
        directives_issued: Optional[list] = None,
        **kwargs
    ):
        """Log meta-loop cycle"""
        
        async with async_session() as session:
            cycle_id = f"cycle_{cycle_number}_{int(datetime.utcnow().timestamp())}"
            
            # Hash and sign
            data_for_hash = {
                'cycle_id': cycle_id,
                'cycle_number': cycle_number,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            entry_hash = self._compute_hash(data_for_hash)
            signature = self._sign_entry(data_for_hash)
            previous_hash = self.chain_hashes.get('meta_loop_logs')
            
            # Create entry
            meta_log = MetaLoopLog(
                cycle_id=cycle_id,
                cycle_number=cycle_number,
                snapshot_before=kwargs.get('snapshot_before'),
                snapshot_after=kwargs.get('snapshot_after'),
                focus_area=focus_area,
                guardrails_mode=guardrails_mode,
                ml_root_causes=ml_root_causes,
                directives_issued=directives_issued,
                directives_executed=kwargs.get('directives_executed', 0),
                directives_successful=kwargs.get('directives_successful', 0),
                duration_seconds=kwargs.get('duration'),
                domains_analyzed=kwargs.get('domains_analyzed', 0),
                outcome=kwargs.get('outcome'),
                improvements_made=kwargs.get('improvements_made'),
                signature=signature,
                hash=entry_hash,
                previous_hash=previous_hash,
                completed_at=kwargs.get('completed_at')
            )
            
            session.add(meta_log)
            self.chain_hashes['meta_loop_logs'] = entry_hash
            
            # Log to data cube
            await self._log_to_data_cube(
                session=session,
                subsystem='meta_loop',
                actor='meta_loop_supervisor',
                action='cycle_completed',
                resource=focus_area or 'system',
                success=kwargs.get('outcome') == 'success',
                duration=kwargs.get('duration'),
                confidence=None,
                severity=None,
                context={'cycle': cycle_number}
            )
            
            await session.commit()
            
            logger.debug(f"[UNIFIED_LOG] Logged meta-loop cycle: {cycle_id}")
    
    async def log_ml_learning(
        self,
        learning_type: str,
        subsystem: str,
        pattern_name: Optional[str] = None,
        pattern_success_rate: Optional[float] = None,
        **kwargs
    ):
        """Log ML/DL learning activity"""
        
        async with async_session() as session:
            learning_id = f"ml_{uuid.uuid4()}"
            
            # Hash and sign
            data_for_hash = {
                'learning_id': learning_id,
                'learning_type': learning_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            entry_hash = self._compute_hash(data_for_hash)
            signature = self._sign_entry(data_for_hash)
            previous_hash = self.chain_hashes.get('ml_learning_logs')
            
            # Create entry
            ml_log = MLLearningLog(
                learning_id=learning_id,
                learning_type=learning_type,
                subsystem=subsystem,
                pattern_name=pattern_name,
                pattern_count=kwargs.get('pattern_count', 0),
                pattern_success_rate=pattern_success_rate,
                pattern_confidence=kwargs.get('pattern_confidence'),
                model_type=kwargs.get('model_type'),
                model_version=kwargs.get('model_version'),
                training_samples=kwargs.get('training_samples', 0),
                accuracy=kwargs.get('accuracy'),
                predicted_error=kwargs.get('predicted_error'),
                predicted_likelihood=kwargs.get('predicted_likelihood'),
                recommendation_confidence=kwargs.get('recommendation_confidence'),
                signature=signature,
                hash=entry_hash,
                previous_hash=previous_hash
            )
            
            session.add(ml_log)
            self.chain_hashes['ml_learning_logs'] = entry_hash
            
            # Log to data cube
            await self._log_to_data_cube(
                session=session,
                subsystem='ml_learning',
                actor=subsystem,
                action=learning_type,
                resource=pattern_name or 'model',
                success=True,
                duration=kwargs.get('training_duration_seconds'),
                confidence=kwargs.get('pattern_confidence'),
                severity=None,
                context={'learning_type': learning_type}
            )
            
            await session.commit()
            
            logger.debug(f"[UNIFIED_LOG] Logged ML learning: {learning_id}")
    
    async def log_trigger_mesh_event(
        self,
        event_id: str,
        event_type: str,
        source: str,
        actor: str,
        resource: str,
        payload: Optional[Dict] = None,
        handlers_notified: int = 0,
        **kwargs
    ):
        """Log trigger mesh event"""
        
        async with async_session() as session:
            # Hash and sign
            data_for_hash = {
                'event_id': event_id,
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            entry_hash = self._compute_hash(data_for_hash)
            signature = self._sign_entry(data_for_hash)
            
            # Create entry
            mesh_log = TriggerMeshLog(
                event_id=event_id,
                event_type=event_type,
                source=source,
                actor=actor,
                resource=resource,
                payload=payload,
                handlers_notified=handlers_notified,
                handlers_succeeded=kwargs.get('handlers_succeeded', 0),
                handlers_failed=kwargs.get('handlers_failed', 0),
                processing_time_ms=kwargs.get('processing_time_ms'),
                signature=signature,
                hash=entry_hash
            )
            
            session.add(mesh_log)
            
            # Log to data cube
            await self._log_to_data_cube(
                session=session,
                subsystem='trigger_mesh',
                actor=actor,
                action=event_type,
                resource=resource,
                success=kwargs.get('handlers_failed', 0) == 0,
                duration=kwargs.get('processing_time_ms', 0) / 1000 if kwargs.get('processing_time_ms') else None,
                confidence=None,
                severity=None,
                context={'source': source}
            )
            
            await session.commit()
            
            logger.debug(f"[UNIFIED_LOG] Logged trigger mesh event: {event_id}")
    
    async def _log_to_data_cube(
        self,
        session,
        subsystem: str,
        actor: str,
        action: str,
        resource: str,
        success: Optional[bool] = None,
        duration: Optional[float] = None,
        confidence: Optional[float] = None,
        severity: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """Log to data cube for analytics"""
        
        cube_id = f"cube_{uuid.uuid4()}"
        
        # Hash for crypto
        data_for_hash = {
            'cube_id': cube_id,
            'subsystem': subsystem,
            'action': action,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        entry_hash = self._compute_hash(data_for_hash)
        signature = self._sign_entry(data_for_hash)
        
        # Determine metrics
        metric_error_count = 0 if success else 1 if success is not None else 0
        metric_fix_count = 1 if 'fix' in action.lower() else 0
        metric_learning_count = 1 if 'learn' in action.lower() else 0
        
        # Create data cube entry
        cube_entry = DataCubeEntry(
            cube_id=cube_id,
            dimension_time=datetime.utcnow(),
            dimension_subsystem=subsystem,
            dimension_actor=actor,
            dimension_action=action,
            dimension_resource=resource,
            metric_success=success,
            metric_duration=duration,
            metric_confidence=confidence,
            metric_count=1,
            metric_error_count=metric_error_count,
            metric_fix_count=metric_fix_count,
            metric_learning_count=metric_learning_count,
            category_severity=severity,
            category_type=action.split('_')[0] if '_' in action else action,
            context_data=context,
            signature=signature,
            hash=entry_hash
        )
        
        session.add(cube_entry)
    
    async def update_healing_attempt(
        self,
        attempt_id: str,
        status: Optional[str] = None,
        success: Optional[bool] = None,
        applied_at: Optional[datetime] = None,
        verified_at: Optional[datetime] = None,
        failure_reason: Optional[str] = None,
        approved_by: Optional[str] = None
    ):
        """Update existing healing attempt with outcome"""
        
        async with async_session() as session:
            from sqlalchemy import update
            
            update_data = {}
            if status:
                update_data['status'] = status
            if success is not None:
                update_data['success'] = success
            if applied_at:
                update_data['applied_at'] = applied_at
            if verified_at:
                update_data['verified_at'] = verified_at
            if failure_reason:
                update_data['failure_reason'] = failure_reason
            if approved_by:
                update_data['approved_by'] = approved_by
                update_data['approval_timestamp'] = datetime.utcnow()
            
            if update_data:
                await session.execute(
                    update(HealingAttempt)
                    .where(HealingAttempt.attempt_id == attempt_id)
                    .values(**update_data)
                )
                
                await session.commit()
                
                logger.debug(f"[UNIFIED_LOG] Updated healing attempt: {attempt_id}")


# Global instance
unified_logger = UnifiedLogger()
