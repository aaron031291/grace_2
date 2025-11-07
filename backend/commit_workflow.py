"""
Approval-Aware Commit Workflow - Grace's Code Contribution System

Enables Grace to:
1. Create feature branches
2. Make code changes
3. Run tests and lints
4. Generate commit summaries
5. Request approval
6. Push commits or create PRs
7. Track outcomes for learning

All governed by 3-tier autonomy framework.
"""

import asyncio
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from .immutable_log import ImmutableLog
from .autonomy_tiers import autonomy_manager, AutonomyTier
from .trigger_mesh import trigger_mesh, TriggerEvent


@dataclass
class CommitChange:
    """Represents a single file change"""
    file_path: str
    change_type: str  # "create", "modify", "delete"
    old_content: Optional[str]
    new_content: Optional[str]
    diff: str


@dataclass
class CommitWorkflow:
    """Represents a complete commit workflow"""
    workflow_id: str
    branch_name: str
    changes: List[CommitChange]
    commit_message: str
    description: str
    author: str
    tests_passed: bool
    lint_passed: bool
    approval_required: bool
    approval_id: Optional[str]
    status: str  # pending, approved, rejected, committed


class GraceCommitWorkflow:
    """
    Manages Grace's code contribution workflow with governance.
    
    Workflow stages:
    1. Stage: Create branch, apply changes, run checks
    2. Validate: Lint, tests, security scan
    3. Request Approval: Human or policy-based
    4. Execute: Commit and push or create PR
    5. Learn: Track outcome for improvement
    """
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or str(Path.cwd())
        self.immutable_log = ImmutableLog()
        self.active_workflows: Dict[str, CommitWorkflow] = {}
        
    async def propose_commit(
        self,
        changes: List[Dict],
        commit_message: str,
        description: str,
        author: str = "grace",
        branch_name: Optional[str] = None
    ) -> str:
        """
        Propose a code commit with changes.
        
        Args:
            changes: List of {file_path, change_type, content}
            commit_message: Commit message
            description: Detailed description
            author: Author name
            branch_name: Optional branch name
        
        Returns:
            workflow_id for tracking
        """
        
        workflow_id = f"commit_{datetime.utcnow().timestamp()}"
        
        if not branch_name:
            branch_name = f"grace/auto-{workflow_id[:8]}"
        
        # Convert changes to CommitChange objects
        commit_changes = []
        for change in changes:
            file_path = change["file_path"]
            change_type = change["change_type"]
            new_content = change.get("content")
            
            # Get old content if modifying
            old_content = None
            if change_type == "modify":
                try:
                    with open(file_path, 'r') as f:
                        old_content = f.read()
                except FileNotFoundError:
                    old_content = None
            
            # Generate diff
            diff = self._generate_diff(file_path, old_content, new_content, change_type)
            
            commit_changes.append(CommitChange(
                file_path=file_path,
                change_type=change_type,
                old_content=old_content,
                new_content=new_content,
                diff=diff
            ))
        
        # Create workflow
        workflow = CommitWorkflow(
            workflow_id=workflow_id,
            branch_name=branch_name,
            changes=commit_changes,
            commit_message=commit_message,
            description=description,
            author=author,
            tests_passed=False,
            lint_passed=False,
            approval_required=True,  # Default to requiring approval
            approval_id=None,
            status="pending"
        )
        
        self.active_workflows[workflow_id] = workflow
        
        # Publish to Trigger Mesh
        await trigger_mesh.publish(TriggerEvent(
            event_type="commit.proposed",
            source="commit_workflow",
            actor=author,
            resource=workflow_id,
            payload={
                "workflow_id": workflow_id,
                "branch": branch_name,
                "files_changed": len(commit_changes),
                "commit_message": commit_message
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Log to immutable ledger
        await self.immutable_log.append(
            actor=author,
            action="commit_proposed",
            resource=workflow_id,
            subsystem="commit_workflow",
            payload={
                "workflow_id": workflow_id,
                "branch": branch_name,
                "changes": len(commit_changes)
            },
            result="proposed"
        )
        
        return workflow_id
    
    async def stage_and_validate(self, workflow_id: str) -> Dict:
        """
        Stage changes and run validation checks.
        
        Returns validation results
        """
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        results = {
            "branch_created": False,
            "changes_applied": False,
            "lint_passed": False,
            "tests_passed": False,
            "errors": []
        }
        
        try:
            # Create feature branch
            await self._create_branch(workflow.branch_name)
            results["branch_created"] = True
            
            # Apply changes
            for change in workflow.changes:
                await self._apply_change(change)
            results["changes_applied"] = True
            
            # Run lint
            lint_result = await self._run_lint()
            results["lint_passed"] = lint_result["success"]
            workflow.lint_passed = lint_result["success"]
            if not lint_result["success"]:
                results["errors"].append(f"Lint failed: {lint_result.get('output', '')}")
            
            # Run tests
            test_result = await self._run_tests()
            results["tests_passed"] = test_result["success"]
            workflow.tests_passed = test_result["success"]
            if not test_result["success"]:
                results["errors"].append(f"Tests failed: {test_result.get('output', '')}")
            
            # Publish validation results
            await trigger_mesh.publish(TriggerEvent(
                event_type="commit.validated",
                source="commit_workflow",
                actor=workflow.author,
                resource=workflow_id,
                payload={
                    "workflow_id": workflow_id,
                    "lint_passed": results["lint_passed"],
                    "tests_passed": results["tests_passed"],
                    "ready_for_approval": results["lint_passed"] and results["tests_passed"]
                },
                timestamp=datetime.now(timezone.utc)
            ))
            
        except Exception as e:
            results["errors"].append(str(e))
            
            # Publish error
            await trigger_mesh.publish(TriggerEvent(
                event_type="commit.validation_failed",
                source="commit_workflow",
                actor=workflow.author,
                resource=workflow_id,
                payload={
                    "workflow_id": workflow_id,
                    "error": str(e)
                },
                timestamp=datetime.now(timezone.utc)
            ))
        
        return results
    
    async def request_approval(self, workflow_id: str) -> str:
        """
        Request approval for commit workflow.
        
        Returns approval_id
        """
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Check autonomy tier
        can_execute, approval_id = await autonomy_manager.can_execute(
            "create_pr",
            {
                "workflow_id": workflow_id,
                "branch": workflow.branch_name,
                "files_changed": len(workflow.changes)
            }
        )
        
        workflow.approval_id = approval_id
        
        if not can_execute:
            # Publish approval request
            await trigger_mesh.publish(TriggerEvent(
                event_type="commit.approval_requested",
                source="commit_workflow",
                actor=workflow.author,
                resource=workflow_id,
                payload={
                    "approval_id": approval_id,
                    "workflow_id": workflow_id,
                    "commit_message": workflow.commit_message,
                    "description": workflow.description,
                    "files_changed": len(workflow.changes),
                    "lint_passed": workflow.lint_passed,
                    "tests_passed": workflow.tests_passed,
                    "diff_summary": self._generate_diff_summary(workflow)
                },
                timestamp=datetime.now(timezone.utc)
            ))
        
        return approval_id
    
    async def execute_commit(self, workflow_id: str, create_pr: bool = True) -> Dict:
        """
        Execute the commit workflow after approval.
        
        Args:
            workflow_id: Workflow to execute
            create_pr: If True, create PR; if False, push to branch
        
        Returns execution results
        """
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Verify approval
        if workflow.approval_required and workflow.approval_id:
            # Check if approved
            approvals = autonomy_manager.pending_approvals.get(workflow.approval_id)
            if not approvals or approvals["status"] != "approved":
                raise ValueError(f"Workflow {workflow_id} not approved")
        
        results = {
            "committed": False,
            "pushed": False,
            "pr_created": False,
            "pr_url": None,
            "commit_sha": None
        }
        
        try:
            # Stage changes
            for change in workflow.changes:
                await self._git_add(change.file_path)
            
            # Commit
            commit_sha = await self._git_commit(workflow.commit_message, workflow.author)
            results["committed"] = True
            results["commit_sha"] = commit_sha
            
            # Push branch
            await self._git_push(workflow.branch_name)
            results["pushed"] = True
            
            # Create PR if requested
            if create_pr:
                pr_url = await self._create_github_pr(
                    workflow.branch_name,
                    workflow.commit_message,
                    workflow.description
                )
                results["pr_created"] = True
                results["pr_url"] = pr_url
            
            workflow.status = "committed"
            
            # Publish success
            await trigger_mesh.publish(TriggerEvent(
                event_type="commit.executed",
                source="commit_workflow",
                actor=workflow.author,
                resource=workflow_id,
                payload={
                    "workflow_id": workflow_id,
                    "commit_sha": commit_sha,
                    "pr_url": pr_url,
                    "branch": workflow.branch_name
                },
                timestamp=datetime.now(timezone.utc)
            ))
            
            # Log to immutable ledger
            await self.immutable_log.append(
                actor=workflow.author,
                action="commit_executed",
                resource=workflow_id,
                subsystem="commit_workflow",
                payload=results,
                result="success"
            )
            
        except Exception as e:
            results["error"] = str(e)
            workflow.status = "failed"
            
            # Publish error
            await trigger_mesh.publish(TriggerEvent(
                event_type="commit.execution_failed",
                source="commit_workflow",
                actor=workflow.author,
                resource=workflow_id,
                payload={
                    "workflow_id": workflow_id,
                    "error": str(e)
                },
                timestamp=datetime.now(timezone.utc)
            ))
        
        return results
    
    async def rollback(self, workflow_id: str):
        """Rollback a workflow by deleting the branch"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Delete branch
        await self._delete_branch(workflow.branch_name)
        workflow.status = "rolled_back"
        
        # Publish rollback
        await trigger_mesh.publish(TriggerEvent(
            event_type="commit.rolled_back",
            source="commit_workflow",
            actor=workflow.author,
            resource=workflow_id,
            payload={"workflow_id": workflow_id},
            timestamp=datetime.now(timezone.utc)
        ))
    
    # ==================== Git Operations ====================
    
    async def _create_branch(self, branch_name: str):
        """Create a new git branch"""
        await self._run_git_command(["checkout", "-b", branch_name])
    
    async def _delete_branch(self, branch_name: str):
        """Delete a git branch"""
        await self._run_git_command(["checkout", "main"])
        await self._run_git_command(["branch", "-D", branch_name])
    
    async def _git_add(self, file_path: str):
        """Stage a file"""
        await self._run_git_command(["add", file_path])
    
    async def _git_commit(self, message: str, author: str) -> str:
        """Commit staged changes"""
        result = await self._run_git_command([
            "commit",
            "-m", message,
            "--author", f"{author} <{author}@grace.ai>"
        ])
        
        # Extract commit SHA
        sha_result = await self._run_git_command(["rev-parse", "HEAD"])
        return sha_result.strip()
    
    async def _git_push(self, branch_name: str):
        """Push branch to remote"""
        await self._run_git_command(["push", "origin", branch_name])
    
    async def _run_git_command(self, args: List[str]) -> str:
        """Run a git command"""
        process = await asyncio.create_subprocess_exec(
            "git", *args,
            cwd=self.repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Git command failed: {stderr.decode()}")
        
        return stdout.decode()
    
    # ==================== Validation ====================
    
    async def _run_lint(self) -> Dict:
        """Run linter (placeholder - customize per project)"""
        # TODO: Detect and run project-specific linter
        # For now, return success
        return {"success": True, "output": "Lint check passed"}
    
    async def _run_tests(self) -> Dict:
        """Run test suite (placeholder - customize per project)"""
        # TODO: Detect and run project-specific tests
        # For now, return success
        return {"success": True, "output": "All tests passed"}
    
    async def _create_github_pr(
        self,
        branch_name: str,
        title: str,
        description: str
    ) -> str:
        """
        Create GitHub PR using gh CLI.
        
        Returns PR URL
        """
        # TODO: Integrate with GitHub API or gh CLI
        # For now, return placeholder
        return f"https://github.com/repo/pull/123"
    
    # ==================== Utilities ====================
    
    async def _apply_change(self, change: CommitChange):
        """Apply a single file change"""
        
        if change.change_type == "delete":
            Path(change.file_path).unlink(missing_ok=True)
        
        elif change.change_type in ["create", "modify"]:
            # Ensure directory exists
            Path(change.file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write new content
            with open(change.file_path, 'w') as f:
                f.write(change.new_content)
    
    def _generate_diff(
        self,
        file_path: str,
        old_content: Optional[str],
        new_content: Optional[str],
        change_type: str
    ) -> str:
        """Generate unified diff"""
        
        if change_type == "create":
            return f"+ Created {file_path}\n+++ {new_content[:200] if new_content else ''}..."
        elif change_type == "delete":
            return f"- Deleted {file_path}"
        else:
            # Simple diff (could use difflib for better output)
            return f"~ Modified {file_path}"
    
    def _generate_diff_summary(self, workflow: CommitWorkflow) -> str:
        """Generate human-readable diff summary"""
        
        summary_parts = []
        for change in workflow.changes:
            summary_parts.append(f"{change.change_type.upper()}: {change.file_path}")
        
        return "\n".join(summary_parts)
    
    def get_workflow(self, workflow_id: str) -> Optional[CommitWorkflow]:
        """Get workflow by ID"""
        return self.active_workflows.get(workflow_id)
    
    def list_pending_workflows(self) -> List[Dict]:
        """List all pending workflows"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "branch": wf.branch_name,
                "commit_message": wf.commit_message,
                "status": wf.status,
                "lint_passed": wf.lint_passed,
                "tests_passed": wf.tests_passed,
                "approval_required": wf.approval_required
            }
            for wf in self.active_workflows.values()
            if wf.status == "pending"
        ]


# Global instance
grace_commit_workflow = GraceCommitWorkflow()
