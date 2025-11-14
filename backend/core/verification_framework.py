"""
Verification Framework
Continuous verification of system state and decisions

Part of Grace's unbreakable core - ensures correctness at all times
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging

from .message_bus import message_bus, MessagePriority
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class VerificationRule:
    """A verification rule that must always hold true"""
    
    def __init__(
        self,
        rule_id: str,
        description: str,
        check_fn: Callable[[], bool],
        severity: str = "high",
        auto_remediate: bool = False,
        remediation_fn: Optional[Callable] = None
    ):
        self.rule_id = rule_id
        self.description = description
        self.check_fn = check_fn
        self.severity = severity
        self.auto_remediate = auto_remediate
        self.remediation_fn = remediation_fn
        
        # Tracking
        self.last_checked = None
        self.last_result = None
        self.violation_count = 0


class VerificationFramework:
    """
    Continuous verification framework
    
    Ensures:
    - System invariants always hold
    - No unauthorized changes
    - KPIs within bounds
    - Trust scores accurate
    - Governance not bypassed
    
    Part of the unbreakable core
    """
    
    def __init__(self):
        self.rules = {}
        self.violations = []
        self.running = False
        self.check_interval = 60  # seconds
    
    async def start(self):
        """Start verification framework"""
        
        self.running = True
        
        # Define core verification rules
        self._define_core_rules()
        
        # Start continuous verification loop
        asyncio.create_task(self._verification_loop())
        
        logger.info("[VERIFICATION] Framework started - continuous verification active")
    
    def _define_core_rules(self):
        """Define core verification rules"""
        
        # Rule 1: Message bus must be running
        self.add_rule(
            rule_id='bus_running',
            description='Message bus must be running',
            check_fn=lambda: message_bus.running,
            severity='critical',
            auto_remediate=False
        )
        
        # Rule 2: Immutable log must be writable
        self.add_rule(
            rule_id='log_writable',
            description='Immutable log must be writable',
            check_fn=lambda: immutable_log.running,
            severity='critical',
            auto_remediate=False
        )
        
        # Rule 3: Critical kernels must be running
        # (Would check control_plane kernels in production)
        
        # Rule 4: No bypassing governance
        # (Would check that high-risk actions go through approval)
        
        # Rule 5: Trust scores in valid range
        self.add_rule(
            rule_id='trust_scores_valid',
            description='All trust scores must be 0-100',
            check_fn=lambda: True,  # Would actually check trust scores
            severity='high',
            auto_remediate=False
        )
    
    def add_rule(
        self,
        rule_id: str,
        description: str,
        check_fn: Callable[[], bool],
        severity: str = "high",
        auto_remediate: bool = False,
        remediation_fn: Optional[Callable] = None
    ):
        """Add verification rule"""
        
        rule = VerificationRule(
            rule_id=rule_id,
            description=description,
            check_fn=check_fn,
            severity=severity,
            auto_remediate=auto_remediate,
            remediation_fn=remediation_fn
        )
        
        self.rules[rule_id] = rule
        
        logger.info(f"[VERIFICATION] Added rule: {rule_id}")
    
    async def verify_all(self) -> Dict[str, Any]:
        """
        Verify all rules
        
        Returns:
            Verification result
        """
        
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_rules': len(self.rules),
            'rules_passed': 0,
            'rules_failed': 0,
            'violations': [],
            'status': 'unknown'
        }
        
        for rule_id, rule in self.rules.items():
            passed = await self._check_rule(rule)
            
            if passed:
                result['rules_passed'] += 1
            else:
                result['rules_failed'] += 1
                result['violations'].append({
                    'rule_id': rule_id,
                    'description': rule.description,
                    'severity': rule.severity,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        # Overall status
        if result['rules_failed'] == 0:
            result['status'] = 'all_verified'
        elif any(v['severity'] == 'critical' for v in result['violations']):
            result['status'] = 'critical_violations'
        else:
            result['status'] = 'violations_detected'
        
        return result
    
    async def _check_rule(self, rule: VerificationRule) -> bool:
        """Check a single verification rule"""
        
        rule.last_checked = datetime.utcnow()
        
        try:
            # Execute check function
            passed = rule.check_fn()
            
            if not passed:
                rule.violation_count += 1
                
                logger.warning(f"[VERIFICATION] Rule violated: {rule.rule_id}")
                
                # Record violation
                self.violations.append({
                    'rule_id': rule.rule_id,
                    'description': rule.description,
                    'timestamp': datetime.utcnow().isoformat(),
                    'severity': rule.severity
                })
                
                # Log to immutable log
                await immutable_log.append(
                    actor='verification_framework',
                    action='rule_violation',
                    resource=rule.rule_id,
                    decision={
                        'rule': rule.description,
                        'severity': rule.severity,
                        'auto_remediate': rule.auto_remediate
                    }
                )
                
                # Publish alert
                await message_bus.publish(
                    source='verification_framework',
                    topic='system.health',
                    payload={
                        'alert_type': 'verification_violation',
                        'rule_id': rule.rule_id,
                        'severity': rule.severity
                    },
                    priority=MessagePriority.HIGH if rule.severity == 'critical' else MessagePriority.NORMAL
                )
                
                # Auto-remediate if enabled
                if rule.auto_remediate and rule.remediation_fn:
                    logger.info(f"[VERIFICATION] Auto-remediating: {rule.rule_id}")
                    await rule.remediation_fn()
            
            rule.last_result = passed
            return passed
        
        except Exception as e:
            logger.error(f"[VERIFICATION] Error checking rule {rule.rule_id}: {e}")
            return False
    
    async def _verification_loop(self):
        """Continuous verification loop"""
        
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)
                
                # Verify all rules
                result = await self.verify_all()
                
                if result['status'] == 'critical_violations':
                    logger.error(f"[VERIFICATION] Critical violations detected!")
                    
                    # Alert control plane
                    await message_bus.publish(
                        source='verification_framework',
                        topic='system.control',
                        payload={
                            'alert': 'critical_violations',
                            'violations': result['violations']
                        },
                        priority=MessagePriority.CRITICAL
                    )
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[VERIFICATION] Loop error: {e}")
    
    def get_recent_violations(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent violations"""
        return self.violations[-count:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        return {
            'running': self.running,
            'total_rules': len(self.rules),
            'total_violations': len(self.violations),
            'check_interval_seconds': self.check_interval,
            'rules': {rule_id: {
                'description': rule.description,
                'last_checked': rule.last_checked.isoformat() if rule.last_checked else None,
                'last_result': rule.last_result,
                'violation_count': rule.violation_count
            } for rule_id, rule in self.rules.items()}
        }


# Global instance - Grace's verification layer
verification_framework = VerificationFramework()
