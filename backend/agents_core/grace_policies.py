"""
Grace Domain Policies & Constitutional Principles
Pillar 2 Enhancement: Domain-specific governance rules

Defines:
- Constitutional principles (what's good for Grace)
- Domain-specific policies
- Layer 3 intent mapping
- Model performance thresholds
- Test suite requirements
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ConstitutionalPrinciple(str, Enum):
    """Core constitutional principles for Grace"""
    PRESERVE_LAYER1_STABILITY = "preserve_layer1_stability"
    PROTECT_GOVERNANCE_DECISIONS = "protect_governance_decisions"
    KEEP_MODELS_VERIFIABLE = "keep_models_verifiable"
    PRESERVE_MODEL_COMPLIANCE = "preserve_model_compliance"
    OPTIMIZE_WITH_CLARITY = "optimize_with_clarity"
    NEVER_SACRIFICE_SAFETY = "never_sacrifice_safety"
    MAINTAIN_AUDIT_TRAIL = "maintain_audit_trail"
    RESPECT_TRUST_SCORES = "respect_trust_scores"


@dataclass
class DomainPolicy:
    """Policy for a specific Grace domain"""
    domain_name: str
    description: str
    
    # Approval requirements
    requires_governance_approval: bool = True
    min_autonomy_tier: int = 2  # 1=safe, 2=internal, 3=sensitive
    
    # Test requirements
    required_test_suites: List[str] = field(default_factory=list)
    requires_chaos_test: bool = False
    requires_integration_test: bool = True
    
    # Performance thresholds
    max_latency_ms: Optional[int] = None
    min_trust_score: float = 0.7
    max_error_rate: float = 0.05
    
    # Constitutional constraints
    principles: List[ConstitutionalPrinciple] = field(default_factory=list)
    
    # Layer 3 intent mapping
    layer3_intents: List[str] = field(default_factory=list)


@dataclass
class ModelFingerprint:
    """Metadata fingerprint for an OSS model"""
    model_name: str
    model_type: str  # llama, mistral, phi, etc.
    
    # Strengths & weaknesses
    strengths: List[str] = field(default_factory=list)  # code_gen, reasoning, long_form, etc.
    weaknesses: List[str] = field(default_factory=list)
    
    # Performance characteristics
    typical_latency_ms: int = 2000
    context_window: int = 4096
    output_quality: str = "medium"  # low, medium, high
    
    # Trust & compliance
    trust_score: float = 0.8
    compliance_flags: List[str] = field(default_factory=list)  # gdpr_compliant, open_license, etc.
    hallucination_rate: str = "low"  # low, medium, high
    bias_risk: str = "low"
    
    # Validation requirements
    requires_hallucination_test: bool = False
    requires_bias_check: bool = False
    requires_accuracy_validation: bool = True
    
    # Usage recommendations
    recommended_for: List[str] = field(default_factory=list)
    not_recommended_for: List[str] = field(default_factory=list)


class GracePolicyEngine:
    """
    Grace-specific policy engine
    
    Provides:
    - Constitutional principles enforcement
    - Domain-specific policies
    - Model fingerprints
    - Layer 3 intent mapping
    - Test suite selection
    """
    
    def __init__(self):
        self.principles: Dict[str, str] = {}
        self.domain_policies: Dict[str, DomainPolicy] = {}
        self.model_fingerprints: Dict[str, ModelFingerprint] = {}
        
        # Initialize
        self._load_constitutional_principles()
        self._load_domain_policies()
        self._load_model_fingerprints()
    
    def _load_constitutional_principles(self):
        """Load Grace's constitutional principles"""
        
        self.principles = {
            ConstitutionalPrinciple.PRESERVE_LAYER1_STABILITY: (
                "Layer 1 (boot, core kernels, foundational adapters) must remain stable. "
                "Changes require chaos testing and explicit governance approval."
            ),
            ConstitutionalPrinciple.PROTECT_GOVERNANCE_DECISIONS: (
                "Governance policies and trust decisions are sacred. "
                "Changes require Tier 3 approval and full audit trail."
            ),
            ConstitutionalPrinciple.KEEP_MODELS_VERIFIABLE: (
                "All open-source models must remain verifiable with contracts, "
                "health checks, and performance baselines."
            ),
            ConstitutionalPrinciple.PRESERVE_MODEL_COMPLIANCE: (
                "Models must maintain compliance flags (GDPR, licensing, bias). "
                "Adapter changes require compliance re-verification."
            ),
            ConstitutionalPrinciple.OPTIMIZE_WITH_CLARITY: (
                "Efficiency optimizations are good, but never at the expense of clarity. "
                "All changes must maintain clear audit trails and rationale."
            ),
            ConstitutionalPrinciple.NEVER_SACRIFICE_SAFETY: (
                "Safety and trust come first. No change can bypass verification, "
                "hallucination checks, or governance approval when required."
            ),
            ConstitutionalPrinciple.MAINTAIN_AUDIT_TRAIL: (
                "Every change must be logged to immutable log with full 5W1H context. "
                "Future audits depend on complete history."
            ),
            ConstitutionalPrinciple.RESPECT_TRUST_SCORES: (
                "Trust scores reflect system confidence. Changes that degrade trust "
                "below thresholds must be rejected or escalated."
            )
        }
        
        logger.info(f"[GRACE POLICIES] Loaded {len(self.principles)} constitutional principles")
    
    def _load_domain_policies(self):
        """Load domain-specific policies"""
        
        # Layer 1 / Core Boot
        self.domain_policies["layer1"] = DomainPolicy(
            domain_name="layer1",
            description="Layer 1 core boot and orchestration",
            requires_governance_approval=True,
            min_autonomy_tier=3,
            required_test_suites=["layer1_boot", "chaos_smoke"],
            requires_chaos_test=True,
            requires_integration_test=True,
            max_latency_ms=1000,
            min_trust_score=0.9,
            principles=[
                ConstitutionalPrinciple.PRESERVE_LAYER1_STABILITY,
                ConstitutionalPrinciple.MAINTAIN_AUDIT_TRAIL
            ],
            layer3_intents=["system.boot", "system.recovery"]
        )
        
        # Self-Healing
        self.domain_policies["self_healing"] = DomainPolicy(
            domain_name="self_healing",
            description="Self-healing mechanisms and playbooks",
            requires_governance_approval=True,
            min_autonomy_tier=2,
            required_test_suites=["self_healing_flows", "trigger_system"],
            requires_chaos_test=True,
            max_latency_ms=5000,
            min_trust_score=0.8,
            principles=[
                ConstitutionalPrinciple.NEVER_SACRIFICE_SAFETY,
                ConstitutionalPrinciple.MAINTAIN_AUDIT_TRAIL
            ],
            layer3_intents=["heal.trigger", "heal.verify"]
        )
        
        # Governance
        self.domain_policies["governance"] = DomainPolicy(
            domain_name="governance",
            description="Governance policies and decision frameworks",
            requires_governance_approval=True,
            min_autonomy_tier=3,
            required_test_suites=["governance_decisions", "policy_enforcement"],
            requires_chaos_test=False,
            min_trust_score=0.95,
            max_error_rate=0.01,
            principles=[
                ConstitutionalPrinciple.PROTECT_GOVERNANCE_DECISIONS,
                ConstitutionalPrinciple.MAINTAIN_AUDIT_TRAIL
            ],
            layer3_intents=["govern.approve", "govern.audit"]
        )
        
        # Multi-Model Routing
        self.domain_policies["model_routing"] = DomainPolicy(
            domain_name="model_routing",
            description="OSS model selection and orchestration",
            requires_governance_approval=True,
            min_autonomy_tier=2,
            required_test_suites=["multi_model_routing", "model_failover"],
            requires_integration_test=True,
            max_latency_ms=3000,
            min_trust_score=0.75,
            principles=[
                ConstitutionalPrinciple.KEEP_MODELS_VERIFIABLE,
                ConstitutionalPrinciple.PRESERVE_MODEL_COMPLIANCE
            ],
            layer3_intents=["model.select", "model.route"]
        )
        
        # Cognition / Intelligence
        self.domain_policies["cognition"] = DomainPolicy(
            domain_name="cognition",
            description="Cognitive loops and intelligence systems",
            requires_governance_approval=False,
            min_autonomy_tier=2,
            required_test_suites=["cognition_loops"],
            max_latency_ms=10000,
            min_trust_score=0.7,
            principles=[
                ConstitutionalPrinciple.OPTIMIZE_WITH_CLARITY,
                ConstitutionalPrinciple.RESPECT_TRUST_SCORES
            ]
        )
        
        logger.info(f"[GRACE POLICIES] Loaded {len(self.domain_policies)} domain policies")
    
    def _load_model_fingerprints(self):
        """Load fingerprints for all 15 OSS models"""
        
        # 1. Llama 3.2 3B - Primary workhorse
        self.model_fingerprints["llama3.2:3b"] = ModelFingerprint(
            model_name="llama3.2:3b",
            model_type="llama",
            strengths=["code_generation", "reasoning", "balanced_performance"],
            weaknesses=["context_limited"],
            typical_latency_ms=2000,
            context_window=4096,
            output_quality="high",
            trust_score=0.9,
            compliance_flags=["open_license", "llama_license"],
            hallucination_rate="low",
            bias_risk="low",
            requires_hallucination_test=False,
            requires_bias_check=False,
            recommended_for=["code_generation", "general_tasks", "reasoning"],
            not_recommended_for=["very_long_documents"]
        )
        
        # 2. Mistral 7B - Balanced
        self.model_fingerprints["mistral:7b"] = ModelFingerprint(
            model_name="mistral:7b",
            model_type="mistral",
            strengths=["reasoning", "instruction_following", "long_form"],
            weaknesses=["slower_than_phi"],
            typical_latency_ms=3000,
            context_window=8192,
            output_quality="high",
            trust_score=0.85,
            compliance_flags=["apache2_license", "open_license"],
            hallucination_rate="low",
            bias_risk="medium",
            requires_hallucination_test=True,  # Long-form output
            requires_bias_check=True,
            recommended_for=["long_form_text", "reasoning", "complex_tasks"],
            not_recommended_for=["latency_critical"]
        )
        
        # 3. Phi-3 Medium - Efficiency
        self.model_fingerprints["phi3:medium"] = ModelFingerprint(
            model_name="phi3:medium",
            model_type="phi",
            strengths=["speed", "efficiency", "low_resource"],
            weaknesses=["context_limited", "quality_tradeoff"],
            typical_latency_ms=1500,
            context_window=4096,
            output_quality="medium",
            trust_score=0.8,
            compliance_flags=["mit_license", "open_license"],
            hallucination_rate="medium",
            bias_risk="low",
            requires_hallucination_test=True,
            recommended_for=["fast_responses", "low_resource", "simple_tasks"],
            not_recommended_for=["complex_reasoning", "long_context"]
        )
        
        # 4. Qwen 2.5 Coder - Code specialist
        self.model_fingerprints["qwen2.5-coder:7b"] = ModelFingerprint(
            model_name="qwen2.5-coder:7b",
            model_type="qwen",
            strengths=["code_generation", "code_understanding", "debugging"],
            weaknesses=["not_for_general_text"],
            typical_latency_ms=2500,
            context_window=32768,
            output_quality="high",
            trust_score=0.9,
            compliance_flags=["qwen_license", "open_license"],
            hallucination_rate="low",
            bias_risk="low",
            requires_accuracy_validation=True,
            recommended_for=["code_generation", "debugging", "refactoring"],
            not_recommended_for=["general_conversation", "creative_writing"]
        )
        
        # 5. Gemma 2 9B - Google's offering
        self.model_fingerprints["gemma2:9b"] = ModelFingerprint(
            model_name="gemma2:9b",
            model_type="gemma",
            strengths=["reasoning", "safety", "instruction_following"],
            weaknesses=["slower", "resource_intensive"],
            typical_latency_ms=4000,
            context_window=8192,
            output_quality="high",
            trust_score=0.85,
            compliance_flags=["gemma_license", "open_license"],
            hallucination_rate="low",
            bias_risk="low",
            requires_bias_check=True,
            recommended_for=["reasoning", "safety_critical", "instruction_following"],
            not_recommended_for=["latency_critical", "low_resource"]
        )
        
        # Add remaining 10 models with simplified fingerprints
        for model_name, model_type, strengths in [
            ("codellama:7b", "codellama", ["code_generation"]),
            ("deepseek-coder:6.7b", "deepseek", ["code_generation", "efficiency"]),
            ("starcoder2:7b", "starcoder", ["code_generation", "multilingual"]),
            ("solar:10.7b", "solar", ["reasoning", "long_context"]),
            ("yi:6b", "yi", ["reasoning", "chinese_support"]),
            ("orca-mini:3b", "orca", ["speed", "efficiency"]),
            ("vicuna:7b", "vicuna", ["conversation", "instruction_following"]),
            ("openhermes:7b", "openhermes", ["reasoning", "balanced"]),
            ("wizardcoder:7b", "wizardcoder", ["code_generation"]),
            ("nous-hermes2:10.7b", "nous", ["reasoning", "long_form"])
        ]:
            self.model_fingerprints[model_name] = ModelFingerprint(
                model_name=model_name,
                model_type=model_type,
                strengths=strengths,
                typical_latency_ms=3000,
                trust_score=0.75,
                compliance_flags=["open_license"],
                recommended_for=strengths
            )
        
        logger.info(f"[GRACE POLICIES] Loaded {len(self.model_fingerprints)} model fingerprints")
    
    def get_policy_for_node(self, node) -> Optional[DomainPolicy]:
        """Get policy for a source graph node"""
        
        # Check by domain
        if node.grace_domain and node.grace_domain in self.domain_policies:
            return self.domain_policies[node.grace_domain]
        
        # Check by layer
        if node.grace_layer and node.grace_layer in self.domain_policies:
            return self.domain_policies[node.grace_layer]
        
        # Check by semantic type
        if node.grace_semantic_type == "oss_model_wrapper":
            return self.domain_policies.get("model_routing")
        
        return None
    
    def get_required_tests(self, nodes: List[Any]) -> List[str]:
        """Get required test suites for affected nodes"""
        
        test_suites = set()
        
        for node in nodes:
            policy = self.get_policy_for_node(node)
            if policy:
                test_suites.update(policy.required_test_suites)
                
                if policy.requires_chaos_test:
                    test_suites.add("chaos_smoke")
                
                if policy.requires_integration_test:
                    test_suites.add("integration")
        
        return list(test_suites)
    
    def get_model_validation_strategy(self, model_name: str) -> Dict[str, Any]:
        """Get validation strategy for a model based on fingerprint"""
        
        fingerprint = self.model_fingerprints.get(model_name)
        if not fingerprint:
            return {"tests": ["basic_inference"]}
        
        tests = []
        
        if fingerprint.requires_hallucination_test:
            tests.append("hallucination_detection")
        
        if fingerprint.requires_bias_check:
            tests.append("bias_evaluation")
        
        if fingerprint.requires_accuracy_validation:
            tests.append("accuracy_validation")
        
        return {
            "tests": tests or ["basic_inference"],
            "max_latency": fingerprint.typical_latency_ms * 1.5,  # 50% margin
            "min_trust": fingerprint.trust_score - 0.1
        }
    
    def check_constitutional_compliance(
        self,
        operation: str,
        affected_nodes: List[Any]
    ) -> Dict[str, Any]:
        """Check if operation complies with constitutional principles"""
        
        violations = []
        constraints = set()
        
        for node in affected_nodes:
            constraints.update(node.constitutional_constraints)
        
        # Check Layer 1 stability
        if ConstitutionalPrinciple.PRESERVE_LAYER1_STABILITY.value in constraints:
            if not any("chaos" in op or "test" in op for op in [operation]):
                violations.append(
                    f"Layer 1 change requires chaos testing per {ConstitutionalPrinciple.PRESERVE_LAYER1_STABILITY.value}"
                )
        
        # Check model verifiability
        if ConstitutionalPrinciple.KEEP_MODELS_VERIFIABLE.value in constraints:
            if "model" in operation.lower() and "verify" not in operation.lower():
                violations.append(
                    f"Model change requires verification per {ConstitutionalPrinciple.KEEP_MODELS_VERIFIABLE.value}"
                )
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "constraints": list(constraints)
        }


# Global policy engine
_grace_policy_engine: Optional[GracePolicyEngine] = None


def get_grace_policy_engine() -> GracePolicyEngine:
    """Get or create the global Grace policy engine"""
    global _grace_policy_engine
    
    if _grace_policy_engine is None:
        _grace_policy_engine = GracePolicyEngine()
    
    return _grace_policy_engine
