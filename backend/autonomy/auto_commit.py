"""
Auto-Commit System
Grace automatically commits her code fixes to Git with governance approval
"""

import subprocess
from typing import Dict, Any
import logging

from .governance_framework import governance_framework
from .immutable_log import ImmutableLog

logger = logging.getLogger(__name__)


class AutoCommitEngine:
    """
    Automatically commits code fixes to version control
    with governance oversight
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.commits_made = 0
        self.auto_commit_enabled = True
        self.require_approval = True
    
    async def commit_fix(
        self,
        file_path: str,
        fix_description: str,
        actor: str = "grace",
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """
        Commit a code fix to Git
        
        Args:
            file_path: File that was fixed
            fix_description: Description of the fix
            actor: Who made the fix
            auto_approve: Skip approval if True
        
        Returns:
            Commit result
        """
        
        if not self.auto_commit_enabled:
            return {
                "committed": False,
                "reason": "Auto-commit disabled"
            }
        
        # Check governance
        if self.require_approval and not auto_approve:
            approval = await governance_framework.check_action(
                actor=actor,
                action="git_commit",
                resource=file_path,
                context={"description": fix_description},
                confidence=0.8
            )
            
            if not approval.get("approved", False):
                logger.info(f"[AUTO_COMMIT] ⏸️  Commit requires approval: {fix_description}")
                return {
                    "committed": False,
                    "reason": "Awaiting approval",
                    "approval_required": True,
                    "fix_description": fix_description
                }
        
        # Execute git commit
        try:
            # Git add
            result_add = subprocess.run(
                ['git', 'add', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_add.returncode != 0:
                logger.error(f"[AUTO_COMMIT] Git add failed: {result_add.stderr}")
                return {
                    "committed": False,
                    "reason": f"Git add failed: {result_add.stderr}"
                }
            
            # Git commit
            commit_message = f"[Grace Auto-Fix] {fix_description}"
            result_commit = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_commit.returncode != 0:
                # Check if it's "nothing to commit"
                if "nothing to commit" in result_commit.stdout:
                    return {
                        "committed": False,
                        "reason": "No changes to commit"
                    }
                
                logger.error(f"[AUTO_COMMIT] Git commit failed: {result_commit.stderr}")
                return {
                    "committed": False,
                    "reason": f"Git commit failed: {result_commit.stderr}"
                }
            
            self.commits_made += 1
            
            # Log to immutable log
            await self.immutable_log.append(
                actor=actor,
                action="auto_commit",
                resource=file_path,
                subsystem="auto_commit",
                payload={
                    "commit_message": commit_message,
                    "file": file_path
                },
                result="success"
            )
            
            logger.info(f"[AUTO_COMMIT] ✅ Committed: {commit_message}")
            
            return {
                "committed": True,
                "commit_message": commit_message,
                "file": file_path,
                "stdout": result_commit.stdout
            }
        
        except Exception as e:
            logger.error(f"[AUTO_COMMIT] Error: {e}", exc_info=True)
            return {
                "committed": False,
                "reason": f"Exception: {str(e)}"
            }
    
    async def push_commits(self, remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
        """
        Push commits to remote (requires high-level approval)
        """
        
        # Always require approval for push
        approval = await governance_framework.check_action(
            actor="grace",
            action="git_push",
            resource=f"{remote}/{branch}",
            context={"commits": self.commits_made},
            confidence=0.9
        )
        
        if not approval.get("approved", False):
            return {
                "pushed": False,
                "reason": "Push requires human approval",
                "approval_required": True
            }
        
        # Execute git push
        try:
            result = subprocess.run(
                ['git', 'push', remote, branch],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"[AUTO_COMMIT] Git push failed: {result.stderr}")
                return {
                    "pushed": False,
                    "reason": f"Git push failed: {result.stderr}"
                }
            
            logger.info(f"[AUTO_COMMIT] ✅ Pushed to {remote}/{branch}")
            
            return {
                "pushed": True,
                "remote": remote,
                "branch": branch,
                "stdout": result.stdout
            }
        
        except Exception as e:
            logger.error(f"[AUTO_COMMIT] Push error: {e}", exc_info=True)
            return {
                "pushed": False,
                "reason": f"Exception: {str(e)}"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get auto-commit status"""
        return {
            "enabled": self.auto_commit_enabled,
            "require_approval": self.require_approval,
            "commits_made": self.commits_made
        }


# Global instance
auto_commit = AutoCommitEngine()
