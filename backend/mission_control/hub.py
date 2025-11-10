"""
Mission Control Hub
Central coordination point for all autonomous operations

Features:
- Git state tracking
- Active mission management
- Health metrics aggregation
- Trust score management
- CAPA integration
- Diagnostics coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone, timedelta
from pathlib import Path
import subprocess
import hashlib
import json

from .schemas import (
    MissionPackage, MissionStatus, Severity, SubsystemHealth,
    MissionControlStatus, RemediationEvent, TestResult, MetricObservation
)
from ..immutable_log import immutable_log
from ..trigger_mesh import trigger_mesh, TriggerEvent
from ..models import async_session

logger = logging.getLogger(__name__)


class MissionControlHub:
    """
    Central Mission Control Hub
    
    This is the single source of truth for:
    - Current system state (git, config, environment)
    - Active missions and their status
    - Health metrics and diagnostics
    - Trust scores and permissions
    - CAPA tickets and remediation history
    """
    
    def __init__(self):
        self.running = False
        
        # Mission storage
        self.missions: Dict[str, MissionPackage] = {}
        self.mission_queue: List[str] = []  # Ordered by priority
        
        # System state
        self.git_sha: Optional[str] = None
        self.git_branch: Optional[str] = None
        self.config_hash: Optional[str] = None
        self.grace_version: str = "2.0.0"
        self.environment: str = "prod"
        
        # Health tracking
        self.subsystem_health: Dict[str, SubsystemHealth] = {}
        
        # Metrics catalog (loaded from config)
        self.metrics_catalog: Dict[str, Dict] = {}
        
        # Trust scores (agent_id -> score)
        self.trust_scores: Dict[str, float] = {}
        
        # CAPA integration
        self.capa_tickets: Dict[str, Dict] = {}
        
        # Diagnostics & stress test results
        self.diagnostics_reports: Dict[str, Dict] = {}
        self.stress_test_results: Dict[str, Dict] = {}
        
        # Agent registry
        self.registered_agents: Dict[str, Dict] = {}
    
    async def start(self):
        """Start Mission Control Hub"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("=" * 80)
        logger.info("MISSION CONTROL HUB - STARTING")
        logger.info("=" * 80)
        
        # Detect git state
        await self._detect_git_state()
        logger.info(f"[MISSION_CONTROL] Git: {self.git_branch}@{self.git_sha[:8]}")
        
        # Calculate config hash
        await self._calculate_config_hash()
        logger.info(f"[MISSION_CONTROL] Config hash: {self.config_hash[:16]}...")
        
        # Load metrics catalog
        await self._load_metrics_catalog()
        logger.info(f"[MISSION_CONTROL] Loaded {len(self.metrics_catalog)} metrics")
        
        # Initialize subsystem health
        await self._initialize_subsystem_health()
        logger.info(f"[MISSION_CONTROL] Tracking {len(self.subsystem_health)} subsystems")
        
        # Load trust scores
        await self._load_trust_scores()
        logger.info(f"[MISSION_CONTROL] Loaded {len(self.trust_scores)} trust scores")
        
        # Subscribe to events
        await self._subscribe_to_events()
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[MISSION_CONTROL] ✅ Mission Control Hub OPERATIONAL")
        logger.info("=" * 80)
        
        # Log to immutable log
        await immutable_log.append(
            actor="mission_control_hub",
            action="system_start",
            resource="mission_control",
            subsystem="mission_control",
            payload={
                "git_sha": self.git_sha,
                "git_branch": self.git_branch,
                "environment": self.environment
            },
            result="started"
        )
    
    async def stop(self):
        """Stop Mission Control Hub"""
        self.running = False
        logger.info("[MISSION_CONTROL] Mission Control Hub stopped")
    
    async def _detect_git_state(self):
        """Detect current git SHA and branch"""
        try:
            # Get current SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            if result.returncode == 0:
                self.git_sha = result.stdout.strip()
            
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            if result.returncode == 0:
                self.git_branch = result.stdout.strip()
        except Exception as e:
            logger.warning(f"[MISSION_CONTROL] Could not detect git state: {e}")
            self.git_sha = "unknown"
            self.git_branch = "unknown"
    
    async def _calculate_config_hash(self):
        """Calculate hash of current configuration"""
        try:
            config_files = [
                "config/metrics_catalog.yaml",
                "config/governance_policies.yaml",
                ".env"
            ]
            
            hasher = hashlib.sha256()
            for config_file in config_files:
                path = Path(__file__).parent.parent.parent / config_file
                if path.exists():
                    hasher.update(path.read_bytes())
            
            self.config_hash = f"sha256:{hasher.hexdigest()}"
        except Exception as e:
            logger.warning(f"[MISSION_CONTROL] Could not calculate config hash: {e}")
            self.config_hash = "unknown"
    
    async def _load_metrics_catalog(self):
        """Load metrics catalog from config"""
        try:
            catalog_path = Path(__file__).parent.parent.parent / "config" / "metrics_catalog.yaml"
            if catalog_path.exists():
                import yaml
                with open(catalog_path) as f:
                    catalog = yaml.safe_load(f)
                    self.metrics_catalog = catalog.get("metrics", {})
        except Exception as e:
            logger.warning(f"[MISSION_CONTROL] Could not load metrics catalog: {e}")
    
    async def _initialize_subsystem_health(self):
        """Initialize health tracking for all subsystems"""
        subsystems = [
            "trigger_mesh", "immutable_log", "governance", "hunter",
            "elite_self_healing", "elite_coding_agent", "shared_orchestrator",
            "memory_kernel", "code_kernel", "intelligence_kernel",
            "verification_kernel", "infrastructure_kernel"
        ]
        
        for subsystem_id in subsystems:
            self.subsystem_health[subsystem_id] = SubsystemHealth(
                subsystem_id=subsystem_id,
                status="unknown",
                trust_score=1.0
            )
    
    async def _load_trust_scores(self):
        """Load trust scores from database"""
        try:
            async with async_session() as session:
                from sqlalchemy import text
                result = await session.execute(
                    text("SELECT agent_id, trust_score FROM agent_trust")
                )
                for row in result:
                    self.trust_scores[row[0]] = row[1]
        except Exception as e:
            logger.debug(f"[MISSION_CONTROL] Could not load trust scores: {e}")
    
    async def _subscribe_to_events(self):
        """Subscribe to trigger mesh events"""
        await trigger_mesh.subscribe("mission.*", self._handle_mission_event)
        await trigger_mesh.subscribe("health.*", self._handle_health_event)
        await trigger_mesh.subscribe("diagnostics.*", self._handle_diagnostics_event)
        logger.info("[MISSION_CONTROL] Subscribed to trigger mesh events")
    
    async def _handle_mission_event(self, event: TriggerEvent):
        """Handle mission-related events"""
        if event.event_type == "mission.created":
            mission_id = event.payload.get("mission_id")
            if mission_id and mission_id in self.missions:
                logger.info(f"[MISSION_CONTROL] Mission created: {mission_id}")
    
    async def _handle_health_event(self, event: TriggerEvent):
        """Handle health check events"""
        subsystem_id = event.payload.get("subsystem_id")
        if subsystem_id and subsystem_id in self.subsystem_health:
            self.subsystem_health[subsystem_id].status = event.payload.get("status", "unknown")
            self.subsystem_health[subsystem_id].last_check = datetime.now(timezone.utc)
    
    async def _handle_diagnostics_event(self, event: TriggerEvent):
        """Handle diagnostics events"""
        report_id = event.payload.get("report_id")
        if report_id:
            self.diagnostics_reports[report_id] = event.payload
    
    async def _monitoring_loop(self):
        """Monitor system health and mission progress"""
        while self.running:
            try:
                # Update subsystem health
                await self._update_subsystem_health()
                
                # Check mission timeouts
                await self._check_mission_timeouts()
                
                # Update metrics
                await self._update_metrics()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[MISSION_CONTROL] Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def _update_subsystem_health(self):
        """Update health status of all subsystems"""
        # This would query actual subsystem health endpoints
        pass
    
    async def _check_mission_timeouts(self):
        """Check for missions that have timed out"""
        now = datetime.now(timezone.utc)
        for mission_id, mission in self.missions.items():
            if mission.status == MissionStatus.IN_PROGRESS:
                # Check if mission has been running too long
                elapsed = (now - mission.updated_at).total_seconds()
                if elapsed > 3600:  # 1 hour timeout
                    logger.warning(f"[MISSION_CONTROL] Mission {mission_id} timed out")
                    mission.status = MissionStatus.ESCALATED
                    mission.add_remediation_event(
                        actor="mission_control_hub",
                        role="system",
                        action="timeout_escalation",
                        result="Mission exceeded 1 hour timeout",
                        success=False
                    )
    
    async def _update_metrics(self):
        """Update metrics from all subsystems"""
        # This would collect metrics from subsystems
        pass
    
    # ========== Public API ==========
    
    async def create_mission(self, mission: MissionPackage) -> str:
        """
        Create a new mission
        
        Args:
            mission: Mission package
        
        Returns:
            Mission ID
        """
        # Store mission
        self.missions[mission.mission_id] = mission
        
        # Add to queue (sorted by severity)
        self.mission_queue.append(mission.mission_id)
        self._sort_mission_queue()
        
        # Publish event
        await trigger_mesh.publish(TriggerEvent(
            event_type="mission.created",
            source="mission_control_hub",
            actor="mission_control_hub",
            resource=mission.mission_id,
            payload={
                "mission_id": mission.mission_id,
                "subsystem_id": mission.subsystem_id,
                "severity": mission.severity.value,
                "assigned_to": mission.assigned_to
            }
        ))
        
        # Log to immutable log
        await immutable_log.append(
            actor="mission_control_hub",
            action="mission_created",
            resource=mission.mission_id,
            subsystem="mission_control",
            payload=mission.dict(),
            result="created"
        )
        
        logger.info(f"[MISSION_CONTROL] Created mission: {mission.mission_id}")
        
        return mission.mission_id
    
    def _sort_mission_queue(self):
        """Sort mission queue by severity and age"""
        severity_order = {
            Severity.CRITICAL: 4,
            Severity.HIGH: 3,
            Severity.MEDIUM: 2,
            Severity.LOW: 1
        }
        
        self.mission_queue.sort(
            key=lambda mid: (
                -severity_order.get(self.missions[mid].severity, 0),
                self.missions[mid].created_at
            )
        )
    
    async def get_mission(self, mission_id: str) -> Optional[MissionPackage]:
        """Get mission by ID"""
        return self.missions.get(mission_id)
    
    async def update_mission(self, mission_id: str, mission: MissionPackage):
        """Update mission"""
        self.missions[mission_id] = mission
        mission.updated_at = datetime.now(timezone.utc)
        
        # Publish event
        await trigger_mesh.publish(TriggerEvent(
            event_type="mission.updated",
            source="mission_control_hub",
            actor="mission_control_hub",
            resource=mission_id,
            payload={"mission_id": mission_id, "status": mission.status.value}
        ))
    
    async def get_status(self) -> MissionControlStatus:
        """Get overall Mission Control status"""
        total = len(self.missions)
        open_count = len([m for m in self.missions.values() if m.status == MissionStatus.OPEN])
        in_progress = len([m for m in self.missions.values() if m.status == MissionStatus.IN_PROGRESS])
        resolved = len([m for m in self.missions.values() if m.status == MissionStatus.RESOLVED])
        
        # Determine overall health
        critical_subsystems = [s for s in self.subsystem_health.values() if s.status == "critical"]
        if critical_subsystems:
            overall_health = "critical"
        elif any(s.status == "degraded" for s in self.subsystem_health.values()):
            overall_health = "degraded"
        else:
            overall_health = "healthy"
        
        return MissionControlStatus(
            git_sha=self.git_sha or "unknown",
            git_branch=self.git_branch or "unknown",
            grace_version=self.grace_version,
            environment=self.environment,
            total_missions=total,
            open_missions=open_count,
            in_progress_missions=in_progress,
            resolved_missions=resolved,
            subsystems=list(self.subsystem_health.values()),
            diagnostics_reports_count=len(self.diagnostics_reports),
            stress_test_results_count=len(self.stress_test_results),
            capa_tickets_count=len(self.capa_tickets),
            overall_health=overall_health
        )
    
    async def get_next_mission(self, agent_id: str, agent_role: str) -> Optional[MissionPackage]:
        """
        Get next mission for an agent
        
        Args:
            agent_id: Agent identifier
            agent_role: Agent role
        
        Returns:
            Next mission or None
        """
        trust_score = self.trust_scores.get(agent_id, 0.5)
        
        for mission_id in self.mission_queue:
            mission = self.missions[mission_id]
            
            # Skip if not open
            if mission.status != MissionStatus.OPEN:
                continue
            
            # Check if agent can execute
            if mission.can_agent_execute(agent_id, agent_role, trust_score):
                return mission
        
        return None
    
    def get_trust_score(self, agent_id: str) -> float:
        """Get trust score for an agent"""
        return self.trust_scores.get(agent_id, 0.5)
    
    def update_trust_score(self, agent_id: str, score: float):
        """Update trust score for an agent"""
        self.trust_scores[agent_id] = max(0.0, min(1.0, score))


# Singleton instance
mission_control_hub = MissionControlHub()

