"""
Knowledge + Application Loop
Grace's complete learn-test-apply cycle with sandbox validation
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgeApplicationLoop:
    """
    Complete knowledge + application cycle:
    1. Learn from web/research (creative problem solving)
    2. Test in sandbox (validate knowledge)
    3. Apply if tests pass (real-world usage)
    4. Learn from results (feedback loop)
    """
    
    def __init__(self):
        self.cycles_completed = 0
        self.knowledge_applied_successfully = 0
        self.sandbox_failures_learned_from = 0
        self._initialized = False
    
    async def initialize(self):
        """Initialize the knowledge + application loop"""
        if self._initialized:
            return
        
        logger.info("[KNOWLEDGE-APP-LOOP] Initializing knowledge + application cycle")
        self._initialized = True
    
    async def learn_and_apply(
        self,
        problem: str,
        goal: str = None,
        max_attempts: int = 3,
        deep_ingest: bool = True
    ) -> Dict[str, Any]:
        """
        Complete cycle: Learn → Ingest Real Data → Test → Apply → Feedback
        
        Args:
            problem: Problem to solve
            goal: Desired outcome
            max_attempts: Max attempts before giving up
            deep_ingest: Whether to ingest real documentation/examples/datasets
        
        Returns:
            Complete cycle report with knowledge and application results
        """
        from backend.agents.creative_problem_solver import creative_problem_solver
        from backend.agents.autonomous_web_navigator import autonomous_web_navigator
        from backend.knowledge.knowledge_application_sandbox import knowledge_sandbox
        from backend.services.closed_loop_learning import closed_loop_learning
        
        cycle_report = {
            'problem': problem,
            'goal': goal or 'solve problem',
            'started_at': datetime.utcnow().isoformat(),
            'phases': {},
            'final_result': None,
            'knowledge_acquired': False,
            'real_data_ingested': False,
            'application_successful': False,
            'terms_discovered': [],
            'resources_downloaded': []
        }
        
        logger.info(f"[KNOWLEDGE-APP-LOOP] 🔄 Starting learn-test-apply cycle")
        logger.info(f"[KNOWLEDGE-APP-LOOP] Problem: {problem[:100]}...")
        
        attempt = 0
        solution_found = False
        
        while attempt < max_attempts and not solution_found:
            attempt += 1
            logger.info(f"[KNOWLEDGE-APP-LOOP] Attempt {attempt}/{max_attempts}")
            
            # PHASE 1: LEARN (Creative Problem Solving + Web Search)
            logger.info("[KNOWLEDGE-APP-LOOP] Phase 1: Learning...")
            
            try:
                # Try autonomous web search first
                web_result = await autonomous_web_navigator.auto_navigate(
                    user_query=problem,
                    grace_confidence=0.3,  # Low confidence = trigger search
                    knowledge_match=0.2
                )
                
                if web_result:
                    cycle_report['phases'][f'attempt_{attempt}_web_search'] = {
                        'searched': True,
                        'results_found': web_result.get('count', 0)
                    }
                    logger.info(f"[KNOWLEDGE-APP-LOOP] Found {web_result.get('count', 0)} web sources")
            
            except Exception as e:
                logger.warning(f"[KNOWLEDGE-APP-LOOP] Web search failed: {e}")
            
            # Creative problem solving (extracts terms, generates approaches)
            try:
                solution = await creative_problem_solver.solve_problem_creatively(
                    problem=problem,
                    context={'goal': goal} if goal else None,
                    test_in_sandbox=True  # Always test in sandbox
                )
                
                # DEEP INGEST: Use extracted terms to get REAL data
                if deep_ingest and solution.get('learned_terminology'):
                    logger.info("[KNOWLEDGE-APP-LOOP] 📥 Deep ingesting real data from discovered terms...")
                    
                    from backend.agents.real_data_ingestion import real_data_ingestion
                    
                    # Get all unknown/new terms
                    terms_to_ingest = solution['learned_terminology'].get('unknown_terms', [])
                    if not terms_to_ingest:
                        # Fallback to all terms if no unknown
                        terms_to_ingest = list(solution['learned_terminology'].get('all_terms', set()))[:10]
                    
                    if terms_to_ingest:
                        ingestion_result = await real_data_ingestion.ingest_from_terms(
                            terms=terms_to_ingest,
                            context=problem
                        )
                        
                        cycle_report['real_data_ingested'] = True
                        cycle_report['terms_discovered'] = terms_to_ingest
                        cycle_report['resources_downloaded'] = ingestion_result.get('total_ingested', 0)
                        cycle_report['phases'][f'attempt_{attempt}_data_ingestion'] = ingestion_result
                        
                        logger.info(f"[KNOWLEDGE-APP-LOOP] ✅ Ingested {ingestion_result.get('total_ingested', 0)} real resources")
                        logger.info(f"[KNOWLEDGE-APP-LOOP] - Docs: {len(ingestion_result.get('documentation_found', []))}")
                        logger.info(f"[KNOWLEDGE-APP-LOOP] - Code: {len(ingestion_result.get('code_examples_found', []))}")
                        logger.info(f"[KNOWLEDGE-APP-LOOP] - Datasets: {len(ingestion_result.get('datasets_found', []))}")
                        logger.info(f"[KNOWLEDGE-APP-LOOP] - Repos: {len(ingestion_result.get('repos_found', []))}")
                
                cycle_report['phases'][f'attempt_{attempt}_creative_solving'] = {
                    'approaches_generated': len(solution.get('alternatives', [])),
                    'terminology_extracted': len(solution.get('learned_terminology', {}).get('all_terms', set())),
                    'sandbox_tested': 'sandbox_testing' in solution
                }
                
                cycle_report['knowledge_acquired'] = True
                logger.info(f"[KNOWLEDGE-APP-LOOP] Generated {len(solution.get('alternatives', []))} approaches")
                
                # Check sandbox test results
                sandbox_result = solution.get('sandbox_testing')
                if sandbox_result and sandbox_result.get('passed'):
                    logger.info("[KNOWLEDGE-APP-LOOP] ✅ Sandbox test PASSED!")
                    
                    # PHASE 2: APPLY (Use the validated knowledge)
                    logger.info("[KNOWLEDGE-APP-LOOP] Phase 2: Applying validated solution...")
                    
                    application_result = {
                        'solution_approach': solution['recommendation']['primary_approach'],
                        'sandbox_validated': True,
                        'applied_at': datetime.utcnow().isoformat()
                    }
                    
                    cycle_report['phases'][f'attempt_{attempt}_application'] = application_result
                    cycle_report['application_successful'] = True
                    cycle_report['final_result'] = 'success'
                    
                    solution_found = True
                    self.knowledge_applied_successfully += 1
                    
                    # PHASE 3: FEEDBACK (Learn from success)
                    await closed_loop_learning.capture_outcome(
                        execution_id=f"knowledge-app-{datetime.utcnow().timestamp()}",
                        task_description=f"Learn and apply solution for: {problem}",
                        approach_taken="Knowledge + Application Loop with sandbox validation",
                        outcome_type="success",
                        outcome_narrative=f"Successfully solved '{problem}' through iterative learning and sandbox testing",
                        metrics={
                            'attempts': attempt,
                            'approaches_tried': len(solution.get('alternatives', [])),
                            'sandbox_passed': True
                        },
                        learning_points=[
                            f"Problem: {problem}",
                            f"Solution: {solution['recommendation']['primary_approach'].get('description', '')}",
                            "Sandbox validation passed",
                            "Knowledge successfully applied"
                        ]
                    )
                    
                else:
                    logger.warning(f"[KNOWLEDGE-APP-LOOP] ❌ Sandbox test failed on attempt {attempt}")
                    self.sandbox_failures_learned_from += 1
                    
                    # Record failure for learning
                    await creative_problem_solver.record_failure(
                        approach=solution['recommendation']['primary_approach'].get('name', 'unknown'),
                        problem=problem,
                        reason=sandbox_result.get('failure_reason', 'Sandbox test failed') if sandbox_result else 'No sandbox result'
                    )
                    
                    # Try alternative approach next iteration
                    if attempt < max_attempts:
                        logger.info("[KNOWLEDGE-APP-LOOP] Trying alternative approach...")
            
            except Exception as e:
                logger.error(f"[KNOWLEDGE-APP-LOOP] Attempt {attempt} failed: {e}")
                cycle_report['phases'][f'attempt_{attempt}_error'] = str(e)
        
        # Final reporting
        if solution_found:
            cycle_report['completed_at'] = datetime.utcnow().isoformat()
            cycle_report['total_attempts'] = attempt
            logger.info(f"[KNOWLEDGE-APP-LOOP] ✅ Cycle completed successfully in {attempt} attempts!")
        else:
            cycle_report['final_result'] = 'failed'
            cycle_report['completed_at'] = datetime.utcnow().isoformat()
            cycle_report['total_attempts'] = max_attempts
            logger.warning(f"[KNOWLEDGE-APP-LOOP] ❌ Failed after {max_attempts} attempts")
            
            # Capture failure for learning
            await closed_loop_learning.capture_outcome(
                execution_id=f"knowledge-app-fail-{datetime.utcnow().timestamp()}",
                task_description=f"Attempted to solve: {problem}",
                approach_taken="Knowledge + Application Loop",
                outcome_type="failure",
                outcome_narrative=f"Failed to solve '{problem}' after {max_attempts} attempts",
                metrics={'attempts': max_attempts, 'sandbox_failures': self.sandbox_failures_learned_from},
                learning_points=[f"Need different approach for: {problem}", "Consider human assistance"]
            )
        
        self.cycles_completed += 1
        return cycle_report
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get knowledge + application metrics"""
        return {
            'cycles_completed': self.cycles_completed,
            'successful_applications': self.knowledge_applied_successfully,
            'sandbox_failures_learned_from': self.sandbox_failures_learned_from,
            'success_rate': (self.knowledge_applied_successfully / self.cycles_completed * 100) 
                           if self.cycles_completed > 0 else 0.0,
            'initialized': self._initialized
        }


# Global instance
knowledge_application_loop = KnowledgeApplicationLoop()
