"""
Adaptive Guardrails - PRODUCTION
Dynamic trust thresholds, consensus depth, and alignment prompts based on mission risk
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

from .mission_manifest import MissionManifest, RiskLevel
from .hallucination_ledger import hallucination_ledger


class GuardrailLevel(Enum):
    """Guardrail enforcement levels"""
    MINIMAL = "minimal"  # Low risk, fast
    STANDARD = "standard"  # Medium risk
    STRICT = "strict"  # High risk
    MAXIMUM = "maximum"  # Critical risk


@dataclass
class GuardrailConfig:
    """Configuration for adaptive guardrails"""
    
    # Trust thresholds
    min_trust_score: float
    truth_threshold: float
    governance_threshold: float
    
    # Consensus requirements
    quorum_size: int
    require_unanimous: bool
    
    # Verification depth
    verification_layers: int  # How many verification steps
    require_citations: bool
    min_citation_coverage: float
    
    # Alignment
    alignment_prompt_level: str  # "basic", "standard", "strict", "maximum"
    
    # Context management (no defaults - must come before fields with defaults)
    max_context_tokens: int
    force_summarization_at: int
    
    # Fields with defaults
    system_prompt_additions: List[str] = field(default_factory=list)
    enable_htm_detection: bool = True
    anomaly_threshold: float = 0.7
    
    def to_dict(self) -> Dict:
        return {
            'trust_thresholds': {
                'min_trust_score': self.min_trust_score,
                'truth': self.truth_threshold,
                'governance': self.governance_threshold
            },
            'consensus': {
                'quorum_size': self.quorum_size,
                'require_unanimous': self.require_unanimous
            },
            'verification': {
                'layers': self.verification_layers,
                'require_citations': self.require_citations,
                'min_citation_coverage': self.min_citation_coverage
            },
            'alignment': {
                'level': self.alignment_prompt_level,
                'additions': self.system_prompt_additions
            },
            'context': {
                'max_tokens': self.max_context_tokens,
                'summarize_at': self.force_summarization_at
            },
            'monitoring': {
                'htm_enabled': self.enable_htm_detection,
                'anomaly_threshold': self.anomaly_threshold
            }
        }


class AdaptiveGuardrailSystem:
    """
    Production adaptive guardrails that adjust based on:
    - Mission risk level
    - Recent hallucination debt
    - Model health status
    - Historical performance
    """
    
    # Preset configurations for each risk level
    PRESET_CONFIGS = {
        RiskLevel.LOW: GuardrailConfig(
            min_trust_score=0.6,
            truth_threshold=0.5,
            governance_threshold=0.5,
            quorum_size=2,
            require_unanimous=False,
            verification_layers=1,
            require_citations=False,
            min_citation_coverage=0.3,
            alignment_prompt_level="basic",
            max_context_tokens=100_000,
            force_summarization_at=80_000,
            anomaly_threshold=0.8
        ),
        
        RiskLevel.MEDIUM: GuardrailConfig(
            min_trust_score=0.7,
            truth_threshold=0.6,
            governance_threshold=0.7,
            quorum_size=3,
            require_unanimous=False,
            verification_layers=2,
            require_citations=True,
            min_citation_coverage=0.5,
            alignment_prompt_level="standard",
            max_context_tokens=80_000,
            force_summarization_at=60_000,
            anomaly_threshold=0.7
        ),
        
        RiskLevel.HIGH: GuardrailConfig(
            min_trust_score=0.8,
            truth_threshold=0.75,
            governance_threshold=0.85,
            quorum_size=4,
            require_unanimous=False,
            verification_layers=3,
            require_citations=True,
            min_citation_coverage=0.7,
            alignment_prompt_level="strict",
            system_prompt_additions=[
                "Verify all facts against sources",
                "Cite evidence for all claims",
                "Flag any uncertainties explicitly"
            ],
            max_context_tokens=60_000,
            force_summarization_at=40_000,
            anomaly_threshold=0.6
        ),
        
        RiskLevel.CRITICAL: GuardrailConfig(
            min_trust_score=0.9,
            truth_threshold=0.85,
            governance_threshold=0.95,
            quorum_size=5,
            require_unanimous=True,
            verification_layers=4,
            require_citations=True,
            min_citation_coverage=0.9,
            alignment_prompt_level="maximum",
            system_prompt_additions=[
                "CRITICAL MISSION: Extreme accuracy required",
                "Triple-check all facts",
                "Provide sources for EVERY claim",
                "Escalate ANY uncertainty",
                "No assumptions permitted"
            ],
            max_context_tokens=40_000,
            force_summarization_at=30_000,
            anomaly_threshold=0.5
        )
    }
    
    def __init__(self, storage_path: str = "databases/guardrail_history"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Track adjustments over time
        self.adjustment_history: List[Dict] = []
        self.current_adjustments: Dict[str, float] = {}
        
        # Load history
        self._load_history()
    
    def _load_history(self):
        """Load adjustment history"""
        history_file = self.storage_path / "adjustments.json"
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.adjustment_history = data.get('history', [])
                    self.current_adjustments = data.get('current', {})
            except Exception as e:
                print(f"[GUARDRAILS] Failed to load history: {e}")
    
    def _save_history(self):
        """Save adjustment history"""
        history_file = self.storage_path / "adjustments.json"
        
        try:
            data = {
                'history': self.adjustment_history[-1000:],  # Keep last 1000
                'current': self.current_adjustments,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[GUARDRAILS] Failed to save history: {e}")
    
    def get_config_for_mission(
        self,
        manifest: MissionManifest,
        model_name: Optional[str] = None
    ) -> GuardrailConfig:
        """
        Get adaptive guardrail configuration for a mission
        
        Adjusts based on:
        - Mission risk level
        - Recent hallucination debt
        - Model-specific issues
        """
        
        # Start with preset for risk level
        base_config = self.PRESET_CONFIGS[manifest.risk_level]
        
        # Clone config for modification
        config = GuardrailConfig(
            min_trust_score=base_config.min_trust_score,
            truth_threshold=base_config.truth_threshold,
            governance_threshold=base_config.governance_threshold,
            quorum_size=base_config.quorum_size,
            require_unanimous=base_config.require_unanimous,
            verification_layers=base_config.verification_layers,
            require_citations=base_config.require_citations,
            min_citation_coverage=base_config.min_citation_coverage,
            alignment_prompt_level=base_config.alignment_prompt_level,
            system_prompt_additions=base_config.system_prompt_additions.copy(),
            max_context_tokens=base_config.max_context_tokens,
            force_summarization_at=base_config.force_summarization_at,
            enable_htm_detection=base_config.enable_htm_detection,
            anomaly_threshold=base_config.anomaly_threshold
        )
        
        # Adjust based on hallucination debt
        hallucination_adjustment = self._calculate_hallucination_adjustment(model_name)
        
        if hallucination_adjustment > 0:
            # Tighten guardrails
            config.min_trust_score = min(1.0, config.min_trust_score + hallucination_adjustment)
            config.truth_threshold = min(1.0, config.truth_threshold + hallucination_adjustment)
            config.quorum_size = min(5, config.quorum_size + 1)
            config.verification_layers = min(5, config.verification_layers + 1)
            config.anomaly_threshold = max(0.3, config.anomaly_threshold - hallucination_adjustment)
            
            # Add warning to system prompt
            config.system_prompt_additions.append(
                f"WARNING: This model has recent hallucination issues. Extra verification required."
            )
        
        # Adjust based on mission-specific factors
        if manifest.governance_required:
            config.governance_threshold = max(config.governance_threshold, 0.8)
        
        if manifest.verification_required:
            config.verification_layers = max(config.verification_layers, 2)
        
        # Log adjustment
        self._log_adjustment(manifest, model_name, hallucination_adjustment)
        
        return config
    
    def _calculate_hallucination_adjustment(self, model_name: Optional[str]) -> float:
        """
        Calculate trust threshold adjustment based on recent hallucinations
        
        Returns: Adjustment amount (0.0 to 0.2)
        """
        
        if not model_name:
            return 0.0
        
        # Get model's hallucination stats
        trust_adjustment = hallucination_ledger.get_model_trust_adjustment(model_name)
        
        # Convert to guardrail tightening
        # More negative trust = tighter guardrails
        if trust_adjustment < -0.15:
            return 0.2  # Maximum tightening
        elif trust_adjustment < -0.10:
            return 0.15
        elif trust_adjustment < -0.05:
            return 0.10
        elif trust_adjustment < -0.01:
            return 0.05
        else:
            return 0.0
    
    def _log_adjustment(
        self,
        manifest: MissionManifest,
        model_name: Optional[str],
        hallucination_adjustment: float
    ):
        """Log guardrail adjustment"""
        
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'mission_id': manifest.mission_id,
            'risk_level': manifest.risk_level.value,
            'model_name': model_name,
            'hallucination_adjustment': hallucination_adjustment
        }
        
        self.adjustment_history.append(entry)
        
        # Save periodically
        if len(self.adjustment_history) % 10 == 0:
            self._save_history()
    
    def get_alignment_prompt(self, config: GuardrailConfig) -> str:
        """
        Get alignment system prompt for configuration level
        """
        
        base_prompts = {
            "basic": """You are Grace, an AI assistant. Provide helpful, accurate responses.""",
            
            "standard": """You are Grace, an AI assistant focused on accuracy and truthfulness.
- Verify facts before stating them
- Cite sources when making claims
- Acknowledge uncertainty when appropriate
- Follow instructions precisely""",
            
            "strict": """You are Grace, an AI assistant operating under STRICT governance.
- VERIFY ALL FACTS against reliable sources
- CITE EVIDENCE for every significant claim
- FLAG ANY UNCERTAINTIES explicitly
- PRIORITIZE accuracy over completeness
- FOLLOW the mission constraints exactly
- ESCALATE if requirements conflict""",
            
            "maximum": """You are Grace, an AI assistant operating under MAXIMUM GOVERNANCE - CRITICAL MISSION.
- TRIPLE-CHECK all factual claims
- PROVIDE SOURCES for EVERY statement
- ESCALATE IMMEDIATELY if ANY uncertainty exists
- NO ASSUMPTIONS - only verified facts
- EXTREME accuracy required - errors are not acceptable
- FOLLOW all governance rules WITHOUT exception
- REQUEST HUMAN REVIEW for any edge cases"""
        }
        
        base = base_prompts.get(config.alignment_prompt_level, base_prompts["standard"])
        
        # Add custom additions
        if config.system_prompt_additions:
            additions = "\n\nADDITIONAL REQUIREMENTS:\n" + "\n".join(
                f"- {add}" for add in config.system_prompt_additions
            )
            base += additions
        
        return base
    
    def should_escalate(
        self,
        config: GuardrailConfig,
        trust_score: float,
        warnings: List[str]
    ) -> bool:
        """
        Determine if mission should escalate based on guardrails
        """
        
        # Below minimum trust threshold
        if trust_score < config.min_trust_score:
            return True
        
        # Too many warnings
        if len(warnings) > config.verification_layers:
            return True
        
        # Critical risk missions with any warnings
        if config.alignment_prompt_level == "maximum" and len(warnings) > 0:
            return True
        
        return False
    
    def get_stats(self) -> Dict:
        """Get guardrail statistics"""
        
        # Calculate adjustment frequency
        recent_adjustments = [
            a for a in self.adjustment_history
            if datetime.fromisoformat(a['timestamp']) > datetime.utcnow() - timedelta(days=7)
        ]
        
        total_adjustments = len(self.adjustment_history)
        recent_count = len(recent_adjustments)
        
        # Risk level distribution
        risk_distribution = {}
        for entry in recent_adjustments:
            risk = entry['risk_level']
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        return {
            'total_adjustments': total_adjustments,
            'recent_adjustments_7d': recent_count,
            'risk_level_distribution': risk_distribution,
            'models_with_adjustments': len(set(
                a['model_name'] for a in recent_adjustments if a.get('model_name')
            ))
        }


# Global guardrail system
adaptive_guardrails = AdaptiveGuardrailSystem()
