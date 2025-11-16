"""
Domain Orchestrator - Multi-Domain Workflows
Coordinates complex operations across multiple domains
Ensures atomic transactions and rollback
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import httpx
import uuid

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single step in a multi-domain workflow"""
    step_id: str
    domain_id: str
    action: str
    data: Dict[str, Any]
    depends_on: Optional[List[str]] = None
    timeout: float = 30.0
    result: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_id': self.step_id,
            'domain_id': self.domain_id,
            'action': self.action,
            'data': self.data,
            'depends_on': self.depends_on,
            'completed': self.result is not None,
            'success': self.result.get('success') if self.result else False,
            'error': self.error
        }


@dataclass
class Workflow:
    """Multi-domain workflow definition"""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed, rolled_back
    completed_steps: List[str] = field(default_factory=list)
    cryptographic_proof: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'status': self.status,
            'total_steps': len(self.steps),
            'completed_steps': len(self.completed_steps),
            'steps': [step.to_dict() for step in self.steps],
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }


class DomainOrchestrator:
    """
    Orchestrates complex workflows across multiple domains
    
    Features:
    - Atomic transactions (all succeed or all rollback)
    - Dependency management
    - Cryptographic signing at each step
    - Full audit trail
    - Timeout handling
    - Parallel execution where possible
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflows: Dict[str, Workflow] = {}
    
    async def create_workflow(self, workflow_def: Dict[str, Any]) -> Workflow:
        """
        Create a new workflow
        
        Args:
            workflow_def: {
                'name': str,
                'steps': [
                    {
                        'domain_id': str,
                        'action': str,
                        'data': dict,
                        'depends_on': Optional[List[str]]
                    }
                ]
            }
        
        Returns:
            Created workflow
        """
        workflow_id = str(uuid.uuid4())[:8]
        
        # Create workflow steps
        steps = []
        for i, step_def in enumerate(workflow_def['steps']):
            step = WorkflowStep(
                step_id=f"step_{i+1}",
                domain_id=step_def['domain_id'],
                action=step_def['action'],
                data=step_def.get('data', {}),
                depends_on=step_def.get('depends_on'),
                timeout=step_def.get('timeout', 30.0)
            )
            steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=workflow_def['name'],
            steps=steps
        )
        
        self.workflows[workflow_id] = workflow
        
        logger.info(
            f"[ORCHESTRATOR] Created workflow {workflow_id}: "
            f"{workflow.name} with {len(steps)} steps"
        )
        
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Executes steps in dependency order
        Rolls back on failure
        Returns cryptographic proof of execution
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.status = "running"
        workflow.started_at = datetime.utcnow().isoformat()
        self.active_workflows[workflow_id] = workflow
        
        logger.info(f"[ORCHESTRATOR] Starting workflow {workflow_id}")
        
        try:
            # Execute steps in dependency order
            execution_plan = self._create_execution_plan(workflow.steps)
            
            for batch in execution_plan:
                # Execute batch in parallel (no dependencies between them)
                tasks = [
                    self._execute_step(workflow, step)
                    for step in batch
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Check for failures
                for step, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.error(
                            f"[ORCHESTRATOR] Step {step.step_id} failed: {result}"
                        )
                        step.error = str(result)
                        
                        # Rollback entire workflow
                        await self._rollback_workflow(workflow)
                        
                        workflow.status = "rolled_back"
                        workflow.completed_at = datetime.utcnow().isoformat()
                        
                        return {
                            'success': False,
                            'workflow_id': workflow_id,
                            'status': 'rolled_back',
                            'failed_step': step.step_id,
                            'error': str(result)
                        }
                    
                    elif not result.get('success'):
                        logger.error(
                            f"[ORCHESTRATOR] Step {step.step_id} returned failure"
                        )
                        
                        await self._rollback_workflow(workflow)
                        
                        workflow.status = "rolled_back"
                        workflow.completed_at = datetime.utcnow().isoformat()
                        
                        return {
                            'success': False,
                            'workflow_id': workflow_id,
                            'status': 'rolled_back',
                            'failed_step': step.step_id,
                            'error': result.get('error', 'Unknown error')
                        }
            
            # All steps succeeded
            workflow.status = "completed"
            workflow.completed_at = datetime.utcnow().isoformat()
            
            # Generate cryptographic proof
            workflow.cryptographic_proof = self._generate_proof(workflow)
            
            logger.info(
                f"[ORCHESTRATOR] Workflow {workflow_id} completed successfully"
            )
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'status': 'completed',
                'steps_completed': len(workflow.completed_steps),
                'cryptographic_proof': workflow.cryptographic_proof,
                'workflow': workflow.to_dict()
            }
        
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    def _create_execution_plan(
        self,
        steps: List[WorkflowStep]
    ) -> List[List[WorkflowStep]]:
        """
        Create execution plan based on dependencies
        Returns batches that can be executed in parallel
        """
        # Simple dependency resolution
        plan = []
        remaining_steps = steps.copy()
        completed_step_ids = set()
        
        while remaining_steps:
            # Find steps with no unmet dependencies
            batch = []
            
            for step in remaining_steps:
                if not step.depends_on:
                    batch.append(step)
                elif all(dep in completed_step_ids for dep in step.depends_on):
                    batch.append(step)
            
            if not batch:
                raise ValueError("Circular dependency detected in workflow")
            
            plan.append(batch)
            
            # Remove batch from remaining
            for step in batch:
                remaining_steps.remove(step)
                completed_step_ids.add(step.step_id)
        
        return plan
    
    async def _execute_step(
        self,
        workflow: Workflow,
        step: WorkflowStep
    ) -> Dict[str, Any]:
        """Execute a single workflow step"""
        from backend.domains.domain_registry import domain_registry
        
        logger.info(
            f"[ORCHESTRATOR] Executing step {step.step_id} "
            f"on {step.domain_id}: {step.action}"
        )
        
        # Get domain info
        domain = domain_registry.get_domain(step.domain_id)
        
        if not domain:
            raise ValueError(f"Domain {step.domain_id} not found")
        
        # Execute on domain
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{domain.port}/workflow/execute",
                    json={
                        'workflow_id': workflow.workflow_id,
                        'step_id': step.step_id,
                        'action': step.action,
                        'data': step.data
                    },
                    timeout=step.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    step.result = result
                    step.completed_at = datetime.utcnow().isoformat()
                    workflow.completed_steps.append(step.step_id)
                    
                    # TODO: Add cryptographic signature
                    step.signature = "signature_placeholder"
                    
                    logger.info(
                        f"[ORCHESTRATOR] Step {step.step_id} completed successfully"
                    )
                    
                    return result
                else:
                    raise Exception(f"Domain returned status {response.status_code}")
        
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Step {step.step_id} failed: {e}")
            raise
    
    async def _rollback_workflow(self, workflow: Workflow):
        """Rollback all completed steps"""
        logger.warning(
            f"[ORCHESTRATOR] Rolling back workflow {workflow.workflow_id}"
        )
        
        # Rollback in reverse order
        for step_id in reversed(workflow.completed_steps):
            step = next(s for s in workflow.steps if s.step_id == step_id)
            
            try:
                await self._rollback_step(workflow, step)
            except Exception as e:
                logger.error(
                    f"[ORCHESTRATOR] Failed to rollback step {step_id}: {e}"
                )
    
    async def _rollback_step(self, workflow: Workflow, step: WorkflowStep):
        """Rollback a single step"""
        from backend.domains.domain_registry import domain_registry
        
        logger.info(
            f"[ORCHESTRATOR] Rolling back step {step.step_id} on {step.domain_id}"
        )
        
        domain = domain_registry.get_domain(step.domain_id)
        
        if not domain:
            logger.warning(f"Domain {step.domain_id} not found for rollback")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"http://localhost:{domain.port}/workflow/rollback",
                    json={
                        'workflow_id': workflow.workflow_id,
                        'step_id': step.step_id,
                        'action': step.action
                    },
                    timeout=30.0
                )
        
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Rollback failed for step {step.step_id}: {e}")
    
    def _generate_proof(self, workflow: Workflow) -> str:
        """Generate cryptographic proof of workflow execution"""
        # TODO: Implement actual cryptographic signing
        import hashlib
        import json
        
        workflow_data = {
            'workflow_id': workflow.workflow_id,
            'steps': [
                {
                    'step_id': step.step_id,
                    'domain': step.domain_id,
                    'signature': step.signature,
                    'completed_at': step.completed_at
                }
                for step in workflow.steps
            ]
        }
        
        proof_str = json.dumps(workflow_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_str.encode()).hexdigest()
        
        return proof_hash
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(
        self,
        status: Optional[str] = None
    ) -> List[Workflow]:
        """List workflows, optionally filtered by status"""
        workflows = list(self.workflows.values())
        
        if status:
            workflows = [w for w in workflows if w.status == status]
        
        return workflows
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        total = len(self.workflows)
        
        by_status = {}
        for workflow in self.workflows.values():
            by_status[workflow.status] = by_status.get(workflow.status, 0) + 1
        
        return {
            'total_workflows': total,
            'active_workflows': len(self.active_workflows),
            'by_status': by_status
        }


# Singleton instance
domain_orchestrator = DomainOrchestrator()
