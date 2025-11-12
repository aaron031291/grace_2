#!/usr/bin/env python3
"""
Memory Tables API - Routes through Unified Logic Hub
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory/tables", tags=["memory-tables"])


# Pydantic models
class SchemaProposal(BaseModel):
    table_name: str
    description: str
    fields: List[Dict[str, Any]]
    confidence: float
    reason: str


class TableRow(BaseModel):
    data: Dict[str, Any]


class SchemaUpdateRequest(BaseModel):
    table_name: str
    fields: List[Dict[str, Any]]
    description: Optional[str] = None


class FileAnalysisRequest(BaseModel):
    file_path: str


class RowUpdateRequest(BaseModel):
    row_id: str
    updates: Dict[str, Any]


# Routes
@router.get("/")
async def list_tables():
    """List all registered memory tables"""
    try:
        from backend.memory_tables.registry import table_registry
        
        tables = []
        for table_name in table_registry.list_tables():
            schema = table_registry.get_schema(table_name)
            tables.append({
                'name': table_name,
                'description': schema.get('description', ''),
                'field_count': len(schema.get('fields', [])),
                'status': 'active'
            })
        
        return {
            'success': True,
            'tables': tables,
            'count': len(tables)
        }
    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Get schema definition for a table"""
    try:
        from backend.memory_tables.registry import table_registry
        
        schema = table_registry.get_schema(table_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        return {
            'success': True,
            'schema': schema
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{table_name}/rows")
async def query_table_rows(
    table_name: str,
    limit: int = 100,
    offset: int = 0,
    filters: Optional[str] = None
):
    """Query rows from a table"""
    try:
        from backend.memory_tables.registry import table_registry
        
        # Parse filters if provided
        filter_dict = {}
        if filters:
            import json
            filter_dict = json.loads(filters)
        
        rows = table_registry.query_rows(table_name, filters=filter_dict, limit=limit)
        
        # Convert to dict for JSON serialization
        rows_data = [
            {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in row.__dict__.items() if not k.startswith('_')}
            for row in rows
        ]
        
        return {
            'success': True,
            'table': table_name,
            'rows': rows_data,
            'count': len(rows_data),
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        logger.error(f"Failed to query rows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{table_name}/rows")
async def insert_table_row(table_name: str, row: TableRow, background_tasks: BackgroundTasks):
    """
    Insert a row into a table
    Routes through Unified Logic Hub for governance
    """
    try:
        # Import here to avoid circular dependencies
        from backend.unified_logic_hub import unified_logic_hub
        from backend.memory_tables.registry import table_registry
        
        # Submit through unified logic hub
        update_result = await unified_logic_hub.submit_update(
            update_type="memory_table_insert",
            component_targets=["memory_tables", "memory_fusion"],
            content={
                'table': table_name,
                'data': row.data,
                'source': 'api'
            },
            risk_level="low",
            created_by="memory_tables_api"
        )
        
        if not update_result.get('approved', False):
            raise HTTPException(
                status_code=403,
                detail=f"Insert rejected: {update_result.get('reason', 'Unknown')}"
            )
        
        # Actually insert the row
        inserted_row = table_registry.insert_row(table_name, row.data)
        
        if not inserted_row:
            raise HTTPException(status_code=500, detail="Failed to insert row")
        
        # Convert to dict
        row_dict = {
            k: str(v) if isinstance(v, uuid.UUID) else v
            for k, v in inserted_row.__dict__.items()
            if not k.startswith('_')
        }
        
        return {
            'success': True,
            'table': table_name,
            'row': row_dict,
            'update_id': update_result.get('update_id')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to insert row: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{table_name}/rows/{row_id}")
async def update_table_row(table_name: str, row_id: str, request: RowUpdateRequest):
    """Update a row in a table"""
    try:
        from backend.unified_logic_hub import unified_logic_hub
        from backend.memory_tables.registry import table_registry
        
        # Submit through unified logic hub
        update_result = await unified_logic_hub.submit_update(
            update_type="memory_table_update",
            component_targets=["memory_tables"],
            content={
                'table': table_name,
                'row_id': row_id,
                'updates': request.updates
            },
            risk_level="low",
            created_by="memory_tables_api"
        )
        
        if not update_result.get('approved', False):
            raise HTTPException(status_code=403, detail="Update rejected")
        
        # Perform update
        success = table_registry.update_row(table_name, uuid.UUID(row_id), request.updates)
        
        return {
            'success': success,
            'table': table_name,
            'row_id': row_id,
            'update_id': update_result.get('update_id')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update row: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_file_for_schema(request: FileAnalysisRequest):
    """
    Analyze a file and propose appropriate schema
    Uses LLM Schema Inference Agent
    """
    try:
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        from backend.memory_tables.registry import table_registry
        
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Initialize agent
        agent = SchemaInferenceAgent(registry=table_registry)
        
        # Analyze file
        file_summary = await agent.analyze_file(file_path)
        
        # Get schema proposal
        existing_tables = table_registry.list_tables()
        proposal = await agent.propose_schema(file_summary, existing_tables)
        
        return {
            'success': True,
            'file_path': request.file_path,
            'analysis': file_summary,
            'proposal': proposal
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schemas")
async def create_schema(proposal: SchemaProposal, background_tasks: BackgroundTasks):
    """
    Create a new table schema
    Routes through Unified Logic Hub for approval
    """
    try:
        from backend.unified_logic_hub import unified_logic_hub
        from backend.memory_tables.registry import table_registry
        
        # Build schema dict
        schema = {
            'table': proposal.table_name,
            'description': proposal.description,
            'fields': proposal.fields,
            'indexes': [],
            'proposed_at': datetime.now().isoformat(),
            'status': 'pending_approval'
        }
        
        # Submit through unified logic hub
        update_result = await unified_logic_hub.submit_update(
            update_type="schema_creation",
            component_targets=["memory_tables", "clarity"],
            content={
                'schema': schema,
                'confidence': proposal.confidence,
                'reason': proposal.reason
            },
            risk_level="medium",  # Schema changes are medium risk
            created_by="schema_agent"
        )
        
        if not update_result.get('approved', False):
            return {
                'success': False,
                'status': 'pending_approval',
                'message': 'Schema creation requires approval',
                'update_id': update_result.get('update_id')
            }
        
        # Save the schema
        success = table_registry.save_schema(schema)
        
        if success:
            # Initialize the table in database
            table_registry.create_model_class(proposal.table_name)
            
            return {
                'success': True,
                'status': 'created',
                'table_name': proposal.table_name,
                'update_id': update_result.get('update_id')
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save schema")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/{table_name}")
async def ingest_file_to_table(
    table_name: str,
    file_path: str,
    background_tasks: BackgroundTasks
):
    """
    Ingest a file into a table
    Analyzes file, extracts data, and populates table row
    """
    try:
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        from backend.memory_tables.registry import table_registry
        from backend.unified_logic_hub import unified_logic_hub
        
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # Initialize agent
        agent = SchemaInferenceAgent(registry=table_registry)
        
        # Extract row data
        row_data = await agent.extract_row_data(path, table_name)
        
        # Submit through unified logic hub
        update_result = await unified_logic_hub.submit_update(
            update_type="file_ingestion",
            component_targets=["memory_tables", "ingestion"],
            content={
                'table': table_name,
                'file_path': file_path,
                'data': row_data
            },
            risk_level="low",
            created_by="ingestion_api"
        )
        
        if not update_result.get('approved', False):
            raise HTTPException(status_code=403, detail="Ingestion rejected")
        
        # Insert the row
        inserted_row = table_registry.insert_row(table_name, row_data)
        
        if not inserted_row:
            raise HTTPException(status_code=500, detail="Failed to insert row")
        
        return {
            'success': True,
            'table': table_name,
            'file_path': file_path,
            'row_id': str(inserted_row.id),
            'update_id': update_result.get('update_id')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_memory_tables_stats():
    """Get overall statistics for memory tables system"""
    try:
        from backend.memory_tables.registry import table_registry
        
        stats = {
            'total_tables': len(table_registry.list_tables()),
            'tables': []
        }
        
        for table_name in table_registry.list_tables():
            schema = table_registry.get_schema(table_name)
            rows = table_registry.query_rows(table_name, limit=10000)  # Get count
            
            stats['tables'].append({
                'name': table_name,
                'row_count': len(rows),
                'field_count': len(schema.get('fields', [])),
                'description': schema.get('description', '')
            })
        
        return {
            'success': True,
            'stats': stats
        }
    
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
