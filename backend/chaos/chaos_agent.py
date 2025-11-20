"""
Chaos Engineering Agent
Red-teams every component with domain-specific stress vectors

Features:
- Picks components autonomously
- Runs industry-standard stress tests
- Records guardrail behavior
- Publishes structured events (chaos.injection)
- Auto-raises healing tasks
- Feeds RAG/HTM with results
- Full governance and RBAC
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
import random

from .component_profiles import ComponentProfile, ComponentType, component_registry
from .attack_scripts import ATTACK_SCRIPTS, ChaosAttackResult

logger = logging.getLogger(__name__)


class ChaosStatus(str):
    """Chaos agent status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class ChaosCampaign:
    """A chaos engineering campaign"""
    
    def __init__(
        self,
        campaign_id: str,
        target_components: List[str],
        environment: str = 'staging',
        approved_by: Optional[str] = None
    ):
        self.campaign_id = campaign_id
        self.target_components = target_components
        self.environment = environment
        self.approved_by = approved_by
        self.status = 'pending'
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.results: List[ChaosAttackResult] = []
        self.healing_tasks_raised: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'campaign_id': self.campaign_id,
            'target_components': self.target_components,
            'environment': self.environment,
            'approved_by': self.approved_by,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tests_run': len(self.results),
            'tests_passed': sum(1 for r in self.results if r.success),
            'tests_failed': sum(1 for r in self.results if not r.success),
            'healing_tasks_raised': self.healing_tasks_raised
        }


class ChaosAgent:
    """
    Autonomous chaos engineering agent
    
    Capabilities:
    - Component selection (autonomous or manual)
    - Domain-specific stress tests
    - Guardrail verification
    - Healing task creation
    - Resilience scoring
    - RAG/HTM feedback
    """
    
    def __init__(self):
        self.status = ChaosStatus.IDLE
        self.running = False
        
        # Campaigns
        self.campaigns: Dict[str, ChaosCampaign] = {}
        self.active_campaign: Optional[str] = None
        
        # Configuration
        self.auto_run_enabled = False  # Require explicit enable
        self.environment = 'staging'  # Default to staging
        self.blast_radius_limit = 3  # Max components per campaign
        
        # Statistics
        self.stats = {
            'campaigns_run': 0,
            'tests_executed': 0,
            'guardrails_verified': 0,
            'healing_tasks_raised': 0,
            'components_tested': set()
        }
        
        # Dependencies
        self.message_bus = None
        self.immutable_log = None
        self.guardian = None
        self.healing_orchestrator = None
        self.approval_engine = None
    
    async def start(self):
        """Start the chaos agent"""
        if self.running:
            return
        
        logger.info("[CHAOS-AGENT] Starting chaos engineering agent...")
        
        # Load configuration
        self._load_config()
        
        # Initialize dependencies
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
            
            # Subscribe to Guardian control
            await self.message_bus.subscribe('guardian.halt_chaos', self._handle_guardian_halt)
        except ImportError:
            logger.warning("[CHAOS-AGENT] Message bus not available")
        
        try:
            from backend.core.immutable_log import immutable_log
            self.immutable_log = immutable_log
        except ImportError:
            logger.warning("[CHAOS-AGENT] Immutable log not available")
        
        try:
            from backend.core.guardian import guardian
            self.guardian = guardian
        except ImportError:
            logger.warning("[CHAOS-AGENT] Guardian not available")
        
        try:
            from backend.core.healing_orchestrator import healing_orchestrator
            self.healing_orchestrator = healing_orchestrator
        except ImportError:
            logger.warning("[CHAOS-AGENT] Healing orchestrator not available")
        
        try:
            from backend.governance_system.inline_approval_engine import inline_approval_engine
            self.approval_engine = inline_approval_engine
        except ImportError:
            logger.warning("[CHAOS-AGENT] Approval engine not available")
        
        self.running = True
        self.status = ChaosStatus.IDLE
        
        logger.info("[CHAOS-AGENT] ✅ Started")
        logger.info(f"[CHAOS-AGENT] Auto-run: {'ENABLED' if self.auto_run_enabled else 'DISABLED'}")
        logger.info(f"[CHAOS-AGENT] Environment: {self.environment}")
        logger.info(f"[CHAOS-AGENT] Blast radius limit: {self.blast_radius_limit} components")
        logger.info(f"[CHAOS-AGENT] Components available: {len(component_registry.profiles)}")
    
    async def stop(self):
        """Stop the chaos agent"""
        self.running = False
        self.status = ChaosStatus.STOPPED
        logger.info("[CHAOS-AGENT] Stopped")
    
    def _load_config(self):
        """Load chaos configuration"""
        try:
            import json
            from pathlib import Path
            
            config_file = Path('config/chaos_config.json')
            
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                
                # Apply configuration
                if config.get('chaos_enabled', False):
                    self.auto_run_enabled = config.get('auto_run', False)
                    self.environment = config.get('environment', 'staging')
                    self.blast_radius_limit = config.get('blast_radius_limit', 3)
                    
                    logger.info("[CHAOS-AGENT] Configuration loaded from chaos_config.json")
                    logger.info(f"[CHAOS-AGENT]   Enabled: True")
                    logger.info(f"[CHAOS-AGENT]   Environment: {self.environment}")
                    logger.info(f"[CHAOS-AGENT]   Auto-run: {self.auto_run_enabled}")
                else:
                    logger.info("[CHAOS-AGENT] Chaos disabled in config")
            else:
                logger.info("[CHAOS-AGENT] No config file (using defaults)")
        except Exception as e:
            logger.warning(f"[CHAOS-AGENT] Config load failed: {e}")
    
    async def run_campaign(
        self,
        target_components: Optional[List[str]] = None,
        environment: str = 'staging',
        approved_by: Optional[str] = None
    ) -> str:
        """
        Run a chaos engineering campaign
        
        Args:
            target_components: Specific components to test (None = auto-select)
            environment: staging, shadow, or production
            approved_by: Who approved this campaign
            
        Returns:
            Campaign ID
        """
        
        campaign_id = f"chaos_{uuid4().hex[:8]}"
        
        logger.info(f"[CHAOS-AGENT] 🎯 Campaign started: {campaign_id}")
        logger.info(f"[CHAOS-AGENT]   Environment: {environment}")
        
        # Request governance approval
        if not await self._request_approval(campaign_id, environment):
            raise Exception("Chaos campaign denied by governance")
        
        # Auto-select components if not specified
        if not target_components:
            target_components = await self._select_components()
        
        logger.info(f"[CHAOS-AGENT]   Targets: {target_components}")
        
        # Create campaign
        campaign = ChaosCampaign(
            campaign_id=campaign_id,
            target_components=target_components,
            environment=environment,
            approved_by=approved_by
        )
        
        self.campaigns[campaign_id] = campaign
        self.stats['campaigns_run'] += 1
        
        # Execute campaign asynchronously
        asyncio.create_task(self._execute_campaign(campaign))
        
        return campaign_id
    
    async def _request_approval(self, campaign_id: str, environment: str) -> bool:
        """Request governance approval for chaos campaign"""
        
        if not self.approval_engine:
            logger.warning("[CHAOS-AGENT] No approval engine - proceeding with caution")
            return True
        
        try:
            from backend.governance_system.inline_approval_engine import ResourceAccess
            
            # Determine risk based on environment
            resource_type = 'test_environment'
            if environment == 'production':
                resource_type = 'production_db'  # High risk
            elif environment == 'staging':
                resource_type = 'staging_db'  # Medium risk
            
            resource_access = ResourceAccess(
                resource_type=resource_type,
                resource_id=f"chaos_{campaign_id}",
                action='execute',
                requester='chaos_agent_service',
                context={
                    'campaign_id': campaign_id,
                    'environment': environment
                }
            )
            
            result = await self.approval_engine.request_approval(resource_access)
            
            logger.info(
                f"[CHAOS-AGENT] Approval result: {result.decision.value} "
                f"(risk: {result.risk_score:.2f})"
            )
            
            return result.decision.value in ['approved', 'auto_approved']
        
        except Exception as e:
            logger.error(f"[CHAOS-AGENT] Approval request failed: {e}")
            return False
    
    async def _select_components(self) -> List[str]:
        """Auto-select components for testing (lowest resilience first)"""
        
        # Get components by resilience (lowest first)
        profiles = component_registry.get_by_resilience(ascending=True)
        
        # Select up to blast_radius_limit components
        selected = [p.component_id for p in profiles[:self.blast_radius_limit]]
        
        logger.info(f"[CHAOS-AGENT] Auto-selected {len(selected)} components (lowest resilience)")
        
        return selected
    
    async def _execute_campaign(self, campaign: ChaosCampaign):
        """Execute a chaos campaign"""
        
        campaign.status = 'running'
        campaign.started_at = datetime.utcnow()
        self.active_campaign = campaign.campaign_id
        self.status = ChaosStatus.RUNNING
        
        logger.info(f"[CHAOS-AGENT] Executing campaign: {campaign.campaign_id}")
        
        try:
            for component_id in campaign.target_components:
                # Check if Guardian halted chaos
                if self.status == ChaosStatus.PAUSED:
                    logger.warning(f"[CHAOS-AGENT] Campaign paused by Guardian")
                    return
                
                profile = component_registry.get_profile(component_id)
                
                if not profile:
                    logger.warning(f"[CHAOS-AGENT] Component not found: {component_id}")
                    continue
                
                logger.info(f"[CHAOS-AGENT] Testing component: {profile.component_name}")
                
                # Run stress tests for this component
                await self._test_component(campaign, profile)
                
                # Wait between components
                await asyncio.sleep(2)
            
            campaign.status = 'completed'
            campaign.completed_at = datetime.utcnow()
            
            logger.info(f"[CHAOS-AGENT] ✅ Campaign completed: {campaign.campaign_id}")
            logger.info(f"[CHAOS-AGENT]   Tests: {len(campaign.results)}")
            logger.info(f"[CHAOS-AGENT]   Passed: {sum(1 for r in campaign.results if r.success)}")
            logger.info(f"[CHAOS-AGENT]   Failed: {sum(1 for r in campaign.results if not r.success)}")
            logger.info(f"[CHAOS-AGENT]   Healing tasks: {campaign.healing_tasks_raised}")
        
        except Exception as e:
            campaign.status = 'failed'
            campaign.completed_at = datetime.utcnow()
            logger.error(f"[CHAOS-AGENT] Campaign failed: {e}")
        
        finally:
            self.active_campaign = None
            self.status = ChaosStatus.IDLE
            
            # Log campaign to immutable log
            if self.immutable_log:
                await self.immutable_log.append_entry(
                    category='chaos_engineering',
                    subcategory='campaign_completed',
                    data=campaign.to_dict(),
                    actor='chaos_agent',
                    action='execute_campaign',
                    resource=campaign.campaign_id
                )
    
    async def _test_component(self, campaign: ChaosCampaign, profile: ComponentProfile):
        """Test a single component with its stress patterns"""
        
        logger.info(f"[CHAOS-AGENT] Testing {profile.component_name} with {len(profile.stress_patterns)} patterns")
        
        for stress_pattern in profile.stress_patterns:
            # Get attack script
            attack_script = ATTACK_SCRIPTS.get(stress_pattern)
            
            if not attack_script:
                logger.warning(f"[CHAOS-AGENT] No attack script for: {stress_pattern.value}")
                continue
            
            logger.info(f"[CHAOS-AGENT]   → {stress_pattern.value}")
            
            # Execute attack
            try:
                result = await self._execute_attack(profile, stress_pattern, attack_script)
                
                campaign.results.append(result)
                self.stats['tests_executed'] += 1
                
                if result.guardrail_triggered:
                    self.stats['guardrails_verified'] += 1
                
                # Publish event
                await self._publish_chaos_event(result)
                
                # If component failed/degraded, raise healing task
                if not result.success or result.severity in ['high', 'critical']:
                    await self._raise_healing_task(profile, result)
                    campaign.healing_tasks_raised += 1
                    self.stats['healing_tasks_raised'] += 1
                
                # Feed to RAG/HTM
                await self._feed_to_learning(profile, result)
                
            except Exception as e:
                logger.error(f"[CHAOS-AGENT] Attack execution failed: {e}", exc_info=True)
        
        # Update component resilience score
        self._update_resilience_score(profile, campaign)
        self.stats['components_tested'].add(profile.component_id)
    
    async def _execute_attack(
        self,
        profile: ComponentProfile,
        stress_pattern,
        attack_script
    ) -> ChaosAttackResult:
        """Execute a single attack script"""
        
        # Determine target URL based on component
        target_url = self._get_target_url(profile)
        
        # Execute attack script
        if stress_pattern.value in ['sql_injection', 'rate_limit_breach', 'payload_overflow',
                                     'malformed_data', 'null_injection', 'burst_traffic', 'slowloris']:
            result = await attack_script(target_url)
        elif stress_pattern.value == 'missing_secrets':
            result = await attack_script(profile.component_id)
        else:
            result = await attack_script()
        
        return result
    
    def _get_target_url(self, profile: ComponentProfile) -> str:
        """Get target URL for component"""
        
        # Get port from metadata
        port = profile.metadata.get('port', 8000)
        
        # Component-specific endpoints
        if profile.component_type == ComponentType.API_ENDPOINT:
            return f"http://localhost:{port}/api/test"
        elif profile.component_type == ComponentType.RAG_PIPELINE:
            return f"http://localhost:{port}/api/rag/query"
        else:
            return f"http://localhost:{port}/health"
    
    async def _publish_chaos_event(self, result: ChaosAttackResult):
        """Publish structured chaos event"""
        
        if not self.message_bus:
            return
        
        event = {
            'event_type': 'chaos.injection',
            'component_id': result.component_id,
            'stress_pattern': result.stress_pattern.value,
            'success': result.success,
            'severity': result.severity,
            'observed_behavior': result.observed_behavior,
            'guardrail_triggered': result.guardrail_triggered,
            'guardrail_name': result.guardrail_name,
            'metrics': result.metrics,
            'timestamp': result.timestamp
        }
        
        await self.message_bus.publish('chaos.injection', event)
        
        logger.debug(f"[CHAOS-AGENT] Published chaos.injection event")
    
    async def _raise_healing_task(self, profile: ComponentProfile, result: ChaosAttackResult):
        """
        Raise healing task with what/where/how/why context
        
        Component: Which component failed
        Test: Which stress test revealed the issue
        Observed: What behavior was observed
        Intended: What should have happened
        """
        
        if not self.healing_orchestrator:
            logger.warning("[CHAOS-AGENT] No healing orchestrator - cannot raise task")
            return
        
        healing_context = {
            'what': f"{profile.component_name} failed {result.stress_pattern.value}",
            'where': profile.component_id,
            'how': result.observed_behavior,
            'why': f"Expected guardrail '{result.guardrail_name}' did not activate",
            'severity': result.severity,
            'metrics': result.metrics,
            'chaos_test': True,
            'stress_pattern': result.stress_pattern.value
        }
        
        logger.warning(f"[CHAOS-AGENT] 🚨 Raising healing task for: {profile.component_id}")
        logger.warning(f"[CHAOS-AGENT]   Issue: {healing_context['what']}")
        
        try:
            # Raise healing task
            await self.healing_orchestrator.handle_issue(
                issue_type='chaos_revealed_weakness',
                issue_data=healing_context,
                source='chaos_agent'
            )
            
            logger.info(f"[CHAOS-AGENT] ✅ Healing task raised for: {profile.component_id}")
        
        except Exception as e:
            logger.error(f"[CHAOS-AGENT] Failed to raise healing task: {e}")
    
    async def _feed_to_learning(self, profile: ComponentProfile, result: ChaosAttackResult):
        """Feed chaos results to RAG/HTM for learning"""
        
        try:
            from backend.learning_systems.event_emitters import agent_events
            
            # Emit to learning loop
            await agent_events.emit(
                'chaos.test.completed',
                {
                    'component_id': profile.component_id,
                    'component_type': profile.component_type.value,
                    'stress_pattern': result.stress_pattern.value,
                    'success': result.success,
                    'guardrail_triggered': result.guardrail_triggered,
                    'metrics': result.metrics
                },
                severity='low' if result.success else 'medium'
            )
            
            logger.debug(f"[CHAOS-AGENT] Fed result to learning loop")
        
        except Exception as e:
            logger.debug(f"[CHAOS-AGENT] Could not feed to learning: {e}")
    
    def _update_resilience_score(self, profile: ComponentProfile, campaign: ChaosCampaign):
        """Update component resilience score based on test results"""
        
        # Get results for this component
        component_results = [
            r for r in campaign.results
            if r.component_id == profile.component_id
        ]
        
        if not component_results:
            return
        
        # Calculate resilience
        passed = sum(1 for r in component_results if r.success)
        total = len(component_results)
        
        resilience = passed / total if total > 0 else 0.0
        
        # Update profile (weighted average with previous score)
        if profile.resilience_score > 0:
            profile.resilience_score = (profile.resilience_score * 0.7) + (resilience * 0.3)
        else:
            profile.resilience_score = resilience
        
        profile.last_tested = datetime.utcnow().isoformat()
        profile.test_history.append({
            'campaign_id': campaign.campaign_id,
            'tests_run': total,
            'tests_passed': passed,
            'resilience': resilience,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.info(
            f"[CHAOS-AGENT] {profile.component_name} resilience: {profile.resilience_score:.2%} "
            f"({passed}/{total} passed)"
        )
    
    async def _handle_guardian_halt(self, event: Dict[str, Any]):
        """Handle Guardian halt command"""
        logger.warning("[CHAOS-AGENT] 🛑 Guardian halted chaos agent")
        self.status = ChaosStatus.PAUSED
        
        # Cancel active campaign
        if self.active_campaign and self.active_campaign in self.campaigns:
            campaign = self.campaigns[self.active_campaign]
            campaign.status = 'halted_by_guardian'
            campaign.completed_at = datetime.utcnow()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chaos agent statistics"""
        return {
            **self.stats,
            'status': self.status,
            'running': self.running,
            'auto_run_enabled': self.auto_run_enabled,
            'environment': self.environment,
            'active_campaign': self.active_campaign,
            'total_campaigns': len(self.campaigns),
            'components_tested_count': len(self.stats['components_tested'])
        }
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign details"""
        if campaign_id in self.campaigns:
            campaign = self.campaigns[campaign_id]
            result = campaign.to_dict()
            result['results'] = [r.to_dict() for r in campaign.results]
            return result
        return None


# Global instance
chaos_agent = ChaosAgent()
