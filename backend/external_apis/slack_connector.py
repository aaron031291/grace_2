"""Slack Integration with Governance and Security

Integrates with Slack using slack_sdk with governance approval,
Hunter scanning, and webhook receiver.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    WebClient = None
    SlackApiError = Exception

from ..secrets_vault import secrets_vault
from ..governance import GovernanceEngine
from ..hunter import Hunter
from ..verification import VerificationEngine
from ..memory_service import MemoryService
from ..immutable_log import ImmutableLogger


class SlackClient:
    """Slack client with governance and security"""
    
    def __init__(self, actor: str = "grace"):
        """
        Initialize Slack client
        
        Args:
            actor: User/service making Slack operations
        """
        if WebClient is None:
            raise ImportError("slack_sdk not installed. Run: pip install slack-sdk")
        
        self.actor = actor
        self.client: Optional[WebClient] = None
        self.governance = GovernanceEngine()
        self.hunter = Hunter()
        self.verification = VerificationEngine()
        self.memory = MemoryService()
        self.audit = ImmutableLogger()
    
    async def authenticate_with_token(self, token_key: str = "slack_token") -> bool:
        """
        Authenticate using token from secrets vault
        
        Args:
            token_key: Key in secrets vault for Slack token
        
        Returns:
            True if authentication successful
        """
        try:
            # Retrieve token from vault
            token = await secrets_vault.retrieve_secret(
                secret_key=token_key,
                accessor=self.actor,
                service="slack"
            )
            
            # Create Slack client
            self.client = WebClient(token=token)
            
            # Test authentication
            response = self.client.auth_test()
            team_name = response["team"]
            user_name = response["user"]
            
            # Log authentication
            await self.audit.log_event(
                actor=self.actor,
                action="slack_auth",
                resource="slack",
                result="success",
                details={"team": team_name, "user": user_name}
            )
            
            print(f"[OK] Slack authenticated as {user_name} in {team_name}")
            return True
            
        except Exception as e:
            await self.audit.log_event(
                actor=self.actor,
                action="slack_auth",
                resource="slack",
                result="failure",
                details={"error": str(e)}
            )
            raise PermissionError(f"Slack authentication failed: {e}")
    
    async def _check_governance(
        self,
        action: str,
        resource: str,
        payload: Dict[str, Any]
    ) -> None:
        """Check governance policy before action"""
        
        result = await self.governance.check(
            actor=self.actor,
            action=f"slack_{action}",
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
            action="slack_content_scan",
            resource=context.get("resource", "slack"),
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
        
        action_id = f"slack_{action}_{datetime.utcnow().timestamp()}"
        
        return await self.verification.log_verified_action(
            action_id=action_id,
            actor=self.actor,
            action_type=f"slack_{action}",
            resource=resource,
            input_data=input_data
        )
    
    async def _store_in_memory(
        self,
        content_type: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> int:
        """Store Slack data in memory system"""
        
        return await self.memory.store_memory(
            agent=self.actor,
            memory_type="slack_data",
            content=content,
            metadata={
                **metadata,
                "source": "slack",
                "content_type": content_type
            }
        )
    
    async def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message to Slack channel (requires governance approval)
        
        Args:
            channel: Channel ID or name
            text: Message text
            thread_ts: Optional thread timestamp for replies
        
        Returns:
            Message information
        """
        if not self.client:
            raise RuntimeError("Not authenticated. Call authenticate_with_token() first")
        
        # Governance check (outbound messages require approval)
        await self._check_governance(
            action="send_message",
            resource=channel,
            payload={"text": text, "channel": channel}
        )
        
        # Hunter scan message before sending
        await self._hunter_scan(
            content=text,
            context={"resource": f"slack/{channel}", "type": "message"}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="send_message",
            resource=channel,
            input_data={"channel": channel, "text": text, "thread_ts": thread_ts}
        )
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )
            
            result = {
                "ok": response["ok"],
                "channel": response["channel"],
                "ts": response["ts"],
                "message": response.get("message", {}),
                "verification_id": verification_id
            }
            
            # Store in memory
            await self._store_in_memory(
                content_type="sent_message",
                content=text,
                metadata={
                    "channel": channel,
                    "ts": response["ts"],
                    "verification_id": verification_id
                }
            )
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="slack_send_message",
                resource=channel,
                result="success",
                details={"ts": response["ts"], "message_length": len(text)}
            )
            
            return result
            
        except SlackApiError as e:
            await self.audit.log_event(
                actor=self.actor,
                action="slack_send_message",
                resource=channel,
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def list_channels(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List Slack channels
        
        Args:
            limit: Maximum channels to retrieve
        
        Returns:
            List of channels
        """
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="list_channels",
            resource="slack",
            payload={"limit": limit}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="list_channels",
            resource="slack",
            input_data={"limit": limit}
        )
        
        try:
            response = self.client.conversations_list(limit=limit)
            
            channels = []
            for channel in response["channels"]:
                channels.append({
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_channel": channel.get("is_channel", False),
                    "is_private": channel.get("is_private", False),
                    "is_archived": channel.get("is_archived", False),
                    "num_members": channel.get("num_members", 0),
                    "topic": channel.get("topic", {}).get("value", ""),
                    "purpose": channel.get("purpose", {}).get("value", "")
                })
            
            # Store in memory
            await self._store_in_memory(
                content_type="channel_list",
                content=json.dumps(channels, indent=2),
                metadata={"count": len(channels), "verification_id": verification_id}
            )
            
            # Audit
            await self.audit.log_event(
                actor=self.actor,
                action="slack_list_channels",
                resource="slack",
                result="success",
                details={"count": len(channels)}
            )
            
            return channels
            
        except SlackApiError as e:
            await self.audit.log_event(
                actor=self.actor,
                action="slack_list_channels",
                resource="slack",
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def get_channel_history(
        self,
        channel: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get channel message history
        
        Args:
            channel: Channel ID
            limit: Maximum messages to retrieve
        
        Returns:
            List of messages
        """
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="get_history",
            resource=channel,
            payload={"limit": limit}
        )
        
        try:
            response = self.client.conversations_history(
                channel=channel,
                limit=limit
            )
            
            messages = []
            for msg in response["messages"]:
                message_data = {
                    "type": msg.get("type"),
                    "user": msg.get("user"),
                    "text": msg.get("text", ""),
                    "ts": msg.get("ts"),
                    "thread_ts": msg.get("thread_ts")
                }
                
                # Hunter scan fetched messages
                if msg.get("text"):
                    await self._hunter_scan(
                        content=msg["text"],
                        context={"resource": f"slack/{channel}", "type": "history", "ts": msg.get("ts")}
                    )
                
                messages.append(message_data)
            
            # Store in memory
            await self._store_in_memory(
                content_type="channel_history",
                content=json.dumps(messages, indent=2),
                metadata={"channel": channel, "count": len(messages)}
            )
            
            return messages
            
        except SlackApiError as e:
            raise
    
    async def upload_file(
        self,
        channel: str,
        file_path: str,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Slack channel (requires governance)
        
        Args:
            channel: Channel ID or name
            file_path: Path to file
            title: Optional file title
            initial_comment: Optional comment
        
        Returns:
            Upload information
        """
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="upload_file",
            resource=channel,
            payload={"file_path": file_path, "title": title}
        )
        
        # Verification
        verification_id = await self._create_verification(
            action="upload_file",
            resource=channel,
            input_data={"file_path": file_path, "title": title}
        )
        
        try:
            response = self.client.files_upload(
                channels=channel,
                file=file_path,
                title=title,
                initial_comment=initial_comment
            )
            
            result = {
                "ok": response["ok"],
                "file": {
                    "id": response["file"]["id"],
                    "name": response["file"]["name"],
                    "title": response["file"]["title"],
                    "url": response["file"]["url_private"]
                },
                "verification_id": verification_id
            }
            
            await self.audit.log_event(
                actor=self.actor,
                action="slack_upload_file",
                resource=channel,
                result="success",
                details={"file_id": response["file"]["id"], "title": title}
            )
            
            return result
            
        except SlackApiError as e:
            await self.audit.log_event(
                actor=self.actor,
                action="slack_upload_file",
                resource=channel,
                result="failure",
                details={"error": str(e)}
            )
            raise
    
    async def create_reminder(
        self,
        text: str,
        time: str,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create reminder in Slack
        
        Args:
            text: Reminder text
            time: Time string (e.g., "in 20 minutes", "tomorrow at 9am")
            user: Optional user ID (defaults to self)
        
        Returns:
            Reminder information
        """
        if not self.client:
            raise RuntimeError("Not authenticated")
        
        # Governance
        await self._check_governance(
            action="create_reminder",
            resource="slack",
            payload={"text": text, "time": time}
        )
        
        try:
            response = self.client.reminders_add(
                text=text,
                time=time,
                user=user
            )
            
            result = {
                "ok": response["ok"],
                "reminder": response.get("reminder", {})
            }
            
            await self.audit.log_event(
                actor=self.actor,
                action="slack_create_reminder",
                resource="slack",
                result="success",
                details={"text": text, "time": time}
            )
            
            return result
            
        except SlackApiError as e:
            raise


class SlackWebhookReceiver:
    """Receive and process incoming Slack events"""
    
    def __init__(self):
        self.memory = MemoryService()
        self.hunter = Hunter()
        self.audit = ImmutableLogger()
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming Slack event
        
        Args:
            event_data: Event payload from Slack
        
        Returns:
            Processing result
        """
        event_type = event_data.get("type", "unknown")
        
        # Hunter scan incoming event
        await self.hunter.inspect(
            actor="slack_webhook",
            action="incoming_event",
            resource="slack",
            payload={"event_type": event_type, "data": event_data}
        )
        
        # Store event in memory
        await self.memory.store_memory(
            agent="slack_webhook",
            memory_type="slack_event",
            content=json.dumps(event_data, indent=2),
            metadata={"event_type": event_type, "timestamp": datetime.utcnow().isoformat()}
        )
        
        # Audit
        await self.audit.log_event(
            actor="slack_webhook",
            action="slack_event_received",
            resource="slack",
            result="success",
            details={"event_type": event_type}
        )
        
        return {"status": "processed", "event_type": event_type}


class SecurityError(Exception):
    """Security scan failure"""
    pass
