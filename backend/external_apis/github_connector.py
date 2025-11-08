"""GitHub API Connector with Governance and Security

Integrates with GitHub using PyGithub with full governance, Hunter scanning,
and verification signatures on all operations.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from github import Github, GithubException
except ImportError:
    Github = None
    GithubException = Exception

from ..secrets_vault import secrets_vault
from ..governance import GovernanceEngine
from ..hunter import Hunter
from ..verification import VerificationEngine
from ..memory_service import MemoryService
from ..immutable_log import ImmutableLogger


class GitHubClient:
    """GitHub API client with governance and security"""
    
    def __init__(self, actor: str = "grace"):
        """
        Initialize GitHub client
        
        Args:
            actor: User/service making GitHub operations
        """
        if Github is None:
            raise ImportError("PyGithub not installed. Run: pip install PyGithub")
        
        self.actor = actor
        self.client: Optional[Github] = None
        self.governance = GovernanceEngine()
        self.hunter = Hunter()
        self.verification = VerificationEngine()
        self.memory = MemoryService()
        self.audit = ImmutableLogger()
    
    async def authenticate_with_token(self, token_key: str = "github_token") -> bool:
        """
        Authenticate using token from secrets vault
        
        Args:
            token_key: Key in secrets vault for GitHub token
        
        Returns:
            True if authentication successful
        """
        try:
            # Retrieve token from vault
            token = await secrets_vault.retrieve_secret(
                secret_key=token_key,
                accessor=self.actor,
                service="github"
            )
            
            # Create GitHub client
            self.client = Github(token)
            
            # Test authentication
            user = self.client.get_user()
            username = user.login
            
            # Log authentication
            await self.audit.log_event(
                actor=self.actor,
                action="github_auth",
                resource="github",
                result="success",
                details={"username": username}
            )
            
            print(f"[OK] GitHub authenticated as {username}")
            return True
            
        except Exception as e:
            await self.audit.log_event(
                actor=self.actor,
                action="github_auth",
                resource="github",
                result="failure",
                details={"error": str(e)}
            )
            raise PermissionError(f"GitHub authentication failed: {e}")
    
    async def _check_governance(
        self,
        action: str,
        resource: str,
        payload: Dict[str, Any]
    ) -> None:
        """Check governance policy before action"""
        
        result = await self.governance.check(
            actor=self.actor,
            action=f"github_{action}",
            resource=resource,
            payload=payload
        )
        
        if result["decision"] == "deny":
            raise PermissionError(f"Governance denied: {result.get('reason', 'No reason')}")
        
        if result["decision"] == "parliament_pending":
            raise PermissionError(
                f"Parliament review required. Session ID: {result.get('parliament_session_id')}"
            )
    
    async def _hunter_scan(
        self,
        content: str,
        context: Dict[str, Any]
    ) -> None:
        """Scan content with Hunter"""
        
        alerts = await self.hunter.inspect(
            actor=self.actor,
            action="github_content_scan",
            resource=context.get("resource", "github"),
            payload={"content_hash": hashlib.sha256(content.encode()).hexdigest(), **context}
        )
        
        if alerts:
            critical_alerts = [a for a in alerts if "critical" in str(a).lower()]
            if critical_alerts:
                raise SecurityError(f"Hunter detected critical security issues: {alerts}")
    
    async def _create_verification(
        self,
        action: str,
        resource: str,
        input_data: Dict[str, Any]
    ) -> int:
        """Create verification envelope"""
        
        action_id = f"github_{action}_{datetime.utcnow().timestamp()}"
        
        return await self.verification.log_verified_action(
            action_id=action_id,
            actor=self.actor,
            action_type=f"github_{action}",
            resource=resource,
            input_data=input_data
        )
    
    async def _store_in_memory(
        self,
        content_type: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> int:
        """Store GitHub data in memory system"""
        
        return await self.memory.store_memory(
            agent=self.actor,
            memory_type="github_data",
            content=content,
            metadata={
                **metadata,
                "source": "github",
                "content_type": content_type
            }
        )
    
    async def list_repositories(self, org: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List repositories
        
        Args:
            org: Organization name (if None, lists user repos)
        
        Returns:
            List of repository information
        """
        if not self.client:
            raise RuntimeError("Not authenticated. Call authenticate_with_token() first")
        
        # Governance check
        await self._check_governance(
            action="list_repos",
            resource=org or "user",
            payload={"org": org}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="list_repos",
            resource=org or "user",
            input_data={"org": org}
        )
        
        try:
            if org:
                repos = self.client.get_organization(org).get_repos()
            else:
                repos = self.client.get_user().get_repos()
            
            repo_list = []
            for repo in repos:
                repo_data = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                }
                repo_list.append(repo_data)
            
            # Store in memory
            await self._store_in_memory(
                content_type="repository_list",
                content=json.dumps(repo_list, indent=2),
                metadata={"org": org, "count": len(repo_list), "verification_id": verification_id}
            )
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="github_list_repos",
                resource=org or "user",
                result="success",
                details={"count": len(repo_list)}
            )
            
            return repo_list
            
        except GithubException as e:
            await self.audit.log_event(
                actor=self.actor,
                action="github_list_repos",
                resource=org or "user",
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def get_issues(
        self,
        repo: str,
        state: str = "open",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get issues from repository
        
        Args:
            repo: Repository name (org/repo or user/repo)
            state: Issue state (open, closed, all)
            limit: Maximum issues to retrieve
        
        Returns:
            List of issues
        """
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="get_issues",
            resource=repo,
            payload={"state": state, "limit": limit}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="get_issues",
            resource=repo,
            input_data={"state": state, "limit": limit}
        )
        
        try:
            repository = self.client.get_repo(repo)
            issues = repository.get_issues(state=state)
            
            issue_list = []
            for i, issue in enumerate(issues):
                if i >= limit:
                    break
                
                issue_data = {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body or "",
                    "state": issue.state,
                    "user": issue.user.login if issue.user else None,
                    "labels": [label.name for label in issue.labels],
                    "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                    "url": issue.html_url
                }
                
                # Hunter scan issue content
                await self._hunter_scan(
                    content=f"{issue.title}\n{issue.body or ''}",
                    context={"resource": f"{repo}/issues/{issue.number}", "type": "issue"}
                )
                
                issue_list.append(issue_data)
            
            # Store in memory
            await self._store_in_memory(
                content_type="issues",
                content=json.dumps(issue_list, indent=2),
                metadata={"repo": repo, "state": state, "count": len(issue_list), "verification_id": verification_id}
            )
            
            return issue_list
            
        except GithubException as e:
            await self.audit.log_event(
                actor=self.actor,
                action="github_get_issues",
                resource=repo,
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def create_issue(
        self,
        repo: str,
        title: str,
        body: str,
        labels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create GitHub issue (requires governance approval)
        
        Args:
            repo: Repository name
            title: Issue title
            body: Issue body
            labels: Optional labels
        
        Returns:
            Created issue information
        """
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        # Governance check (mutations require approval)
        await self._check_governance(
            action="create_issue",
            resource=repo,
            payload={"title": title, "body": body, "labels": labels}
        )
        
        # Hunter scan content before posting
        await self._hunter_scan(
            content=f"{title}\n{body}",
            context={"resource": f"{repo}/issues", "type": "create_issue"}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="create_issue",
            resource=repo,
            input_data={"title": title, "body": body, "labels": labels}
        )
        
        try:
            repository = self.client.get_repo(repo)
            issue = repository.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            
            result = {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
                "verification_id": verification_id
            }
            
            # Store in memory
            await self._store_in_memory(
                content_type="created_issue",
                content=json.dumps(result, indent=2),
                metadata={"repo": repo, "issue_number": issue.number}
            )
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="github_create_issue",
                resource=repo,
                result="success",
                details={"issue_number": issue.number, "title": title}
            )
            
            return result
            
        except GithubException as e:
            await self.audit.log_event(
                actor=self.actor,
                action="github_create_issue",
                resource=repo,
                result="failure",
                details={"error": str(e), "title": title}
            )
            raise
    
    async def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """
        Create pull request (requires governance approval)
        
        Args:
            repo: Repository name
            title: PR title
            body: PR description
            head: Head branch
            base: Base branch (default: main)
        
        Returns:
            Created PR information
        """
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="create_pr",
            resource=repo,
            payload={"title": title, "head": head, "base": base}
        )
        
        # Hunter scan
        await self._hunter_scan(
            content=f"{title}\n{body}",
            context={"resource": f"{repo}/pulls", "type": "create_pr"}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="create_pr",
            resource=repo,
            input_data={"title": title, "body": body, "head": head, "base": base}
        )
        
        try:
            repository = self.client.get_repo(repo)
            pr = repository.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            result = {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "state": pr.state,
                "verification_id": verification_id
            }
            
            await self.audit.log_event(
                actor=self.actor,
                action="github_create_pr",
                resource=repo,
                result="success",
                details={"pr_number": pr.number, "title": title}
            )
            
            return result
            
        except GithubException as e:
            await self.audit.log_event(
                actor=self.actor,
                action="github_create_pr",
                resource=repo,
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def list_commits(
        self,
        repo: str,
        branch: str = "main",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List commits from repository branch"""
        
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        await self._check_governance(
            action="list_commits",
            resource=repo,
            payload={"branch": branch, "limit": limit}
        )
        
        try:
            repository = self.client.get_repo(repo)
            commits = repository.get_commits(sha=branch)
            
            commit_list = []
            for i, commit in enumerate(commits):
                if i >= limit:
                    break
                
                commit_list.append({
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name if commit.commit.author else None,
                    "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
                    "url": commit.html_url
                })
            
            return commit_list
            
        except GithubException as e:
            raise
    
    async def create_comment(
        self,
        repo: str,
        issue_number: int,
        comment: str
    ) -> Dict[str, Any]:
        """Create comment on issue/PR (requires governance)"""
        
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        await self._check_governance(
            action="create_comment",
            resource=f"{repo}/issues/{issue_number}",
            payload={"comment": comment}
        )
        
        await self._hunter_scan(
            content=comment,
            context={"resource": f"{repo}/issues/{issue_number}", "type": "comment"}
        )
        
        try:
            repository = self.client.get_repo(repo)
            issue = repository.get_issue(issue_number)
            comment_obj = issue.create_comment(comment)
            
            result = {
                "id": comment_obj.id,
                "url": comment_obj.html_url,
                "created_at": comment_obj.created_at.isoformat() if comment_obj.created_at else None
            }
            
            await self.audit.log_event(
                actor=self.actor,
                action="github_create_comment",
                resource=f"{repo}/issues/{issue_number}",
                result="success",
                details={"comment_id": comment_obj.id}
            )
            
            return result
            
        except GithubException as e:
            raise


class SecurityError(Exception):
    """Security scan failure"""
    pass
