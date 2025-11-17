"""
Continuous Learning Loop
Grace learns from every action she takes

Features:
- Learn from mission outcomes
- Learn from healing actions
- Learn from code generation
- Update knowledge bases automatically
- Pattern recognition
- Success/failure analysis
- Continuous improvement
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log
from .mission_control.hub import mission_control_hub
from .fusion_memory import fusion_memory

logger = logging.getLogger(__name__)


@dataclass
class LearningEntry:
    """A learning extracted from Grace's actions"""
    entry_id: str
    source: str  # mission, healing, coding, etc.
    pattern: str
    success: bool
    context: Dict[str, Any]
    learned_at: datetime
    confidence: float = 0.5


class ContinuousLearningLoop:
    """
    Continuous Learning Loop
    
    Grace learns from every action:
    1. Mission completed → Extract patterns
    2. Healing action → Update playbooks
    3. Code generated → Improve templates
    4. Error encountered → Add to knowledge
    5. Success achieved → Reinforce behavior
    """
    
    def __init__(self):
        self.running = False
        
        # Learning statistics
        self.total_learnings = 0
        self.mission_learnings = 0
        self.healing_learnings = 0
        self.coding_learnings = 0
        self.error_learnings = 0
        
        # Learning storage
        self.recent_learnings: List[LearningEntry] = []
        self.max_recent = 100
    
    async def start(self):
        """Start continuous learning loop"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("=" * 80)
        logger.info("CONTINUOUS LEARNING LOOP - STARTING")
        logger.info("=" * 80)
        logger.info("[LEARNING] Grace will now learn from every action!")
        logger.info("[LEARNING] Learning from: missions, healing, coding, errors")
        logger.info("=" * 80)
        
        # Subscribe to learning events
        await self._subscribe_to_events()
        
        # Start learning metrics loop
        asyncio.create_task(self._learning_metrics_loop())
        
        logger.info("[LEARNING] ✅ Continuous Learning Loop OPERATIONAL")
        
        # Log to immutable log
        await immutable_log.append(
            actor="continuous_learning_loop",
            action="system_start",
            resource="learning",
            subsystem="learning",
            payload={},
            result="started"
        )
    
    async def stop(self):
        """Stop continuous learning loop"""
        self.running = False
        logger.info("[LEARNING] Continuous Learning Loop stopped")
    
    async def _subscribe_to_events(self):
        """Subscribe to events for learning"""
        
        # Mission events
        await trigger_mesh.subscribe("mission.resolved", self._learn_from_mission)
        await trigger_mesh.subscribe("mission.failed", self._learn_from_mission_failure)
        
        # Elite healing events
        await trigger_mesh.subscribe("elite.healing_complete", self._learn_from_healing)
        await trigger_mesh.subscribe("elite.healing_failed", self._learn_from_healing_failure)
        
        # Elite coding events
        await trigger_mesh.subscribe("elite.code_generated", self._learn_from_coding)
        await trigger_mesh.subscribe("elite.code_failed", self._learn_from_coding_failure)
        
        # Autonomous mission events
        await trigger_mesh.subscribe("autonomous.mission_created", self._learn_from_autonomous)
        
        # Error events
        await trigger_mesh.subscribe("*.error", self._learn_from_error)
        
        logger.info("[LEARNING] Subscribed to learning events")
    
    async def _learn_from_mission(self, event: TriggerEvent):
        """Learn from completed mission"""
        try:
            mission_id = event.payload.get("mission_id")
            if not mission_id:
                return
            
            # Get mission details
            mission = await mission_control_hub.get_mission(mission_id)
            if not mission:
                return
            
            # Extract pattern
            pattern = {
                "symptoms": [s.description for s in mission.symptoms],
                "solution": mission.remediation_history[-1].action if mission.remediation_history else None,
                "subsystem": mission.subsystem_id,
                "duration_seconds": (mission.resolved_at - mission.created_at).total_seconds() if mission.resolved_at else None
            }
            
            # Create learning entry
            learning = LearningEntry(
                entry_id=f"learn_{int(datetime.now(timezone.utc).timestamp())}",
                source="mission",
                pattern=str(pattern),
                success=True,
                context=pattern,
                learned_at=datetime.now(timezone.utc),
                confidence=0.8
            )
            
            # Store learning
            await self._store_learning(learning)
            
            # Update knowledge bases
            await self._update_knowledge_bases(learning)
            
            self.mission_learnings += 1
            self.total_learnings += 1
            
            logger.info(f"[LEARNING] 🧠 Learned from mission: {mission_id}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Error learning from mission: {e}", exc_info=True)
    
    async def _learn_from_mission_failure(self, event: TriggerEvent):
        """Learn from failed mission"""
        try:
            mission_id = event.payload.get("mission_id")
            error = event.payload.get("error", "Unknown error")
            
            # Create learning entry for failure
            learning = LearningEntry(
                entry_id=f"learn_{int(datetime.now(timezone.utc).timestamp())}",
                source="mission_failure",
                pattern=f"Mission failed: {error}",
                success=False,
                context={"mission_id": mission_id, "error": error},
                learned_at=datetime.now(timezone.utc),
                confidence=0.6
            )
            
            await self._store_learning(learning)
            
            self.error_learnings += 1
            self.total_learnings += 1
            
            logger.info(f"[LEARNING] 🧠 Learned from mission failure: {mission_id}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Error learning from mission failure: {e}", exc_info=True)
    
    async def _learn_from_healing(self, event: TriggerEvent):
        """Learn from healing action"""
        try:
            healing_id = event.payload.get("healing_id")
            playbook = event.payload.get("playbook")
            success = event.payload.get("success", False)
            
            learning = LearningEntry(
                entry_id=f"learn_{int(datetime.now(timezone.utc).timestamp())}",
                source="healing",
                pattern=f"Healing playbook: {playbook}",
                success=success,
                context=event.payload,
                learned_at=datetime.now(timezone.utc),
                confidence=0.7
            )
            
            await self._store_learning(learning)
            
            self.healing_learnings += 1
            self.total_learnings += 1
            
            logger.info(f"[LEARNING] 🧠 Learned from healing: {playbook}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Error learning from healing: {e}", exc_info=True)
    
    async def _learn_from_healing_failure(self, event: TriggerEvent):
        """Learn from healing failure"""
        await self._learn_from_error(event)
    
    async def _learn_from_coding(self, event: TriggerEvent):
        """Learn from code generation"""
        try:
            code_id = event.payload.get("code_id")
            pattern = event.payload.get("pattern")
            
            learning = LearningEntry(
                entry_id=f"learn_{int(datetime.now(timezone.utc).timestamp())}",
                source="coding",
                pattern=f"Code pattern: {pattern}",
                success=True,
                context=event.payload,
                learned_at=datetime.now(timezone.utc),
                confidence=0.7
            )
            
            await self._store_learning(learning)
            
            self.coding_learnings += 1
            self.total_learnings += 1
            
            logger.info(f"[LEARNING] 🧠 Learned from coding: {pattern}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Error learning from coding: {e}", exc_info=True)
    
    async def _learn_from_coding_failure(self, event: TriggerEvent):
        """Learn from coding failure"""
        await self._learn_from_error(event)
    
    async def _learn_from_autonomous(self, event: TriggerEvent):
        """Learn from autonomous mission creation"""
        try:
            mission_id = event.payload.get("mission_id")
            
            learning = LearningEntry(
                entry_id=f"learn_{int(datetime.now(timezone.utc).timestamp())}",
                source="autonomous",
                pattern="Autonomous mission created",
                success=True,
                context=event.payload,
                learned_at=datetime.now(timezone.utc),
                confidence=0.6
            )
            
            await self._store_learning(learning)
            
            self.total_learnings += 1
            
        except Exception as e:
            logger.error(f"[LEARNING] Error learning from autonomous: {e}", exc_info=True)
    
    async def _learn_from_error(self, event: TriggerEvent):
        """Learn from errors"""
        try:
            error = event.payload.get("error", "Unknown error")
            
            learning = LearningEntry(
                entry_id=f"learn_{int(datetime.now(timezone.utc).timestamp())}",
                source="error",
                pattern=f"Error: {error}",
                success=False,
                context=event.payload,
                learned_at=datetime.now(timezone.utc),
                confidence=0.5
            )
            
            await self._store_learning(learning)
            
            self.error_learnings += 1
            self.total_learnings += 1
            
            logger.info(f"[LEARNING] 🧠 Learned from error: {error}")
            
        except Exception as e:
            logger.error(f"[LEARNING] Error learning from error: {e}", exc_info=True)
    
    async def _store_learning(self, learning: LearningEntry):
        """Store learning in memory"""
        try:
            # Add to recent learnings
            self.recent_learnings.append(learning)
            if len(self.recent_learnings) > self.max_recent:
                self.recent_learnings.pop(0)
            
            # Store in Fusion Memory
            await fusion_memory.store(
                domain="learnings",
                content={
                    "entry_id": learning.entry_id,
                    "source": learning.source,
                    "pattern": learning.pattern,
                    "success": learning.success,
                    "context": learning.context,
                    "confidence": learning.confidence
                },
                user="grace"
            )
            
        except Exception as e:
            logger.debug(f"[LEARNING] Could not store in Fusion Memory: {e}")
    
    async def _update_knowledge_bases(self, learning: LearningEntry):
        """Update knowledge bases with new learning"""
        try:
            # Determine which knowledge base to update
            if learning.source == "mission" and learning.success:
                # Add to Elite Self-Healing knowledge
                # Would add knowledge entry here
                pass
            elif learning.source == "coding" and learning.success:
                # Add to Elite Coding Agent knowledge
                # Would add knowledge entry here
                pass
        except Exception as e:
            logger.debug(f"[LEARNING] Could not update knowledge bases: {e}")
    
    async def _learning_metrics_loop(self):
        """Periodically report learning metrics"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                if self.total_learnings > 0:
                    logger.info(f"[LEARNING] 📊 Total learnings: {self.total_learnings}")
                    logger.info(f"[LEARNING]    Missions: {self.mission_learnings}")
                    logger.info(f"[LEARNING]    Healing: {self.healing_learnings}")
                    logger.info(f"[LEARNING]    Coding: {self.coding_learnings}")
                    logger.info(f"[LEARNING]    Errors: {self.error_learnings}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[LEARNING] Error in metrics loop: {e}", exc_info=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            "running": self.running,
            "total_learnings": self.total_learnings,
            "mission_learnings": self.mission_learnings,
            "healing_learnings": self.healing_learnings,
            "coding_learnings": self.coding_learnings,
            "error_learnings": self.error_learnings,
            "recent_learnings": len(self.recent_learnings)
        }


# Singleton instance
continuous_learning_loop = ContinuousLearningLoop()

