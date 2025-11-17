"""
Autonomy Gates - Governance-Gated Coding Agent
Pillar 2: Governance + Safety Gates

Implements 3-tier autonomy system with intent routing and verification bundles.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from backend.execution.governance import governance_engine
from backend.execution.verification import verification_engine
from backend.execution.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class AutonomyTier(int, Enum):
    """Autonomy levels for coding agent"""
    TIER_1_SAFE = 1      # Lint, docs, tests - auto-approved
    TIER_2_INTERNAL = 2  # Internal refactors - governance check
    TIER_3_SENSITIVE = 3 # Model routing, security, config - explicit approval


@dataclass
class CodingIntent:
    """
    Signed intent for coding-agent tasks
    Required before any edit can proceed
    """
    intent_id: str
    task_description: str
    autonomy_tier: AutonomyTier
    
    # What will be modified
    target_files: List[str]
    operation: str  # refactor, add_feature, fix_bug, update_model
    
    # Authorization
    requested_by: str  # layer3, governance, human
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    
    # Context
    source_graph_context: Optional[Dict[str, Any]] = None
    model_adapters_affected: List[str] = field(default_factory=list)
    
    # Constraints
    requires_tests: bool = True
    requires_verification: bool = True
    max_files_changed: int = 10
    
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class VerificationBundle:
    """
    Complete verification results for a coding task
    Includes lint, tests, model metrics, trust scores
    """
    bundle_id: str
    intent_id: str
    
    # Code quality
    lint_passed: bool = False
    lint_errors: List[str] = field(default_factory=list)
    
    # Testing
    tests_passed: bool = False
    tests_run: int = 0
    tests_failed: int = 0
    test_output: str = ""
    
    # Model-specific verification
    model_metrics: Dict[str, Any] = field(default_factory=dict)
    contract_violations: List[str] = field(default_factory=list)
    
    # Trust & governance
    trust_score: float = 1.0
    governance_approved: bool = False
    
    # Clarity integration
    clarity_verified: bool = False
    clarity_score: float = 1.0
    
    # Immutable log
    immutable_log_id: Optional[str] = None
    
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AutonomyGatekeeper:
    """
    Gatekeeper for coding agent autonomy
    
    Enforces:
    - Intent-based routing through governance
    - 3-tier autonomy levels
    - Verification bundles for all changes
    """
    
    def __init__(self):
        self.pending_intents: Dict[str, CodingIntent] = {}
        self.approved_intents: Dict[str, CodingIntent] = {}
        self.verification_bundles: Dict[str, VerificationBundle] = {}
        
        # Statistics
        self.stats = {
            "total_intents": 0,
            "tier1_auto_approved": 0,
            "tier2_governed": 0,
            "tier3_explicit": 0,
            "rejected": 0
        }
    
    async def request_intent(
        self,
        task_description: str,
        target_files: List[str],
        operation: str,
        requested_by: str = "coding_agent",
        source_graph_context: Optional[Dict[str, Any]] = None
    ) -> CodingIntent:
        """
        Request an intent to perform a coding task
        
        Returns signed intent (may require approval)
        """
        
        # Determine autonomy tier
        autonomy_tier = self._determine_tier(operation, target_files, source_graph_context)
        
        # Create intent
        intent_id = f"intent_{len(self.pending_intents)}_{datetime.utcnow().timestamp()}"
        
        intent = CodingIntent(
            intent_id=intent_id,
            task_description=task_description,
            autonomy_tier=autonomy_tier,
            target_files=target_files,
            operation=operation,
            requested_by=requested_by,
            source_graph_context=source_graph_context
        )
        
        # Extract affected model adapters from context
        if source_graph_context:
            intent.model_adapters_affected = [
                adapter["name"] for adapter in source_graph_context.get("affected_model_adapters", [])
            ]
        
        self.pending_intents[intent_id] = intent
        self.stats["total_intents"] += 1
        
        # Route through appropriate approval process
        approved = await self._route_intent(intent)
        
        if approved:
            intent.approved = True
            intent.approved_at = datetime.utcnow().isoformat()
            self.approved_intents[intent_id] = intent
            logger.info(f"[AUTONOMY] Intent {intent_id} approved (Tier {autonomy_tier})")
        else:
            logger.warning(f"[AUTONOMY] Intent {intent_id} pending approval")
        
        return intent
    
    def _determine_tier(
        self,
        operation: str,
        target_files: List[str],
        context: Optional[Dict[str, Any]]
    ) -> AutonomyTier:
        """Determine autonomy tier based on operation and context"""
        
        # Tier 3: Sensitive operations
        sensitive_operations = ['update_model', 'change_security', 'modify_config', 'update_contract']
        if operation in sensitive_operations:
            return AutonomyTier.TIER_3_SENSITIVE
        
        # Tier 3: Model adapters affected
        if context and context.get("affected_model_adapters"):
            return AutonomyTier.TIER_3_SENSITIVE
        
        # Tier 3: Security/governance files
        sensitive_paths = ['security/', 'governance/', 'execution/governance', 'agents_core/']
        if any(any(sp in f for sp in sensitive_paths) for f in target_files):
            return AutonomyTier.TIER_3_SENSITIVE
        
        # Tier 2: Internal refactors, feature additions
        internal_operations = ['refactor', 'add_feature', 'optimize']
        if operation in internal_operations:
            return AutonomyTier.TIER_2_INTERNAL
        
        # Tier 1: Safe operations (lint, docs, tests)
        safe_operations = ['lint', 'format', 'add_docs', 'add_tests', 'fix_typo']
        if operation in safe_operations:
            return AutonomyTier.TIER_1_SAFE
        
        # Default to Tier 2
        return AutonomyTier.TIER_2_INTERNAL
    
    async def _route_intent(self, intent: CodingIntent) -> bool:
        """Route intent through appropriate approval process"""
        
        if intent.autonomy_tier == AutonomyTier.TIER_1_SAFE:
            # Auto-approve safe operations
            intent.approved_by = "auto_approved"
            self.stats["tier1_auto_approved"] += 1
            return True
        
        elif intent.autonomy_tier == AutonomyTier.TIER_2_INTERNAL:
            # Governance check
            self.stats["tier2_governed"] += 1
            
            governance_result = await governance_engine.check(
                actor=intent.requested_by,
                action=f"code.{intent.operation}",
                resource="codebase",
                payload={
                    "intent_id": intent.intent_id,
                    "files": intent.target_files,
                    "model_adapters": intent.model_adapters_affected
                }
            )
            
            if governance_result["decision"] == "allow":
                intent.approved_by = "governance"
                return True
            else:
                logger.warning(f"[AUTONOMY] Governance denied intent {intent.intent_id}: {governance_result.get('reason')}")
                return False
        
        elif intent.autonomy_tier == AutonomyTier.TIER_3_SENSITIVE:
            # Requires explicit human/Layer3 approval
            self.stats["tier3_explicit"] += 1
            
            logger.info(f"[AUTONOMY] Tier 3 intent {intent.intent_id} requires explicit approval")
            
            # Create approval request in governance system
            await governance_engine.request_approval(
                action=f"code.{intent.operation}",
                context={
                    "intent_id": intent.intent_id,
                    "description": intent.task_description,
                    "files": intent.target_files,
                    "model_adapters": intent.model_adapters_affected
                },
                auto_approve_low_risk=False
            )
            
            # Intent stays pending until explicitly approved
            return False
        
        return False
    
    async def approve_intent(self, intent_id: str, approved_by: str):
        """Explicitly approve a pending intent"""
        
        intent = self.pending_intents.get(intent_id)
        if not intent:
            raise ValueError(f"Intent {intent_id} not found")
        
        intent.approved = True
        intent.approved_by = approved_by
        intent.approved_at = datetime.utcnow().isoformat()
        
        self.approved_intents[intent_id] = intent
        
        logger.info(f"[AUTONOMY] Intent {intent_id} approved by {approved_by}")
    
    async def create_verification_bundle(
        self,
        intent_id: str,
        files_changed: List[str],
        test_command: Optional[str] = None
    ) -> VerificationBundle:
        """
        Create verification bundle for a coding task
        
        Runs:
        - Linting
        - Tests
        - Model-specific verification
        - Trust scoring
        - Clarity verification
        """
        
        intent = self.approved_intents.get(intent_id)
        if not intent:
            raise ValueError(f"Intent {intent_id} not approved or not found")
        
        bundle_id = f"bundle_{intent_id}"
        
        bundle = VerificationBundle(
            bundle_id=bundle_id,
            intent_id=intent_id
        )
        
        # 1. Run linting
        logger.info(f"[VERIFICATION] Running lint for {intent_id}")
        lint_result = await self._run_lint(files_changed)
        bundle.lint_passed = lint_result["passed"]
        bundle.lint_errors = lint_result.get("errors", [])
        
        # 2. Run tests
        if intent.requires_tests and test_command:
            logger.info(f"[VERIFICATION] Running tests for {intent_id}")
            test_result = await self._run_tests(test_command)
            bundle.tests_passed = test_result["passed"]
            bundle.tests_run = test_result["total"]
            bundle.tests_failed = test_result["failed"]
            bundle.test_output = test_result.get("output", "")
        
        # 3. Model-specific verification
        if intent.model_adapters_affected:
            logger.info(f"[VERIFICATION] Verifying model contracts for {intent_id}")
            model_result = await self._verify_models(intent.model_adapters_affected)
            bundle.model_metrics = model_result["metrics"]
            bundle.contract_violations = model_result["violations"]
        
        # 4. Trust scoring
        trust_result = await verification_engine.calculate_trust(
            component="coding_agent",
            metrics={
                "lint_passed": bundle.lint_passed,
                "tests_passed": bundle.tests_passed,
                "contract_violations": len(bundle.contract_violations)
            }
        )
        bundle.trust_score = trust_result.get("trust_score", 0.5)
        
        # 5. Governance final check
        governance_result = await governance_engine.check(
            actor="coding_agent",
            action="code.commit",
            resource="codebase",
            payload={"verification_bundle": asdict(bundle)}
        )
        bundle.governance_approved = governance_result["decision"] == "allow"
        
        # 6. Log to immutable log
        log_id = await immutable_log.record(
            actor="autonomy_gatekeeper",
            action="verification_bundle",
            result=asdict(bundle),
            trust_score=bundle.trust_score
        )
        bundle.immutable_log_id = log_id
        
        # Store bundle
        self.verification_bundles[bundle_id] = bundle
        
        logger.info(f"[VERIFICATION] Bundle {bundle_id} created - Trust: {bundle.trust_score:.2f}")
        
        return bundle
    
    async def _run_lint(self, files: List[str]) -> Dict[str, Any]:
        """Run linting on files"""
        
        # Simplified linting - in production, use flake8, pylint, etc.
        errors = []
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    source = f.read()
                
                # Basic checks
                if len(source) > 10000:
                    errors.append(f"{file_path}: File too long (>10k chars)")
                
                if source.count('\n\n\n') > 5:
                    errors.append(f"{file_path}: Too many blank lines")
            
            except Exception as e:
                errors.append(f"{file_path}: {e}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }
    
    async def _run_tests(self, test_command: str) -> Dict[str, Any]:
        """Run test suite"""
        
        import subprocess
        
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "passed": result.returncode == 0,
                "total": 1,  # Simplified
                "failed": 0 if result.returncode == 0 else 1,
                "output": result.stdout
            }
        
        except Exception as e:
            return {
                "passed": False,
                "total": 1,
                "failed": 1,
                "output": str(e)
            }
    
    async def _verify_models(self, model_adapters: List[str]) -> Dict[str, Any]:
        """Verify model adapters after changes"""
        
        from .model_adapter_registry import get_model_registry
        
        registry = await get_model_registry()
        
        metrics = {}
        violations = []
        
        for adapter_name in model_adapters:
            # Find adapter
            adapter = None
            for aid, adp in registry.adapters.items():
                if adp.model_name == adapter_name:
                    adapter = adp
                    break
            
            if not adapter:
                violations.append(f"Adapter {adapter_name} not found in registry")
                continue
            
            # Health check
            health = await registry.health_check(adapter.adapter_id)
            
            metrics[adapter_name] = {
                "healthy": health.is_healthy,
                "latency": health.avg_latency_ms,
                "error_rate": health.error_rate
            }
            
            if not health.is_healthy:
                violations.append(f"Adapter {adapter_name} unhealthy after changes")
        
        return {
            "metrics": metrics,
            "violations": violations
        }
    
    def get_intent_status(self, intent_id: str) -> Dict[str, Any]:
        """Get status of an intent"""
        
        intent = self.approved_intents.get(intent_id) or self.pending_intents.get(intent_id)
        if not intent:
            return {"error": "Intent not found"}
        
        return {
            "intent": asdict(intent),
            "status": "approved" if intent.approved else "pending"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gatekeeper statistics"""
        return self.stats.copy()


# Global gatekeeper instance
_autonomy_gatekeeper: Optional[AutonomyGatekeeper] = None


def get_autonomy_gatekeeper() -> AutonomyGatekeeper:
    """Get or create the global autonomy gatekeeper"""
    global _autonomy_gatekeeper
    
    if _autonomy_gatekeeper is None:
        _autonomy_gatekeeper = AutonomyGatekeeper()
    
    return _autonomy_gatekeeper
