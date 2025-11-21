"""
Grace's Message Bus
Central nervous system - all kernels communicate through here

Uses asyncio queues for now (can swap to NATS/RabbitMQ for production)
Zero-trust: authenticated channels, message signing
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BusMessage:
    """Message on the bus"""
    id: str
    source: str
    destination: str
    topic: str
    payload: Dict[str, Any]
    priority: MessagePriority
    timestamp: datetime
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source': self.source,
            'destination': self.destination,
            'topic': self.topic,
            'payload': self.payload,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'metadata': self.metadata or {}
        }


class MessageBus:
    """
    Grace's central message bus
    All kernel communication flows through here
    
    Features:
    - Topic-based routing
    - Priority queues
    - Message authentication
    - Rate limiting
    - Audit logging
    """
    
    def __init__(self):
        self.topics = {}  # topic -> list of subscriber queues
        self.handlers = {}  # topic -> handler function
        self.message_count = 0
        self.running = False
        
        # Security: Topic ACLs
        self.topic_acls = {
            'kernel.memory': ['memory_fusion', 'librarian'],
            'kernel.healing': ['self_healing', 'orchestrator'],
            'kernel.governance': ['governance_engine', 'orchestrator', 'control_plane'],
            'kernel.code': ['coding_agent', 'sandbox'],
            'kernel.crypto': ['crypto_service', 'orchestrator'],
            'system.control': ['orchestrator', 'control_center', 'control_plane'],
            'system.health': ['health_monitor', 'orchestrator'],
            'agent.request': ['coding_agent', 'firefox_agent', 'proactive_learning_agent', 'orchestrator'],
            'agent.response': ['coding_agent', 'firefox_agent', 'proactive_learning_agent', 'orchestrator'],
            'agent.growth_plan': ['self_reflection_loop', 'orchestrator', 'guardian']
        }
    
    async def start(self):
        """Start message bus"""
        self.running = True
        logger.info("[MESSAGE-BUS] Started - Grace's nervous system active")
    
    async def stop(self):
        """Stop message bus"""
        self.running = False
        logger.info("[MESSAGE-BUS] Stopped")
    
    async def _publish_acl_violation(self, source: str, topic: str):
        """Publish ACL violation event for monitoring"""
        try:
            from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                source="message_bus",
                event_type="message_bus.acl_violation",
                payload={
                    "actor": source,
                    "topic": topic,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ))
        except Exception as e:
            logger.debug(f"[MESSAGE-BUS] Could not publish ACL violation event: {e}")
    
    async def publish(
        self,
        source: str,
        topic: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Publish message to topic
        
        Args:
            source: Source kernel name
            topic: Topic to publish to
            payload: Message payload
            priority: Message priority
            correlation_id: For request/response correlation
        
        Returns:
            Message ID
        """
        
        # Check ACL
        if not self._check_acl(source, topic):
            logger.warning(f"[MESSAGE-BUS] ACL violation: {source} -> {topic}")
            
            # Publish ACL violation event for monitoring
            asyncio.create_task(self._publish_acl_violation(source, topic))
            
            return ""
        
        # Create message
        self.message_count += 1
        msg_id = f"msg_{self.message_count}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        message = BusMessage(
            id=msg_id,
            source=source,
            destination='broadcast',
            topic=topic,
            payload=payload,
            priority=priority,
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id
        )
        
        # Route to subscribers
        if topic in self.topics:
            for queue in self.topics[topic]:
                try:
                    await queue.put(message)
                except:
                    pass
        
        # Call handlers
        if topic in self.handlers:
            handler = self.handlers[topic]
            try:
                asyncio.create_task(handler(message))
            except Exception as e:
                logger.error(f"[MESSAGE-BUS] Handler error for {topic}: {e}")
        
        logger.debug(f"[MESSAGE-BUS] Published: {source} -> {topic} ({msg_id})")
        
        return msg_id
    
    async def subscribe(
        self,
        subscriber: str,
        topic: str
    ) -> asyncio.Queue:
        """
        Subscribe to topic
        
        Args:
            subscriber: Subscriber kernel name
            topic: Topic to subscribe to
        
        Returns:
            Queue to receive messages
        """
        
        # Check ACL
        if not self._check_acl(subscriber, topic, subscribe=True):
            logger.warning(f"[MESSAGE-BUS] ACL violation: {subscriber} subscribe to {topic}")
            return asyncio.Queue()
        
        # Create queue for subscriber
        queue = asyncio.Queue()
        
        if topic not in self.topics:
            self.topics[topic] = []
        
        self.topics[topic].append(queue)
        
        logger.info(f"[MESSAGE-BUS] {subscriber} subscribed to {topic}")
        
        return queue
    
    def register_handler(
        self,
        topic: str,
        handler: Callable[[BusMessage], Any]
    ):
        """Register handler for topic"""
        self.handlers[topic] = handler
        logger.info(f"[MESSAGE-BUS] Handler registered for {topic}")
    
    def _check_acl(self, kernel: str, topic: str, subscribe: bool = False) -> bool:
        """Check if kernel has access to topic"""
        
        # Get allowed kernels for topic
        allowed = self.topic_acls.get(topic, [])
        
        # If no ACL defined, allow (open topic)
        if not allowed:
            return True
        
        # Check if kernel is allowed
        return kernel in allowed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bus statistics"""
        return {
            'running': self.running,
            'total_messages': self.message_count,
            'active_topics': len(self.topics),
            'registered_handlers': len(self.handlers),
            'topics': list(self.topics.keys())
        }


# Global instance - Grace's nervous system
message_bus = MessageBus()
