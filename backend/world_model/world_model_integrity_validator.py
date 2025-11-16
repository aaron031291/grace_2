"""
World Model Integrity Validator

Validates that Grace's self-knowledge matches reality.

Process:
1. Query world model for known facts about critical systems
2. Run live system checks to verify those facts
3. Detect mismatches (fact says X, reality is Y)
4. Publish discrepancies as system artifacts
5. Trigger healing playbooks via Guardian
6. Update world model with healed state

This creates self-awareness: Grace knows when her understanding drifts from reality
and automatically corrects it.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class IntegrityCheck:
    """A fact to verify against reality"""
    fact_id: str
    category: str
    fact_statement: str
    check_type: str  # 'port_open', 'service_running', 'file_exists', 'endpoint_reachable'
    check_params: Dict[str, Any]
    expected_state: Any
    confidence: float


@dataclass
class IntegrityViolation:
    """A detected mismatch between fact and reality"""
    fact_id: str
    fact_statement: str
    expected: Any
    actual: Any
    severity: str  # 'low', 'medium', 'high', 'critical'
    auto_fixable: bool
    healing_playbook: Optional[str]
    detected_at: str


class WorldModelIntegrityValidator:
    """
    Validates world model facts against live system state
    
    Runs on schedule to ensure Grace's self-knowledge stays accurate
    """
    
    def __init__(self):
        self._initialized = False
        self._running = False
        self.checks_performed = 0
        self.violations_detected = 0
        self.violations_fixed = 0
        self.validation_interval_seconds = 300  # 5 minutes
    
    async def initialize(self):
        """Initialize integrity validator"""
        if self._initialized:
            return
        
        logger.info("[INTEGRITY-VALIDATOR] Initializing world model integrity validator")
        
        # Build fact checklist from world model
        await self._build_fact_checklist()
        
        self._initialized = True
        logger.info("[INTEGRITY-VALIDATOR] Validator ready")
    
    async def start_validation_loop(self):
        """Start continuous validation loop"""
        if self._running:
            return
        
        self._running = True
        logger.info("[INTEGRITY-VALIDATOR] Starting validation loop")
        
        while self._running:
            try:
                await self.validate_all_facts()
                await asyncio.sleep(self.validation_interval_seconds)
            except Exception as e:
                logger.error(f"[INTEGRITY-VALIDATOR] Validation error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop_validation_loop(self):
        """Stop validation loop"""
        self._running = False
        logger.info("[INTEGRITY-VALIDATOR] Validation loop stopped")
    
    async def _build_fact_checklist(self) -> List[IntegrityCheck]:
        """Build list of facts to check from world model"""
        checks = []
        
        # Critical system facts to verify
        critical_facts = [
            IntegrityCheck(
                fact_id="vector_store_reachable",
                category="system",
                fact_statement="Vector store is reachable",
                check_type="endpoint_reachable",
                check_params={"url": "http://localhost:8000/api/vectors/health"},
                expected_state=True,
                confidence=0.9
            ),
            IntegrityCheck(
                fact_id="backend_api_running",
                category="system",
                fact_statement="Backend API is running",
                check_type="endpoint_reachable",
                check_params={"url": "http://localhost:8000/health"},
                expected_state=True,
                confidence=0.95
            ),
            IntegrityCheck(
                fact_id="world_model_accessible",
                category="system",
                fact_statement="World model is accessible",
                check_type="endpoint_reachable",
                check_params={"url": "http://localhost:8000/world-model/stats"},
                expected_state=True,
                confidence=0.9
            )
        ]
        
        # Store in instance
        self.fact_checklist = critical_facts
        
        return checks
    
    async def validate_all_facts(self) -> Dict[str, Any]:
        """
        Validate all facts in checklist
        
        Returns:
            {
                "checks_performed": int,
                "violations_detected": int,
                "violations": List[IntegrityViolation],
                "timestamp": str
            }
        """
        logger.info("[INTEGRITY-VALIDATOR] Starting fact validation")
        
        violations = []
        
        for check in self.fact_checklist:
            self.checks_performed += 1
            
            # Perform check
            actual_state = await self._perform_check(check)
            
            # Compare with expected
            if actual_state != check.expected_state:
                violation = IntegrityViolation(
                    fact_id=check.fact_id,
                    fact_statement=check.fact_statement,
                    expected=check.expected_state,
                    actual=actual_state,
                    severity=self._assess_severity(check, actual_state),
                    auto_fixable=self._is_auto_fixable(check),
                    healing_playbook=self._get_healing_playbook(check),
                    detected_at=datetime.utcnow().isoformat()
                )
                
                violations.append(violation)
                self.violations_detected += 1
                
                # Publish violation
                await self._publish_violation(violation)
                
                # Attempt auto-fix
                if violation.auto_fixable:
                    await self._attempt_auto_fix(violation)
        
        logger.info(
            f"[INTEGRITY-VALIDATOR] Validation complete: "
            f"{self.checks_performed} checks, {len(violations)} violations"
        )
        
        return {
            "checks_performed": len(self.fact_checklist),
            "violations_detected": len(violations),
            "violations": [
                {
                    "fact_id": v.fact_id,
                    "fact": v.fact_statement,
                    "expected": v.expected,
                    "actual": v.actual,
                    "severity": v.severity,
                    "auto_fixable": v.auto_fixable
                }
                for v in violations
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _perform_check(self, check: IntegrityCheck) -> Any:
        """Perform a single integrity check"""
        try:
            if check.check_type == "endpoint_reachable":
               return await self._check_endpoint_reachable(check.check_params["url"])
            
            elif check.check_type == "port_open":
                return await self._check_port_open(
                    check.check_params["host"],
                    check.check_params["port"]
                )
            
            elif check.check_type == "service_running":
                return await self._check_service_running(check.check_params["service_id"])
            
            elif check.check_type == "file_exists":
                return await self._check_file_exists(check.check_params["path"])
            
            else:
                logger.warning(f"Unknown check type: {check.check_type}")
                return None
                
        except Exception as e:
            logger.error(f"[INTEGRITY-VALIDATOR] Check failed: {check.fact_id} - {e}")
            return None
    
    async def _check_endpoint_reachable(self, url: str) -> bool:
        """Check if HTTP endpoint is reachable"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code < 500
        except:
            return False
    
    async def _check_port_open(self, host: str, port: int) -> bool:
        """Check if port is open"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=2.0
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
    
    async def _check_service_running(self, service_id: str) -> bool:
        """Check if service is registered and healthy"""
        try:
            from backend.infrastructure import service_discovery
            service = service_discovery.get_service(service_id)
            return service is not None and service.health_status == "healthy"
        except:
            return False
    
    async def _check_file_exists(self, path: str) -> bool:
        """Check if file exists"""
        from pathlib import Path
        return Path(path).exists()
    
    def _assess_severity(self, check: IntegrityCheck, actual_state: Any) -> str:
        """Assess severity of violation"""
        if check.category == "system" and check.check_type == "endpoint_reachable":
            return "high"  # System endpoints down = high severity
        elif check.confidence > 0.9:
            return "medium"  # High confidence facts = medium severity if wrong
        else:
            return "low"
    
    def _is_auto_fixable(self, check: IntegrityCheck) -> bool:
        """Determine if violation can be auto-fixed"""
        # Endpoint reachability issues often fixable by restart
        if check.check_type == "endpoint_reachable":
            return True
        # Service health issues fixable by restart/heal
        elif check.check_type == "service_running":
            return True
        else:
            return False
    
    def _get_healing_playbook(self, check: IntegrityCheck) -> Optional[str]:
        """Get healing playbook for this check type"""
        playbook_map = {
            "endpoint_reachable": "restart_service",
            "service_running": "restart_service",
            "port_open": "restart_port_assignment"
        }
        return playbook_map.get(check.check_type)
    
    async def _publish_violation(self, violation: IntegrityViolation):
        """Publish integrity violation to knowledge systems"""
        try:
            # Publish to domain event bus
            from backend.domains import domain_event_bus, DomainEvent
            
            await domain_event_bus.publish(DomainEvent(
                event_type="integrity.violation.detected",
                source_domain="core",
                timestamp=datetime.now().isoformat(),
                data={
                    "fact_id": violation.fact_id,
                    "fact_statement": violation.fact_statement,
                    "expected": str(violation.expected),
                    "actual": str(violation.actual),
                    "severity": violation.severity,
                    "auto_fixable": violation.auto_fixable,
                    "healing_playbook": violation.healing_playbook,
                    "detected_at": violation.detected_at
                }
            ))
            
            # Add to world model as system knowledge
            from backend.world_model import grace_world_model
            
            await grace_world_model.add_knowledge(
                category='system',
                content=f"Integrity issue detected: {violation.fact_statement}. Expected {violation.expected}, found {violation.actual}.",
                source='integrity_validator',
                confidence=0.9,
                tags=['integrity', 'self_heal', violation.severity],
                metadata={
                    "fact_id": violation.fact_id,
                    "severity": violation.severity,
                    "auto_fixable": violation.auto_fixable,
                    "healing_playbook": violation.healing_playbook
                }
            )
            
            logger.info(f"[INTEGRITY-VALIDATOR] Published violation: {violation.fact_id}")
            
        except Exception as e:
            logger.error(f"[INTEGRITY-VALIDATOR] Failed to publish violation: {e}")
    
    async def _attempt_auto_fix(self, violation: IntegrityViolation) -> bool:
        """Attempt to auto-fix violation using healing playbooks"""
        if not violation.auto_fixable or not violation.healing_playbook:
            return False
        
        logger.info(
            f"[INTEGRITY-VALIDATOR] Attempting auto-fix for {violation.fact_id} "
            f"using playbook: {violation.healing_playbook}"
        )
        
        try:
            # Trigger Guardian/healing system
            from backend.core.guardian import guardian_service
            
            fix_result = await guardian_service.execute_healing_action(
                playbook=violation.healing_playbook,
                context={
                    "fact_id": violation.fact_id,
                    "violation": violation.fact_statement,
                    "severity": violation.severity
                }
            )
            
            if fix_result.get("success"):
                # Publish successful repair
                await self._publish_repair_completed(violation, fix_result)
                self.violations_fixed += 1
                return True
            else:
                logger.warning(f"[INTEGRITY-VALIDATOR] Auto-fix failed: {fix_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"[INTEGRITY-VALIDATOR] Auto-fix error: {e}")
            return False
    
    async def _publish_repair_completed(
        self,
        violation: IntegrityViolation,
        fix_result: Dict[str, Any]
    ):
        """Publish successful repair back to world model"""
        try:
            from backend.world_model import grace_world_model, publish_incident_summary
            
            # Publish as incident resolution
            await publish_incident_summary(
                domain_id="core",
                incident_title=f"Integrity Violation: {violation.fact_id}",
                resolution_summary=f"Automatically fixed {violation.fact_statement}",
                root_cause=f"Expected {violation.expected}, found {violation.actual}",
                fix_applied=fix_result.get("action_taken", "Applied healing playbook"),
                confidence=1.0,
                priority=violation.severity,
                auto_remediated=True,
                healing_playbook=violation.healing_playbook
            )
            
            # Update world model with restored state
            await grace_world_model.add_knowledge(
                category='system',
                content=f"{violation.fact_statement} - Verified and restored.",
                source='integrity_validator',
                confidence=1.0,
                tags=['integrity', 'verified', 'healed'],
                metadata={
                    "fact_id": violation.fact_id,
                    "previously_violated": True,
                    "fix_applied": fix_result.get("action_taken"),
                    "restored_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"[INTEGRITY-VALIDATOR] Repair completed and logged: {violation.fact_id}")
            
        except Exception as e:
            logger.error(f"[INTEGRITY-VALIDATOR] Failed to publish repair: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics"""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "checks_performed": self.checks_performed,
            "violations_detected": self.violations_detected,
            "violations_fixed": self.violations_fixed,
            "fix_success_rate": (
                (self.violations_fixed / self.violations_detected)
                if self.violations_detected > 0
                else 1.0
            ),
            "validation_interval_seconds": self.validation_interval_seconds
        }
    
    async def validate_fact(self, fact_id: str) -> Dict[str, Any]:
        """Validate a specific fact"""
        # Find fact in checklist
        check = next((c for c in self.fact_checklist if c.fact_id == fact_id), None)
        
        if not check:
            return {"error": "fact_not_found", "fact_id": fact_id}
        
        actual_state = await self._perform_check(check)
        
        is_valid = actual_state == check.expected_state
        
        result = {
            "fact_id": fact_id,
            "fact": check.fact_statement,
            "expected": check.expected_state,
            "actual": actual_state,
            "valid": is_valid,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        if not is_valid:
            violation = IntegrityViolation(
                fact_id=fact_id,
                fact_statement=check.fact_statement,
                expected=check.expected_state,
                actual=actual_state,
                severity=self._assess_severity(check, actual_state),
                auto_fixable=self._is_auto_fixable(check),
                healing_playbook=self._get_healing_playbook(check),
                detected_at=datetime.utcnow().isoformat()
            )
            
            result["violation"] = violation
            await self._publish_violation(violation)
            
            if violation.auto_fixable:
                fixed = await self._attempt_auto_fix(violation)
                result["auto_fixed"] = fixed
        
        return result


# Global instance
world_model_integrity_validator = WorldModelIntegrityValidator()


# Convenience function
async def validate_system_integrity() -> Dict[str, Any]:
    """
    Run integrity validation check
    
    Returns validation report with any violations detected
    """
    return await world_model_integrity_validator.validate_all_facts()