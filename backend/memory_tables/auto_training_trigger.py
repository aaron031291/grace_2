"""
Auto-Training Trigger System
Automatically triggers training/learning when new data is ingested
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class AutoTrainingTrigger:
    """
    Monitors data ingestion and automatically triggers training workflows
    when sufficient new data is available.
    """
    
    def __init__(self):
        self.registry = None
        self.ingestion_counters: Dict[str, int] = defaultdict(int)
        self.last_training: Dict[str, datetime] = {}
        self.training_thresholds = self._load_training_thresholds()
        self._initialized = False
    
    async def initialize(self):
        """Initialize registry and load configuration"""
        if self._initialized:
            return
        
        from backend.memory_tables.registry import table_registry
        self.registry = table_registry
        
        if not self.registry.list_tables():
            self.registry.load_all_schemas()
        
        self._initialized = True
        logger.info("✅ Auto-training trigger initialized")
    
    def _load_training_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """
        Define training triggers for each table type.
        Specifies when and how to trigger training based on new data.
        """
        return {
            'memory_documents': {
                'row_threshold': 50,  # Train after 50 new documents
                'time_threshold_hours': 24,  # Or train every 24 hours
                'min_rows': 10,  # But need at least 10 new rows
                'training_type': 'document_embedding'
            },
            'memory_codebases': {
                'row_threshold': 10,
                'time_threshold_hours': 48,
                'min_rows': 5,
                'training_type': 'code_analysis'
            },
            'memory_prompts': {
                'row_threshold': 100,
                'time_threshold_hours': 12,
                'min_rows': 20,
                'training_type': 'prompt_optimization'
            },
            'memory_self_healing_playbooks': {
                'row_threshold': 20,
                'time_threshold_hours': 6,
                'min_rows': 5,
                'training_type': 'playbook_learning'
            },
            'memory_coding_work_orders': {
                'row_threshold': 30,
                'time_threshold_hours': 24,
                'min_rows': 10,
                'training_type': 'coding_pattern_learning'
            },
            'memory_sub_agents': {
                'row_threshold': 15,
                'time_threshold_hours': 12,
                'min_rows': 5,
                'training_type': 'agent_performance_learning'
            }
        }
    
    async def on_row_inserted(self, table_name: str, row_data: Dict[str, Any]):
        """
        Called when a new row is inserted into a table.
        Checks if training should be triggered.
        """
        if not self._initialized:
            await self.initialize()
        
        # Increment counter
        self.ingestion_counters[table_name] += 1
        logger.debug(f"📊 {table_name}: {self.ingestion_counters[table_name]} new rows since last training")
        
        # Check if should trigger training
        should_train = await self._should_trigger_training(table_name)
        
        if should_train:
            await self._trigger_training(table_name)
    
    async def _should_trigger_training(self, table_name: str) -> bool:
        """Determine if training should be triggered for this table"""
        config = self.training_thresholds.get(table_name)
        if not config:
            return False  # No training config for this table
        
        new_rows = self.ingestion_counters.get(table_name, 0)
        
        # Check row threshold
        if new_rows >= config['row_threshold']:
            logger.info(f"🎯 Row threshold met for {table_name}: {new_rows} >= {config['row_threshold']}")
            return True
        
        # Check time threshold
        last_train = self.last_training.get(table_name)
        if last_train:
            hours_since_training = (datetime.utcnow() - last_train).total_seconds() / 3600
            
            if hours_since_training >= config['time_threshold_hours']:
                # But only if we have minimum rows
                if new_rows >= config['min_rows']:
                    logger.info(
                        f"🎯 Time threshold met for {table_name}: "
                        f"{hours_since_training:.1f}h >= {config['time_threshold_hours']}h "
                        f"with {new_rows} new rows"
                    )
                    return True
        else:
            # First time - check if we have minimum rows
            if new_rows >= config['min_rows']:
                logger.info(f"🎯 Initial training for {table_name}: {new_rows} rows")
                return True
        
        return False
    
    async def _trigger_training(self, table_name: str):
        """Trigger training workflow for a table"""
        config = self.training_thresholds.get(table_name)
        if not config:
            return
        
        training_type = config['training_type']
        new_rows = self.ingestion_counters.get(table_name, 0)
        
        logger.info(f"🚀 Triggering training: {training_type} for {table_name} ({new_rows} new rows)")
        
        try:
            # Get new rows
            rows = self.registry.query_rows(table_name, limit=new_rows)
            
            # Trigger appropriate training based on type
            if training_type == 'document_embedding':
                await self._train_document_embeddings(rows)
            
            elif training_type == 'code_analysis':
                await self._train_code_analysis(rows)
            
            elif training_type == 'prompt_optimization':
                await self._train_prompt_optimization(rows)
            
            elif training_type == 'playbook_learning':
                await self._train_playbook_learning(rows)
            
            elif training_type == 'coding_pattern_learning':
                await self._train_coding_patterns(rows)
            
            elif training_type == 'agent_performance_learning':
                await self._train_agent_performance(rows)
            
            # Update counters
            self.ingestion_counters[table_name] = 0
            self.last_training[table_name] = datetime.utcnow()
            
            logger.info(f"✅ Training completed for {table_name}")
            
            # Emit event
            await self._emit_training_event(table_name, training_type, new_rows)
        
        except Exception as e:
            logger.error(f"❌ Training failed for {table_name}: {e}")
    
    async def _train_document_embeddings(self, rows: List[Any]):
        """Train document embeddings"""
        # Extract text from documents
        documents = []
        for row in rows:
            text = f"{row.title}\n{row.summary}"
            documents.append({
                'id': str(row.id),
                'text': text,
                'metadata': {
                    'source_type': row.source_type,
                    'file_path': row.file_path
                }
            })
        
        # Would integrate with embedding service here
        logger.info(f"📚 Training embeddings for {len(documents)} documents")
        # TODO: Call embedding service
    
    async def _train_code_analysis(self, rows: List[Any]):
        """Train code analysis models"""
        logger.info(f"💻 Training code analysis for {len(rows)} codebases")
        # TODO: Analyze code patterns, dependencies, etc.
    
    async def _train_prompt_optimization(self, rows: List[Any]):
        """Train prompt optimization models"""
        # Extract prompts with performance metrics
        prompts_with_metrics = []
        for row in rows:
            if hasattr(row, 'performance_score'):
                prompts_with_metrics.append({
                    'prompt': row.prompt_text,
                    'score': row.performance_score,
                    'usage_count': getattr(row, 'usage_count', 0)
                })
        
        logger.info(f"📝 Training prompt optimization for {len(prompts_with_metrics)} prompts")
        # TODO: Optimize prompts based on performance
    
    async def _train_playbook_learning(self, rows: List[Any]):
        """Learn from playbook executions"""
        # Extract successful patterns
        successful_playbooks = [
            row for row in rows
            if getattr(row, 'success_rate', 0) >= 0.8
        ]
        
        logger.info(f"🔧 Learning from {len(successful_playbooks)} successful playbooks")
        # TODO: Extract and generalize successful patterns
    
    async def _train_coding_patterns(self, rows: List[Any]):
        """Learn coding patterns from work orders"""
        # Extract completed work orders with tests
        completed_with_tests = [
            row for row in rows
            if row.status == 'deployed' and row.test_results
        ]
        
        logger.info(f"💡 Learning coding patterns from {len(completed_with_tests)} work orders")
        # TODO: Extract successful coding patterns
    
    async def _train_agent_performance(self, rows: List[Any]):
        """Learn from agent performance"""
        # Extract high-performing agents
        high_performers = [
            row for row in rows
            if getattr(row, 'success_rate', 0) >= 0.85
        ]
        
        logger.info(f"🤖 Learning from {len(high_performers)} high-performing agents")
        # TODO: Extract successful agent strategies
    
    async def _emit_training_event(
        self,
        table_name: str,
        training_type: str,
        row_count: int
    ):
        """Emit event for training completion"""
        try:
            from backend.unified_logic_hub import unified_logic_hub
            
            await unified_logic_hub.submit_update(
                update_type="auto_training_completed",
                component_targets=["memory_tables", "learning_system", table_name],
                content={
                    'table': table_name,
                    'training_type': training_type,
                    'row_count': row_count,
                    'timestamp': datetime.utcnow().isoformat()
                },
                risk_level="low",
                created_by="auto_training_trigger"
            )
        except Exception as e:
            logger.warning(f"Failed to emit training event: {e}")
    
    async def get_training_status(self) -> Dict[str, Any]:
        """Get status of auto-training for all tables"""
        status = {}
        
        for table_name, config in self.training_thresholds.items():
            new_rows = self.ingestion_counters.get(table_name, 0)
            last_train = self.last_training.get(table_name)
            
            progress = min((new_rows / config['row_threshold']) * 100, 100)
            
            status[table_name] = {
                'new_rows': new_rows,
                'threshold': config['row_threshold'],
                'progress_percent': progress,
                'last_training': last_train.isoformat() if last_train else None,
                'training_type': config['training_type'],
                'ready_for_training': new_rows >= config['min_rows']
            }
        
        return status
    
    async def force_training(self, table_name: str) -> Dict[str, Any]:
        """Force training for a specific table"""
        if not self._initialized:
            await self.initialize()
        
        if table_name not in self.training_thresholds:
            return {'success': False, 'error': 'No training config for this table'}
        
        try:
            await self._trigger_training(table_name)
            return {'success': True, 'table': table_name}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Singleton instance
auto_training_trigger = AutoTrainingTrigger()
