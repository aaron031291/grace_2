"""
Proactive Mission Engine
Grace detects issues and creates missions automatically

Features:
- Continuous system monitoring
- Anomaly detection
- Automatic mission creation
- Priority-based execution
- Pattern recognition
- Predictive issue detection
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum

from .autonomous_mission_creator import autonomous_mission_creator
from .mission_control.hub import mission_control_hub
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class AnomalyType(str, Enum):
    """Types of anomalies Grace can detect"""
    HIGH_LATENCY = "high_latency"
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_MEMORY = "high_memory"
    HIGH_CPU = "high_cpu"
    LOW_TEST_COVERAGE = "low_test_coverage"
    SECURITY_VULNERABILITY = "security_vulnerability"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATABASE_ISSUES = "database_issues"
    INTEGRATION_FAILURE = "integration_failure"


@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_type: AnomalyType
    subsystem: str
    severity: str  # critical, high, medium, low
    description: str
    current_value: float
    threshold: float
    detected_at: datetime
    evidence: Dict[str, Any]


class ProactiveMissionEngine:
    """
    Proactive Mission Engine
    
    Grace continuously monitors the system and automatically:
    1. Detects anomalies and issues
    2. Creates missions to fix them
    3. Prioritizes by severity and impact
    4. Executes low-risk missions autonomously
    5. Escalates high-risk missions to you
    """
    
    def __init__(self):
        self.running = False
        
        # Detection settings
        self.check_interval = 60  # Check every minute
        self.anomalies_detected = 0
        self.missions_created = 0
        
        # Thresholds
        self.thresholds = {
            "latency_ms": 100.0,
            "error_rate": 0.05,  # 5%
            "memory_percent": 80.0,
            "cpu_percent": 80.0,
            "test_coverage": 80.0
        }
        
        # Recent anomalies (to avoid duplicates)
        self.recent_anomalies: List[Anomaly] = []
        self.anomaly_window = timedelta(minutes=30)
    
    async def start(self):
        """Start proactive mission engine"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("=" * 80)
        logger.info("PROACTIVE MISSION ENGINE - STARTING")
        logger.info("=" * 80)
        logger.info("[PROACTIVE] Grace will now detect and fix issues automatically!")
        logger.info(f"[PROACTIVE] Check interval: {self.check_interval}s")
        logger.info(f"[PROACTIVE] Thresholds: {self.thresholds}")
        logger.info("=" * 80)
        
        # Start detection loop
        asyncio.create_task(self._detection_loop())
        
        # Log to immutable log
        await immutable_log.append(
            actor="proactive_mission_engine",
            action="system_start",
            resource="proactive_detection",
            subsystem="mission_control",
            payload={"thresholds": self.thresholds},
            result="started"
        )
    
    async def stop(self):
        """Stop proactive mission engine"""
        self.running = False
        logger.info("[PROACTIVE] Proactive Mission Engine stopped")
    
    async def _detection_loop(self):
        """Continuous detection loop"""
        while self.running:
            try:
                logger.debug("[PROACTIVE] Running detection cycle...")
                
                # Detect anomalies
                anomalies = await self._detect_anomalies()
                
                if anomalies:
                    logger.info(f"[PROACTIVE] 🔍 Detected {len(anomalies)} anomalies")
                    
                    for anomaly in anomalies:
                        # Check if we've already created a mission for this
                        if not self._is_duplicate_anomaly(anomaly):
                            # Create mission
                            await self._create_mission_for_anomaly(anomaly)
                            
                            # Track anomaly
                            self.recent_anomalies.append(anomaly)
                            self.anomalies_detected += 1
                
                # Clean up old anomalies
                self._cleanup_old_anomalies()
                
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[PROACTIVE] Error in detection loop: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)
    
    async def _detect_anomalies(self) -> List[Anomaly]:
        """Detect anomalies across all systems"""
        anomalies = []
        
        # Check Mission Control health
        try:
            status = await mission_control_hub.get_status()
            
            # Check for degraded subsystems
            for subsystem in status.subsystems:
                if subsystem.status == "critical":
                    anomalies.append(Anomaly(
                        anomaly_type=AnomalyType.INTEGRATION_FAILURE,
                        subsystem=subsystem.subsystem_id,
                        severity="critical",
                        description=f"Subsystem {subsystem.subsystem_id} is in critical state",
                        current_value=0.0,
                        threshold=1.0,
                        detected_at=datetime.now(timezone.utc),
                        evidence={"subsystem_status": subsystem.status}
                    ))
                elif subsystem.status == "degraded":
                    anomalies.append(Anomaly(
                        anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                        subsystem=subsystem.subsystem_id,
                        severity="high",
                        description=f"Subsystem {subsystem.subsystem_id} is degraded",
                        current_value=0.5,
                        threshold=1.0,
                        detected_at=datetime.now(timezone.utc),
                        evidence={"subsystem_status": subsystem.status}
                    ))
        except Exception as e:
            logger.debug(f"[PROACTIVE] Could not check Mission Control health: {e}")
        
        # Check database latency (placeholder - would check actual metrics)
        # anomalies.extend(await self._check_database_latency())
        
        # Check error rates (placeholder - would check actual metrics)
        # anomalies.extend(await self._check_error_rates())
        
        # Check memory usage (placeholder - would check actual metrics)
        # anomalies.extend(await self._check_memory_usage())
        
        # Check test coverage (placeholder - would check actual metrics)
        # anomalies.extend(await self._check_test_coverage())
        
        return anomalies
    
    def _is_duplicate_anomaly(self, anomaly: Anomaly) -> bool:
        """Check if we've already detected this anomaly recently"""
        for recent in self.recent_anomalies:
            if (recent.anomaly_type == anomaly.anomaly_type and
                recent.subsystem == anomaly.subsystem):
                return True
        return False
    
    def _cleanup_old_anomalies(self):
        """Remove old anomalies from tracking"""
        now = datetime.now(timezone.utc)
        self.recent_anomalies = [
            a for a in self.recent_anomalies
            if now - a.detected_at < self.anomaly_window
        ]
    
    async def _create_mission_for_anomaly(self, anomaly: Anomaly):
        """Create autonomous mission for detected anomaly"""
        
        # Generate mission details
        title = self._generate_mission_title(anomaly)
        description = self._generate_mission_description(anomaly)
        rationale = self._generate_mission_rationale(anomaly)
        
        logger.info(f"[PROACTIVE] 🎯 Creating mission: {title}")
        
        try:
            # Create autonomous mission
            mission = await autonomous_mission_creator.create_autonomous_mission(
                title=title,
                description=description,
                rationale=rationale
            )
            
            self.missions_created += 1
            
            # Publish event
            await trigger_mesh.publish(TriggerEvent(
                event_type="proactive.mission_created",
                source="proactive_mission_engine",
                actor="grace",
                resource=mission.mission_id,
                payload={
                    "mission_id": mission.mission_id,
                    "anomaly_type": anomaly.anomaly_type.value,
                    "subsystem": anomaly.subsystem,
                    "severity": anomaly.severity
                }
            ))
            
            logger.info(f"[PROACTIVE] ✅ Mission created: {mission.mission_id}")
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Failed to create mission: {e}", exc_info=True)
    
    def _generate_mission_title(self, anomaly: Anomaly) -> str:
        """Generate mission title from anomaly"""
        titles = {
            AnomalyType.HIGH_LATENCY: f"Reduce latency in {anomaly.subsystem}",
            AnomalyType.HIGH_ERROR_RATE: f"Fix errors in {anomaly.subsystem}",
            AnomalyType.HIGH_MEMORY: f"Optimize memory usage in {anomaly.subsystem}",
            AnomalyType.HIGH_CPU: f"Optimize CPU usage in {anomaly.subsystem}",
            AnomalyType.LOW_TEST_COVERAGE: f"Improve test coverage for {anomaly.subsystem}",
            AnomalyType.SECURITY_VULNERABILITY: f"Fix security vulnerability in {anomaly.subsystem}",
            AnomalyType.PERFORMANCE_DEGRADATION: f"Improve performance of {anomaly.subsystem}",
            AnomalyType.DATABASE_ISSUES: f"Fix database issues in {anomaly.subsystem}",
            AnomalyType.INTEGRATION_FAILURE: f"Restore {anomaly.subsystem} integration"
        }
        return titles.get(anomaly.anomaly_type, f"Fix issue in {anomaly.subsystem}")
    
    def _generate_mission_description(self, anomaly: Anomaly) -> str:
        """Generate mission description from anomaly"""
        return f"{anomaly.description}. Current value: {anomaly.current_value}, Threshold: {anomaly.threshold}"
    
    def _generate_mission_rationale(self, anomaly: Anomaly) -> str:
        """Generate mission rationale from anomaly"""
        return f"Detected {anomaly.anomaly_type.value} in {anomaly.subsystem}. This is impacting system health and should be addressed."
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get proactive engine statistics"""
        return {
            "running": self.running,
            "anomalies_detected": self.anomalies_detected,
            "missions_created": self.missions_created,
            "recent_anomalies": len(self.recent_anomalies),
            "check_interval": self.check_interval,
            "thresholds": self.thresholds
        }


# Singleton instance
proactive_mission_engine = ProactiveMissionEngine()

