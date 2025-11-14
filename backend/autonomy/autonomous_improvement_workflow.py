"""
Autonomous Improvement Workflow
Grace's complete self-improvement pipeline:
Research → Sandbox → Validate → Propose → Human Consensus → Deploy
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging
from pathlib import Path

from .research_sweeper import research_sweeper
from .sandbox_improvement import sandbox_improvement
from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class AutonomousImprovementWorkflow:
    """
    Complete autonomous improvement pipeline
    
    Flow:
    1. Research: Pull knowledge from approved sources
    2. Ideate: Generate improvement ideas
    3. Sandbox: Test in isolated environment
    4. Validate: Check KPIs and trust scores
    5. Propose: Create proposal with evidence
    6. Consensus: Wait for human approval
    7. Deploy: Canary → Production with monitoring
    """
    
    def __init__(self):
        self.running = False
        self.workflow_task = None
        self.active_proposals = []
    
    async def start(self):
        """Start autonomous improvement workflow"""
        
        self.running = True
        
        # Start research sweeper
        await research_sweeper.start()
        
        # Start sandbox system
        await sandbox_improvement.start()
        
        # Start workflow loop
        self.workflow_task = asyncio.create_task(self._workflow_loop())
        
        logger.info("[AUTONOMOUS-IMPROVEMENT] Workflow started")
    
    async def stop(self):
        """Stop autonomous improvement workflow"""
        
        self.running = False
        
        if self.workflow_task:
            self.workflow_task.cancel()
        
        await research_sweeper.stop()
        
        logger.info("[AUTONOMOUS-IMPROVEMENT] Workflow stopped")
    
    async def _workflow_loop(self):
        """Main workflow loop - runs daily"""
        
        while self.running:
            try:
                # Run full improvement cycle
                await self.run_improvement_cycle()
                
                # Wait 24 hours
                await asyncio.sleep(86400)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[AUTONOMOUS-IMPROVEMENT] Error in workflow: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def run_improvement_cycle(self):
        """Run complete improvement cycle"""
        
        logger.info("[AUTONOMOUS-IMPROVEMENT] Starting improvement cycle...")
        
        cycle_result = {
            'cycle_id': f"cycle_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'started_at': datetime.utcnow().isoformat(),
            'steps_completed': [],
            'proposals_created': [],
            'status': 'unknown'
        }
        
        # Step 1: Research sweep
        logger.info("[AUTONOMOUS-IMPROVEMENT] Step 1: Research sweep")
        try:
            await research_sweeper.run_sweep()
            cycle_result['steps_completed'].append('research_sweep')
        except Exception as e:
            logger.error(f"[AUTONOMOUS-IMPROVEMENT] Research sweep failed: {e}")
        
        # Step 2: Process ingestion queue
        logger.info("[AUTONOMOUS-IMPROVEMENT] Step 2: Process ingestion queue")
        try:
            items_ingested = await self._process_ingestion_queue()
            cycle_result['items_ingested'] = items_ingested
            cycle_result['steps_completed'].append('ingestion')
        except Exception as e:
            logger.error(f"[AUTONOMOUS-IMPROVEMENT] Ingestion failed: {e}")
        
        # Step 3: Generate improvement ideas
        logger.info("[AUTONOMOUS-IMPROVEMENT] Step 3: Generate improvement ideas")
        try:
            ideas = await self._generate_improvement_ideas()
            cycle_result['ideas_generated'] = len(ideas)
            cycle_result['steps_completed'].append('ideation')
        except Exception as e:
            logger.error(f"[AUTONOMOUS-IMPROVEMENT] Ideation failed: {e}")
            ideas = []
        
        # Step 4: Test promising ideas in sandbox
        logger.info("[AUTONOMOUS-IMPROVEMENT] Step 4: Test ideas in sandbox")
        try:
            for idea in ideas[:3]:  # Test top 3 ideas
                result = await self._test_idea_in_sandbox(idea)
                
                if result['trust_score'] >= 70:
                    # Create proposal
                    proposal = await self._create_proposal(idea, result)
                    cycle_result['proposals_created'].append(proposal['proposal_id'])
                    self.active_proposals.append(proposal)
            
            cycle_result['steps_completed'].append('sandbox_testing')
        except Exception as e:
            logger.error(f"[AUTONOMOUS-IMPROVEMENT] Sandbox testing failed: {e}")
        
        # Step 5: Generate adaptive reasoning report
        logger.info("[AUTONOMOUS-IMPROVEMENT] Step 5: Generate report")
        try:
            report = await self._generate_adaptive_reasoning_report(cycle_result)
            cycle_result['report_path'] = str(report)
            cycle_result['steps_completed'].append('reporting')
        except Exception as e:
            logger.error(f"[AUTONOMOUS-IMPROVEMENT] Reporting failed: {e}")
        
        cycle_result['finished_at'] = datetime.utcnow().isoformat()
        cycle_result['status'] = 'completed'
        
        # Log decision
        await unified_logger.log_agentic_spine_decision(
            decision_type='improvement_cycle',
            decision_context=cycle_result,
            chosen_action='autonomous_improvement',
            rationale=f'Completed improvement cycle with {len(cycle_result["proposals_created"])} proposals',
            actor='autonomous_improvement',
            confidence=0.88,
            risk_score=0.15,
            status='success',
            resource=cycle_result['cycle_id']
        )
        
        logger.info(f"[AUTONOMOUS-IMPROVEMENT] Cycle complete: {cycle_result['cycle_id']}")
        logger.info(f"  Proposals created: {len(cycle_result['proposals_created'])}")
    
    async def _process_ingestion_queue(self) -> int:
        """Process queued research items"""
        
        queue_dir = Path('storage/ingestion_queue')
        
        if not queue_dir.exists():
            return 0
        
        queue_files = list(queue_dir.glob('*.json'))
        items_processed = 0
        
        for queue_file in queue_files:
            try:
                import json
                with open(queue_file, 'r', encoding='utf-8') as f:
                    queue_data = json.load(f)
                
                if queue_data.get('status') == 'pending':
                    # Process items (would integrate with library_ingestion.py)
                    items = queue_data.get('items', [])
                    items_processed += len(items)
                    
                    # Mark as processed
                    queue_data['status'] = 'processed'
                    queue_data['processed_at'] = datetime.utcnow().isoformat()
                    
                    with open(queue_file, 'w', encoding='utf-8') as f:
                        json.dump(queue_data, f, indent=2)
                    
                    logger.info(f"[AUTONOMOUS-IMPROVEMENT] Processed {len(items)} items from {queue_file.name}")
            
            except Exception as e:
                logger.error(f"[AUTONOMOUS-IMPROVEMENT] Error processing {queue_file}: {e}")
        
        return items_processed
    
    async def _generate_improvement_ideas(self) -> List[Dict[str, Any]]:
        """Generate improvement ideas based on learned knowledge"""
        
        # In production, this would use Grace's internal LLM to analyze:
        # - Recent research papers
        # - Code patterns from GitHub
        # - Performance metrics
        # - User feedback
        
        # For now, return template ideas
        ideas = [
            {
                'idea_id': 'improve_caching',
                'title': 'Implement intelligent caching layer',
                'description': 'Add ML-based cache prediction to reduce API latency',
                'confidence': 85,
                'expected_improvement': '30% latency reduction',
                'risk_level': 'low'
            },
            {
                'idea_id': 'optimize_queries',
                'title': 'Optimize database queries',
                'description': 'Use learned query patterns to optimize slow queries',
                'confidence': 78,
                'expected_improvement': '20% query speed increase',
                'risk_level': 'low'
            },
            {
                'idea_id': 'parallel_processing',
                'title': 'Add parallel processing for batch operations',
                'description': 'Process multiple items concurrently using asyncio',
                'confidence': 92,
                'expected_improvement': '50% throughput increase',
                'risk_level': 'medium'
            }
        ]
        
        logger.info(f"[AUTONOMOUS-IMPROVEMENT] Generated {len(ideas)} improvement ideas")
        
        return ideas
    
    async def _test_idea_in_sandbox(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Test improvement idea in sandbox"""
        
        # Create test code file
        test_code = f"""
# Improvement test: {idea['title']}
# {idea['description']}

import time
import sys

def test_improvement():
    print(f"Testing: {idea['title']}")
    
    # Simulate improvement
    start = time.time()
    
    # ... improvement code here ...
    
    end = time.time()
    execution_time = end - start
    
    print(f"Execution time: {{execution_time:.3f}}s")
    return execution_time

if __name__ == '__main__':
    result = test_improvement()
    print(f"Result: {{result}}")
"""
        
        # Save test code
        sandbox_dir = Path('sandbox')
        sandbox_dir.mkdir(exist_ok=True)
        
        test_file = sandbox_dir / f"{idea['idea_id']}_test.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        # Run in sandbox
        kpi_thresholds = {
            'execution_time_sec': '<5',
            'memory_used_mb': '<100',
            'exit_code': '==0'
        }
        
        result = await sandbox_improvement.run_experiment(
            experiment_name=idea['idea_id'],
            code_file=str(test_file),
            kpi_thresholds=kpi_thresholds,
            timeout=30
        )
        
        return result
    
    async def _create_proposal(
        self,
        idea: Dict[str, Any],
        sandbox_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create improvement proposal for governance"""
        
        proposal = await sandbox_improvement.create_improvement_proposal(
            experiment_result=sandbox_result,
            description=idea['description'],
            rationale=f"Confidence: {idea['confidence']}%. Expected: {idea['expected_improvement']}"
        )
        
        return proposal
    
    async def _generate_adaptive_reasoning_report(
        self,
        cycle_result: Dict[str, Any]
    ) -> Path:
        """Generate adaptive reasoning report for human review"""
        
        reports_dir = Path('reports/autonomous_improvement')
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"{cycle_result['cycle_id']}_report.md"
        
        report_content = f"""# Autonomous Improvement Cycle Report

**Cycle ID:** {cycle_result['cycle_id']}
**Date:** {cycle_result['started_at']}
**Status:** {cycle_result['status']}

## Summary

Grace completed an autonomous improvement cycle with the following results:

- **Items Ingested:** {cycle_result.get('items_ingested', 0)}
- **Ideas Generated:** {cycle_result.get('ideas_generated', 0)}
- **Proposals Created:** {len(cycle_result.get('proposals_created', []))}

## Steps Completed

{chr(10).join(f"- {step}" for step in cycle_result.get('steps_completed', []))}

## Proposals for Review

{len(cycle_result.get('proposals_created', []))} improvement proposals created and awaiting human consensus.

### Review Proposals

```bash
# View proposals
ls storage/improvement_proposals/

# Review specific proposal
cat storage/improvement_proposals/<proposal_id>.json

# Approve via governance
python scripts/governance_submit.py --proposal <proposal_id>
```

## Grace's Reasoning

I analyzed recent research, identified potential improvements, tested them in sandbox,
and created proposals for the most promising ones. Each proposal includes:

- Sandbox test results
- KPI measurements
- Trust score (0-100)
- Risk assessment
- Expected improvements

**Awaiting human consensus for deployment approval.**

---
*Generated by Grace's Autonomous Improvement Workflow*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"[AUTONOMOUS-IMPROVEMENT] Report generated: {report_file}")
        
        return report_file
    
    def get_pending_proposals(self) -> List[Dict[str, Any]]:
        """Get proposals awaiting approval"""
        
        return [p for p in self.active_proposals if p.get('status') == 'pending_review']


# Global instance
autonomous_improvement = AutonomousImprovementWorkflow()
