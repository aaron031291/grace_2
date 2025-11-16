"""
Uncertainty Reporting System - PRODUCTION
Calibrated confidence scores + what's needed to close the gap

Converts residual risk into actionable data requirements
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class UncertaintyType(Enum):
    """Types of uncertainty"""
    KNOWLEDGE_GAP = "knowledge_gap"  # Missing information
    CONFLICTING_SOURCES = "conflicting_sources"  # Sources disagree
    LOW_CONFIDENCE = "low_confidence"  # Model unsure
    STALE_DATA = "stale_data"  # Information outdated
    INSUFFICIENT_VERIFICATION = "insufficient_verification"  # Not enough validation
    AMBIGUOUS_INTENT = "ambiguous_intent"  # Unclear what's being asked


@dataclass
class UncertaintyGap:
    """Specific gap preventing higher confidence"""
    
    gap_type: UncertaintyType
    description: str
    
    # Impact
    current_confidence: float
    target_confidence: float
    confidence_gap: float
    
    # What's needed to close gap
    required_data: List[str] = field(default_factory=list)
    required_sources: List[str] = field(default_factory=list)
    required_expert: Optional[str] = None
    required_verification: List[str] = field(default_factory=list)
    
    # Priority
    priority: int = 5  # 1-10
    blocking: bool = False  # Blocks completion
    
    def to_dict(self) -> Dict:
        return {
            'type': self.gap_type.value,
            'description': self.description,
            'impact': {
                'current_confidence': self.current_confidence,
                'target_confidence': self.target_confidence,
                'gap': self.confidence_gap
            },
            'requirements': {
                'data': self.required_data,
                'sources': self.required_sources,
                'expert': self.required_expert,
                'verification': self.required_verification
            },
            'priority': self.priority,
            'blocking': self.blocking
        }


@dataclass
class UncertaintyReport:
    """
    Complete uncertainty report with calibrated confidence
    
    Example: "60% confident—need current sales figures, regulatory update,
    and Expert X interview to reach ≥90%"
    
    Turns residual risk into actionable requests
    """
    
    # Overall confidence
    confidence: float  # 0-1, calibrated
    confidence_calibrated: bool = True
    
    # Target
    target_confidence: float = 0.9  # What we're aiming for
    
    # Uncertainty breakdown
    gaps: List[UncertaintyGap] = field(default_factory=list)
    
    # Actionable next steps
    recommended_actions: List[str] = field(default_factory=list)
    can_proceed: bool = True
    
    # Metadata
    report_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Context
    mission_id: Optional[str] = None
    model_used: str = ""
    
    def add_gap(
        self,
        gap_type: UncertaintyType,
        description: str,
        required_data: List[str],
        impact_on_confidence: float = 0.1,
        blocking: bool = False
    ):
        """Add uncertainty gap"""
        
        gap = UncertaintyGap(
            gap_type=gap_type,
            description=description,
            current_confidence=self.confidence,
            target_confidence=min(1.0, self.confidence + impact_on_confidence),
            confidence_gap=impact_on_confidence,
            required_data=required_data,
            blocking=blocking
        )
        
        self.gaps.append(gap)
        
        # Update can_proceed flag
        if blocking:
            self.can_proceed = False
    
    def get_confidence_ceiling(self) -> float:
        """Calculate maximum achievable confidence with current data"""
        
        if not self.gaps:
            return self.confidence
        
        # Sum potential confidence gains
        potential_gain = sum(gap.confidence_gap for gap in self.gaps)
        
        return min(1.0, self.confidence + potential_gain)
    
    def get_blocking_gaps(self) -> List[UncertaintyGap]:
        """Get gaps that block proceeding"""
        return [gap for gap in self.gaps if gap.blocking]
    
    def get_all_requirements(self) -> Dict[str, List[str]]:
        """Get all requirements aggregated"""
        
        all_data = []
        all_sources = []
        all_experts = []
        all_verification = []
        
        for gap in self.gaps:
            all_data.extend(gap.required_data)
            all_sources.extend(gap.required_sources)
            if gap.required_expert:
                all_experts.append(gap.required_expert)
            all_verification.extend(gap.required_verification)
        
        return {
            'data': list(set(all_data)),
            'sources': list(set(all_sources)),
            'experts': list(set(all_experts)),
            'verification': list(set(all_verification))
        }
    
    def generate_summary(self) -> str:
        """Generate human-readable uncertainty summary"""
        
        if self.confidence >= self.target_confidence:
            return f"High confidence ({self.confidence:.0%}) - ready to proceed"
        
        requirements = self.get_all_requirements()
        
        summary_parts = [
            f"{self.confidence:.0%} confident"
        ]
        
        needs = []
        if requirements['data']:
            needs.append(f"{len(requirements['data'])} data points")
        if requirements['sources']:
            needs.append(f"{len(requirements['sources'])} source verifications")
        if requirements['experts']:
            needs.append(f"expert review from {', '.join(requirements['experts'])}")
        if requirements['verification']:
            needs.append(f"{len(requirements['verification'])} verification steps")
        
        if needs:
            summary_parts.append("need " + ", ".join(needs))
            summary_parts.append(f"to reach ≥{self.target_confidence:.0%}")
        
        return "—".join(summary_parts)
    
    def to_dict(self) -> Dict:
        return {
            'report_id': self.report_id,
            'confidence': {
                'current': self.confidence,
                'target': self.target_confidence,
                'calibrated': self.confidence_calibrated,
                'ceiling': self.get_confidence_ceiling()
            },
            'gaps': [gap.to_dict() for gap in self.gaps],
            'requirements': self.get_all_requirements(),
            'recommended_actions': self.recommended_actions,
            'can_proceed': self.can_proceed,
            'blocking_gaps': len(self.get_blocking_gaps()),
            'summary': self.generate_summary(),
            'timestamp': self.timestamp,
            'context': {
                'mission_id': self.mission_id,
                'model_used': self.model_used
            }
        }


class UncertaintyReportingSystem:
    """
    Production uncertainty reporting
    
    Agents output:
    - Calibrated confidence
    - Specific gaps
    - What's needed to close gaps
    - Actionable next steps
    """
    
    def __init__(self):
        # Statistics
        self.reports_generated = 0
        self.high_confidence_count = 0
        self.low_confidence_count = 0
        self.escalations = 0
        
        logger.info("[UNCERTAINTY] Reporting system initialized")
    
    def create_report(
        self,
        confidence: float,
        mission_id: Optional[str] = None,
        model_used: str = "",
        target_confidence: float = 0.9
    ) -> UncertaintyReport:
        """Create new uncertainty report"""
        
        self.reports_generated += 1
        
        if confidence >= 0.8:
            self.high_confidence_count += 1
        elif confidence < 0.6:
            self.low_confidence_count += 1
        
        report = UncertaintyReport(
            report_id=f"uncertainty_{datetime.utcnow().timestamp()}",
            confidence=confidence,
            target_confidence=target_confidence,
            mission_id=mission_id,
            model_used=model_used
        )
        
        # Auto-analyze common gaps
        self._auto_identify_gaps(report)
        
        return report
    
    def _auto_identify_gaps(self, report: UncertaintyReport):
        """Automatically identify likely uncertainty gaps"""
        
        # If confidence <60%, likely knowledge gap
        if report.confidence < 0.6:
            report.add_gap(
                gap_type=UncertaintyType.KNOWLEDGE_GAP,
                description="Insufficient information to provide high-confidence answer",
                required_data=[
                    "Additional source documents",
                    "Expert verification",
                    "Current data (not historical)"
                ],
                impact_on_confidence=0.2,
                blocking=True
            )
        
        # If confidence 60-80%, likely needs verification
        elif report.confidence < 0.8:
            report.add_gap(
                gap_type=UncertaintyType.INSUFFICIENT_VERIFICATION,
                description="Answer needs additional verification",
                required_data=[
                    "Cross-reference with authoritative source",
                    "Fact-checking validation"
                ],
                impact_on_confidence=0.15,
                blocking=False
            )
        
        # Generate recommended actions
        if report.gaps:
            all_reqs = report.get_all_requirements()
            
            if all_reqs['data']:
                report.recommended_actions.append(
                    f"Gather: {', '.join(all_reqs['data'][:3])}"
                )
            
            if all_reqs['sources']:
                report.recommended_actions.append(
                    "Verify against authoritative sources"
                )
            
            if all_reqs['experts']:
                report.recommended_actions.append(
                    f"Consult expert: {all_reqs['experts'][0]}"
                )
    
    def get_stats(self) -> Dict:
        """Get reporting statistics"""
        
        return {
            'reports_generated': self.reports_generated,
            'high_confidence': self.high_confidence_count,
            'low_confidence': self.low_confidence_count,
            'escalations': self.escalations
        }


# Global system
uncertainty_reporting = UncertaintyReportingSystem()
