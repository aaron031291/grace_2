"""
Agent Lifecycle Manager
Spawns, manages, monitors, and terminates sub-agents on-demand
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

from backend.agents.base_agent_component import (
    BaseAgentComponent,
    SchemaInferenceAgent,
    IngestionAgent,
    CrossDomainLearningAgent
)

logger = logging.getLogger(__name__)


class AgentLifecycleManager:
    """
    Manages the lifecycle of sub-agents:
    - Spawn agents on-demand for jobs
    - Execute jobs through agents
    - Monitor agent health and performance
    - Terminate agents when jobs complete
    - Revoke misbehaving agents
    """
    
    def __init__(self):
        self.active_agents: Dict[str, BaseAgentComponent] = {}
        self.agent_registry: Dict[str, Type[BaseAgentComponent]] = {
            'schema_inference': SchemaInferenceAgent,
            'ingestion': IngestionAgent,
            'cross_domain_learning': CrossDomainLearningAgent
        }
        
        # Job queue
        self.job_queue: List[Dict[str, Any]] = []
        self.job_results: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring
        self.agent_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Revocation list
        self.revoked_agents: List[str] = []
        
        # Settings
        self.max_agent_lifetime_minutes = 60  # Auto-terminate after 1 hour
        self.max_idle_minutes = 10  # Terminate if idle for 10 minutes
        self.min_trust_threshold = 0.3  # Revoke if trust drops below 0.3
        
        self._monitor_task = None
        self._running = False
    
    async def start_monitoring(self):
        """Start background monitoring of agents"""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("🔍 Agent lifecycle monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Agent lifecycle monitoring stopped")
    
    async def _monitor_loop(self):
        """Monitor agent health and lifecycle"""
        while self._running:
            try:
                await self._check_agent_health()
                await self._cleanup_idle_agents()
                await self._cleanup_old_agents()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(60)
    
    async def spawn_agent(
        self,
        agent_type: str,
        instance_id: str = None
    ) -> BaseAgentComponent:
        """
        Spawn a new agent instance.
        
        Args:
            agent_type: Type of agent (schema_inference, ingestion, etc.)
            instance_id: Optional specific instance ID
        
        Returns:
            Initialized agent instance
        """
        # Get agent class
        agent_class = self.agent_registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create instance
        agent = agent_class(instance_id=instance_id)
        
        # Initialize with clarity contracts
        await agent.initialize()
        
        # Track active agent
        self.active_agents[agent.agent_id] = agent
        
        # Initialize metrics
        self.agent_metrics[agent.agent_id] = {
            'spawned_at': datetime.utcnow(),
            'last_job_at': None,
            'jobs_executed': 0
        }
        
        logger.info(f"🚀 Spawned {agent.agent_name} ({agent.agent_id})")
        
        return agent
    
    async def execute_job(
        self,
        agent_type: str,
        job: Dict[str, Any],
        reuse_agent: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a job using an agent.
        
        Args:
            agent_type: Type of agent needed
            job: Job specification
            reuse_agent: If True, reuse existing agent if available
        
        Returns:
            Job result
        """
        job_id = job.get('job_id', str(uuid.uuid4()))
        job['job_id'] = job_id
        job['job_type'] = agent_type
        
        logger.info(f"📋 Executing job {job_id} (type: {agent_type})")
        
        # Find or spawn agent
        agent = None
        
        if reuse_agent:
            # Try to find idle agent of this type
            for existing_agent in self.active_agents.values():
                if (existing_agent.__class__.__name__.lower().replace('agent', '') == agent_type.replace('_', '') and
                    existing_agent.status == "idle" and
                    existing_agent.agent_id not in self.revoked_agents):
                    agent = existing_agent
                    logger.info(f"♻️  Reusing agent {agent.agent_id}")
                    break
        
        if not agent:
            # Spawn new agent
            agent = await self.spawn_agent(agent_type)
        
        # Execute job
        try:
            result = await agent.execute_job(job)
            
            # Store result
            self.job_results[job_id] = result
            
            # Update metrics
            self.agent_metrics[agent.agent_id]['last_job_at'] = datetime.utcnow()
            self.agent_metrics[agent.agent_id]['jobs_executed'] += 1
            
            # Check if agent should be terminated
            if not reuse_agent:
                await self.terminate_agent(agent.agent_id)
            
            return result
        
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            
            # Check if agent should be revoked
            if agent.trust_score < self.min_trust_threshold:
                await self.revoke_agent(agent.agent_id, f"Trust score too low: {agent.trust_score:.2f}")
            
            raise
    
    async def terminate_agent(self, agent_id: str):
        """
        Gracefully terminate an agent.
        
        Args:
            agent_id: Agent to terminate
        """
        agent = self.active_agents.get(agent_id)
        if not agent:
            logger.warning(f"Agent {agent_id} not found for termination")
            return
        
        logger.info(f"🔴 Terminating {agent.agent_name} ({agent_id})")
        
        # Terminate agent
        await agent.terminate()
        
        # Remove from active agents
        del self.active_agents[agent_id]
        
        # Archive metrics
        metrics = self.agent_metrics.get(agent_id)
        if metrics:
            logger.info(
                f"📊 Agent {agent_id} final stats: "
                f"{metrics['jobs_executed']} jobs, trust: {agent.trust_score:.2f}"
            )
    
    async def revoke_agent(self, agent_id: str, reason: str):
        """
        Revoke an agent (mark as untrusted and terminate).
        
        Args:
            agent_id: Agent to revoke
            reason: Reason for revocation
        """
        logger.warning(f"⛔ Revoking agent {agent_id}: {reason}")
        
        # Add to revoked list
        if agent_id not in self.revoked_agents:
            self.revoked_agents.append(agent_id)
        
        # Terminate agent
        await self.terminate_agent(agent_id)
        
        # Log revocation event
        try:
            from backend.unified_logic_hub import unified_logic_hub
            
            await unified_logic_hub.submit_update(
                update_type="agent_revocation",
                component_targets=["clarity_manifest", "sub_agents"],
                content={
                    'agent_id': agent_id,
                    'reason': reason,
                    'revoked_at': datetime.utcnow().isoformat()
                },
                risk_level="high",
                created_by="agent_lifecycle_manager"
            )
        except Exception as e:
            logger.warning(f"Failed to log revocation: {e}")
    
    async def _check_agent_health(self):
        """Check health of all active agents"""
        for agent_id, agent in list(self.active_agents.items()):
            # Check heartbeat
            if agent.last_heartbeat:
                time_since_heartbeat = (datetime.utcnow() - agent.last_heartbeat).total_seconds()
                if time_since_heartbeat > 120:  # 2 minutes
                    logger.warning(f"⚠️  Agent {agent_id} missed heartbeat ({time_since_heartbeat:.0f}s)")
            
            # Check trust score
            if agent.trust_score < self.min_trust_threshold:
                await self.revoke_agent(
                    agent_id,
                    f"Trust score below threshold: {agent.trust_score:.2f} < {self.min_trust_threshold}"
                )
            
            # Send heartbeat
            try:
                await agent.heartbeat()
            except Exception as e:
                logger.error(f"Heartbeat failed for {agent_id}: {e}")
    
    async def _cleanup_idle_agents(self):
        """Terminate agents that have been idle too long"""
        for agent_id, agent in list(self.active_agents.items()):
            metrics = self.agent_metrics.get(agent_id)
            if not metrics:
                continue
            
            last_job = metrics.get('last_job_at')
            if last_job:
                idle_time = (datetime.utcnow() - last_job).total_seconds() / 60
                if idle_time > self.max_idle_minutes:
                    logger.info(f"🧹 Terminating idle agent {agent_id} ({idle_time:.1f} min idle)")
                    await self.terminate_agent(agent_id)
    
    async def _cleanup_old_agents(self):
        """Terminate agents that exceeded max lifetime"""
        for agent_id, agent in list(self.active_agents.items()):
            metrics = self.agent_metrics.get(agent_id)
            if not metrics:
                continue
            
            spawned_at = metrics.get('spawned_at')
            if spawned_at:
                lifetime = (datetime.utcnow() - spawned_at).total_seconds() / 60
                if lifetime > self.max_agent_lifetime_minutes:
                    logger.info(f"🧹 Terminating old agent {agent_id} ({lifetime:.1f} min lifetime)")
                    await self.terminate_agent(agent_id)
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        agent = self.active_agents.get(agent_id)
        if not agent:
            return None
        
        status = await agent.get_status()
        metrics = self.agent_metrics.get(agent_id, {})
        
        return {
            **status,
            'metrics': metrics,
            'is_revoked': agent_id in self.revoked_agents
        }
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get status of all active agents"""
        statuses = []
        
        for agent_id in self.active_agents:
            status = await self.get_agent_status(agent_id)
            if status:
                statuses.append(status)
        
        return statuses
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get overall lifecycle manager metrics"""
        active_count = len(self.active_agents)
        revoked_count = len(self.revoked_agents)
        
        # Count by type
        by_type = defaultdict(int)
        for agent in self.active_agents.values():
            agent_type = agent.__class__.__name__
            by_type[agent_type] += 1
        
        # Total jobs executed
        total_jobs = sum(
            metrics.get('jobs_executed', 0)
            for metrics in self.agent_metrics.values()
        )
        
        # Average trust
        if self.active_agents:
            avg_trust = sum(agent.trust_score for agent in self.active_agents.values()) / len(self.active_agents)
        else:
            avg_trust = 0.0
        
        return {
            'active_agents': active_count,
            'revoked_agents': revoked_count,
            'agents_by_type': dict(by_type),
            'total_jobs_executed': total_jobs,
            'average_trust_score': avg_trust,
            'pending_jobs': len(self.job_queue),
            'completed_jobs': len(self.job_results)
        }
    
    async def submit_job_to_queue(self, agent_type: str, job: Dict[str, Any]):
        """Submit a job to the queue for asynchronous processing"""
        job_id = str(uuid.uuid4())
        job['job_id'] = job_id
        job['agent_type'] = agent_type
        job['submitted_at'] = datetime.utcnow().isoformat()
        
        self.job_queue.append(job)
        logger.info(f"📥 Job {job_id} queued ({len(self.job_queue)} in queue)")
        
        return job_id
    
    async def process_job_queue(self, max_concurrent: int = 5):
        """Process jobs from queue"""
        if not self.job_queue:
            return
        
        logger.info(f"🔄 Processing {len(self.job_queue)} queued jobs (max {max_concurrent} concurrent)")
        
        # Process jobs in batches
        while self.job_queue and len([a for a in self.active_agents.values() if a.status == "busy"]) < max_concurrent:
            job = self.job_queue.pop(0)
            
            # Execute job asynchronously
            asyncio.create_task(
                self.execute_job(
                    job['agent_type'],
                    job,
                    reuse_agent=True
                )
            )


# Global instance
agent_lifecycle_manager = AgentLifecycleManager()
