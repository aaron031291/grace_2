"""
Learning Mission Launcher
Autonomously launches and manages learning missions

Integrates with:
- Guardian mission system
- Web learning orchestrator
- GitHub knowledge miner
- RAG system for context retrieval
- Immutable log for traceability
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
import json

logger = logging.getLogger(__name__)


class LearningMission:
    """Represents a learning mission"""
    
    def __init__(
        self,
        mission_id: str,
        mission_type: str,
        description: str,
        context: Dict[str, Any],
        priority: float,
        launched_by: str
    ):
        self.mission_id = mission_id
        self.mission_type = mission_type
        self.description = description
        self.context = context
        self.priority = priority  # 0.0 - 1.0
        self.launched_by = launched_by
        self.status = 'pending'
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        
        # Risk/impact scoring
        self.risk_score: float = self._calculate_risk_score()
        self.impact_score: float = self._calculate_impact_score()
        self.combined_score: float = (self.risk_score * 0.4) + (self.impact_score * 0.6)
        
        # Suspension
        self.suspended = False
        self.suspension_reason: Optional[str] = None
    
    def _calculate_risk_score(self) -> float:
        """Calculate risk score based on context"""
        
        # Base risk from domain
        domain_risk = {
            'guardian': 0.9,
            'system': 0.8,
            'agent': 0.6,
            'remote_access': 0.5,
            'rag': 0.4
        }
        
        domain = self.context.get('domain', 'unknown')
        base_risk = domain_risk.get(domain, 0.5)
        
        # Adjust for severity
        severity = self.context.get('severity', 'medium')
        severity_multiplier = {
            'critical': 1.5,
            'high': 1.2,
            'medium': 1.0,
            'low': 0.7
        }
        
        return min(1.0, base_risk * severity_multiplier.get(severity, 1.0))
    
    def _calculate_impact_score(self) -> float:
        """Calculate impact score"""
        
        # Event count impact
        event_count = self.context.get('event_count', 1)
        count_score = min(1.0, event_count / 10)  # Max at 10 events
        
        # Urgency from context
        urgency = self.context.get('urgency_score', self.priority)
        
        # Recurrence impact
        recurrence = self.context.get('recurrence_score', 0.5)
        
        # Combined impact
        return (count_score * 0.3) + (urgency * 0.4) + (recurrence * 0.3)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'mission_id': self.mission_id,
            'mission_type': self.mission_type,
            'description': self.description,
            'context': self.context,
            'priority': self.priority,
            'launched_by': self.launched_by,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error': self.error,
            'risk_score': self.risk_score,
            'impact_score': self.impact_score,
            'combined_score': self.combined_score,
            'suspended': self.suspended,
            'suspension_reason': self.suspension_reason
        }


class LearningMissionLauncher:
    """
    Autonomous learning mission launcher
    
    Launches missions based on:
    - Event clusters from triage agent
    - Knowledge gaps detected by RAG
    - Explicit requests from other systems
    """
    
    def __init__(self):
        self.running = False
        self.missions: Dict[str, LearningMission] = {}
        self.active_missions: List[str] = []
        self.max_concurrent_missions = 3
        
        # Statistics
        self.stats = {
            'missions_launched': 0,
            'missions_completed': 0,
            'missions_failed': 0
        }
        
        # Dependencies
        self.message_bus = None
        self.immutable_log = None
        self.rag_system = None
        self.web_orchestrator = None
        self.github_miner = None
    
    async def start(self):
        """Start the mission launcher"""
        if self.running:
            return
        
        logger.info("[MISSION-LAUNCHER] Starting learning mission launcher...")
        
        # Initialize dependencies
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
        except ImportError:
            logger.warning("[MISSION-LAUNCHER] Message bus not available")
        
        try:
            from backend.core.immutable_log import immutable_log
            self.immutable_log = immutable_log
        except ImportError:
            logger.warning("[MISSION-LAUNCHER] Immutable log not available")
        
        try:
            from backend.orchestrators.web_learning_orchestrator import WebLearningOrchestrator
            self.web_orchestrator = WebLearningOrchestrator()
            await self.web_orchestrator.start()
        except ImportError as e:
            logger.info("[MISSION-LAUNCHER] Web learning orchestrator not available (will use direct scrapers)")
        except Exception as e:
            logger.warning(f"[MISSION-LAUNCHER] Web orchestrator startup issue: {e}")
        
        try:
            from backend.knowledge.github_knowledge_miner import GitHubKnowledgeMiner
            self.github_miner = GitHubKnowledgeMiner()
            await self.github_miner.start()
        except ImportError:
            logger.info("[MISSION-LAUNCHER] GitHub miner not available (will use alternatives)")
        except Exception as e:
            logger.warning(f"[MISSION-LAUNCHER] GitHub miner startup issue: {e}")
        
        self.running = True
        
        # Start mission processor
        asyncio.create_task(self._mission_processor())
        
        logger.info("[MISSION-LAUNCHER] ✅ Started")
        logger.info(f"[MISSION-LAUNCHER] Max concurrent missions: {self.max_concurrent_missions}")
    
    async def stop(self):
        """Stop the mission launcher"""
        self.running = False
        logger.info("[MISSION-LAUNCHER] Stopped")
    
    async def launch_mission(
        self,
        mission_type: str,
        description: str,
        context: Dict[str, Any],
        priority: float = 0.5,
        launched_by: str = 'system'
    ) -> str:
        """
        Launch a new learning mission
        
        Args:
            mission_type: Type of mission ('autonomous_learning', 'knowledge_gap', etc.)
            description: Human-readable description
            context: Mission context and data
            priority: Priority score (0-1)
            launched_by: Who/what launched this mission
            
        Returns:
            Mission ID
        """
        
        mission_id = f"mission_{uuid4().hex[:8]}"
        
        mission = LearningMission(
            mission_id=mission_id,
            mission_type=mission_type,
            description=description,
            context=context,
            priority=priority,
            launched_by=launched_by
        )
        
        self.missions[mission_id] = mission
        self.stats['missions_launched'] += 1
        
        logger.info(f"[MISSION-LAUNCHER] 🚀 Mission launched: {mission_id}")
        logger.info(f"[MISSION-LAUNCHER]   Type: {mission_type}")
        logger.info(f"[MISSION-LAUNCHER]   Description: {description}")
        logger.info(f"[MISSION-LAUNCHER]   Priority: {priority:.2f}")
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='learning_mission',
                subcategory='launched',
                data=mission.to_dict(),
                actor=launched_by,
                action='launch_mission',
                resource=mission_id
            )
        
        # Publish event
        if self.message_bus:
            await self.message_bus.publish('mission.created', mission.to_dict())
        
        return mission_id
    
    async def _mission_processor(self):
        """Process pending missions with priority-based selection"""
        
        logger.info("[MISSION-LAUNCHER] Mission processor started")
        logger.info("[MISSION-LAUNCHER] Priority scoring: (risk * 0.4) + (impact * 0.6)")
        
        while self.running:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Clean up completed missions
                self.active_missions = [
                    m_id for m_id in self.active_missions
                    if self.missions[m_id].status == 'running'
                ]
                
                # Suspend low-value missions if Guardian requests it
                await self._check_suspension_requests()
                
                # Can we start more missions?
                if len(self.active_missions) >= self.max_concurrent_missions:
                    continue
                
                # Get pending, non-suspended missions
                pending = [
                    m for m in self.missions.values()
                    if m.status == 'pending' and not m.suspended
                ]
                
                if not pending:
                    continue
                
                # Sort by combined score (risk + impact)
                pending.sort(key=lambda m: m.combined_score, reverse=True)
                
                # Start highest combined score mission
                mission = pending[0]
                
                logger.info(
                    f"[MISSION-LAUNCHER] Selected mission: {mission.mission_id} "
                    f"(combined_score={mission.combined_score:.2f}, "
                    f"risk={mission.risk_score:.2f}, impact={mission.impact_score:.2f})"
                )
                
                await self._execute_mission(mission)
                
            except Exception as e:
                logger.error(f"[MISSION-LAUNCHER] Error in processor: {e}", exc_info=True)
    
    async def _execute_mission(self, mission: LearningMission):
        """Execute a learning mission"""
        
        logger.info(f"[MISSION-LAUNCHER] Executing mission: {mission.mission_id}")
        
        mission.status = 'running'
        mission.started_at = datetime.utcnow()
        self.active_missions.append(mission.mission_id)
        
        try:
            # Request approval for mission execution
            approval_granted = await self._request_mission_approval(mission)
            
            if not approval_granted:
                raise Exception("Mission approval denied by governance system")
            
            # Retrieve context from RAG if needed
            rag_context = await self._get_rag_context(mission)
            
            # Execute based on mission type
            if mission.mission_type == 'autonomous_learning':
                result = await self._execute_autonomous_learning(mission, rag_context)
            elif mission.mission_type == 'knowledge_gap':
                result = await self._execute_knowledge_gap(mission, rag_context)
            elif mission.mission_type == 'pattern_learning':
                result = await self._execute_pattern_learning(mission, rag_context)
            else:
                result = await self._execute_generic_learning(mission, rag_context)
            
            mission.result = result
            mission.status = 'completed'
            mission.completed_at = datetime.utcnow()
            self.stats['missions_completed'] += 1
            
            logger.info(f"[MISSION-LAUNCHER] ✅ Mission completed: {mission.mission_id}")
            
            # Publish completion
            if self.message_bus:
                await self.message_bus.publish('mission.resolved', mission.to_dict())
        
        except Exception as e:
            mission.error = str(e)
            mission.status = 'failed'
            mission.completed_at = datetime.utcnow()
            self.stats['missions_failed'] += 1
            
            logger.error(f"[MISSION-LAUNCHER] ❌ Mission failed: {mission.mission_id} - {e}")
            
            # Publish failure
            if self.message_bus:
                await self.message_bus.publish('mission.failed', mission.to_dict())
        
        finally:
            # Log to immutable log
            if self.immutable_log:
                await self.immutable_log.append_entry(
                    category='learning_mission',
                    subcategory='completed' if mission.status == 'completed' else 'failed',
                    data=mission.to_dict(),
                    actor='mission_launcher',
                    action='complete_mission',
                    resource=mission.mission_id
                )
    
    async def _get_rag_context(self, mission: LearningMission) -> Dict[str, Any]:
        """Retrieve relevant context from RAG system"""
        
        # Extract key terms from mission
        query_terms = self._extract_query_terms(mission)
        
        # Query RAG (simulated for now)
        rag_context = {
            'query': query_terms,
            'relevant_docs': [],
            'confidence': 0.0
        }
        
        logger.info(f"[MISSION-LAUNCHER] Retrieved RAG context for: {mission.mission_id}")
        
        return rag_context
    
    def _extract_query_terms(self, mission: LearningMission) -> str:
        """Extract query terms from mission"""
        
        terms = []
        
        # Add domain
        if 'domain' in mission.context:
            terms.append(mission.context['domain'])
        
        # Add pattern type
        if 'pattern_type' in mission.context:
            terms.append(mission.context['pattern_type'])
        
        # Add description keywords
        desc_words = mission.description.lower().split()
        terms.extend([w for w in desc_words if len(w) > 4])
        
        return ' '.join(terms[:5])  # Top 5 terms
    
    async def _request_mission_approval(self, mission: LearningMission) -> bool:
        """
        Request approval for mission execution
        
        Returns:
            True if approved, False if denied
        """
        try:
            from backend.governance_system.inline_approval_engine import (
                inline_approval_engine,
                ResourceAccess
            )
            
            # Determine resource type based on mission context
            resource_type = 'staging_model'  # Default to staging
            if mission.context.get('modify_production', False):
                resource_type = 'production_model'
            
            # Create resource access request
            resource_access = ResourceAccess(
                resource_type=resource_type,
                resource_id=f"mission_{mission.mission_id}",
                action='modify',
                requester='learning_mission_service',
                mission_id=mission.mission_id,
                context={
                    'mission_type': mission.mission_type,
                    'priority': mission.priority,
                    'description': mission.description
                }
            )
            
            # Request approval
            result = await inline_approval_engine.request_approval(resource_access)
            
            logger.info(
                f"[MISSION-LAUNCHER] Approval result: {result.decision.value} "
                f"(risk: {result.risk_score:.2f})"
            )
            
            # Approved or auto-approved
            if result.decision.value in ['approved', 'auto_approved']:
                return True
            
            # Escalated or pending - wait for Guardian decision
            if result.decision.value == 'escalated':
                logger.warning(f"[MISSION-LAUNCHER] Mission escalated to Guardian: {mission.mission_id}")
                # For now, deny escalated missions
                # In production, would wait for Guardian decision
                return False
            
            # Denied
            logger.warning(f"[MISSION-LAUNCHER] Mission denied: {mission.mission_id} - {result.reason}")
            return False
        
        except Exception as e:
            logger.error(f"[MISSION-LAUNCHER] Approval request failed: {e}")
            # Fail safe - deny on error
            return False
    
    async def _execute_autonomous_learning(
        self,
        mission: LearningMission,
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute autonomous learning mission"""
        
        logger.info(f"[MISSION-LAUNCHER] Autonomous learning: {mission.description}")
        
        domain = mission.context.get('domain', 'unknown')
        pattern_type = mission.context.get('pattern_type', 'error')
        
        # Construct learning query
        query = f"{domain} {pattern_type} resolution best practices"
        
        # Learn from web if available
        web_result = {'sources': [], 'learned': False}
        if self.web_orchestrator:
            try:
                web_result = await self.web_orchestrator.learn_and_apply(
                    topic=query,
                    learning_type='web',
                    max_sources=3
                )
                logger.info(f"[MISSION-LAUNCHER] Learned from {len(web_result.get('sources', []))} web sources")
            except Exception as e:
                logger.warning(f"[MISSION-LAUNCHER] Web learning failed: {e}")
        else:
            # Fallback: Use web scraper directly
            try:
                from backend.utilities.safe_web_scraper import safe_web_scraper
                if safe_web_scraper.enabled:
                    web_result = await safe_web_scraper.search_and_learn(query, max_sources=3)
                    logger.info(f"[MISSION-LAUNCHER] Learned from {web_result.get('scraped', 0)} web sources (direct)")
            except Exception as e:
                logger.debug(f"[MISSION-LAUNCHER] Direct web scraper fallback failed: {e}")
        
        # Learn from GitHub if relevant
        github_result = {'repos': [], 'learned': False}
        if self.github_miner and domain in ['coding', 'agent', 'system']:
            try:
                github_result = await self.github_miner.learn_from_trending(
                    category='python',
                    max_repos=2
                )
                logger.info(f"[MISSION-LAUNCHER] Learned from {len(github_result.get('repos', []))} GitHub repos")
            except Exception as e:
                logger.warning(f"[MISSION-LAUNCHER] GitHub learning failed: {e}")
        
        return {
            'learning_method': 'autonomous',
            'query': query,
            'web_sources': len(web_result.get('sources', [])),
            'github_repos': len(github_result.get('repos', [])),
            'rag_context': rag_context,
            'knowledge_acquired': True
        }
    
    async def _execute_knowledge_gap(
        self,
        mission: LearningMission,
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute knowledge gap filling mission"""
        
        logger.info(f"[MISSION-LAUNCHER] Knowledge gap: {mission.description}")
        
        gap_topic = mission.context.get('topic', 'unknown')
        
        # Learn about the gap
        if self.web_orchestrator:
            result = await self.web_orchestrator.learn_and_apply(
                topic=gap_topic,
                learning_type='web',
                max_sources=5
            )
            
            return {
                'learning_method': 'knowledge_gap',
                'topic': gap_topic,
                'sources': len(result.get('sources', [])),
                'gap_filled': True
            }
        
        return {'learning_method': 'knowledge_gap', 'gap_filled': False}
    
    async def _execute_pattern_learning(
        self,
        mission: LearningMission,
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute pattern learning mission"""
        
        logger.info(f"[MISSION-LAUNCHER] Pattern learning: {mission.description}")
        
        return {
            'learning_method': 'pattern_learning',
            'patterns_learned': 0
        }
    
    async def _execute_generic_learning(
        self,
        mission: LearningMission,
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute generic learning mission"""
        
        logger.info(f"[MISSION-LAUNCHER] Generic learning: {mission.description}")
        
        return {
            'learning_method': 'generic',
            'completed': True
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get launcher statistics"""
        return {
            **self.stats,
            'running': self.running,
            'total_missions': len(self.missions),
            'active_missions': len(self.active_missions),
            'pending_missions': len([m for m in self.missions.values() if m.status == 'pending'])
        }
    
    async def _check_suspension_requests(self):
        """Check for suspension requests from Guardian or governance"""
        
        if not self.message_bus:
            return
        
        # This would be triggered by Guardian via message bus
        # For now, placeholder for the mechanism
        pass
    
    async def suspend_mission(
        self,
        mission_id: str,
        reason: str,
        suspended_by: str = 'system'
    ) -> bool:
        """
        Suspend a low-value mission
        
        Args:
            mission_id: Mission to suspend
            reason: Reason for suspension
            suspended_by: Who/what suspended it
            
        Returns:
            True if suspended, False if not found or already running
        """
        
        if mission_id not in self.missions:
            return False
        
        mission = self.missions[mission_id]
        
        # Can only suspend pending missions
        if mission.status != 'pending':
            logger.warning(f"[MISSION-LAUNCHER] Cannot suspend {mission.status} mission: {mission_id}")
            return False
        
        mission.suspended = True
        mission.suspension_reason = reason
        self.stats['missions_suspended'] = self.stats.get('missions_suspended', 0) + 1
        
        logger.warning(
            f"[MISSION-LAUNCHER] Mission suspended: {mission_id} "
            f"(by {suspended_by}, reason: {reason})"
        )
        
        # Log to immutable log
        if hasattr(self, 'immutable_log') and self.immutable_log:
            await self.immutable_log.append_entry(
                category='learning_mission',
                subcategory='suspended',
                data={
                    'mission_id': mission_id,
                    'reason': reason,
                    'suspended_by': suspended_by
                },
                actor=suspended_by,
                action='suspend_mission',
                resource=mission_id
            )
        
        return True
    
    async def resume_mission(self, mission_id: str) -> bool:
        """Resume a suspended mission"""
        
        if mission_id not in self.missions:
            return False
        
        mission = self.missions[mission_id]
        
        if not mission.suspended:
            return False
        
        mission.suspended = False
        mission.suspension_reason = None
        
        logger.info(f"[MISSION-LAUNCHER] Mission resumed: {mission_id}")
        
        return True
    
    def get_missions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get missions, optionally filtered by status"""
        
        missions = []
        
        for mission in self.missions.values():
            if status and mission.status != status:
                continue
            
            missions.append(mission.to_dict())
        
        # Sort by combined score (highest priority first)
        missions.sort(key=lambda m: m.get('combined_score', 0), reverse=True)
        
        return missions


# Global instance
learning_mission_launcher = LearningMissionLauncher()
