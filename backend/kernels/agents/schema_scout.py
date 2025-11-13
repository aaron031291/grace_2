"""
Schema Scout Agent
Runs schema inference and submits proposals through Unified Logic
"""

from typing import Dict, Any
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SchemaScout:
    """
    Analyzes files/data and proposes database schemas.
    Routes proposals through Unified Logic for approval.
    """
    
    def __init__(self, agent_id: str, task_data: Dict, registry=None, kernel=None):
        self.agent_id = agent_id
        self.task_data = task_data
        self.registry = registry
        self.kernel = kernel
        
        self.file_path = task_data.get('path')
        self.confidence = 0.0
        self.proposed_schema = None
    
    async def execute(self) -> Dict[str, Any]:
        """
        Main execution flow:
        1. Analyze file/data
        2. Infer schema
        3. Check confidence threshold
        4. Submit to Unified Logic (auto-approve or manual review)
        5. Log results
        """
        try:
            logger.info(f"Schema Scout {self.agent_id} analyzing: {self.file_path}")
            
            # Step 1: Analyze file
            analysis = await self._analyze_file()
            
            # Step 2: Infer schema
            schema_proposal = await self._infer_schema(analysis)
            
            self.proposed_schema = schema_proposal
            self.confidence = schema_proposal.get('confidence', 0.0)
            
            # Step 3: Check auto-approve threshold
            auto_approve = self.confidence >= 0.8  # From kernel config
            
            # Step 4: Submit to Unified Logic
            result = await self._submit_proposal(schema_proposal, auto_approve)
            
            # Step 5: Log to memory tables
            await self._log_results(result)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'file_path': self.file_path,
                'confidence': self.confidence,
                'auto_approved': auto_approve,
                'proposal_id': result.get('proposal_id')
            }
            
        except Exception as e:
            logger.error(f"Schema Scout {self.agent_id} failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _analyze_file(self) -> Dict:
        """Analyze file structure and content"""
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        
        try:
            if self.registry:
                agent = SchemaInferenceAgent(registry=self.registry)
                analysis = await agent.analyze_file(Path(self.file_path))
                return analysis
        except Exception as e:
            logger.warning(f"Schema analysis failed: {e}")
        
        # Fallback: basic analysis
        return {
            'file_path': self.file_path,
            'detected_type': 'unknown',
            'features': {}
        }
    
    async def _infer_schema(self, analysis: Dict) -> Dict:
        """Infer database schema from analysis"""
        detected_type = analysis.get('detected_type')
        
        # Determine target table based on file type
        table_mapping = {
            'document': 'memory_documents',
            'dataset': 'memory_datasets',
            'code': 'memory_documents',
            'media': 'memory_documents'
        }
        
        suggested_table = table_mapping.get(detected_type, 'memory_documents')
        
        return {
            'table_name': suggested_table,
            'fields': {
                'file_path': self.file_path,
                'file_type': detected_type,
                'analysis': analysis,
                'ingestion_status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            },
            'confidence': 0.9 if detected_type != 'unknown' else 0.3,
            'reasoning': f"File detected as {detected_type}, mapping to {suggested_table}"
        }
    
    async def _submit_proposal(self, proposal: Dict, auto_approve: bool) -> Dict:
        """Submit proposal through Unified Logic"""
        if not self.registry:
            return {'status': 'skipped', 'reason': 'no_registry'}
        
        try:
            # Insert into schema proposals table
            proposal_id = self.registry.insert_row('memory_schema_proposals', {
                'table_name': proposal['table_name'],
                'proposed_fields': proposal['fields'],
                'confidence': proposal['confidence'],
                'reasoning': proposal['reasoning'],
                'status': 'approved' if auto_approve else 'pending',
                'auto_approved': auto_approve,
                'submitted_by': self.agent_id,
                'submitted_at': datetime.utcnow().isoformat()
            })
            
            # If auto-approved, execute immediately
            if auto_approve:
                await self._execute_approved_schema(proposal)
            
            return {
                'status': 'submitted',
                'proposal_id': proposal_id,
                'auto_approved': auto_approve
            }
            
        except Exception as e:
            logger.error(f"Failed to submit proposal: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _execute_approved_schema(self, proposal: Dict):
        """Execute an approved schema (insert row into target table)"""
        try:
            table_name = proposal['table_name']
            fields = proposal['fields']
            
            self.registry.insert_row(table_name, fields)
            
            logger.info(f"Inserted row into {table_name} for {self.file_path}")
            
        except Exception as e:
            logger.error(f"Failed to execute schema: {e}")
    
    async def _log_results(self, result: Dict):
        """Log agent execution to memory_execution_logs"""
        if self.registry:
            try:
                self.registry.insert_row('memory_execution_logs', {
                    'agent_id': self.agent_id,
                    'agent_type': 'schema_scout',
                    'task_type': 'schema_inference',
                    'status': result.get('status'),
                    'metadata': {
                        'file_path': self.file_path,
                        'confidence': self.confidence,
                        'proposal': self.proposed_schema
                    },
                    'executed_at': datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.warning(f"Could not log execution: {e}")
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping Schema Scout {self.agent_id}")
