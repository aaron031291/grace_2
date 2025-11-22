"""GitHub integration for repository monitoring and automated actions"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.trigger_mesh import trigger_mesh, TriggerEvent


class GitHubIntegration:
    """Handles GitHub repository monitoring and automated actions"""

    def __init__(self):
        self.token = None
        self.repositories = []
        self.webhook_secret = None
        self.enabled = False
        self.base_url = "https://api.github.com"

    async def initialize(self, token: str = None, repositories: List[str] = None,
                        webhook_secret: str = None):
        """Initialize GitHub integration"""
        self.token = token
        self.repositories = repositories or []
        self.webhook_secret = webhook_secret

        if token and repositories:
            self.enabled = True
            print("✅ GitHub integration initialized")
            print(f"   Monitoring repositories: {', '.join(repositories)}")
        else:
            print("⚠️ GitHub integration not configured - set GITHUB_TOKEN and GITHUB_REPOS")

    async def create_issue(self, repo: str, title: str, body: str,
                          labels: List[str] = None) -> Optional[str]:
        """Create a GitHub issue"""
        if not self.enabled:
            return None

        url = f"{self.base_url}/repos/{repo}/issues"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        data = {
            "title": title,
            "body": body,
            "labels": labels or []
        }

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=10)

                if response.status_code == 201:
                    issue_data = response.json()
                    issue_number = issue_data["number"]
                    print(f"✅ GitHub issue created: {repo}#{issue_number}")
                    return str(issue_number)
                else:
                    print(f"❌ GitHub issue creation failed: {response.status_code}")
                    return None

        except Exception as e:
            print(f"❌ GitHub API error: {e}")
            return None

    async def create_pull_request(self, repo: str, title: str, head: str, base: str,
                                body: str) -> Optional[str]:
        """Create a GitHub pull request"""
        if not self.enabled:
            return None

        url = f"{self.base_url}/repos/{repo}/pulls"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=10)

                if response.status_code == 201:
                    pr_data = response.json()
                    pr_number = pr_data["number"]
                    print(f"✅ GitHub PR created: {repo}#{pr_number}")
                    return str(pr_number)
                else:
                    print(f"❌ GitHub PR creation failed: {response.status_code}")
                    return None

        except Exception as e:
            print(f"❌ GitHub API error: {e}")
            return None

    async def get_recent_commits(self, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits from a repository"""
        if not self.enabled:
            return []

        url = f"{self.base_url}/repos/{repo}/commits"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

        params = {"per_page": min(limit, 100)}

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    commits = response.json()
                    return [{
                        "sha": commit["sha"][:7],
                        "message": commit["commit"]["message"].split('\n')[0],
                        "author": commit["commit"]["author"]["name"],
                        "date": commit["commit"]["author"]["date"]
                    } for commit in commits]
                else:
                    print(f"❌ Failed to get commits: {response.status_code}")
                    return []

        except Exception as e:
            print(f"❌ GitHub API error: {e}")
            return []

    async def notify_code_change(self, change: Dict[str, Any]):
        """Create GitHub issue for significant code changes"""
        repo = change.get("repository", "unknown")
        title = f"🤖 Autonomous Code Change: {change.get('type', 'Unknown')}"

        body = f"""## Autonomous Code Modification

**Type:** {change.get('type', 'Unknown')}
**File:** {change.get('file', 'Unknown')}
**Actor:** Grace AI Agentic Spine
**Risk Score:** {change.get('risk_score', 0):.2f}

### Description
{change.get('description', 'Automated code modification by Grace AI')}

### Verification Required
- [ ] Code review completed
- [ ] Tests passing
- [ ] No breaking changes
- [ ] Documentation updated

*This change was made autonomously by Grace AI. Please review carefully.*

**Timestamp:** {datetime.utcnow().isoformat()}
"""

        labels = ["autonomous-change", "needs-review"]
        if change.get('risk_score', 0) > 0.7:
            labels.append("high-risk")

        return await self.create_issue(repo, title, body, labels)

    async def notify_system_incident(self, incident: Dict[str, Any]):
        """Create GitHub issue for system incidents"""
        repo = incident.get("repository", self.repositories[0] if self.repositories else "unknown")
        title = f"🚨 System Incident: {incident.get('type', 'Unknown')}"

        body = f"""## System Incident Report

**Type:** {incident.get('type', 'Unknown')}
**Severity:** {incident.get('severity', 'Unknown')}
**Status:** {incident.get('status', 'Active')}

### Description
{incident.get('description', 'System incident detected')}

### Impact Assessment
{incident.get('impact', 'Impact assessment pending')}

### Recovery Actions Taken
{incident.get('recovery_actions', 'No automated recovery attempted')}

### Next Steps
- [ ] Investigate root cause
- [ ] Implement fixes
- [ ] Update monitoring
- [ ] Document incident

**Detected by:** Grace AI Agentic Spine
**Timestamp:** {datetime.utcnow().isoformat()}
"""

        labels = ["incident", f"severity-{incident.get('severity', 'unknown')}"]
        return await self.create_issue(repo, title, body, labels)

    async def create_feature_request(self, feature: Dict[str, Any]):
        """Create GitHub issue for feature requests identified by Grace"""
        repo = feature.get("repository", self.repositories[0] if self.repositories else "unknown")
        title = f"💡 AI-Generated Feature Request: {feature.get('title', 'Unknown')}"

        body = f"""## AI-Generated Feature Request

**Confidence:** {feature.get('confidence', 0):.1%}
**Priority:** {feature.get('priority', 'Medium')}

### Problem Statement
{feature.get('problem', 'Feature identified through autonomous analysis')}

### Proposed Solution
{feature.get('solution', 'Solution to be determined')}

### Business Value
{feature.get('value', 'Value assessment pending')}

### Implementation Notes
{feature.get('implementation', 'Implementation details to be determined')}

**Identified by:** Grace AI Meta-Loop Analysis
**Timestamp:** {datetime.utcnow().isoformat()}
"""

        labels = ["enhancement", "ai-generated", f"priority-{feature.get('priority', 'medium').lower()}"]
        return await self.create_issue(repo, title, body, labels)

    async def handle_github_webhook(self, webhook_data: Dict[str, Any]):
        """Handle incoming GitHub webhooks"""
        event_type = webhook_data.get("action", "unknown")

        if event_type == "push":
            print("📨 GitHub push event received")
            # Could trigger Grace to analyze new code changes
        elif event_type == "pull_request":
            print("📨 GitHub PR event received")
            # Could trigger automated review or testing
        elif event_type == "issues":
            print("📨 GitHub issue event received")
            # Could trigger autonomous issue analysis
        else:
            print(f"📨 GitHub webhook: {event_type}")

        # Publish to trigger mesh for other systems to handle
        await trigger_mesh.publish(TriggerEvent(
            event_type="external.github_event",
            source="github_integration",
            actor="github",
            resource=webhook_data.get("repository", {}).get("full_name", "unknown"),
            payload=webhook_data,
            timestamp=datetime.utcnow()
        ))


# Global instance
github_integration = GitHubIntegration()
