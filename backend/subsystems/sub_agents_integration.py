"""
Sub-Agents Subsystem Integration with Memory Tables
Tracks agent configurations, status, and performance to memory_sub_agents
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SubAgentsIntegration:
    """
    Integrates sub-agents subsystem with memory tables.
    Tracks agent lifecycle, performance, and trust metrics.
    """
    
    def __init__(self):
        self.registry = None
        self.table_name = "memory_sub_agents"
        self._initialized = False
    
    async def initialize(self):
        """Initialize registry connection"""
        if self._initialized:
            return
        
        from backend.memory_tables.registry import table_registry
        self.registry = table_registry
        
        if not self.registry.tables:
            self.registry.load_all_schemas()
            self.registry.initialize_database()
        
        self._initialized = True
        logger.info(f"✅ Sub-agents integration initialized → {self.table_name}")
    
    async def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        mission: str,
        capabilities: List[str],
        constraints: Dict[str, Any] = None
    ) -> Optional[Any]:
        """
        Register a new sub-agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable name
            agent_type: shard|specialist|orchestrator|worker
            mission: Primary purpose
            capabilities: List of agent capabilities
            constraints: Resource limits, access restrictions
        
        Returns:
            Created row
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            row_data = {
                'agent_id': agent_id,
                'agent_name': agent_name,
                'agent_type': agent_type,
                'mission': mission,
                'capabilities': capabilities,
                'constraints': constraints or {},
                'status': 'idle',
                'tasks_completed': 0,
                'tasks_failed': 0,
                'success_rate': 0.0,
                'trust_score': 0.5,  # Start at neutral
                'last_active_at': datetime.utcnow(),
                'heartbeat_interval_sec': 30,
                'governance_stamp': {
                    'registered_by': 'sub_agents_integration',
                    'registered_at': datetime.utcnow().isoformat()
                }
            }
            
            result = self.registry.insert_row(self.table_name, row_data)
            logger.info(f"🤖 Registered agent: {agent_id} ({agent_type})")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to register agent: {e}")
            return None
    
    async def update_agent_status(
        self,
        agent_id: str,
        status: str,
        current_task: Optional[str] = None
    ) -> Optional[Any]:
        """
        Update agent status.
        
        Args:
            agent_id: Agent to update
            status: idle|active|busy|error|offline
            current_task: Current task description (if any)
        
        Returns:
            Updated row
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            rows = self.registry.query_rows(
                self.table_name,
                filters={'agent_id': agent_id},
                limit=1
            )
            
            if not rows:
                logger.warning(f"Agent not found: {agent_id}")
                return None
            
            agent = rows[0]
            updates = {
                'status': status,
                'current_task': current_task,
                'last_active_at': datetime.utcnow()
            }
            
            result = self.registry.update_row(
                self.table_name,
                str(agent.id),
                updates
            )
            
            logger.debug(f"🤖 Agent {agent_id} → {status}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to update agent status: {e}")
            return None
    
    async def log_task_completion(
        self,
        agent_id: str,
        success: bool
    ) -> Optional[Any]:
        """Log task completion for an agent and update metrics"""
        if not self._initialized:
            await self.initialize()
        
        try:
            rows = self.registry.query_rows(
                self.table_name,
                filters={'agent_id': agent_id},
                limit=1
            )
            
            if not rows:
                logger.warning(f"Agent not found: {agent_id}")
                return None
            
            agent = rows[0]
            
            # Update metrics
            tasks_completed = agent.tasks_completed + (1 if success else 0)
            tasks_failed = agent.tasks_failed + (0 if success else 1)
            total_tasks = tasks_completed + tasks_failed
            success_rate = tasks_completed / total_tasks if total_tasks > 0 else 0.0
            
            # Update trust score based on recent performance
            # Trust = 70% success rate + 30% previous trust (exponential moving average)
            new_trust = (0.7 * success_rate) + (0.3 * agent.trust_score)
            
            updates = {
                'tasks_completed': tasks_completed,
                'tasks_failed': tasks_failed,
                'success_rate': success_rate,
                'trust_score': min(max(new_trust, 0.0), 1.0),  # Clamp [0, 1]
                'status': 'idle',
                'current_task': None,
                'last_active_at': datetime.utcnow()
            }
            
            result = self.registry.update_row(
                self.table_name,
                str(agent.id),
                updates
            )
            
            status_emoji = "✅" if success else "❌"
            logger.info(
                f"{status_emoji} Agent {agent_id}: {tasks_completed}/{total_tasks} "
                f"({success_rate:.1%} success, {new_trust:.2f} trust)"
            )
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to log task completion: {e}")
            return None
    
    async def heartbeat(self, agent_id: str) -> Optional[Any]:
        """Update agent heartbeat (shows it's still alive)"""
        if not self._initialized:
            await self.initialize()
        
        try:
            rows = self.registry.query_rows(
                self.table_name,
                filters={'agent_id': agent_id},
                limit=1
            )
            
            if not rows:
                return None
            
            agent = rows[0]
            updates = {
                'last_active_at': datetime.utcnow()
            }
            
            return self.registry.update_row(
                self.table_name,
                str(agent.id),
                updates
            )
        
        except Exception as e:
            logger.error(f"❌ Heartbeat failed for {agent_id}: {e}")
            return None
    
    async def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific agent"""
        if not self._initialized:
            await self.initialize()
        
        rows = self.registry.query_rows(
            self.table_name,
            filters={'agent_id': agent_id},
            limit=1
        )
        
        if not rows:
            return None
        
        agent = rows[0]
        return {
            'agent_id': agent.agent_id,
            'agent_name': agent.agent_name,
            'agent_type': agent.agent_type,
            'status': agent.status,
            'tasks_completed': agent.tasks_completed,
            'tasks_failed': agent.tasks_failed,
            'success_rate': agent.success_rate,
            'trust_score': agent.trust_score,
            'current_task': agent.current_task,
            'last_active_at': agent.last_active_at.isoformat() if agent.last_active_at else None
        }
    
    async def get_active_agents(self) -> List[Dict[str, Any]]:
        """Get all active agents"""
        if not self._initialized:
            await self.initialize()
        
        # Query agents by status
        rows = self.registry.query_rows(self.table_name, limit=100)
        
        active_agents = [
            {
                'agent_id': row.agent_id,
                'agent_name': row.agent_name,
                'status': row.status,
                'current_task': row.current_task,
                'trust_score': row.trust_score
            }
            for row in rows
            if row.status in ['active', 'busy']
        ]
        
        return active_agents
    
    async def get_fleet_stats(self) -> Dict[str, Any]:
        """Get overall sub-agent fleet statistics"""
        if not self._initialized:
            await self.initialize()
        
        rows = self.registry.query_rows(self.table_name, limit=1000)
        
        total = len(rows)
        by_status = {}
        by_type = {}
        total_tasks = 0
        total_success = 0
        avg_trust = 0.0
        
        for row in rows:
            by_status[row.status] = by_status.get(row.status, 0) + 1
            by_type[row.agent_type] = by_type.get(row.agent_type, 0) + 1
            total_tasks += (row.tasks_completed + row.tasks_failed)
            total_success += row.tasks_completed
            avg_trust += row.trust_score
        
        avg_trust = avg_trust / total if total > 0 else 0.0
        fleet_success_rate = total_success / total_tasks if total_tasks > 0 else 0.0
        
        return {
            'total_agents': total,
            'by_status': by_status,
            'by_type': by_type,
            'total_tasks_processed': total_tasks,
            'total_successful_tasks': total_success,
            'fleet_success_rate': fleet_success_rate,
            'average_trust_score': avg_trust
        }


# Singleton instance
sub_agents_integration = SubAgentsIntegration()
