"""Integration Example - Cognition System in Grace Pipeline

Shows how QuorumEngine and GraceCognitionLinter integrate with
the full Grace processing pipeline.
"""

from typing import Dict, Any, List
from datetime import datetime

from .QuorumEngine import QuorumEngine
from .GraceCognitionLinter import GraceCognitionLinter
from .models import (
    DecisionTask, SpecialistProposal, DecisionStrategy, 
    RiskLevel, ViolationSeverity
)
from .GraceLoopOutput import GraceLoopOutput, OutputType

class CognitionPipeline:
    """
    Integrated cognition pipeline combining linting and consensus.
    
    Pipeline flow:
    1. Specialists generate proposals
    2. Lint each proposal
    3. Reach consensus via QuorumEngine
    4. Lint final decision
    5. Pass to governance
    """
    
    def __init__(self):
        self.quorum = QuorumEngine()
        self.linter = GraceCognitionLinter()
        self.execution_log: List[Dict[str, Any]] = []
    
    def process_decision(
        self,
        task_description: str,
        specialist_outputs: Dict[str, GraceLoopOutput],
        strategy: DecisionStrategy = DecisionStrategy.SOFTMAX_WEIGHTED,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        constraints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Process a decision through the full cognition pipeline.
        
        Args:
            task_description: What we're deciding
            specialist_outputs: Outputs from each specialist
            strategy: Consensus strategy to use
            risk_level: Risk level for this decision
            constraints: Governance constraints
            
        Returns:
            Pipeline result with decision and lint reports
        """
        task_id = f"task_{datetime.utcnow().timestamp()}"
        
        # Step 1: Lint all specialist outputs
        print(f"[PIPELINE] Linting {len(specialist_outputs)} specialist proposals...")
        lint_reports = {}
        valid_proposals = []
        
        for specialist_name, output in specialist_outputs.items():
            # Lint the output
            lint_report = self.linter.lint(output)
            lint_reports[specialist_name] = lint_report
            
            if lint_report.passed:
                # Create proposal for valid outputs
                proposal = SpecialistProposal(
                    specialist_name=specialist_name,
                    output=output,
                    trust_score=self.quorum.specialist_trust.get(specialist_name, 0.5),
                    track_record=self.quorum.get_specialist_track_record(specialist_name),
                    recency_weight=0.9
                )
                valid_proposals.append(proposal)
            elif lint_report.severity == ViolationSeverity.CRITICAL:
                # Critical violations block immediately
                print(f"[PIPELINE] ❌ CRITICAL violation in {specialist_name}, blocking")
                return {
                    'success': False,
                    'error': 'Critical violation in specialist output',
                    'specialist': specialist_name,
                    'lint_report': lint_report.to_dict()
                }
            elif lint_report.auto_remediable:
                # Try auto-remediation
                print(f"[PIPELINE] 🔧 Auto-remediating {specialist_name}...")
                self.linter.auto_remediate(lint_report)
                
                # Re-lint
                lint_report = self.linter.lint(output)
                if lint_report.passed:
                    proposal = SpecialistProposal(
                        specialist_name=specialist_name,
                        output=output,
                        trust_score=self.quorum.specialist_trust.get(specialist_name, 0.5),
                        track_record=self.quorum.get_specialist_track_record(specialist_name),
                        recency_weight=0.9
                    )
                    valid_proposals.append(proposal)
            else:
                # Non-critical violations - penalize but include
                print(f"[PIPELINE] [WARN]  {specialist_name} has violations, penalizing trust")
                proposal = SpecialistProposal(
                    specialist_name=specialist_name,
                    output=output,
                    trust_score=self.quorum.specialist_trust.get(specialist_name, 0.5) * 0.7,
                    track_record=self.quorum.get_specialist_track_record(specialist_name),
                    recency_weight=0.9
                )
                valid_proposals.append(proposal)
        
        if not valid_proposals:
            return {
                'success': False,
                'error': 'No valid proposals after linting',
                'lint_reports': {k: v.to_dict() for k, v in lint_reports.items()}
            }
        
        # Step 2: Create decision task
        print(f"[PIPELINE] Creating decision task with {len(valid_proposals)} proposals...")
        task = DecisionTask(
            task_id=task_id,
            description=task_description,
            context={'specialist_count': len(valid_proposals)},
            specialist_proposals=valid_proposals,
            constraints=constraints or [],
            risk_level=risk_level,
            strategy=strategy
        )
        
        # Step 3: Reach consensus
        print(f"[PIPELINE] Deliberating with strategy: {strategy.value}...")
        decision = self.quorum.deliberate(task)
        
        # Step 4: Lint final decision
        print("[PIPELINE] Linting final decision...")
        final_lint = self.linter.lint(decision.chosen_proposal)
        
        if not final_lint.passed:
            if final_lint.severity == ViolationSeverity.CRITICAL:
                return {
                    'success': False,
                    'error': 'Critical violation in final decision',
                    'decision': decision.to_dict(),
                    'final_lint': final_lint.to_dict()
                }
            elif final_lint.auto_remediable:
                print("[PIPELINE] 🔧 Auto-remediating final decision...")
                self.linter.auto_remediate(final_lint)
        
        # Step 5: Check if escalation needed
        requires_escalation = (
            decision.voting_summary.get('requires_escalation', False) or
            decision.chosen_proposal.requires_approval or
            not decision.governance_validated
        )
        
        # Log execution
        self.execution_log.append({
            'task_id': task_id,
            'timestamp': datetime.utcnow().isoformat(),
            'strategy': strategy.value,
            'risk_level': risk_level.value,
            'specialist_count': len(valid_proposals),
            'winner': decision.chosen_proposal.component,
            'confidence': decision.confidence,
            'requires_escalation': requires_escalation
        })
        
        print(f"[PIPELINE] ✅ Decision complete: {decision.chosen_proposal.component} won")
        
        return {
            'success': True,
            'task_id': task_id,
            'decision': decision.to_dict(),
            'lint_reports': {k: v.to_dict() for k, v in lint_reports.items()},
            'final_lint': final_lint.to_dict(),
            'requires_escalation': requires_escalation,
            'explanation': self.quorum.explain(decision)
        }
    
    def update_trust_from_outcome(self, task_id: str, outcome_success: bool):
        """Update specialist trust based on execution outcome"""
        # Find the task in execution log
        task_record = next(
            (t for t in self.execution_log if t['task_id'] == task_id),
            None
        )
        
        if task_record:
            specialist = task_record['winner']
            self.quorum.update_specialist_trust(specialist, outcome_success)
            print(f"[PIPELINE] Updated trust for {specialist}: success={outcome_success}")
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics"""
        if not self.execution_log:
            return {'error': 'No executions recorded'}
        
        total = len(self.execution_log)
        escalations = sum(1 for t in self.execution_log if t['requires_escalation'])
        
        # Strategy distribution
        strategy_counts = {}
        for task in self.execution_log:
            strategy = task['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # Winner distribution
        winner_counts = {}
        for task in self.execution_log:
            winner = task['winner']
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
        
        # Average confidence
        avg_confidence = sum(t['confidence'] for t in self.execution_log) / total
        
        return {
            'total_decisions': total,
            'escalation_rate': escalations / total,
            'strategy_distribution': strategy_counts,
            'winner_distribution': winner_counts,
            'average_confidence': avg_confidence,
            'specialist_trust_scores': self.quorum.specialist_trust
        }


# Example usage
if __name__ == '__main__':
    # Initialize pipeline
    pipeline = CognitionPipeline()
    
    # Simulate specialist outputs
    reflection_output = GraceLoopOutput(
        loop_id="reflection_001",
        component="reflection",
        output_type=OutputType.DECISION,
        result="deploy_model",
        confidence=0.92,
        constitutional_compliance=True
    )
    reflection_output.add_policy_tag('safety_policy', 'compliant')
    
    hunter_output = GraceLoopOutput(
        loop_id="hunter_001",
        component="hunter",
        output_type=OutputType.DECISION,
        result="hold_deployment",
        confidence=0.75,
        constitutional_compliance=True
    )
    hunter_output.add_policy_tag('safety_policy', 'requires_review', 'Anomaly detected')
    
    meta_output = GraceLoopOutput(
        loop_id="meta_001",
        component="meta",
        output_type=OutputType.DECISION,
        result="deploy_model",
        confidence=0.88,
        constitutional_compliance=True
    )
    
    # Process decision
    result = pipeline.process_decision(
        task_description="Should we deploy model v2.0?",
        specialist_outputs={
            'reflection': reflection_output,
            'hunter': hunter_output,
            'meta': meta_output
        },
        strategy=DecisionStrategy.SOFTMAX_WEIGHTED,
        risk_level=RiskLevel.HIGH,
        constraints=['safety_policy', 'reversibility']
    )
    
    print("\n=== DECISION RESULT ===")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Winner: {result['explanation']['winner']['component']}")
        print(f"Confidence: {result['explanation']['overall_confidence']:.2f}")
        print(f"Requires Escalation: {result['requires_escalation']}")
        print(f"\nRationale: {result['decision']['rationale']}")
    
    # Update trust based on outcome
    if result['success']:
        pipeline.update_trust_from_outcome(result['task_id'], outcome_success=True)
    
    # Get metrics
    metrics = pipeline.get_pipeline_metrics()
    print("\n=== PIPELINE METRICS ===")
    print(f"Total Decisions: {metrics['total_decisions']}")
    print(f"Escalation Rate: {metrics['escalation_rate']:.2%}")
    print(f"Average Confidence: {metrics['average_confidence']:.2f}")
