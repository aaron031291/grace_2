"""
Self-Healing Subsystem Integration with Memory Tables
Logs playbook runs, incidents, and outcomes to memory_self_healing_playbooks
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SelfHealingIntegration:
    """
    Integrates self-healing subsystem with memory tables.
    Logs all playbook executions, incidents, and outcomes.
    """
    
    def __init__(self):
        self.registry = None
        self.table_name = "memory_self_healing_playbooks"
        self._initialized = False
    
    async def initialize(self):
        """Initialize registry connection"""
        if self._initialized:
            return
        
        from backend.memory_tables.registry import table_registry
        self.registry = table_registry
        
        # Ensure schemas are loaded
        tables = self.registry.list_tables()
        if not tables:
            self.registry.load_all_schemas()
            self.registry.initialize_database()
        
        self._initialized = True
        logger.info(f"✅ Self-healing integration initialized → {self.table_name}")
    
    async def log_playbook_execution(
        self,
        playbook_name: str,
        trigger_conditions: Dict[str, Any],
        actions: list,
        target_components: list,
        execution_result: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Log a playbook execution to memory tables.
        
        Args:
            playbook_name: Name of the playbook
            trigger_conditions: What triggered this playbook
            actions: Actions that were executed
            target_components: Components that were targeted
            execution_result: Result of execution (success, duration, etc.)
        
        Returns:
            Row ID if successful
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Check if playbook already exists
            existing = self.registry.query_rows(
                self.table_name,
                filters={'playbook_name': playbook_name},
                limit=1
            )
            
            success = execution_result.get('success', False)
            duration_ms = execution_result.get('duration_ms', 0)
            
            if existing:
                # Update existing playbook stats
                playbook = existing[0]
                total_runs = playbook.total_runs + 1
                successful_runs = playbook.successful_runs + (1 if success else 0)
                success_rate = successful_runs / total_runs if total_runs > 0 else 0.0
                
                # Update average execution time
                prev_avg = playbook.avg_execution_time_ms
                new_avg = ((prev_avg * playbook.total_runs) + duration_ms) / total_runs
                
                updates = {
                    'total_runs': total_runs,
                    'successful_runs': successful_runs,
                    'success_rate': success_rate,
                    'last_used_at': datetime.utcnow(),
                    'avg_execution_time_ms': int(new_avg),
                    'trust_score': min(success_rate, 1.0)  # Simple trust = success rate
                }
                
                result = self.registry.update_row(
                    self.table_name,
                    str(playbook.id),
                    updates
                )
                
                logger.info(f"📊 Updated playbook stats: {playbook_name} ({total_runs} runs, {success_rate:.1%} success)")
                return result
            
            else:
                # Create new playbook entry
                row_data = {
                    'playbook_name': playbook_name,
                    'description': execution_result.get('description', f'Auto-logged playbook: {playbook_name}'),
                    'trigger_conditions': trigger_conditions,
                    'actions': actions,
                    'target_components': target_components,
                    'total_runs': 1,
                    'successful_runs': 1 if success else 0,
                    'success_rate': 1.0 if success else 0.0,
                    'last_used_at': datetime.utcnow(),
                    'avg_execution_time_ms': duration_ms,
                    'trust_score': 1.0 if success else 0.0,
                    'risk_level': execution_result.get('risk_level', 'medium'),
                    'requires_approval': execution_result.get('requires_approval', False),
                    'created_by': 'self_healing_subsystem',
                    'governance_stamp': {
                        'auto_logged': True,
                        'source': 'self_healing_integration',
                        'logged_at': datetime.utcnow().isoformat()
                    }
                }
                
                result = self.registry.insert_row(self.table_name, row_data, upsert=True)
                logger.info(f"📝 Created new playbook entry: {playbook_name}")
                return result
        
        except Exception as e:
            logger.error(f"❌ Failed to log playbook execution: {e}")
            return None
    
    async def get_playbook_stats(self, playbook_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific playbook"""
        if not self._initialized:
            await self.initialize()
        
        rows = self.registry.query_rows(
            self.table_name,
            filters={'playbook_name': playbook_name},
            limit=1
        )
        
        if not rows:
            return None
        
        playbook = rows[0]
        return {
            'playbook_name': playbook.playbook_name,
            'total_runs': playbook.total_runs,
            'successful_runs': playbook.successful_runs,
            'success_rate': playbook.success_rate,
            'trust_score': playbook.trust_score,
            'avg_execution_time_ms': playbook.avg_execution_time_ms,
            'last_used_at': playbook.last_used_at.isoformat() if playbook.last_used_at else None
        }
    
    async def get_top_playbooks(self, limit: int = 10) -> list:
        """Get top-performing playbooks by success rate and usage"""
        if not self._initialized:
            await self.initialize()
        
        rows = self.registry.query_rows(
            self.table_name,
            limit=limit
        )
        
        # Sort by success rate * total runs (reliability + usage)
        sorted_rows = sorted(
            rows,
            key=lambda x: (x.success_rate * x.total_runs),
            reverse=True
        )
        
        return [
            {
                'playbook_name': row.playbook_name,
                'success_rate': row.success_rate,
                'total_runs': row.total_runs,
                'trust_score': row.trust_score,
                'description': row.description
            }
            for row in sorted_rows[:limit]
        ]


# Singleton instance
self_healing_integration = SelfHealingIntegration()
