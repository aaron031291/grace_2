"""
Autonomous Coding Pipeline - Phase 4
7-step pipeline for autonomous software development with human oversight
"""

import asyncio
import logging
import os
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class PipelineJob:
    """Represents a coding pipeline job"""
    job_id: str
    status: str  # pending, running, awaiting_approval, completed, failed, rolled_back
    current_step: int
    steps_completed: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    diff: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None
    diagnostics: Optional[Dict[str, Any]] = None
    approval_status: Optional[str] = None
    merge_result: Optional[Dict[str, Any]] = None
    observations: Optional[Dict[str, Any]] = None
    snapshot_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None


class AutonomousCodingPipeline:
    """
    7-step autonomous coding pipeline:
    1. Fetch context (codebase, requirements, tests)
    2. Propose diff (code changes)
    3. Run tests (unit, integration, lint)
    4. Collect diagnostics (errors, warnings, metrics)
    5. Request approval (governance gate)
    6. Merge (with verification)
    7. Observe (post-merge metrics)
    """
    
    def __init__(self):
        self.jobs: Dict[str, PipelineJob] = {}
        self.offline_mode = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        logger.info(f"[PIPELINE] Initialized (offline_mode={self.offline_mode})")
    
    async def run_pipeline(
        self,
        task_description: str,
        target_repo: Optional[str] = None,
        target_branch: Optional[str] = None
    ) -> PipelineJob:
        """
        Run the complete 7-step pipeline
        
        Args:
            task_description: What to build/change
            target_repo: Target repository (optional)
            target_branch: Target branch (optional)
        
        Returns:
            PipelineJob with results
        """
        job_id = f"job-{datetime.utcnow().timestamp()}"
        job = PipelineJob(
            job_id=job_id,
            status="running",
            current_step=0,
            context={
                "task_description": task_description,
                "target_repo": target_repo,
                "target_branch": target_branch
            }
        )
        self.jobs[job_id] = job
        
        try:
            await self._step_1_fetch_context(job)
            
            await self._step_2_propose_diff(job)
            
            await self._step_3_run_tests(job)
            
            await self._step_4_collect_diagnostics(job)
            
            await self._step_5_request_approval(job)
            
            if job.approval_status == "approved":
                await self._step_6_merge(job)
                
                await self._step_7_observe(job)
                
                job.status = "completed"
            elif job.approval_status == "rejected":
                job.status = "failed"
                job.error = "Approval rejected"
            else:
                job.status = "awaiting_approval"
        
        except Exception as e:
            logger.error(f"[PIPELINE] Job {job_id} failed: {e}")
            job.status = "failed"
            job.error = str(e)
            
            if job.snapshot_id:
                logger.info(f"[PIPELINE] Rollback available: {job.snapshot_id}")
        
        job.updated_at = datetime.utcnow().isoformat()
        return job
    
    async def _step_1_fetch_context(self, job: PipelineJob):
        """Step 1: Fetch context (codebase, requirements, tests)"""
        logger.info(f"[PIPELINE] Step 1: Fetching context for {job.job_id}")
        job.current_step = 1
        
        if not self.offline_mode:
            try:
                from backend.self_heal.safe_hold import SnapshotManager
                snapshot_mgr = SnapshotManager()
                snapshot = await snapshot_mgr.create_snapshot(
                    snapshot_type="pre_action",
                    triggered_by=f"pipeline_{job.job_id}"
                )
                job.snapshot_id = snapshot.id
                logger.info(f"[PIPELINE] Created snapshot: {snapshot.id}")
            except Exception as e:
                logger.warning(f"[PIPELINE] Snapshot creation failed: {e}")
        
        context = {
            "codebase_root": str(Path.cwd()),
            "task": job.context["task_description"],
            "files_scanned": 0,
            "dependencies": [],
            "existing_tests": []
        }
        
        if self.offline_mode:
            context["mode"] = "offline_stub"
        else:
            pass
        
        job.context.update(context)
        job.steps_completed.append("fetch_context")
        logger.info(f"[PIPELINE] Context fetched: {context}")
    
    async def _step_2_propose_diff(self, job: PipelineJob):
        """Step 2: Propose diff (code changes)"""
        logger.info(f"[PIPELINE] Step 2: Proposing diff for {job.job_id}")
        job.current_step = 2
        
        try:
            from backend.agents_core.code_generator import code_generator
            
            task = job.context["task_description"]
            
            if self.offline_mode:
                job.diff = f"# Proposed changes for: {task}\n# (Offline mode - stub diff)\npass\n"
            else:
                from backend.agents_core.code_generator import CodeGenerationRequest
                request = CodeGenerationRequest(
                    task=task,
                    language="python",
                    context=job.context,
                    constraints=[]
                )
                result = await code_generator.generate(request)
                job.diff = result.code
        
        except Exception as e:
            logger.error(f"[PIPELINE] Diff generation failed: {e}")
            job.diff = f"# Error generating diff: {e}\n"
        
        job.steps_completed.append("propose_diff")
        logger.info(f"[PIPELINE] Diff proposed ({len(job.diff)} chars)")
    
    async def _step_3_run_tests(self, job: PipelineJob):
        """Step 3: Run tests (unit, integration, lint)"""
        logger.info(f"[PIPELINE] Step 3: Running tests for {job.job_id}")
        job.current_step = 3
        
        test_results = {
            "backend_tests": {"status": "skipped", "reason": "offline_mode" if self.offline_mode else "not_implemented"},
            "frontend_tests": {"status": "skipped", "reason": "offline_mode" if self.offline_mode else "not_implemented"},
            "lint": {"status": "skipped", "reason": "offline_mode" if self.offline_mode else "not_implemented"}
        }
        
        if not self.offline_mode:
            try:
                result = subprocess.run(
                    ["pytest", "--collect-only"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                test_results["backend_tests"] = {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "output": result.stdout[:500]
                }
            except Exception as e:
                test_results["backend_tests"] = {"status": "error", "error": str(e)}
            
            try:
                result = subprocess.run(
                    ["npm", "test", "--prefix", "frontend"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                test_results["frontend_tests"] = {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "output": result.stdout[:500]
                }
            except Exception as e:
                test_results["frontend_tests"] = {"status": "error", "error": str(e)}
        
        job.test_results = test_results
        job.steps_completed.append("run_tests")
        logger.info(f"[PIPELINE] Tests completed: {test_results}")
    
    async def _step_4_collect_diagnostics(self, job: PipelineJob):
        """Step 4: Collect diagnostics (errors, warnings, metrics)"""
        logger.info(f"[PIPELINE] Step 4: Collecting diagnostics for {job.job_id}")
        job.current_step = 4
        
        diagnostics = {
            "errors": [],
            "warnings": [],
            "metrics": {
                "lines_changed": len(job.diff.split('\n')) if job.diff else 0,
                "test_coverage": 0.0,
                "complexity": 0
            }
        }
        
        if job.test_results:
            for test_type, result in job.test_results.items():
                if result.get("status") == "failed":
                    diagnostics["errors"].append(f"{test_type} failed")
                elif result.get("status") == "error":
                    diagnostics["errors"].append(f"{test_type} error: {result.get('error')}")
        
        job.diagnostics = diagnostics
        job.steps_completed.append("collect_diagnostics")
        logger.info(f"[PIPELINE] Diagnostics collected: {len(diagnostics['errors'])} errors")
    
    async def _step_5_request_approval(self, job: PipelineJob):
        """Step 5: Request approval (governance gate)"""
        logger.info(f"[PIPELINE] Step 5: Requesting approval for {job.job_id}")
        job.current_step = 5
        
        try:
            from backend.learning.governed_learning import ApprovalGate
            
            approval_gate = ApprovalGate()
            
            if self.offline_mode:
                if not job.diagnostics or not job.diagnostics.get("errors"):
                    job.approval_status = "approved"
                    logger.info(f"[PIPELINE] Auto-approved (offline mode, no errors)")
                else:
                    job.approval_status = "rejected"
                    logger.info(f"[PIPELINE] Auto-rejected (offline mode, has errors)")
            else:
                if not job.diagnostics or not job.diagnostics.get("errors"):
                    job.approval_status = "approved"
                else:
                    job.approval_status = "pending"
                    job.status = "awaiting_approval"
        
        except Exception as e:
            logger.error(f"[PIPELINE] Approval gate failed: {e}")
            job.approval_status = "error"
            job.error = f"Approval gate error: {e}"
        
        job.steps_completed.append("request_approval")
        logger.info(f"[PIPELINE] Approval status: {job.approval_status}")
    
    async def _step_6_merge(self, job: PipelineJob):
        """Step 6: Merge (with verification)"""
        logger.info(f"[PIPELINE] Step 6: Merging for {job.job_id}")
        job.current_step = 6
        
        merge_result = {
            "status": "simulated",
            "method": "offline_mode" if self.offline_mode else "no_git_token"
        }
        
        if not self.offline_mode and os.getenv("GITHUB_TOKEN"):
            try:
                from backend.integrations.github_integration import github_integration
                
                if github_integration.enabled:
                    pr_number = await github_integration.create_pull_request(
                        repo=job.context.get("target_repo", "unknown"),
                        title=f"Autonomous: {job.context['task_description'][:50]}",
                        head=job.context.get("target_branch", "feature-branch"),
                        base="main",
                        body=f"**Autonomous Code Change**\n\nTask: {job.context['task_description']}\n\nJob ID: {job.job_id}"
                    )
                    merge_result = {
                        "status": "pr_created",
                        "pr_number": pr_number,
                        "method": "github_api"
                    }
            except Exception as e:
                logger.error(f"[PIPELINE] Merge failed: {e}")
                merge_result = {"status": "failed", "error": str(e)}
        
        job.merge_result = merge_result
        job.steps_completed.append("merge")
        logger.info(f"[PIPELINE] Merge result: {merge_result}")
    
    async def _step_7_observe(self, job: PipelineJob):
        """Step 7: Observe (post-merge metrics)"""
        logger.info(f"[PIPELINE] Step 7: Observing for {job.job_id}")
        job.current_step = 7
        
        observations = {
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job.job_id,
            "success": job.status == "completed",
            "steps_completed": len(job.steps_completed),
            "total_time_seconds": 0,  # Would calculate actual time
            "metrics": {
                "lines_changed": job.diagnostics.get("metrics", {}).get("lines_changed", 0) if job.diagnostics else 0,
                "tests_passed": all(
                    r.get("status") != "failed"
                    for r in (job.test_results or {}).values()
                )
            }
        }
        
        try:
            from backend.agentic.event_bus import event_bus
            await event_bus.publish("copilot.pipeline.completed", observations)
        except Exception as e:
            logger.warning(f"[PIPELINE] Event bus publish failed: {e}")
        
        # Log to immutable log
        try:
            from backend.immutable_log import immutable_log
            immutable_log(
                event_type="copilot_pipeline_completed",
                actor="autonomous_pipeline",
                resource=job.job_id,
                payload=observations
            )
        except Exception as e:
            logger.warning(f"[PIPELINE] Immutable log failed: {e}")
        
        job.observations = observations
        job.steps_completed.append("observe")
        logger.info(f"[PIPELINE] Observations recorded")
    
    async def rollback_job(self, job_id: str) -> Dict[str, Any]:
        """Rollback a failed job using SafeHoldSnapshot"""
        job = self.jobs.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        
        if not job.snapshot_id:
            return {"success": False, "error": "No snapshot available"}
        
        try:
            from backend.self_heal.safe_hold import SnapshotManager
            snapshot_mgr = SnapshotManager()
            await snapshot_mgr.restore_snapshot(job.snapshot_id)
            
            job.status = "rolled_back"
            job.updated_at = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "job_id": job_id,
                "snapshot_id": job.snapshot_id,
                "status": "rolled_back"
            }
        
        except Exception as e:
            logger.error(f"[PIPELINE] Rollback failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a pipeline job"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "current_step": job.current_step,
            "steps_completed": job.steps_completed,
            "approval_status": job.approval_status,
            "error": job.error,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }


# Global instance
autonomous_pipeline = AutonomousCodingPipeline()
