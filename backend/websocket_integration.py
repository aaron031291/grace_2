"""
Real-Time WebSocket Integration
Broadcasts all Grace system events with crypto signatures

Features:
- Real-time event broadcasting
- Crypto-signed messages
- Mission Control events
- Elite Systems events
- Integration events
- Autonomous mission events
- Learning events
"""

import asyncio
import logging
from typing import Dict, Any, List, Set
from datetime import datetime, timezone
import json

from .websocket_handler import websocket_manager
from .trigger_mesh import trigger_mesh, TriggerEvent
from .crypto_key_manager import crypto_key_manager
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class GraceWebSocketBroadcaster:
    """
    Real-time WebSocket broadcaster for all Grace events
    
    Broadcasts:
    - Mission Control events (missions created, executed, completed)
    - Elite Systems events (healing, coding, orchestration)
    - Integration events (system communication, data flows)
    - Autonomous mission events (detection, testing, consensus)
    - Learning events (knowledge acquired, patterns learned)
    - Crypto events (keys generated, signatures verified)
    """
    
    def __init__(self):
        self.running = False
        self.component_id = "websocket_broadcaster"
        self.events_broadcast = 0
        self.connected_clients: Set[str] = set()
    
    async def start(self):
        """Start WebSocket broadcaster"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("=" * 80)
        logger.info("WEBSOCKET BROADCASTER - STARTING")
        logger.info("=" * 80)
        
        # Generate crypto key for signing broadcasts
        await crypto_key_manager.generate_key_for_component(self.component_id)
        logger.info("[WEBSOCKET] Crypto key generated for message signing")
        
        # Subscribe to all trigger mesh events
        await self._subscribe_to_events()
        
        logger.info("[WEBSOCKET] ✅ WebSocket Broadcaster OPERATIONAL")
        logger.info("[WEBSOCKET] All Grace events will be broadcast in real-time")
        logger.info("=" * 80)
        
        # Log to immutable log
        await immutable_log.append(
            actor=self.component_id,
            action="system_start",
            resource="websocket_broadcast",
            subsystem="websocket",
            payload={"component_id": self.component_id},
            result="started"
        )
    
    async def stop(self):
        """Stop WebSocket broadcaster"""
        self.running = False
        logger.info("[WEBSOCKET] WebSocket Broadcaster stopped")
    
    async def _subscribe_to_events(self):
        """Subscribe to all trigger mesh events"""
        
        # Mission Control events
        await trigger_mesh.subscribe("mission.*", self._broadcast_mission_event)
        
        # Elite Systems events
        await trigger_mesh.subscribe("elite.*", self._broadcast_elite_event)
        
        # Integration events
        await trigger_mesh.subscribe("integration.*", self._broadcast_integration_event)
        
        # Autonomous mission events
        await trigger_mesh.subscribe("autonomous.*", self._broadcast_autonomous_event)
        
        # Learning events
        await trigger_mesh.subscribe("learning.*", self._broadcast_learning_event)
        
        # Crypto events
        await trigger_mesh.subscribe("crypto.*", self._broadcast_crypto_event)
        
        # Health events
        await trigger_mesh.subscribe("health.*", self._broadcast_health_event)
        
        logger.info("[WEBSOCKET] Subscribed to all trigger mesh events")
    
    async def _broadcast_mission_event(self, event: TriggerEvent):
        """Broadcast Mission Control events"""
        await self._broadcast_signed_event("mission", event)
    
    async def _broadcast_elite_event(self, event: TriggerEvent):
        """Broadcast Elite Systems events"""
        await self._broadcast_signed_event("elite", event)
    
    async def _broadcast_integration_event(self, event: TriggerEvent):
        """Broadcast integration events"""
        await self._broadcast_signed_event("integration", event)
    
    async def _broadcast_autonomous_event(self, event: TriggerEvent):
        """Broadcast autonomous mission events"""
        await self._broadcast_signed_event("autonomous", event)
    
    async def _broadcast_learning_event(self, event: TriggerEvent):
        """Broadcast learning events"""
        await self._broadcast_signed_event("learning", event)
    
    async def _broadcast_crypto_event(self, event: TriggerEvent):
        """Broadcast crypto events"""
        await self._broadcast_signed_event("crypto", event)
    
    async def _broadcast_health_event(self, event: TriggerEvent):
        """Broadcast health events"""
        await self._broadcast_signed_event("health", event)
    
    async def _broadcast_signed_event(self, category: str, event: TriggerEvent):
        """
        Broadcast event with crypto signature
        
        Args:
            category: Event category
            event: Trigger event to broadcast
        """
        try:
            # Create message payload
            message = {
                "category": category,
                "event_type": event.event_type,
                "source": event.source,
                "actor": event.actor,
                "resource": event.resource,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat()
            }
            
            # Sign message
            signed_message = await crypto_key_manager.sign_message(
                component_id=self.component_id,
                message=message
            )
            
            # Create broadcast payload
            broadcast_payload = {
                "type": "grace_event",
                "category": category,
                "event": message,
                "signature": signed_message.signature,
                "key_id": signed_message.key_id,
                "signed_at": signed_message.signed_at.isoformat(),
                "verified": False  # Client will verify
            }
            
            # Broadcast to all WebSocket clients
            await websocket_manager.broadcast(broadcast_payload)
            
            self.events_broadcast += 1
            
            logger.debug(f"[WEBSOCKET] Broadcast: {category}.{event.event_type}")
            
        except Exception as e:
            logger.error(f"[WEBSOCKET] Error broadcasting event: {e}", exc_info=True)
    
    async def broadcast_custom_message(
        self,
        message_type: str,
        payload: Dict[str, Any],
        sign: bool = True
    ):
        """
        Broadcast custom message
        
        Args:
            message_type: Type of message
            payload: Message payload
            sign: Whether to sign the message
        """
        try:
            message = {
                "type": message_type,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if sign:
                # Sign message
                signed_message = await crypto_key_manager.sign_message(
                    component_id=self.component_id,
                    message=message
                )
                
                broadcast_payload = {
                    "type": "grace_custom",
                    "message": message,
                    "signature": signed_message.signature,
                    "key_id": signed_message.key_id,
                    "signed_at": signed_message.signed_at.isoformat()
                }
            else:
                broadcast_payload = message
            
            await websocket_manager.broadcast(broadcast_payload)
            
            self.events_broadcast += 1
            
        except Exception as e:
            logger.error(f"[WEBSOCKET] Error broadcasting custom message: {e}", exc_info=True)
    
    async def broadcast_grace_status(self):
        """Broadcast Grace's current status"""
        try:
            # Get status from various systems
            from .mission_control.hub import mission_control_hub
            from .integration_orchestrator import integration_orchestrator
            
            mc_status = await mission_control_hub.get_status()
            int_stats = integration_orchestrator.get_statistics()
            crypto_stats = crypto_key_manager.get_statistics()
            
            status = {
                "mission_control": {
                    "total_missions": mc_status.total_missions,
                    "open_missions": mc_status.open_missions,
                    "in_progress_missions": mc_status.in_progress_missions,
                    "overall_health": mc_status.overall_health
                },
                "integration": {
                    "total_systems": int_stats["total_systems"],
                    "healthy_systems": int_stats["healthy_systems"],
                    "total_messages": int_stats["total_messages"]
                },
                "crypto": {
                    "total_keys": crypto_stats["total_keys"],
                    "signatures_generated": crypto_stats["signatures_generated"],
                    "signatures_verified": crypto_stats["signatures_verified"]
                },
                "websocket": {
                    "events_broadcast": self.events_broadcast,
                    "connected_clients": len(self.connected_clients)
                }
            }
            
            await self.broadcast_custom_message("grace_status", status, sign=True)
            
        except Exception as e:
            logger.error(f"[WEBSOCKET] Error broadcasting status: {e}", exc_info=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket broadcaster statistics"""
        return {
            "running": self.running,
            "events_broadcast": self.events_broadcast,
            "connected_clients": len(self.connected_clients),
            "component_id": self.component_id
        }


# Singleton instance
grace_websocket_broadcaster = GraceWebSocketBroadcaster()

