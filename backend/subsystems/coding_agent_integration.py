"""
Coding Agent Subsystem Integration with Memory Tables
Logs work orders, code changes, and deployment artifacts to memory_coding_work_orders
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CodingAgentIntegration:
    """
    Integrates coding agent subsystem with memory tables.
    Logs all work orders, code changes, tests, and deployments.
    """
    
    def __init__(self):
        self.registry = None
        self.table_name = "memory_coding_work_orders"
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
        logger.info(f"✅ Coding agent integration initialized → {self.table_name}")
    
    async def create_work_order(
        self,
        work_order_id: str,
        title: str,
        description: str,
        task_type: str = "feature",
        priority: str = "medium"
    ) -> Optional[Any]:
        """
        Create a new work order.
        
        Args:
            work_order_id: Unique work order ID
            title: Work order title
            description: Detailed description
            task_type: feature|bugfix|refactor|test|documentation|deployment
            priority: low|medium|high|critical
        
        Returns:
            Created row
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            row_data = {
                'work_order_id': work_order_id,
                'title': title,
                'description': description,
                'task_type': task_type,
                'status': 'pending',
                'priority': priority,
                'affected_files': [],
                'lines_added': 0,
                'lines_removed': 0,
                'complexity_score': 0.0,
                'trust_score': 0.5,
                'created_at': datetime.utcnow(),
                'assigned_to': 'grace',
                'governance_stamp': {
                    'created_by': 'coding_agent_integration',
                    'created_at': datetime.utcnow().isoformat()
                }
            }
            
            result = self.registry.insert_row(self.table_name, row_data, upsert=True)
            logger.info(f"📝 Created work order: {work_order_id} - {title}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to create work order: {e}")
            return None
    
    async def update_work_order(
        self,
        work_order_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Any]:
        """Update an existing work order"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Find the work order
            rows = self.registry.query_rows(
                self.table_name,
                filters={'work_order_id': work_order_id},
                limit=1
            )
            
            if not rows:
                logger.warning(f"Work order not found: {work_order_id}")
                return None
            
            work_order = rows[0]
            result = self.registry.update_row(
                self.table_name,
                str(work_order.id),
                updates
            )
            
            logger.info(f"📊 Updated work order: {work_order_id}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to update work order: {e}")
            return None
    
    async def log_code_changes(
        self,
        work_order_id: str,
        affected_files: List[str],
        lines_added: int,
        lines_removed: int,
        code_diff_path: Optional[str] = None
    ) -> Optional[Any]:
        """Log code changes for a work order"""
        if not self._initialized:
            await self.initialize()
        
        # Calculate complexity score (simple heuristic)
        total_lines = lines_added + lines_removed
        file_count = len(affected_files)
        complexity = min((total_lines / 100) + (file_count / 5), 10.0)
        
        updates = {
            'affected_files': affected_files,
            'lines_added': lines_added,
            'lines_removed': lines_removed,
            'complexity_score': complexity,
            'code_diff_path': code_diff_path,
            'status': 'in_progress'
        }
        
        result = await self.update_work_order(work_order_id, updates)
        logger.info(f"📝 Logged code changes: {work_order_id} (+{lines_added}/-{lines_removed} lines, {file_count} files)")
        return result
    
    async def log_test_results(
        self,
        work_order_id: str,
        test_results: Dict[str, Any]
    ) -> Optional[Any]:
        """Log test execution results"""
        if not self._initialized:
            await self.initialize()
        
        # Update trust score based on test results
        passed = test_results.get('passed', 0)
        total = test_results.get('total', 1)
        test_success_rate = passed / total if total > 0 else 0.0
        
        updates = {
            'test_results': test_results,
            'trust_score': test_success_rate,
            'status': 'review' if test_success_rate > 0.8 else 'in_progress'
        }
        
        result = await self.update_work_order(work_order_id, updates)
        logger.info(f"✅ Logged test results: {work_order_id} ({passed}/{total} passed)")
        return result
    
    async def mark_deployed(
        self,
        work_order_id: str,
        deployment_impact: Dict[str, Any]
    ) -> Optional[Any]:
        """Mark work order as deployed"""
        if not self._initialized:
            await self.initialize()
        
        updates = {
            'status': 'deployed',
            'completed_at': datetime.utcnow(),
            'deployment_impact': deployment_impact,
            'trust_score': 1.0  # Successful deployment
        }
        
        result = await self.update_work_order(work_order_id, updates)
        logger.info(f"🚀 Marked as deployed: {work_order_id}")
        return result
    
    async def get_work_order_stats(self) -> Dict[str, Any]:
        """Get overall coding agent statistics"""
        if not self._initialized:
            await self.initialize()
        
        rows = self.registry.query_rows(self.table_name, limit=1000)
        
        total = len(rows)
        by_status = {}
        by_type = {}
        total_lines_added = 0
        total_lines_removed = 0
        avg_trust = 0.0
        
        for row in rows:
            by_status[row.status] = by_status.get(row.status, 0) + 1
            by_type[row.task_type] = by_type.get(row.task_type, 0) + 1
            total_lines_added += row.lines_added
            total_lines_removed += row.lines_removed
            avg_trust += row.trust_score
        
        avg_trust = avg_trust / total if total > 0 else 0.0
        
        return {
            'total_work_orders': total,
            'by_status': by_status,
            'by_type': by_type,
            'total_lines_added': total_lines_added,
            'total_lines_removed': total_lines_removed,
            'average_trust_score': avg_trust,
            'deployment_rate': by_status.get('deployed', 0) / total if total > 0 else 0.0
        }


# Singleton instance
coding_agent_integration = CodingAgentIntegration()
coding_agent = coding_agent_integration  # Alias for backward compatibility
