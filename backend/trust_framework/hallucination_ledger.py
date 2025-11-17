"""
Hallucination Debt Ledger
Tracks every verified error to adjust model trust scores dynamically
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class ErrorSeverity(Enum):
    """Severity of hallucination"""
    MINOR = "minor"  # Small factual error
    MODERATE = "moderate"  # Significant error
    MAJOR = "major"  # Critical hallucination
    CRITICAL = "critical"  # Dangerous misinformation


@dataclass
class HallucinationEntry:
    """Single hallucination incident"""
    
    # Identity
    entry_id: str
    
    # Model info
    origin_model: str  # Which model hallucinated
    
    # Context
    context_window_used: int  # How full was context
    
    # Error details
    hallucinated_content: str  # What was wrong
    correct_content: str  # What should have been
    
    # Fields with defaults
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model_variant: str = ""  # Specific variant/size
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    severity: ErrorSeverity = ErrorSeverity.MODERATE
    error_type: str = ""  # factual, logical, citation, etc.
    
    # Guardrails
    guardrails_active: List[str] = field(default_factory=list)
    guardrails_bypassed: List[str] = field(default_factory=list)
    
    # Cleanup
    detected_by: str = ""  # Which system caught it
    cleanup_action: str = ""  # What was done
    fixed: bool = False
    
    # Impact
    affected_missions: List[str] = field(default_factory=list)
    user_impact: str = ""  # Description of impact
    
    # Learning
    root_cause: str = ""
    prevention_suggestion: str = ""
    retraining_priority: int = 5  # 1-10
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp,
            'model': {
                'origin_model': self.origin_model,
                'variant': self.model_variant
            },
            'context': {
                'window_used': self.context_window_used,
                'prompt_tokens': self.prompt_tokens,
                'completion_tokens': self.completion_tokens,
                'total_tokens': self.total_tokens
            },
            'error': {
                'hallucinated': self.hallucinated_content,
                'correct': self.correct_content,
                'severity': self.severity.value,
                'type': self.error_type
            },
            'guardrails': {
                'active': self.guardrails_active,
                'bypassed': self.guardrails_bypassed
            },
            'cleanup': {
                'detected_by': self.detected_by,
                'action': self.cleanup_action,
                'fixed': self.fixed
            },
            'impact': {
                'affected_missions': self.affected_missions,
                'user_impact': self.user_impact
            },
            'learning': {
                'root_cause': self.root_cause,
                'prevention': self.prevention_suggestion,
                'retraining_priority': self.retraining_priority
            }
        }


class HallucinationLedger:
    """
    Centralized ledger of all hallucinations
    
    Tracks errors to:
    - Adjust model trust scores dynamically
    - Prioritize retraining
    - Guide fine-tuning
    - Improve guardrails
    """
    
    def __init__(self, ledger_path: str = "databases/hallucination_ledger.json"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.entries: List[HallucinationEntry] = []
        self.model_stats: Dict[str, Dict] = {}
        
        self._load_ledger()
    
    def _load_ledger(self):
        """Load existing ledger from disk"""
        if self.ledger_path.exists():
            try:
                with open(self.ledger_path, 'r') as f:
                    data = json.load(f)
                    # Load entries (simplified for now)
                    self.model_stats = data.get('model_stats', {})
            except Exception as e:
                print(f"[LEDGER] Failed to load: {e}")
    
    def _save_ledger(self):
        """Save ledger to disk"""
        try:
            data = {
                'model_stats': self.model_stats,
                'total_entries': len(self.entries),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(self.ledger_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[LEDGER] Failed to save: {e}")
    
    def log_hallucination(self, entry: HallucinationEntry):
        """Log a new hallucination incident"""
        
        self.entries.append(entry)
        
        # Update model stats
        model = entry.origin_model
        if model not in self.model_stats:
            self.model_stats[model] = {
                'total_hallucinations': 0,
                'by_severity': {s.value: 0 for s in ErrorSeverity},
                'by_type': {},
                'avg_context_window': 0,
                'retraining_priority': 5.0,
                'trust_adjustment': 0.0
            }
        
        stats = self.model_stats[model]
        stats['total_hallucinations'] += 1
        stats['by_severity'][entry.severity.value] += 1
        
        if entry.error_type:
            if entry.error_type not in stats['by_type']:
                stats['by_type'][entry.error_type] = 0
            stats['by_type'][entry.error_type] += 1
        
        # Update trust adjustment
        severity_weights = {
            ErrorSeverity.MINOR: -0.01,
            ErrorSeverity.MODERATE: -0.05,
            ErrorSeverity.MAJOR: -0.10,
            ErrorSeverity.CRITICAL: -0.20
        }
        stats['trust_adjustment'] += severity_weights[entry.severity]
        
        # Update retraining priority
        total_errors = stats['total_hallucinations']
        critical_count = stats['by_severity'][ErrorSeverity.CRITICAL.value]
        major_count = stats['by_severity'][ErrorSeverity.MAJOR.value]
        
        stats['retraining_priority'] = min(10, 5 + (critical_count * 2) + major_count)
        
        self._save_ledger()
        
        print(f"[LEDGER] Logged hallucination for {model} (severity: {entry.severity.value})")
    
    def get_model_trust_adjustment(self, model: str) -> float:
        """Get trust score adjustment for a model"""
        if model in self.model_stats:
            return self.model_stats[model]['trust_adjustment']
        return 0.0
    
    def get_model_stats(self, model: str) -> Dict:
        """Get statistics for a model"""
        return self.model_stats.get(model, {})
    
    def get_retraining_priorities(self) -> List[tuple]:
        """Get models ordered by retraining priority"""
        priorities = [
            (model, stats['retraining_priority'])
            for model, stats in self.model_stats.items()
        ]
        return sorted(priorities, key=lambda x: x[1], reverse=True)
    
    def get_ledger_summary(self) -> Dict:
        """Get overall ledger summary"""
        total_errors = sum(stats['total_hallucinations'] for stats in self.model_stats.values())
        
        return {
            'total_entries': len(self.entries),
            'total_models_affected': len(self.model_stats),
            'total_hallucinations': total_errors,
            'models_needing_retraining': [
                model for model, stats in self.model_stats.items()
                if stats['retraining_priority'] >= 7
            ],
            'highest_risk_models': [
                model for model, stats in self.model_stats.items()
                if stats['trust_adjustment'] < -0.15
            ]
        }


# Global instance
hallucination_ledger = HallucinationLedger()
