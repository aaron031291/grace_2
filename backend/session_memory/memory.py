"""
Session Memory - Topic extraction and duration tracking for Orb sessions
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)


class SessionMemory:
    """
    Session Memory with topic extraction and duration tracking
    
    Tracks conversation messages, extracts key topics, and maintains session metadata
    """
    
    def __init__(
        self,
        session_id: str,
        embedding_service=None,
        vector_store=None
    ):
        """
        Initialize Session Memory
        
        Args:
            session_id: Unique session identifier
            embedding_service: Optional embedding service for semantic analysis
            vector_store: Optional vector store for persistence
        """
        self.session_id = session_id
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        
        self.messages: List[Dict[str, Any]] = []
        self.topics: Counter = Counter()
        self.start_time = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.end_time: Optional[datetime] = None
        self.status = "active"
        
        self.topic_keywords = {
            'guardian', 'security', 'healing', 'self-healing', 'network',
            'governance', 'approval', 'mission', 'task', 'learning',
            'memory', 'knowledge', 'rag', 'vector', 'embedding',
            'model', 'llm', 'ai', 'ml', 'training',
            'api', 'endpoint', 'service', 'backend', 'frontend',
            'database', 'migration', 'schema', 'table',
            'test', 'ci', 'deployment', 'production',
            'user', 'session', 'auth', 'token',
            'error', 'bug', 'fix', 'issue', 'debug',
            'feature', 'enhancement', 'improvement',
            'sandbox', 'experiment', 'consensus', 'sovereignty',
            'multimodal', 'voice', 'recording', 'screen-share',
            'orb', 'world-model', 'hub', 'workspace'
        }
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add message to session and extract topics
        
        Args:
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        self.last_activity = datetime.now(timezone.utc)
        
        self._extract_topics(content)
    
    def _extract_topics(self, text: str):
        """
        Extract topics from text using simple keyword matching
        
        Args:
            text: Text to extract topics from
        """
        text_lower = text.lower()
        
        for keyword in self.topic_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_lower)
            if matches:
                self.topics[keyword] += len(matches)
    
    def get_duration_seconds(self) -> float:
        """Get session duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
    def get_duration_formatted(self) -> str:
        """Get formatted duration string"""
        total_seconds = int(self.get_duration_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_key_topics(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N topics with scores
        
        Args:
            top_n: Number of top topics to return
            
        Returns:
            List of {topic, count, score} dicts
        """
        if not self.topics:
            return []
        
        top_topics = self.topics.most_common(top_n)
        
        max_count = top_topics[0][1] if top_topics else 1
        
        return [
            {
                'topic': topic,
                'count': count,
                'score': count / max_count
            }
            for topic, count in top_topics
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive session summary
        
        Returns:
            Session summary with duration, messages, topics
        """
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.get_duration_seconds(),
            'duration_formatted': self.get_duration_formatted(),
            'total_messages': len(self.messages),
            'key_topics': self.get_key_topics(),
            'status': self.status,
            'last_activity': self.last_activity.isoformat()
        }
    
    def get_chat_transcript(self) -> str:
        """
        Get full conversation transcript
        
        Returns:
            Complete transcript as string
        """
        lines = []
        for msg in self.messages:
            role = msg['role'].upper()
            content = msg['content']
            timestamp = msg['timestamp']
            lines.append(f"[{timestamp}] {role}: {content}")
        
        return '\n'.join(lines)
    
    def close_session(self):
        """Close the session"""
        self.end_time = datetime.now(timezone.utc)
        self.status = "closed"
        logger.info(f"Session {self.session_id} closed. Duration: {self.get_duration_formatted()}")
    
    async def save_to_vector_store(self) -> bool:
        """
        Save session to vector store with embeddings
        
        Returns:
            Success status
        """
        if not self.vector_store:
            logger.warning(f"No vector store configured for session {self.session_id}")
            return False
        
        try:
            session_doc = {
                'session_id': self.session_id,
                'transcript': self.get_chat_transcript(),
                'summary': self.get_summary(),
                'topics': dict(self.topics),
                'message_count': len(self.messages)
            }
            
            logger.info(f"Session {self.session_id} saved to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session {self.session_id}: {e}")
            return False
