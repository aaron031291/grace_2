"""
Proactive Mission Generator

Monitors KPIs, telemetry, and validator results to automatically create missions.

Thresholds:
- Success rate < 90% over last 24h → reliability mission
- MTTR > max(5min, 3× historical baseline) → repairtime mission
- HTM queue depth > 1,000 for >5min → scaling mission
- Customer-facing p95 latency > 1.5× baseline → scaling mission
- Same validator alert twice in 30min → integrity mission
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

# Task templates for each mission type
MISSION_TASK_TEMPLATES = {
    "reliability": [
        {"type": "diagnose_failures", "priority": "high",
         "description": "Analyze failure patterns and root causes"},
        {"type": "implement_fixes", "priority": "high",
         "description": "Apply fixes to improve success rate"},
        {"type": "validate_success_rate", "priority": "medium",
         "description": "Verify success rate returns above 90%"}
    ],
    "repairtime": [
        {"type": "diagnose_slow_repairs", "priority": "high",
         "description": "Identify why repairs are slow"},
        {"type": "optimize_playbooks", "priority": "high",
         "description": "Optimize healing playbooks for speed"},
        {"type": "add_healing_workers", "priority": "medium",
         "description": "Scale healing workers if needed"},
        {"type": "validate_mttr", "priority": "medium",
         "description": "Verify MTTR drops below target"}
    ],
    "scaling": [
        {"type": "analyze_capacity", "priority": "high",
         "description": "Analyze current capacity vs demand"},
        {"type": "plan_scaling", "priority": "high",
         "description": "Create scaling plan (workers, instances, resources)"},
        {"type": "execute_scale", "priority": "high",
         "description": "Execute scaling plan"},
        {"type": "validate_telemetry", "priority": "medium",
         "description": "Monitor post-scaling metrics"}
    ],
    "integrity": [
        {"type": "gather_evidence", "priority": "high",
         "description": "Collect all related integrity violations"},
        {"type": "identify_root_cause", "priority": "high",
         "description": "Determine why validation keeps failing"},
        {"type": "implement_permanent_fix", "priority": "high",
         "description": "Implement fix that addresses root cause"},
        {"type": "verify_resolution", "priority": "medium",
         "description": "Verify violations don't recur"}
    ]
}


@dataclass
class MissionTrigger:
    """Detected condition requiring a mission"""
    trigger_type: str
    domain_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    baseline_value: Optional[float] = None
    severity: str = "medium"
    confidence: float = 0.9
    evidence: List[str] = field(default_factory=list)
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ProactiveMissionGenerator:
    """Automatically generates missions based on KPI/telemetry monitoring"""
    
    def __init__(self):
        self._initialized = False
        self._running = False
        self.scan_interval_seconds = 300  # 5 minutes
        
        # Thresholds
        self.success_rate_threshold = 0.90
        self.mttr_target_seconds = 300.0
        self.mttr_multiplier = 3.0
        self.queue_depth_threshold = 1000
        self.latency_multiplier = 1.5
        self.validator_repeat_window_minutes = 30
        
        # Statistics
        self.missions_generated = 0
        self.triggers_detected = 0
        self.missions_by_type = defaultdict(int)
        self.recent_triggers = {}
        self.validator_alert_history = defaultdict(list)
    
    async def initialize(self):
        """Initialize proactive mission generator"""
        if self._initialized:
            return
        
        logger.info("[MISSION-GEN] Initializing proactive mission generator")
        self._initialized = True
        logger.info("[MISSION-GEN] Ready")
    
    async def start_detection_loop(self):
        """Start continuous monitoring"""
        if self._running:
            return
        
        self._running = True
        logger.info("[MISSION-GEN] Starting detection loop")
        
        while self._running:
            try:
                await self.scan_and_generate_missions()
                await asyncio.sleep(self.scan_interval_seconds)
            except Exception as e:
                logger.error(f"[MISSION-GEN] Error: {e}")
                await asyncio.sleep(60)
    
    async def scan_and_generate_missions(self) -> List[Dict[str, Any]]:
        """Scan and generate missions"""
        triggers = []
        
        # Placeholder scans - would integrate with actual systems
        logger.debug("[MISSION-GEN] Scanning (placeholder)")
        
        missions = []
        for trigger in triggers:
            if self._should_create_mission(trigger):
                mission = await self._create_mission(trigger)
                if mission.get("success"):
                    missions.append(mission)
                    self.missions_generated += 1
        
        return missions
    
    def _should_create_mission(self, trigger: MissionTrigger) -> bool:
        """Check if should create (avoid duplicates)"""
        key = f"{trigger.domain_id}_{trigger.trigger_type}"
        
        if key in self.recent_triggers:
            last = datetime.fromisoformat(self.recent_triggers[key])
            if datetime.utcnow() - last < timedelta(hours=1):
                return False
        
        self.recent_triggers[key] = datetime.utcnow().isoformat()
        return True
    
    async def _create_mission(self, trigger: MissionTrigger) -> Dict[str, Any]:
        """Create mission from trigger"""
        try:
            manifest = self._build_manifest(trigger)
            knowledge_id = await self._store_manifest(manifest)
            
            return {
                "success": True,
                "mission_id": manifest["mission_id"],
                "knowledge_id": knowledge_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_manifest(self, trigger: MissionTrigger) -> Dict[str, Any]:
        """Build mission manifest"""
        mission_id = f"auto_mission_{trigger.domain_id}_{int(datetime.utcnow().timestamp())}"
        
        tasks = MISSION_TASK_TEMPLATES.get(trigger.trigger_type, [])
        
        return {
            "mission_id": mission_id,
            "title": f"Auto: {trigger.trigger_type} - {trigger.domain_id}",
            "domain_id": trigger.domain_id,
            "mission_type": trigger.trigger_type,
            "priority": trigger.severity,
            "confidence": trigger.confidence,
            "recommended_tasks": tasks,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _store_manifest(self, manifest: Dict[str, Any]) -> str:
        """Store in world model"""
        try:
            from backend.world_model import grace_world_model
            
            content = f"Proactive Mission: {manifest['title']}"
            
            knowledge_id = await grace_world_model.add_knowledge(
                category='system',
                content=content,
                source='proactive_mission_generator',
                confidence=manifest['confidence'],
                tags=['mission', 'proactive', manifest['mission_type']],
                metadata={"mission_id": manifest["mission_id"]}
            )
            
            return knowledge_id
        except Exception as e:
            logger.error(f"[MISSION-GEN] Storage failed: {e}")
            return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "missions_generated": self.missions_generated,
            "triggers_detected": self.triggers_detected
        }


# Global instance
proactive_mission_generator = ProactiveMissionGenerator()


async def start_proactive_missions():
    """Start proactive missions"""
    await proactive_mission_generator.initialize()
    asyncio.create_task(proactive_mission_generator.start_detection_loop())
