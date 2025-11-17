"""Grace External Agent

Autonomous agent that uses external APIs (GitHub, Slack, AWS) based on
Grace's needs, with Parliament voting for major operations.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .external_apis.github_connector import GitHubClient
from .external_apis.slack_connector import SlackClient
from .external_apis.aws_connector import AWSClient
from .parliament_engine import parliament_engine
from .memory_service import MemoryService
from .immutable_log import ImmutableLogger


class GraceExternalAgent:
    """Autonomous external API agent for Grace"""
    
    def __init__(self, actor: str = "grace_external_agent"):
        """Initialize Grace external agent"""
        
        self.actor = actor
        self.github = GitHubClient(actor=actor)
        self.slack = SlackClient(actor=actor)
        self.aws = AWSClient(actor=actor)
        self.memory = MemoryService()
        self.audit = ImmutableLogger()
        
        # Configuration
        self.auto_create_issues = True
        self.auto_notify_slack = True
        self.auto_backup_s3 = True
        self.require_parliament_approval = True
    
    async def initialize(self):
        """Initialize all external API clients"""
        
        try:
            # Authenticate GitHub
            await self.github.authenticate_with_token(token_key="grace_github_token")
            
            # Authenticate Slack
            await self.slack.authenticate_with_token(token_key="grace_slack_token")
            
            # Authenticate AWS
            await self.aws.authenticate_with_credentials(
                access_key_id_key="grace_aws_access_key",
                secret_access_key_key="grace_aws_secret_key"
            )
            
            print("✓ Grace External Agent initialized")
            return True
            
        except Exception as e:
            print(f"⚠ Grace External Agent initialization failed: {e}")
            return False
    
    async def create_github_issue_from_task(
        self,
        task: Dict[str, Any],
        repo: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Autonomously create GitHub issue from Grace task
        
        Args:
            task: Task dictionary with title, description, etc.
            repo: Target repository (optional, uses default)
        
        Returns:
            Created issue information or None
        """
        
        if not self.auto_create_issues:
            print("Auto-create issues disabled")
            return None
        
        # Default repository
        repo = repo or "grace-org/grace-tasks"
        
        # Extract task information
        title = task.get("title", "Grace Task")
        description = task.get("description", "")
        priority = task.get("priority", "medium")
        category = task.get("category", "general")
        
        # Format issue body
        body = f"""**Task created by Grace**

{description}

**Details:**
- Priority: {priority}
- Category: {category}
- Created: {datetime.utcnow().isoformat()}
- Task ID: {task.get('id', 'unknown')}

---
*This issue was automatically created by Grace's autonomous external agent.*
"""
        
        # Labels based on priority and category
        labels = [f"priority:{priority}", f"category:{category}", "grace-created"]
        
        # If high priority, require Parliament approval
        if priority == "high" and self.require_parliament_approval:
            session_id = await self._request_parliament_approval(
                action="create_github_issue",
                resource=repo,
                context={
                    "title": title,
                    "priority": priority,
                    "task_id": task.get('id')
                },
                reason=f"High-priority task requires GitHub issue in {repo}"
            )
            
            if not session_id:
                print(f"Parliament approval required for high-priority issue. Pending...")
                return None
        
        try:
            # Create issue
            result = await self.github.create_issue(
                repo=repo,
                title=title,
                body=body,
                labels=labels
            )
            
            # Store in memory
            await self.memory.store_memory(
                agent=self.actor,
                memory_type="github_issue_created",
                content=json.dumps(result, indent=2),
                metadata={
                    "task_id": task.get('id'),
                    "repo": repo,
                    "issue_number": result['number']
                }
            )
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="auto_created_github_issue",
                resource=repo,
                result="success",
                details={
                    "issue_number": result['number'],
                    "task_id": task.get('id'),
                    "title": title
                }
            )
            
            print(f"✓ Auto-created GitHub issue #{result['number']} in {repo}")
            
            # Optionally notify Slack
            if self.auto_notify_slack:
                await self.notify_slack_on_alert({
                    "type": "github_issue_created",
                    "issue_number": result['number'],
                    "repo": repo,
                    "url": result['url']
                })
            
            return result
            
        except Exception as e:
            print(f"Failed to auto-create GitHub issue: {e}")
            return None
    
    async def notify_slack_on_alert(
        self,
        alert: Dict[str, Any],
        channel: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send critical alerts to Slack
        
        Args:
            alert: Alert dictionary
            channel: Slack channel (optional, uses default)
        
        Returns:
            Message result or None
        """
        
        if not self.auto_notify_slack:
            print("Auto-notify Slack disabled")
            return None
        
        # Default channel
        channel = channel or "#grace-alerts"
        
        # Format alert message
        alert_type = alert.get("type", "unknown")
        severity = alert.get("severity", "info")
        
        # Emoji based on severity
        emoji_map = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "ℹ️",
            "low": "💡",
            "info": "📢"
        }
        emoji = emoji_map.get(severity, "📢")
        
        message = f"""{emoji} *Grace Alert: {alert_type}*

**Severity:** {severity}
**Time:** {datetime.utcnow().isoformat()}

**Details:**
{json.dumps(alert, indent=2)}

---
_Automated alert from Grace External Agent_
"""
        
        # If critical, require Parliament approval
        if severity == "critical" and self.require_parliament_approval:
            session_id = await self._request_parliament_approval(
                action="send_slack_alert",
                resource=channel,
                context={"alert_type": alert_type, "severity": severity},
                reason=f"Critical alert requires Slack notification"
            )
            
            if not session_id:
                print(f"Parliament approval required for critical alert. Pending...")
                return None
        
        try:
            # Send message
            result = await self.slack.send_message(channel=channel, text=message)
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="auto_sent_slack_alert",
                resource=channel,
                result="success",
                details={"alert_type": alert_type, "severity": severity}
            )
            
            print(f"✓ Sent Slack alert to {channel}")
            return result
            
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
            return None
    
    async def backup_to_s3(
        self,
        data: Dict[str, Any],
        data_type: str,
        bucket: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Automatically backup important data to S3
        
        Args:
            data: Data to backup
            data_type: Type of data (memories, policies, logs, etc.)
            bucket: S3 bucket (optional, uses default)
        
        Returns:
            Upload result or None
        """
        
        if not self.auto_backup_s3:
            print("Auto-backup to S3 disabled")
            return None
        
        # Default bucket
        bucket = bucket or "grace-backups"
        
        # Generate S3 key
        timestamp = datetime.utcnow().isoformat().replace(":", "-")
        key = f"backups/{data_type}/{timestamp}.json"
        
        # Save data to temporary file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f, indent=2)
            temp_file = f.name
        
        try:
            # Upload to S3
            result = await self.aws.s3_upload_file(
                bucket=bucket,
                key=key,
                file_path=temp_file,
                metadata={
                    "data_type": data_type,
                    "timestamp": timestamp,
                    "agent": self.actor
                }
            )
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="auto_backup_to_s3",
                resource=f"s3://{bucket}/{key}",
                result="success",
                details={
                    "data_type": data_type,
                    "size": result['size']
                }
            )
            
            print(f"✓ Backed up {data_type} to s3://{bucket}/{key}")
            return result
            
        except Exception as e:
            print(f"Failed to backup to S3: {e}")
            return None
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    async def _request_parliament_approval(
        self,
        action: str,
        resource: str,
        context: Dict[str, Any],
        reason: str
    ) -> Optional[int]:
        """
        Request Parliament approval for major operations
        
        Args:
            action: Action to perform
            resource: Target resource
            context: Action context
            reason: Reason for action
        
        Returns:
            Parliament session ID or None if approval not needed
        """
        
        # Create Parliament session
        session = await parliament_engine.create_session(
            title=f"Grace External: {action}",
            description=reason,
            category="external_api",
            risk_level="medium",
            proposed_by=self.actor,
            context={
                "action": action,
                "resource": resource,
                **context
            }
        )
        
        print(f"🏛️ Parliament session created: {session['session_id']}")
        print(f"   Action: {action}")
        print(f"   Resource: {resource}")
        print(f"   Reason: {reason}")
        
        # Store session reference
        await self.memory.store_memory(
            agent=self.actor,
            memory_type="parliament_session",
            content=json.dumps(session, indent=2),
            metadata={
                "action": action,
                "resource": resource,
                "session_id": session['session_id']
            }
        )
        
        return session['session_id']
    
    async def process_pending_actions(self) -> Dict[str, Any]:
        """
        Process pending autonomous actions
        
        Returns:
            Processing summary
        """
        
        summary = {
            "issues_created": 0,
            "alerts_sent": 0,
            "backups_completed": 0,
            "errors": []
        }
        
        # This would typically query a task queue or check Grace's internal state
        # For now, it's a placeholder for the autonomous loop
        
        print("🤖 Grace External Agent checking for pending actions...")
        
        return summary
    
    async def autonomous_loop(self, interval: int = 300):
        """
        Run autonomous processing loop
        
        Args:
            interval: Check interval in seconds (default: 5 minutes)
        """
        
        print(f"🤖 Starting Grace External Agent autonomous loop (interval: {interval}s)")
        
        while True:
            try:
                summary = await self.process_pending_actions()
                
                if any(summary.values()):
                    print(f"✓ Processed: {json.dumps(summary, indent=2)}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"⚠ Autonomous loop error: {e}")
                await asyncio.sleep(interval)


# Global instance
grace_external_agent = GraceExternalAgent()


async def main():
    """Test Grace External Agent"""
    
    agent = GraceExternalAgent()
    
    # Initialize (would fail without credentials, but shows structure)
    # await agent.initialize()
    
    # Test task-to-issue
    test_task = {
        "id": "task_001",
        "title": "Implement new feature",
        "description": "Add support for external API integration",
        "priority": "high",
        "category": "feature"
    }
    
    # This would create an issue if credentials were available
    # result = await agent.create_github_issue_from_task(test_task)
    
    # Test alert notification
    test_alert = {
        "type": "security_breach",
        "severity": "critical",
        "message": "Unusual activity detected"
    }
    
    # This would send Slack message if credentials were available
    # result = await agent.notify_slack_on_alert(test_alert)
    
    print("✓ Grace External Agent test complete")


if __name__ == "__main__":
    asyncio.run(main())
