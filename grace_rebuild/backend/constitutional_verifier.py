"""Constitutional Verification - Check compliance BEFORE action execution

Comprehensive constitutional compliance checking integrated with
governance, hunter, and verification systems.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import select

from .models import async_session
from .constitutional_models import ConstitutionalPrinciple, ConstitutionalViolation, ConstitutionalCompliance
from .constitutional_engine import constitutional_engine
from .governance import governance_engine
from .hunter import hunter
from .immutable_log import ImmutableLog

class ConstitutionalVerifier:
    """Verify constitutional compliance before action execution"""
    
    def __init__(self):
        self.audit = ImmutableLog()
        self.strict_mode = True  # Block non-compliant actions
        
    async def verify_action(
        self,
        actor: str,
        action_type: str,
        resource: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive constitutional verification before action execution
        
        Args:
            actor: Who is performing the action
            action_type: Type of action (code_generation, file_write, etc.)
            resource: Resource being acted upon
            payload: Action payload/data
            confidence: GRACE's confidence in this action
            context: Additional context
        
        Returns:
            Verification result with compliance status
        """
        
        action_id = f"{action_type}_{uuid.uuid4().hex[:8]}"
        payload = payload or {}
        context = context or {}
        
        result = {
            'action_id': action_id,
            'compliant': True,
            'allowed': True,
            'violations': [],
            'warnings': [],
            'governance_decision': None,
            'hunter_alerts': [],
            'constitutional_check': None,
            'needs_clarification': False,
            'clarification_request': None
        }
        
        # 1. Constitutional Compliance Check
        constitutional_check = await constitutional_engine.check_constitutional_compliance(
            action_id=action_id,
            actor=actor,
            action_type=action_type,
            resource=resource,
            context=context,
            confidence=confidence
        )
        
        result['constitutional_check'] = constitutional_check
        
        if not constitutional_check['compliant']:
            result['compliant'] = False
            result['violations'].extend(constitutional_check['violations'])
            
            if self.strict_mode:
                result['allowed'] = False
                
                # Log violations
                for violation in constitutional_check['violations']:
                    await self._log_violation(
                        action_id=action_id,
                        actor=actor,
                        action_type=action_type,
                        resource=resource,
                        violation=violation,
                        blocked=True
                    )
        
        # 2. Check if clarification needed
        if constitutional_check.get('needs_clarification'):
            result['needs_clarification'] = True
            result['warnings'].append({
                'type': 'low_confidence',
                'message': constitutional_check['clarification_reason']
            })
            
            # In strict mode, require clarification before proceeding
            if self.strict_mode and confidence < 0.7:
                result['allowed'] = False
        
        # 3. Governance Policy Check
        gov_decision = await governance_engine.check(
            actor=actor,
            action=action_type,
            resource=resource or "unknown",
            payload=payload
        )
        
        result['governance_decision'] = gov_decision
        
        if gov_decision['decision'] == 'block':
            result['allowed'] = False
            result['violations'].append({
                'type': 'governance_block',
                'policy': gov_decision.get('policy'),
                'reason': 'Action blocked by governance policy'
            })
        elif gov_decision['decision'] in ['review', 'parliament_pending']:
            result['warnings'].append({
                'type': 'requires_approval',
                'message': f"Action requires review: {gov_decision.get('policy')}"
            })
        
        # 4. Hunter Security Check
        hunter_alerts = await hunter.inspect(
            actor=actor,
            action=action_type,
            resource=resource or "unknown",
            payload=payload
        )
        
        if hunter_alerts:
            result['hunter_alerts'] = hunter_alerts
            result['warnings'].append({
                'type': 'security_alert',
                'message': f"Security alerts triggered: {len(hunter_alerts)}"
            })
            
            # Check severity
            for rule_name, event_id in hunter_alerts:
                # Get event details
                severity = await self._get_alert_severity(event_id)
                if severity == 'critical':
                    result['allowed'] = False
                    result['violations'].append({
                        'type': 'security_critical',
                        'rule': rule_name,
                        'event_id': event_id,
                        'reason': 'Critical security alert'
                    })
        
        # 5. Check Safety Constraints
        safety_violations = await self._check_safety_constraints(
            action_type, resource, payload, context
        )
        
        if safety_violations:
            result['violations'].extend(safety_violations)
            result['allowed'] = False
            result['compliant'] = False
            
            # Log safety violations
            for violation in safety_violations:
                await self._log_violation(
                    action_id=action_id,
                    actor=actor,
                    action_type=action_type,
                    resource=resource,
                    violation=violation,
                    blocked=True
                )
        
        # 6. Log to audit trail
        await self.audit.append(
            actor="constitutional_verifier",
            action="verify_action",
            resource=action_id,
            subsystem="constitutional_ai",
            payload={
                'actor': actor,
                'action_type': action_type,
                'resource': resource,
                'compliant': result['compliant'],
                'allowed': result['allowed'],
                'violations_count': len(result['violations']),
                'warnings_count': len(result['warnings'])
            },
            result="allowed" if result['allowed'] else "blocked"
        )
        
        return result
    
    async def _check_safety_constraints(
        self,
        action_type: str,
        resource: Optional[str],
        payload: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check hard safety constraints"""
        
        violations = []
        
        # Get safety constraint principles
        async with async_session() as session:
            result = await session.execute(
                select(ConstitutionalPrinciple).where(
                    ConstitutionalPrinciple.principle_level == "safety",
                    ConstitutionalPrinciple.active == True
                )
            )
            safety_principles = result.scalars().all()
        
        # Convert to dict for easier checking
        data_str = str(payload).lower() + str(context).lower() + (resource or "").lower()
        
        # Check each safety constraint
        for principle in safety_principles:
            constraint = principle.principle_name
            
            # Destructive commands
            if constraint == "no_destructive_commands":
                destructive_patterns = [
                    'rm -rf /', 'drop database', 'drop table', 'truncate table',
                    'format c:', 'del /f /s /q', 'git reset --hard HEAD~'
                ]
                for pattern in destructive_patterns:
                    if pattern in data_str:
                        violations.append({
                            'principle': constraint,
                            'reason': f"Destructive command detected: {pattern}",
                            'severity': 'critical'
                        })
            
            # Sensitive data exposure
            elif constraint == "no_sensitive_data_exposure":
                sensitive_patterns = [
                    r'api[_-]?key', r'password', r'secret', r'token',
                    r'private[_-]?key', r'aws[_-]?access', r'bearer\s+\w+'
                ]
                import re
                for pattern in sensitive_patterns:
                    if re.search(pattern, data_str):
                        violations.append({
                            'principle': constraint,
                            'reason': f"Potential sensitive data exposure: {pattern}",
                            'severity': 'critical'
                        })
            
            # Privilege escalation
            elif constraint == "no_privilege_escalation":
                escalation_patterns = [
                    'sudo', 'su root', 'chmod +s', 'setuid',
                    'bypass auth', 'skip authentication'
                ]
                for pattern in escalation_patterns:
                    if pattern in data_str:
                        violations.append({
                            'principle': constraint,
                            'reason': f"Privilege escalation attempt: {pattern}",
                            'severity': 'critical'
                        })
            
            # Code obfuscation
            elif constraint == "no_code_obfuscation":
                if action_type == "code_generation":
                    obfuscation_indicators = [
                        'eval(', 'exec(', 'compile(',
                        '__import__', 'getattr(__builtins__',
                        'base64.b64decode'
                    ]
                    for indicator in obfuscation_indicators:
                        if indicator in data_str:
                            violations.append({
                                'principle': constraint,
                                'reason': f"Code obfuscation detected: {indicator}",
                                'severity': 'high'
                            })
            
            # Malware generation
            elif constraint == "no_malware_generation":
                malware_indicators = [
                    'ransomware', 'keylogger', 'backdoor',
                    'exploit', 'shellcode', 'payload',
                    'reverse shell', 'cryptolocker'
                ]
                for indicator in malware_indicators:
                    if indicator in data_str:
                        violations.append({
                            'principle': constraint,
                            'reason': f"Malware generation detected: {indicator}",
                            'severity': 'critical'
                        })
            
            # Self-modification
            elif constraint == "no_self_modification_without_approval":
                if action_type in ['code_generation', 'file_write']:
                    grace_files = [
                        'grace.py', 'constitutional', 'governance',
                        'hunter.py', 'verification', 'parliament'
                    ]
                    if resource:
                        for grace_file in grace_files:
                            if grace_file in resource.lower():
                                # Check if approved
                                if not context.get('self_modification_approved'):
                                    violations.append({
                                        'principle': constraint,
                                        'reason': f"Self-modification without approval: {resource}",
                                        'severity': 'critical'
                                    })
        
        return violations
    
    async def _get_alert_severity(self, event_id: int) -> str:
        """Get severity of a security event"""
        from .governance_models import SecurityEvent
        
        async with async_session() as session:
            result = await session.execute(
                select(SecurityEvent).where(SecurityEvent.id == event_id)
            )
            event = result.scalar_one_or_none()
            
            return event.severity if event else "unknown"
    
    async def _log_violation(
        self,
        action_id: str,
        actor: str,
        action_type: str,
        resource: Optional[str],
        violation: Dict[str, Any],
        blocked: bool
    ) -> None:
        """Log a constitutional violation"""
        
        await constitutional_engine.log_violation(
            principle_name=violation['principle'],
            actor=actor,
            action=action_type,
            resource=resource,
            violation_type='attempt',
            detected_by='constitutional_verifier',
            severity=violation.get('severity', 'high'),
            details=violation.get('reason'),
            blocked=blocked
        )
    
    async def generate_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate constitutional compliance report"""
        
        async with async_session() as session:
            # Get all compliance records
            query = select(ConstitutionalCompliance)
            if start_date:
                query = query.where(ConstitutionalCompliance.created_at >= start_date)
            if end_date:
                query = query.where(ConstitutionalCompliance.created_at <= end_date)
            
            result = await session.execute(query)
            records = result.scalars().all()
            
            # Get all violations
            violation_query = select(ConstitutionalViolation)
            if start_date:
                violation_query = violation_query.where(ConstitutionalViolation.created_at >= start_date)
            if end_date:
                violation_query = violation_query.where(ConstitutionalViolation.created_at <= end_date)
            
            violation_result = await session.execute(violation_query)
            violations = violation_result.scalars().all()
            
            # Calculate metrics
            total_actions = len(records)
            compliant_actions = len([r for r in records if r.compliant])
            compliance_rate = (compliant_actions / total_actions * 100) if total_actions > 0 else 0
            
            # Group violations by principle
            violations_by_principle = {}
            for v in violations:
                principle_name = v.principle.principle_name if v.principle else "unknown"
                if principle_name not in violations_by_principle:
                    violations_by_principle[principle_name] = []
                violations_by_principle[principle_name].append({
                    'actor': v.actor,
                    'action': v.action,
                    'severity': v.severity,
                    'blocked': v.blocked,
                    'created_at': v.created_at.isoformat()
                })
            
            # Group by severity
            violations_by_severity = {
                'critical': len([v for v in violations if v.severity == 'critical']),
                'high': len([v for v in violations if v.severity == 'high']),
                'medium': len([v for v in violations if v.severity == 'medium']),
                'low': len([v for v in violations if v.severity == 'low'])
            }
            
            return {
                'period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'metrics': {
                    'total_actions': total_actions,
                    'compliant_actions': compliant_actions,
                    'non_compliant_actions': total_actions - compliant_actions,
                    'compliance_rate': round(compliance_rate, 2),
                    'total_violations': len(violations),
                    'violations_blocked': len([v for v in violations if v.blocked])
                },
                'violations_by_severity': violations_by_severity,
                'violations_by_principle': violations_by_principle,
                'top_violators': self._get_top_actors([v.actor for v in violations]),
                'most_violated_principles': sorted(
                    violations_by_principle.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:10]
            }
    
    def _get_top_actors(self, actors: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top violating actors"""
        from collections import Counter
        
        actor_counts = Counter(actors)
        
        return [
            {'actor': actor, 'violation_count': count}
            for actor, count in actor_counts.most_common(limit)
        ]

constitutional_verifier = ConstitutionalVerifier()
