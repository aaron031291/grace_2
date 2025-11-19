"""
Multi-User Presence Service

Features:
- Track active users
- User mentions (@username)
- Targeted notifications
- Presence indicators (online/away/offline)
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

from backend.event_bus import event_bus, Event, EventType


@dataclass
class UserPresence:
    """User presence information"""
    user_id: str
    username: str
    status: str  # online, away, offline
    last_seen: datetime
    active_sessions: Set[str] = field(default_factory=set)
    current_activity: Optional[str] = None


class PresenceService:
    """
    Track user presence and handle mentions
    
    Features:
    - Active user tracking
    - @mention parsing
    - Targeted notifications
    - Presence status (online/away/offline)
    """
    
    def __init__(self):
        self.users: Dict[str, UserPresence] = {}
        self.mention_watchers: Dict[str, List[str]] = {}  # user_id -> list of session_ids
    
    def update_presence(
        self,
        user_id: str,
        username: str,
        session_id: str,
        activity: Optional[str] = None
    ):
        """Update user presence"""
        if user_id not in self.users:
            self.users[user_id] = UserPresence(
                user_id=user_id,
                username=username,
                status="online",
                last_seen=datetime.now(),
            )
        
        user = self.users[user_id]
        user.last_seen = datetime.now()
        user.status = "online"
        user.active_sessions.add(session_id)
        
        if activity:
            user.current_activity = activity
    
    def user_offline(self, user_id: str, session_id: str):
        """Mark user as offline"""
        if user_id in self.users:
            user = self.users[user_id]
            user.active_sessions.discard(session_id)
            
            if not user.active_sessions:
                user.status = "offline"
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get all active users"""
        # Auto-update status based on last_seen
        now = datetime.now()
        
        for user in self.users.values():
            if user.status == "online":
                if now - user.last_seen > timedelta(minutes=5):
                    user.status = "away"
                if now - user.last_seen > timedelta(minutes=30):
                    user.status = "offline"
        
        return [
            {
                "user_id": user.user_id,
                "username": user.username,
                "status": user.status,
                "last_seen": user.last_seen.isoformat(),
                "current_activity": user.current_activity,
            }
            for user in self.users.values()
            if user.status in ["online", "away"]
        ]
    
    def parse_mentions(self, text: str) -> List[str]:
        """
        Parse @mentions from text
        
        Returns list of mentioned usernames
        """
        import re
        mentions = re.findall(r'@(\w+)', text)
        return mentions
    
    async def notify_mentioned_users(
        self,
        text: str,
        from_user: str,
        context: Dict[str, Any]
    ):
        """Notify users who were @mentioned"""
        mentions = self.parse_mentions(text)
        
        for mention in mentions:
            # Find user by username
            mentioned_user = None
            for user in self.users.values():
                if user.username.lower() == mention.lower():
                    mentioned_user = user
                    break
            
            if mentioned_user:
                from backend.routes.notifications_api import notify_user
                await notify_user(
                    user_id=mentioned_user.user_id,
                    notification_type="mention",
                    message=f"@{from_user} mentioned you: {text[:100]}...",
                    data={
                        "from_user": from_user,
                        "text": text,
                        **context
                    },
                    badge="@"
                )
    
    def get_user_by_username(self, username: str) -> Optional[str]:
        """Get user_id by username"""
        for user in self.users.values():
            if user.username.lower() == username.lower():
                return user.user_id
        return None


# Global instance
presence_service = PresenceService()
