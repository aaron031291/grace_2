"""
Grace-Centric Test Bundles
Curated test suites per Grace capability

Test bundles for:
- Self-healing flows
- Governance decisions  
- Multi-model routing
- Layer 1 boot
- Chaos smoke tests
"""

import logging
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TestBundle:
    """Test bundle for a Grace capability"""
    bundle_name: str
    description: str
    
    # Test files
    test_files: List[str] = field(default_factory=list)
    test_command: str = ""
    
    # Requirements
    requires_setup: bool = False
    setup_command: Optional[str] = None
    
    # Execution
    timeout_seconds: int = 300
    max_retries: int = 1
    
    # Validation
    min_pass_rate: float = 1.0  # 100% by default
    critical: bool = False  # Must pass for deployment


@dataclass
class TestResult:
    """Result of running a test bundle"""
    bundle_name: str
    passed: bool
    
    # Execution details
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    
    # Output
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    
    # Failures
    failures: List[str] = field(default_factory=list)


class GraceTestRegistry:
    """Registry of Grace-specific test bundles"""
    
    def __init__(self):
        self.bundles: Dict[str, TestBundle] = {}
        self._register_builtin_bundles()
    
    def _register_builtin_bundles(self):
        """Register built-in Grace test bundles"""
        
        # Layer 1 Boot Tests
        self.bundles["layer1_boot"] = TestBundle(
            bundle_name="layer1_boot",
            description="Layer 1 boot orchestration and initialization",
            test_files=[
                "tests/test_boot_orchestrator.py",
                "tests/test_control_plane.py",
                "tests/test_kernel_loading.py"
            ],
            test_command="pytest tests/test_boot_orchestrator.py tests/test_control_plane.py -v",
            timeout_seconds=120,
            critical=True
        )
        
        # Self-Healing Flow Tests
        self.bundles["self_healing_flows"] = TestBundle(
            bundle_name="self_healing_flows",
            description="Self-healing trigger system and playbook execution",
            test_files=[
                "tests/test_trigger_system.py",
                "tests/test_playbook_engine.py",
                "tests/test_auto_remediation.py"
            ],
            test_command="pytest tests/test_trigger_system.py tests/test_playbook_engine.py -v",
            timeout_seconds=180,
            critical=True
        )
        
        # Governance Decision Tests
        self.bundles["governance_decisions"] = TestBundle(
            bundle_name="governance_decisions",
            description="Governance policy enforcement and approval workflows",
            test_files=[
                "tests/test_governance_engine.py",
                "tests/test_policy_enforcement.py",
                "tests/test_approval_workflows.py"
            ],
            test_command="pytest tests/test_governance_engine.py -v",
            timeout_seconds=120,
            critical=True
        )
        
        # Multi-Model Routing Tests
        self.bundles["multi_model_routing"] = TestBundle(
            bundle_name="multi_model_routing",
            description="OSS model selection, routing, and failover",
            test_files=[
                "tests/test_model_routing.py",
                "tests/test_model_failover.py",
                "tests/test_model_health.py"
            ],
            test_command="pytest tests/test_model_routing.py -v",
            timeout_seconds=300,
            critical=False
        )
        
        # Chaos Smoke Tests
        self.bundles["chaos_smoke"] = TestBundle(
            bundle_name="chaos_smoke",
            description="Quick chaos engineering smoke tests for Layer 1 changes",
            test_files=[
                "tests/chaos/test_chaos_smoke.py"
            ],
            test_command="pytest tests/chaos/test_chaos_smoke.py -v --timeout=60",
            timeout_seconds=120,
            critical=True
        )
        
        # Trigger System Tests
        self.bundles["trigger_system"] = TestBundle(
            bundle_name="trigger_system",
            description="Trigger mesh and event propagation",
            test_files=[
                "tests/test_trigger_mesh.py",
                "tests/test_event_propagation.py"
            ],
            test_command="pytest tests/test_trigger_mesh.py -v",
            timeout_seconds=90,
            critical=False
        )
        
        # Integration Tests
        self.bundles["integration"] = TestBundle(
            bundle_name="integration",
            description="End-to-end integration tests",
            test_files=[
                "tests/e2e/test_integrated_orchestration_e2e.py"
            ],
            test_command="pytest tests/e2e/ -v",
            timeout_seconds=600,
            critical=False
        )
        
        # Cognition Loop Tests
        self.bundles["cognition_loops"] = TestBundle(
            bundle_name="cognition_loops",
            description="Cognitive loop execution and meta-learning",
            test_files=[
                "tests/test_cognition_loop.py",
                "tests/test_meta_loop.py"
            ],
            test_command="pytest tests/test_cognition_loop.py -v",
            timeout_seconds=200,
            critical=False
        )
        
        # Policy Enforcement Tests
        self.bundles["policy_enforcement"] = TestBundle(
            bundle_name="policy_enforcement",
            description="Constitutional principle and policy enforcement",
            test_files=[
                "tests/test_constitutional_engine.py",
                "tests/test_policy_enforcement.py"
            ],
            test_command="pytest tests/test_constitutional_engine.py -v",
            timeout_seconds=90,
            critical=True
        )
        
        # Model Failover Tests
        self.bundles["model_failover"] = TestBundle(
            bundle_name="model_failover",
            description="OSS model health monitoring and automatic failover",
            test_files=[
                "tests/test_model_health.py",
                "tests/test_model_failover.py"
            ],
            test_command="pytest tests/test_model_health.py tests/test_model_failover.py -v",
            timeout_seconds=180,
            critical=False
        )
        
        logger.info(f"[TEST REGISTRY] Registered {len(self.bundles)} test bundles")
    
    def get_bundle(self, bundle_name: str) -> Optional[TestBundle]:
        """Get a test bundle by name"""
        return self.bundles.get(bundle_name)
    
    def get_critical_bundles(self) -> List[TestBundle]:
        """Get all critical test bundles"""
        return [b for b in self.bundles.values() if b.critical]
    
    async def run_bundle(self, bundle_name: str) -> TestResult:
        """Run a test bundle"""
        
        bundle = self.bundles.get(bundle_name)
        if not bundle:
            return TestResult(
                bundle_name=bundle_name,
                passed=False,
                failures=[f"Bundle '{bundle_name}' not found"]
            )
        
        logger.info(f"[TEST BUNDLE] Running {bundle_name}: {bundle.description}")
        
        # Setup if needed
        if bundle.requires_setup and bundle.setup_command:
            logger.info(f"[TEST BUNDLE] Running setup: {bundle.setup_command}")
            try:
                subprocess.run(bundle.setup_command, shell=True, check=True, timeout=60)
            except Exception as e:
                logger.error(f"[TEST BUNDLE] Setup failed: {e}")
                return TestResult(
                    bundle_name=bundle_name,
                    passed=False,
                    failures=[f"Setup failed: {e}"]
                )
        
        # Run tests
        import time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                bundle.test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=bundle.timeout_seconds
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Parse output (simplified - in production, use pytest's JSON output)
            passed = result.returncode == 0
            
            test_result = TestResult(
                bundle_name=bundle_name,
                passed=passed,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=duration_ms
            )
            
            # Parse test counts from output
            if "passed" in result.stdout:
                # Try to extract test counts
                import re
                match = re.search(r'(\d+) passed', result.stdout)
                if match:
                    test_result.tests_passed = int(match.group(1))
                    test_result.tests_run = test_result.tests_passed
            
            if not passed:
                test_result.failures.append(f"Tests failed with exit code {result.returncode}")
            
            logger.info(f"[TEST BUNDLE] {bundle_name} {'PASSED' if passed else 'FAILED'} in {duration_ms}ms")
            
            return test_result
        
        except subprocess.TimeoutExpired:
            logger.error(f"[TEST BUNDLE] {bundle_name} timed out after {bundle.timeout_seconds}s")
            return TestResult(
                bundle_name=bundle_name,
                passed=False,
                failures=[f"Timeout after {bundle.timeout_seconds}s"],
                duration_ms=bundle.timeout_seconds * 1000
            )
        
        except Exception as e:
            logger.error(f"[TEST BUNDLE] {bundle_name} error: {e}")
            return TestResult(
                bundle_name=bundle_name,
                passed=False,
                failures=[str(e)]
            )
    
    async def run_bundles(self, bundle_names: List[str]) -> Dict[str, TestResult]:
        """Run multiple test bundles"""
        
        results = {}
        
        for bundle_name in bundle_names:
            result = await self.run_bundle(bundle_name)
            results[bundle_name] = result
        
        return results
    
    def list_bundles(self) -> List[str]:
        """List all available test bundles"""
        return list(self.bundles.keys())


# Global test registry
_grace_test_registry: Optional[GraceTestRegistry] = None


def get_grace_test_registry() -> GraceTestRegistry:
    """Get or create the global Grace test registry"""
    global _grace_test_registry
    
    if _grace_test_registry is None:
        _grace_test_registry = GraceTestRegistry()
    
    return _grace_test_registry
