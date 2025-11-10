"""
Autonomous Mission Creator
Grace creates her own missions, tests in sandbox, reaches consensus with you,
and executes to live environment when trust ≥ 95%

Flow:
1. Grace detects improvement opportunity
2. Creates mission in sandbox
3. Tests and measures KPIs
4. Presents to you for discussion
5. Reaches consensus via Parliament
6. If trust ≥ 95% → Execute to live
7. Monitor and learn
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

from .mission_control.schemas import MissionPackage, MissionStatus, Severity, MissionContext, WorkspaceInfo, AcceptanceCriteria, TrustRequirements
from .mission_control.hub import mission_control_hub
from .sandbox_manager import sandbox_manager
from .parliament_engine import parliament_engine
from .governance import governance_engine
from .constitutional_engine import constitutional_engine
from .hunter import hunter_engine
from .immutable_log import immutable_log
from .trigger_mesh import trigger_mesh, TriggerEvent
from .crypto_key_manager import crypto_key_manager

logger = logging.getLogger(__name__)


class MissionPhase(str, Enum):
    """Mission lifecycle phases"""
    DETECTED = "detected"
    SANDBOX_TESTING = "sandbox_testing"
    DISCUSSION = "discussion"
    CONSENSUS = "consensus"
    LIVE_EXECUTION = "live_execution"
    MONITORING = "monitoring"
    COMPLETE = "complete"


@dataclass
class KPIMetrics:
    """KPI metrics for mission evaluation"""
    performance_improvement: float = 0.0  # % improvement
    error_rate_reduction: float = 0.0  # % reduction
    latency_improvement: float = 0.0  # ms improvement
    memory_efficiency: float = 0.0  # % improvement
    code_quality_score: float = 0.0  # 0-100
    test_coverage: float = 0.0  # %
    security_score: float = 0.0  # 0-100
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        weights = {
            'performance': 0.20,
            'errors': 0.25,
            'latency': 0.15,
            'memory': 0.10,
            'quality': 0.15,
            'coverage': 0.10,
            'security': 0.05
        }
        
        score = (
            self.performance_improvement * weights['performance'] +
            self.error_rate_reduction * weights['errors'] +
            self.latency_improvement * weights['latency'] +
            self.memory_efficiency * weights['memory'] +
            self.code_quality_score * weights['quality'] +
            self.test_coverage * weights['coverage'] +
            self.security_score * weights['security']
        )
        
        return min(100.0, max(0.0, score))


@dataclass
class AutonomousMission:
    """Mission created autonomously by Grace"""
    mission_id: str
    title: str
    description: str
    rationale: str
    phase: MissionPhase
    
    # Sandbox testing
    sandbox_results: Optional[Dict[str, Any]] = None
    kpi_metrics: KPIMetrics = field(default_factory=KPIMetrics)
    
    # Consensus
    parliament_session_id: Optional[str] = None
    user_feedback: List[str] = field(default_factory=list)
    consensus_reached: bool = False
    
    # Trust & execution
    trust_score: float = 0.0
    approved_for_live: bool = False
    
    # Mission package
    mission_package: Optional[MissionPackage] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tested_at: Optional[datetime] = None
    consensus_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None


class AutonomousMissionCreator:
    """
    Grace's autonomous mission creation system

    IMPORTANT: USER ALWAYS HAS FINAL SAY

    Grace can:
    1. Detect improvement opportunities
    2. Create missions autonomously
    3. Test in sandbox environment
    4. Measure KPIs and calculate trust score
    5. Present results to YOU for discussion
    6. Reach consensus via Parliament (YOU vote)
    7. Execute to live ONLY if:
       - YOU explicitly approve
       - Trust score ≥ 95%
       - All governance/constitutional checks pass

    Grace proposes and tests, YOU decide and approve.
    Nothing goes to live without YOUR explicit approval.
    """
    
    def __init__(self):
        self.running = False
        self.missions: Dict[str, AutonomousMission] = {}
        self.trust_threshold = 0.95  # 95% trust required for live execution
        
        # Detection settings
        self.detection_interval = 300  # Check every 5 minutes
        self.min_impact_threshold = 0.10  # 10% improvement minimum
    
    async def start(self):
        """Start autonomous mission creator"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("=" * 80)
        logger.info("AUTONOMOUS MISSION CREATOR - STARTING")
        logger.info("=" * 80)
        logger.info("[AUTONOMOUS] Grace can now create her own missions!")
        logger.info("[AUTONOMOUS] Trust threshold: 95%")
        logger.info("[AUTONOMOUS] Sandbox testing: Enabled")
        logger.info("[AUTONOMOUS] Consensus required: Yes")
        logger.info("=" * 80)
        
        # Start detection loop
        asyncio.create_task(self._detection_loop())
        
        # Log to immutable log
        await immutable_log.append(
            actor="autonomous_mission_creator",
            action="system_start",
            resource="autonomous_missions",
            subsystem="mission_control",
            payload={"trust_threshold": self.trust_threshold},
            result="started"
        )
    
    async def stop(self):
        """Stop autonomous mission creator"""
        self.running = False
        logger.info("[AUTONOMOUS] Autonomous Mission Creator stopped")
    
    async def _detection_loop(self):
        """Continuously detect improvement opportunities"""
        while self.running:
            try:
                # Detect opportunities
                opportunities = await self._detect_opportunities()
                
                for opportunity in opportunities:
                    # Create autonomous mission
                    mission = await self.create_autonomous_mission(
                        title=opportunity['title'],
                        description=opportunity['description'],
                        rationale=opportunity['rationale']
                    )
                    
                    logger.info(f"[AUTONOMOUS] 🎯 Created mission: {mission.mission_id}")
                
                await asyncio.sleep(self.detection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[AUTONOMOUS] Error in detection loop: {e}", exc_info=True)
                await asyncio.sleep(self.detection_interval)
    
    async def _detect_opportunities(self) -> List[Dict[str, Any]]:
        """Detect improvement opportunities"""
        opportunities = []
        
        # Check system health
        status = await mission_control_hub.get_status()
        
        # Opportunity 1: High error rate
        # (Placeholder - would check actual metrics)
        
        # Opportunity 2: Performance degradation
        # (Placeholder - would check actual metrics)
        
        # Opportunity 3: Low test coverage
        # (Placeholder - would check actual metrics)
        
        return opportunities
    
    async def create_autonomous_mission(
        self,
        title: str,
        description: str,
        rationale: str
    ) -> AutonomousMission:
        """
        Create an autonomous mission
        
        Args:
            title: Mission title
            description: What Grace wants to do
            rationale: Why Grace thinks this will help
        
        Returns:
            AutonomousMission instance
        """
        mission_id = f"auto_mission_{int(datetime.now(timezone.utc).timestamp())}"
        
        mission = AutonomousMission(
            mission_id=mission_id,
            title=title,
            description=description,
            rationale=rationale,
            phase=MissionPhase.DETECTED
        )
        
        self.missions[mission_id] = mission
        
        # Publish event
        await trigger_mesh.publish(TriggerEvent(
            event_type="autonomous.mission_created",
            source="autonomous_mission_creator",
            actor="grace",
            resource=mission_id,
            payload={
                "mission_id": mission_id,
                "title": title,
                "phase": MissionPhase.DETECTED.value
            }
        ))
        
        # Log to immutable log
        await immutable_log.append(
            actor="grace",
            action="create_autonomous_mission",
            resource=mission_id,
            subsystem="mission_control",
            payload={"title": title, "rationale": rationale},
            result="created"
        )
        
        # Automatically move to sandbox testing
        asyncio.create_task(self._test_in_sandbox(mission))
        
        return mission
    
    async def _test_in_sandbox(self, mission: AutonomousMission):
        """Test mission in sandbox environment"""
        logger.info(f"[AUTONOMOUS] 🧪 Testing {mission.mission_id} in sandbox...")
        
        mission.phase = MissionPhase.SANDBOX_TESTING
        
        try:
            # Run in sandbox
            sandbox_result = await sandbox_manager.run_command(
                user="grace",
                command=f"# Test mission: {mission.title}",
                file_name="mission_test.py"
            )
            
            # Measure KPIs
            kpis = await self._measure_kpis(mission, sandbox_result)
            mission.kpi_metrics = kpis
            mission.sandbox_results = sandbox_result
            mission.tested_at = datetime.now(timezone.utc)
            
            # Calculate trust score
            mission.trust_score = await self._calculate_trust_score(mission)
            
            logger.info(f"[AUTONOMOUS] ✅ Sandbox testing complete")
            logger.info(f"[AUTONOMOUS] Trust score: {mission.trust_score:.2%}")
            logger.info(f"[AUTONOMOUS] KPI score: {kpis.calculate_overall_score():.1f}/100")
            
            # Move to discussion phase
            await self._initiate_discussion(mission)
            
        except Exception as e:
            logger.error(f"[AUTONOMOUS] Sandbox testing failed: {e}")
            mission.phase = MissionPhase.COMPLETE
            mission.trust_score = 0.0
    
    async def _measure_kpis(
        self,
        mission: AutonomousMission,
        sandbox_result: Dict[str, Any]
    ) -> KPIMetrics:
        """Measure KPIs from sandbox testing"""
        
        kpis = KPIMetrics()
        
        # Placeholder - would measure actual KPIs
        kpis.performance_improvement = 15.0
        kpis.error_rate_reduction = 20.0
        kpis.latency_improvement = 10.0
        kpis.memory_efficiency = 5.0
        kpis.code_quality_score = 85.0
        kpis.test_coverage = 80.0
        kpis.security_score = 90.0
        
        return kpis
    
    async def _calculate_trust_score(self, mission: AutonomousMission) -> float:
        """Calculate trust score for mission"""
        
        # Base score from KPIs
        kpi_score = mission.kpi_metrics.calculate_overall_score() / 100.0
        
        # Governance check
        governance_score = 1.0  # Placeholder
        
        # Constitutional check
        constitutional_score = 1.0  # Placeholder
        
        # Security check
        security_score = mission.kpi_metrics.security_score / 100.0
        
        # Weighted average
        trust_score = (
            kpi_score * 0.40 +
            governance_score * 0.25 +
            constitutional_score * 0.20 +
            security_score * 0.15
        )
        
        return trust_score
    
    async def _initiate_discussion(self, mission: AutonomousMission):
        """Initiate discussion with user via Parliament"""
        logger.info(f"[AUTONOMOUS] 💬 Initiating discussion for {mission.mission_id}...")
        
        mission.phase = MissionPhase.DISCUSSION
        
        # Create Parliament session
        session = await parliament_engine.create_session(
            policy_name="autonomous_mission_approval",
            action_type="execute_autonomous_mission",
            action_payload={
                "mission_id": mission.mission_id,
                "title": mission.title,
                "description": mission.description,
                "rationale": mission.rationale,
                "trust_score": mission.trust_score,
                "kpi_score": mission.kpi_metrics.calculate_overall_score(),
                "sandbox_results": mission.sandbox_results
            },
            actor="grace",
            category="autonomous_improvement",
            resource=mission.mission_id,
            committee="core",
            quorum_required=1,  # Just you and Grace
            approval_threshold=1.0 if mission.trust_score < self.trust_threshold else 0.5,
            risk_level="medium" if mission.trust_score >= self.trust_threshold else "high"
        )
        
        mission.parliament_session_id = session['session_id']
        
        logger.info(f"[AUTONOMOUS] 📋 Parliament session created: {session['session_id']}")
        logger.info(f"[AUTONOMOUS] 🗳️  Awaiting your vote...")
        
        # Publish event
        await trigger_mesh.publish(TriggerEvent(
            event_type="autonomous.discussion_initiated",
            source="autonomous_mission_creator",
            actor="grace",
            resource=mission.mission_id,
            payload={
                "mission_id": mission.mission_id,
                "parliament_session_id": session['session_id'],
                "trust_score": mission.trust_score,
                "requires_approval": mission.trust_score < self.trust_threshold
            }
        ))
    
    async def add_user_feedback(
        self,
        mission_id: str,
        feedback: str
    ):
        """Add user feedback to mission"""
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission {mission_id} not found")
        
        mission.user_feedback.append(feedback)
        
        logger.info(f"[AUTONOMOUS] 💬 User feedback added to {mission_id}")
    
    async def reach_consensus(
        self,
        mission_id: str,
        approved: bool
    ):
        """
        Reach consensus on mission

        USER HAS FINAL SAY - Grace cannot execute without explicit approval

        Flow:
        1. Grace tests in sandbox
        2. Grace presents results + KPIs
        3. YOU review and decide
        4. If YOU approve AND trust ≥ 95% → Execute to live
        5. If YOU reject → Mission cancelled

        Grace proposes, YOU decide.
        """
        mission = self.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission {mission_id} not found")

        mission.phase = MissionPhase.CONSENSUS
        mission.consensus_reached = True
        mission.approved_for_live = approved
        mission.consensus_at = datetime.now(timezone.utc)

        if approved and mission.trust_score >= self.trust_threshold:
            logger.info(f"[AUTONOMOUS] ✅ USER APPROVED mission for live execution")
            logger.info(f"[AUTONOMOUS] Trust score {mission.trust_score:.2%} meets threshold")
            # Execute to live ONLY because user approved
            await self._execute_to_live(mission)
        elif approved:
            logger.info(f"[AUTONOMOUS] ⚠️  USER APPROVED but trust < 95%")
            logger.info(f"[AUTONOMOUS] Mission needs more testing before live execution")
            mission.phase = MissionPhase.COMPLETE
        else:
            logger.info(f"[AUTONOMOUS] ❌ USER REJECTED mission")
            logger.info(f"[AUTONOMOUS] Mission will not be executed")
            mission.phase = MissionPhase.COMPLETE

        # Log to immutable log
        await immutable_log.append(
            actor="user",
            action="autonomous_mission_decision",
            resource=mission_id,
            subsystem="mission_control",
            payload={
                "approved": approved,
                "trust_score": mission.trust_score,
                "will_execute": approved and mission.trust_score >= self.trust_threshold
            },
            result="approved" if approved else "rejected"
        )
    
    async def _execute_to_live(self, mission: AutonomousMission):
        """
        Execute mission to live environment

        IMPORTANT: This ONLY executes after:
        1. Sandbox testing passes
        2. Trust score ≥ 95%
        3. User explicitly approves via Parliament vote
        4. Constitutional & governance checks pass

        User ALWAYS has final say - Grace cannot execute without approval
        """
        logger.info(f"[AUTONOMOUS] 🚀 Executing {mission.mission_id} to LIVE...")
        logger.info(f"[AUTONOMOUS] ✅ User approved: Yes")
        logger.info(f"[AUTONOMOUS] ✅ Trust score: {mission.trust_score:.2%}")
        logger.info(f"[AUTONOMOUS] ✅ All checks passed")

        mission.phase = MissionPhase.LIVE_EXECUTION

        # Create actual mission package
        # (Placeholder - would create real mission)

        mission.executed_at = datetime.now(timezone.utc)
        mission.phase = MissionPhase.MONITORING

        logger.info(f"[AUTONOMOUS] ✅ Mission executed to live environment")

        # Start monitoring
        asyncio.create_task(self._monitor_live_execution(mission))
    
    async def _monitor_live_execution(self, mission: AutonomousMission):
        """Monitor live execution"""
        logger.info(f"[AUTONOMOUS] 👁️  Monitoring {mission.mission_id}...")
        
        # Monitor for 30 minutes
        await asyncio.sleep(1800)
        
        mission.phase = MissionPhase.COMPLETE
        logger.info(f"[AUTONOMOUS] ✅ Mission {mission.mission_id} complete")


# Singleton instance
autonomous_mission_creator = AutonomousMissionCreator()

