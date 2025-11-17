"""Constitutional AI Engine - Ethical Governance Layer

Implements Anthropic-style Constitutional AI framework ensuring Grace
behaves ethically, transparently, and safely with automatic clarification.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select

from backend.models import async_session
from ..models.constitutional_models import (
    ConstitutionalPrinciple, ConstitutionalViolation,
    ClarificationRequest, ConstitutionalCompliance
)
from ..logging.immutable_log import immutable_log

class ConstitutionalEngine:
    """Enforce constitutional principles across all Grace operations"""
    
    def __init__(self):
        self.audit = immutable_log
        
        # Confidence thresholds
        self.clarification_threshold = 0.7  # Below this, ask for clarification
        self.safety_threshold = 0.9  # Above this required for risky actions
    
    async def check_constitutional_compliance(
        self,
        action_id: str,
        actor: str,
        action_type: str,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Check if action complies with constitutional principles
        
        Args:
            action_id: Unique action identifier
            actor: Who is performing action
            action_type: Type of action
            resource: Resource being acted upon
            context: Additional context
            confidence: Grace's confidence in this action (0.0-1.0)
        
        Returns:
            Compliance result with details
        """
        
        # Get relevant principles
        principles = await self._get_applicable_principles(action_type)
        
        checks = {
            'principles_checked': [],
            'principles_passed': [],
            'principles_failed': [],
            'violations': [],
            'compliant': True,
            'compliance_score': 1.0,
            'needs_clarification': False,
            'clarification_reason': None
        }
        
        # Check each principle
        for principle in principles:
            check_result = await self._check_principle(
                principle, actor, action_type, resource, context, confidence
            )
            
            checks['principles_checked'].append(principle['id'])
            
            if check_result['compliant']:
                checks['principles_passed'].append(principle['id'])
            else:
                checks['principles_failed'].append(principle['id'])
                checks['compliant'] = False
                checks['violations'].append(check_result['violation'])
        
        # Calculate overall compliance score
        if checks['principles_checked']:
            checks['compliance_score'] = len(checks['principles_passed']) / len(checks['principles_checked'])
        
        # Check for low confidence (needs clarification)
        if confidence < self.clarification_threshold:
            checks['needs_clarification'] = True
            checks['clarification_reason'] = f"Low confidence ({confidence:.2f}) below threshold ({self.clarification_threshold})"

        # Store compliance record
        async with async_session() as session:
            compliance = ConstitutionalCompliance(
                action_id=action_id,
                actor=actor,
                action_type=action_type,
                resource=resource,
                principles_checked=checks['principles_checked'],
                principles_passed=checks['principles_passed'],
                principles_failed=checks['principles_failed'],
                compliant=checks['compliant'],
                compliance_score=checks['compliance_score']
            )
            session.add(compliance)
            await session.commit()
        
        return checks
    
    async def _get_applicable_principles(
        self,
        action_type: str
    ) -> List[Dict[str, Any]]:
        """Get principles that apply to this action type"""
        
        async with async_session() as session:
            result = await session.execute(
                select(ConstitutionalPrinciple).where(
                    ConstitutionalPrinciple.active == True
                )
            )
            all_principles = result.scalars().all()
            
            applicable = []
            for principle in all_principles:
                # Check if applies to this action
                applies_to = principle.applies_to or []
                if "all" in applies_to or action_type in applies_to:
                    applicable.append({
                        'id': principle.id,
                        'name': principle.principle_name,
                        'title': principle.title,
                        'description': principle.description,
                        'enforcement_type': principle.enforcement_type,
                        'severity': principle.severity
                    })
            
            return applicable
    
    async def _check_principle(
        self,
        principle: Dict[str, Any],
        actor: str,
        action_type: str,
        resource: Optional[str],
        context: Optional[Dict[str, Any]],
        confidence: float
    ) -> Dict[str, Any]:
        """Check if action complies with a specific principle"""
        
        principle_name = principle['name']
        
        # Beneficence - Check for positive intent
        if principle_name == "beneficence":
            return await self._check_beneficence(actor, action_type, context)
        
        # Transparency - Check for explanation
        elif principle_name == "transparency_honesty":
            return await self._check_transparency(context, confidence)
        
        # Accountability - Check for logging
        elif principle_name == "accountability":
            return await self._check_accountability(context)
        
        # Respect for Law - Check for legal compliance
        elif principle_name == "respect_law_ethics":
            return await self._check_legal_ethical(action_type, resource, context)
        
        # Explainability - Check for reasoning
        elif principle_name == "follow_why":
            return await self._check_explainability(context)
        
        # Default: assume compliant
        return {'compliant': True}
    
    async def _check_beneficence(self, actor: str, action_type: str, context: Dict) -> Dict:
        """Check if action has positive intent"""
        
        # Check for destructive patterns
        destructive_keywords = [
            'delete_all', 'drop_database', 'rm -rf /', 'format',
            'destroy', 'corrupt', 'malicious'
        ]
        
        action_str = f"{action_type} {context}".lower()
        
        for keyword in destructive_keywords:
            if keyword in action_str:
                return {
                    'compliant': False,
                    'violation': {
                        'principle': 'beneficence',
                        'reason': f"Action contains potentially harmful keyword: {keyword}",
                        'severity': 'critical'
                    }
                }
        
        return {'compliant': True}
    
    async def _check_transparency(self, context: Dict, confidence: float) -> Dict:
        """Check if Grace is being transparent about uncertainty"""
        
        # If low confidence, must have clarification request or explicit uncertainty statement
        if confidence < self.clarification_threshold:
            has_clarification = context.get('clarification_requested', False)
            has_uncertainty_notice = context.get('uncertainty_disclosed', False)
            
            if not has_clarification and not has_uncertainty_notice:
                return {
                    'compliant': False,
                    'violation': {
                        'principle': 'transparency_honesty',
                        'reason': f"Low confidence ({confidence:.2f}) without clarification or uncertainty disclosure",
                        'severity': 'high'
                    }
                }
        
        return {'compliant': True}
    
    async def _check_accountability(self, context: Dict) -> Dict:
        """Check if action is properly logged"""
        
        # Verify audit logging is enabled
        has_audit = context.get('audit_log_id') or context.get('audit_enabled', True)
        
        if not has_audit:
            return {
                'compliant': False,
                'violation': {
                    'principle': 'accountability',
                    'reason': "Action not logged to audit trail",
                    'severity': 'critical'
                }
            }
        
        return {'compliant': True}
    
    async def _check_legal_ethical(
        self,
        action_type: str,
        resource: Optional[str],
        context: Dict
    ) -> Dict:
        """Check for legal/ethical compliance"""
        
        # List of prohibited actions
        prohibited = [
            'access_private_data_without_consent',
            'bypass_authentication',
            'privilege_escalation_unauthorized',
            'data_exfiltration',
            'copyright_violation',
            'generate_harmful_content'
        ]
        
        if action_type in prohibited:
            return {
                'compliant': False,
                'violation': {
                    'principle': 'respect_law_ethics',
                    'reason': f"Prohibited action type: {action_type}",
                    'severity': 'critical'
                }
            }
        
        return {'compliant': True}
    
    async def _check_explainability(self, context: Dict) -> Dict:
        """Check if reasoning/explanation is provided"""
        
        # Major decisions should have reasoning
        has_reasoning = (
            context.get('reasoning') or
            context.get('explanation') or
            context.get('why')
        )
        
        # If this is a significant action, reasoning is required
        is_significant = context.get('significant', False) or context.get('requires_approval', False)
        
        if is_significant and not has_reasoning:
            return {
                'compliant': False,
                'violation': {
                    'principle': 'follow_why',
                    'reason': "Significant action without explanation or reasoning",
                    'severity': 'medium'
                }
            }
        
        return {'compliant': True}
    
    async def request_clarification(
        self,
        user: str,
        original_input: str,
        uncertainty_type: str,
        confidence: float,
        question: str,
        options: Optional[List[str]] = None,
        context: Optional[str] = None,
        timeout_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Request clarification from user when Grace is uncertain
        
        Args:
            user: User to ask
            original_input: What user originally said
            uncertainty_type: Why uncertain (ambiguous, low_confidence, conflict, policy)
            confidence: Confidence score (0.0-1.0)
            question: Question to ask user
            options: Possible interpretations/choices
            context: Additional context Grace provides
            timeout_minutes: How long to wait for response
        
        Returns:
            Clarification request details
        """
        
        request_id = str(uuid.uuid4())
        timeout_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        
        async with async_session() as session:
            clarification = ClarificationRequest(
                request_id=request_id,
                user=user,
                original_input=original_input,
                uncertainty_type=uncertainty_type,
                confidence_score=confidence,
                question=question,
                options=options,
                context_provided=context,
                status="pending",
                timeout_at=timeout_at
            )
            
            session.add(clarification)
            await session.commit()
            await session.refresh(clarification)
            
            db_id = clarification.id
        
        # Log to audit
        await self.audit.append(
            actor="constitutional_engine",
            action="clarification_requested",
            resource=f"user_{user}",
            subsystem="constitutional_ai",
            payload={
                'request_id': request_id,
                'uncertainty_type': uncertainty_type,
                'confidence': confidence
            },
            result="pending"
        )
        
        return {
            'request_id': request_id,
            'question': question,
            'options': options,
            'context': context,
            'timeout_at': timeout_at.isoformat()
        }
    
    async def answer_clarification(
        self,
        request_id: str,
        user_response: str,
        selected_option: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record user's response to clarification request
        
        Args:
            request_id: Request identifier
            user_response: User's clarifying response
            selected_option: If options were provided, which one selected
        
        Returns:
            Updated request with resolved action
        """
        
        async with async_session() as session:
            result = await session.execute(
                select(ClarificationRequest).where(
                    ClarificationRequest.request_id == request_id
                )
            )
            clarification = result.scalar_one_or_none()
            
            if not clarification:
                raise ValueError(f"Clarification request not found: {request_id}")
            
            if clarification.status != "pending":
                raise ValueError(f"Request already {clarification.status}")
            
            # Update with response
            clarification.status = "answered"
            clarification.user_response = user_response
            clarification.selected_option = selected_option
            clarification.responded_at = datetime.utcnow()
            
            await session.commit()
        
        # Log response
        await self.audit.append(
            actor=clarification.user,
            action="clarification_answered",
            resource=request_id,
            subsystem="constitutional_ai",
            payload={'response': user_response},
            result="answered"
        )
        
        return {
            'request_id': request_id,
            'status': 'answered',
            'user_response': user_response,
            'original_input': clarification.original_input
        }
    
    async def log_violation(
        self,
        principle_name: str,
        actor: str,
        action: str,
        resource: Optional[str],
        violation_type: str,
        detected_by: str,
        severity: str,
        details: Optional[str] = None,
        blocked: bool = False
    ) -> Dict[str, Any]:
        """
        Log a constitutional violation
        
        Args:
            principle_name: Which principle was violated
            actor: Who violated it
            action: What action violated it
            resource: Resource involved
            violation_type: Type (attempt, accidental, bypassed)
            detected_by: Detection system (governance, hunter, verification, human)
            severity: Severity level
            details: Additional details
            blocked: Was action blocked
        
        Returns:
            Violation record
        """
        
        # Get principle
        async with async_session() as session:
            result = await session.execute(
                select(ConstitutionalPrinciple).where(
                    ConstitutionalPrinciple.principle_name == principle_name
                )
            )
            principle = result.scalar_one_or_none()
            
            if not principle:
                raise ValueError(f"Principle not found: {principle_name}")
            
            # Create violation
            violation = ConstitutionalViolation(
                principle_id=principle.id,
                violation_type=violation_type,
                actor=actor,
                action=action,
                resource=resource,
                detected_by=detected_by,
                severity=severity,
                details=details,
                blocked=blocked
            )
            
            session.add(violation)
            await session.commit()
            await session.refresh(violation)
            
            violation_id = violation.id
        
        # Log to audit
        await self.audit.append(
            actor=detected_by,
            action="constitutional_violation",
            resource=f"violation_{violation_id}",
            subsystem="constitutional_ai",
            payload={
                'principle': principle_name,
                'actor': actor,
                'severity': severity,
                'blocked': blocked
            },
            result="logged"
        )
        
        # If critical, escalate to Parliament or create task
        if severity == "critical" and not blocked:
            # TODO: Escalate to Parliament for review
            print(f"CRITICAL VIOLATION: {principle_name} by {actor}")
        
        return {
            'violation_id': violation_id,
            'principle': principle_name,
            'severity': severity,
            'blocked': blocked
        }

constitutional_engine = ConstitutionalEngine()
