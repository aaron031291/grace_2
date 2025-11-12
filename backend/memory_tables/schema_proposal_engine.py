"""
Schema Proposal Engine
Routes schema changes through Unified Logic Hub for governance approval
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio
from datetime import datetime


class SchemaProposalEngine:
    """
    Manages schema proposals and routes them through Unified Logic Hub.
    Handles schema inference, proposal generation, and approval workflows.
    """
    
    def __init__(self):
        self.registry = None
        self.unified_logic_hub = None
        self.pending_proposals: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self):
        """Initialize with registry and logic hub"""
        from backend.memory_tables.registry import table_registry
        from backend.unified_logic_hub import unified_logic_hub
        
        self.registry = table_registry
        self.unified_logic_hub = unified_logic_hub
        
        if not self.registry.tables:
            self.registry.load_all_schemas()
    
    async def propose_schema_from_file(
        self,
        file_path: Path,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate schema proposal from file analysis and route through governance.
        
        Args:
            file_path: Path to analyzed file
            analysis_result: Analysis from SchemaInferenceAgent
        
        Returns:
            Proposal result with approval status
        """
        if not self.unified_logic_hub:
            await self.initialize()
        
        proposed_table = analysis_result.get('recommended_table')
        confidence = analysis_result.get('confidence', 0.0)
        
        # Check if table exists
        table_exists = proposed_table in self.registry.tables
        
        proposal = {
            'file_path': str(file_path),
            'recommended_table': proposed_table,
            'confidence': confidence,
            'table_exists': table_exists,
            'extracted_fields': analysis_result.get('extracted_fields', {}),
            'reasoning': analysis_result.get('reasoning', ''),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if table_exists:
            # Propose row insertion
            return await self._propose_row_insertion(proposal)
        else:
            # Propose new table creation
            return await self._propose_table_creation(proposal)
    
    async def _propose_row_insertion(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propose inserting a row into existing table via governance.
        """
        table_name = proposal['recommended_table']
        row_data = proposal['extracted_fields']
        
        # Submit to Unified Logic Hub
        try:
            result = await self.unified_logic_hub.submit_update(
                update_type="memory_table_row_insert",
                component_targets=["memory_tables", table_name],
                content={
                    'table_name': table_name,
                    'row_data': row_data,
                    'source_file': proposal['file_path'],
                    'confidence': proposal['confidence']
                },
                risk_level=self._assess_risk_level(proposal['confidence']),
                created_by="schema_proposal_engine"
            )
            
            proposal_id = result.get('update_id')
            self.pending_proposals[proposal_id] = proposal
            
            return {
                'success': True,
                'proposal_id': proposal_id,
                'action': 'row_insertion',
                'table_name': table_name,
                'requires_approval': True,
                'update_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'row_insertion',
                'table_name': table_name
            }
    
    async def _propose_table_creation(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propose creating a new table via governance.
        """
        table_name = proposal['recommended_table']
        
        # Generate schema from extracted fields
        schema = self._generate_schema_from_fields(
            table_name,
            proposal['extracted_fields'],
            proposal.get('reasoning', '')
        )
        
        try:
            result = await self.unified_logic_hub.submit_update(
                update_type="memory_table_schema_create",
                component_targets=["memory_tables", "schema_registry"],
                content={
                    'table_name': table_name,
                    'schema': schema,
                    'source_file': proposal['file_path'],
                    'confidence': proposal['confidence'],
                    'reasoning': proposal['reasoning']
                },
                risk_level="high",  # New table creation is high risk
                created_by="schema_proposal_engine"
            )
            
            proposal_id = result.get('update_id')
            self.pending_proposals[proposal_id] = proposal
            
            return {
                'success': True,
                'proposal_id': proposal_id,
                'action': 'table_creation',
                'table_name': table_name,
                'schema': schema,
                'requires_approval': True,
                'update_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'table_creation',
                'table_name': table_name
            }
    
    async def propose_schema_tweak(
        self,
        table_name: str,
        field_changes: Dict[str, Any],
        reasoning: str
    ) -> Dict[str, Any]:
        """
        Propose schema modifications (add/modify fields) to existing table.
        
        Args:
            table_name: Table to modify
            field_changes: Dict of field modifications
            reasoning: Explanation for changes
        
        Returns:
            Proposal result
        """
        if not self.unified_logic_hub:
            await self.initialize()
        
        try:
            result = await self.unified_logic_hub.submit_update(
                update_type="memory_table_schema_modify",
                component_targets=["memory_tables", table_name],
                content={
                    'table_name': table_name,
                    'field_changes': field_changes,
                    'reasoning': reasoning
                },
                risk_level="high",  # Schema changes are high risk
                created_by="schema_proposal_engine"
            )
            
            return {
                'success': True,
                'proposal_id': result.get('update_id'),
                'action': 'schema_modification',
                'table_name': table_name,
                'requires_approval': True,
                'update_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'schema_modification'
            }
    
    async def get_pending_proposals(self, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pending schema proposals, optionally filtered by table"""
        proposals = []
        
        for proposal_id, proposal in self.pending_proposals.items():
            if table_name and proposal['recommended_table'] != table_name:
                continue
            
            proposals.append({
                'proposal_id': proposal_id,
                **proposal
            })
        
        return proposals
    
    async def approve_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Mark proposal as approved and execute the change.
        (Called by governance workflow after human approval)
        """
        if proposal_id not in self.pending_proposals:
            return {'success': False, 'error': 'Proposal not found'}
        
        proposal = self.pending_proposals[proposal_id]
        
        try:
            # Execute the approved change
            if proposal.get('table_exists'):
                # Insert row
                table_name = proposal['recommended_table']
                row_data = proposal['extracted_fields']
                
                result = self.registry.insert_row(table_name, row_data)
                
                return {
                    'success': True,
                    'action': 'row_inserted',
                    'table_name': table_name,
                    'row_id': str(result.id) if result else None
                }
            else:
                # Create table (would need schema file creation)
                return {
                    'success': False,
                    'error': 'Table creation requires manual schema file creation'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Remove from pending
            del self.pending_proposals[proposal_id]
    
    async def reject_proposal(self, proposal_id: str, reason: str = "") -> Dict[str, Any]:
        """Reject a schema proposal"""
        if proposal_id not in self.pending_proposals:
            return {'success': False, 'error': 'Proposal not found'}
        
        proposal = self.pending_proposals.pop(proposal_id)
        
        return {
            'success': True,
            'action': 'rejected',
            'proposal': proposal,
            'reason': reason
        }
    
    def _generate_schema_from_fields(
        self,
        table_name: str,
        fields: Dict[str, Any],
        description: str
    ) -> Dict[str, Any]:
        """Generate YAML-compatible schema from extracted fields"""
        schema_fields = []
        
        # ID field
        schema_fields.append({
            'name': 'id',
            'type': 'uuid',
            'primary_key': True,
            'generated': True
        })
        
        # Convert extracted fields
        for field_name, field_value in fields.items():
            if field_name in ['id', 'created_at', 'updated_at']:
                continue
            
            field_type = self._infer_field_type(field_value)
            schema_fields.append({
                'name': field_name,
                'type': field_type,
                'nullable': True
            })
        
        # Standard fields
        schema_fields.extend([
            {'name': 'trust_score', 'type': 'float', 'default': 0.0},
            {'name': 'governance_stamp', 'type': 'json', 'nullable': True},
            {'name': 'created_at', 'type': 'datetime', 'required': True}
        ])
        
        return {
            'table': table_name,
            'description': description,
            'fields': schema_fields
        }
    
    def _infer_field_type(self, value: Any) -> str:
        """Infer SQLModel field type from value"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, (list, dict)):
            return 'json'
        else:
            return 'text'
    
    def _assess_risk_level(self, confidence: float) -> str:
        """Assess risk level based on confidence score"""
        if confidence >= 0.9:
            return "low"
        elif confidence >= 0.7:
            return "medium"
        else:
            return "high"


# Singleton instance
schema_proposal_engine = SchemaProposalEngine()
