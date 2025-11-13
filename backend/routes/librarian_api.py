"""
Librarian Kernel API
Control and monitor the Librarian orchestration kernel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/librarian", tags=["librarian-kernel"])

# Global kernel instance (will be initialized on startup)
_librarian_kernel = None


class SpawnAgentRequest(BaseModel):
    agent_type: str
    task_data: Dict[str, Any] = {}
    priority: str = 'normal'


class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}


@router.get("/status")
async def get_kernel_status():
    """
    Get current kernel status, queue depths, and active agents.
    """
    if not _librarian_kernel:
        return {
            'kernel': {
                'kernel_id': 'librarian_kernel',
                'status': 'not_initialized',
                'active_agents': 0,
                'metrics': {
                    'events_processed': 0,
                    'agents_spawned': 0,
                    'jobs_completed': 0,
                    'errors': 0
                }
            },
            'queues': {
                'schema_queue': 0,
                'ingestion_queue': 0,
                'trust_audit_queue': 0
            },
            'agents': []
        }
    
    try:
        kernel_status = _librarian_kernel.get_status()
        queue_status = _librarian_kernel.get_queue_status()
        
        # Get active agent details
        active_agents = []
        for agent_id, agent in _librarian_kernel._sub_agents.items():
            active_agents.append({
                'agent_id': agent_id,
                'agent_type': agent.agent_type if hasattr(agent, 'agent_type') else 'unknown',
                'status': 'running',
                'started_at': agent.task_data.get('started_at', '') if hasattr(agent, 'task_data') else '',
                'task_type': agent.task_data.get('type', '') if hasattr(agent, 'task_data') else ''
            })
        
        return {
            'kernel': kernel_status,
            'queues': queue_status,
            'agents': active_agents
        }
        
    except Exception as e:
        logger.error(f"Failed to get kernel status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_kernel():
    """Start the Librarian kernel"""
    global _librarian_kernel
    
    if _librarian_kernel and _librarian_kernel.status.value == 'running':
        return {'status': 'already_running'}
    
    try:
        from backend.memory_tables.registry import table_registry
        from backend.kernels.event_bus import get_event_bus
        from backend.kernels.librarian_kernel import LibrarianKernel
        
        if not _librarian_kernel:
            event_bus = get_event_bus(registry=table_registry)
            _librarian_kernel = LibrarianKernel(
                registry=table_registry,
                event_bus=event_bus
            )
        
        success = await _librarian_kernel.start()
        
        return {
            'status': 'started' if success else 'failed',
            'kernel_id': _librarian_kernel.kernel_id
        }
        
    except Exception as e:
        logger.error(f"Failed to start kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_kernel():
    """Stop the Librarian kernel"""
    if not _librarian_kernel:
        return {'status': 'not_running'}
    
    try:
        success = await _librarian_kernel.stop()
        
        return {
            'status': 'stopped' if success else 'failed'
        }
        
    except Exception as e:
        logger.error(f"Failed to stop kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause")
async def pause_kernel():
    """Pause the Librarian kernel"""
    if not _librarian_kernel:
        raise HTTPException(status_code=400, detail="Kernel not running")
    
    try:
        await _librarian_kernel.pause()
        return {'status': 'paused'}
        
    except Exception as e:
        logger.error(f"Failed to pause kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume")
async def resume_kernel():
    """Resume the Librarian kernel"""
    if not _librarian_kernel:
        raise HTTPException(status_code=400, detail="Kernel not running")
    
    try:
        await _librarian_kernel.resume()
        return {'status': 'resumed'}
        
    except Exception as e:
        logger.error(f"Failed to resume kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/spawn-agent")
async def spawn_agent(request: SpawnAgentRequest):
    """Manually spawn a sub-agent"""
    if not _librarian_kernel:
        raise HTTPException(status_code=400, detail="Kernel not running")
    
    try:
        agent_id = await _librarian_kernel.spawn_agent(
            agent_type=request.agent_type,
            task_data=request.task_data,
            priority=request.priority
        )
        
        if agent_id:
            return {
                'status': 'spawned',
                'agent_id': agent_id,
                'agent_type': request.agent_type
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to spawn agent")
            
    except Exception as e:
        logger.error(f"Failed to spawn agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_id}")
async def terminate_agent(agent_id: str):
    """Terminate a specific agent"""
    if not _librarian_kernel:
        raise HTTPException(status_code=400, detail="Kernel not running")
    
    try:
        await _librarian_kernel.terminate_agent(agent_id)
        return {'status': 'terminated', 'agent_id': agent_id}
        
    except Exception as e:
        logger.error(f"Failed to terminate agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/schema")
async def queue_schema_proposal(file_path: str):
    """Queue a file for schema inference"""
    if not _librarian_kernel:
        raise HTTPException(status_code=400, detail="Kernel not running")
    
    try:
        await _librarian_kernel.submit_schema_proposal({
            'path': file_path,
            'timestamp': ''
        })
        
        return {'status': 'queued', 'file_path': file_path}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/ingestion")
async def queue_ingestion(file_path: str, metadata: Dict[str, Any] = {}):
    """Queue a file for ingestion"""
    if not _librarian_kernel:
        raise HTTPException(status_code=400, detail="Kernel not running")
    
    try:
        await _librarian_kernel.queue_ingestion(file_path, metadata)
        return {'status': 'queued', 'file_path': file_path}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trust-audit")
async def trigger_trust_audit():
    """Trigger a manual trust audit"""
    if not _librarian_kernel:
        raise HTTPException(status_code=400, detail="Kernel not running")
    
    try:
        await _librarian_kernel.schedule_trust_audit()
        return {'status': 'scheduled'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def librarian_chat(request: ChatRequest):
    """
    Conversational interface to Librarian operations.
    Interprets natural language commands and executes actions.
    """
    try:
        message = request.message.lower()
        context = request.context
        
        # Parse common commands
        if 'summarize' in message:
            return {
                'response': f"I'll summarize {context.get('currentFile', 'the file')} for you.",
                'action': 'summarize_file',
                'data': context
            }
        
        elif 'schema' in message or 'propose' in message:
            return {
                'response': f"I'll analyze {context.get('currentFile', 'the file')} and propose a schema.",
                'action': 'propose_schema',
                'data': context
            }
        
        elif 'ingest' in message or 'ingestion' in message:
            if _librarian_kernel:
                file_path = context.get('currentFile')
                if file_path:
                    await _librarian_kernel.queue_ingestion(file_path, context)
                    return {
                        'response': f"✅ Added {file_path} to ingestion queue.",
                        'action': 'queued_ingestion'
                    }
            return {
                'response': "I'll add this to the ingestion queue.",
                'action': 'queue_ingestion'
            }
        
        elif 'trust' in message or 'score' in message:
            return {
                'response': "Let me check the trust score for this source...",
                'action': 'check_trust'
            }
        
        elif 'flashcard' in message or 'quiz' in message:
            return {
                'response': "I'll generate flashcards from this content.",
                'action': 'generate_flashcards'
            }
        
        elif 'flag' in message or 'review' in message:
            return {
                'response': "I've flagged this for manual review.",
                'action': 'flag_review'
            }
        
        elif 'status' in message or 'queue' in message:
            if _librarian_kernel:
                queues = _librarian_kernel.get_queue_status()
                return {
                    'response': f"Current queues:\n• Schema: {queues['schema_queue']}\n• Ingestion: {queues['ingestion_queue']}\n• Trust Audit: {queues['trust_audit_queue']}",
                    'action': 'show_status'
                }
        
        else:
            return {
                'response': f"I can help with:\n• Summarizing files\n• Proposing schemas\n• Adding to ingestion\n• Checking trust scores\n• Generating flashcards\n\nTry: 'Summarize this file' or 'Add to ingestion queue'",
                'action': 'help'
            }
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions():
    """
    Get intelligent suggestions from Librarian.
    Returns pending actions and recommendations.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        suggestions: List[Dict] = []
        
        # Check for pending schema proposals
        try:
            pending_schemas = table_registry.query_rows(
                'memory_schema_proposals',
                filters={'status': 'pending'},
                limit=5
            )
            
            for schema in pending_schemas:
                schema_dict = schema.dict() if hasattr(schema, 'dict') else dict(schema)
                suggestions.append({
                    'id': schema_dict.get('id'),
                    'type': 'schema_approval',
                    'title': f"Schema proposal: {schema_dict.get('table_name')}",
                    'description': schema_dict.get('reasoning', 'New schema needs approval'),
                    'priority': 'high' if schema_dict.get('confidence', 0) > 0.8 else 'medium',
                    'actionLabel': 'Review',
                    'actionEndpoint': f"/api/memory/schemas/{schema_dict.get('id')}/approve",
                    'metadata': schema_dict
                })
        except Exception as e:
            logger.warning(f"Could not load schema proposals: {e}")
        
        # Check for low trust sources
        try:
            sources = table_registry.query_rows(
                'memory_trusted_sources',
                filters={'status': 'active'},
                limit=100
            )
            
            for source in sources:
                source_dict = source.dict() if hasattr(source, 'dict') else dict(source)
                trust_score = source_dict.get('trust_score', 1.0)
                
                if trust_score < 0.3:
                    suggestions.append({
                        'id': source_dict.get('id'),
                        'type': 'trust_warning',
                        'title': f"Low trust: {source_dict.get('source_name')}",
                        'description': f"Trust score dropped to {int(trust_score * 100)}%",
                        'priority': 'high',
                        'actionLabel': 'Review Source',
                        'actionEndpoint': f"/api/librarian/trust-audit",
                        'metadata': source_dict
                    })
        except Exception as e:
            logger.warning(f"Could not check trust sources: {e}")
        
        return {'suggestions': suggestions}
        
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        return {'suggestions': []}


@router.get("/activity")
async def get_activity(filter: str = 'all', limit: int = 50):
    """
    Get Librarian activity log.
    Shows all actions taken by the kernel and sub-agents.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        filters_dict = {}
        if filter != 'all':
            # Map filter to action types
            type_map = {
                'schema': 'schema_proposal',
                'ingestion': 'ingestion_launch',
                'trust': 'trust_update',
                'governance': 'governance_request'
            }
            if filter in type_map:
                filters_dict['action_type'] = type_map[filter]
        
        actions = table_registry.query_rows(
            'memory_librarian_log',
            filters=filters_dict,
            limit=limit,
            order_by='timestamp DESC'
        )
        
        return {
            'actions': [a.dict() if hasattr(a, 'dict') else dict(a) for a in actions]
        }
        
    except Exception as e:
        logger.error(f"Failed to get activity: {e}")
        return {'actions': []}


@router.get("/daily-summary")
async def get_daily_summary():
    """
    Get summary of Librarian activity for today.
    """
    try:
        from backend.memory_tables.registry import table_registry
        from datetime import datetime, timedelta
        
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time()).isoformat()
        
        # Count actions by type
        all_actions = table_registry.query_rows(
            'memory_librarian_log',
            filters={'timestamp__gte': start_of_day},
            limit=10000
        )
        
        actions_list = [a.dict() if hasattr(a, 'dict') else dict(a) for a in all_actions]
        
        summary = {
            'date': today.isoformat(),
            'new_files': sum(1 for a in actions_list if 'file' in a.get('target_resource', '').lower()),
            'tables_updated': len(set(a.get('target_resource') for a in actions_list if 'memory_' in a.get('target_resource', ''))),
            'schemas_proposed': sum(1 for a in actions_list if a.get('action_type') == 'schema_proposal'),
            'schemas_approved': sum(1 for a in actions_list if a.get('action_type') == 'schema_proposal' and a.get('status') == 'succeeded'),
            'ingestion_jobs': sum(1 for a in actions_list if a.get('action_type') == 'ingestion_launch'),
            'trust_audits': sum(1 for a in actions_list if a.get('action_type') == 'trust_update'),
            'agents_spawned': sum(1 for a in actions_list if a.get('action_type') == 'agent_spawn'),
            'approvals_pending': 0  # Will be calculated below
        }
        
        # Count pending approvals
        try:
            pending = table_registry.query_rows(
                'memory_schema_proposals',
                filters={'status': 'pending'},
                limit=1000
            )
            summary['approvals_pending'] = len(pending)
        except:
            pass
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get daily summary: {e}")
        return {
            'date': datetime.utcnow().date().isoformat(),
            'new_files': 0,
            'tables_updated': 0,
            'schemas_proposed': 0,
            'schemas_approved': 0,
            'ingestion_jobs': 0,
            'trust_audits': 0,
            'agents_spawned': 0,
            'approvals_pending': 0
        }


@router.get("/pending-approvals")
async def get_pending_approvals():
    """
    Get list of items pending approval.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        approvals = []
        
        # Get schema proposals
        schemas = table_registry.query_rows(
            'memory_schema_proposals',
            filters={'status': 'pending'},
            limit=20
        )
        
        for schema in schemas:
            schema_dict = schema.dict() if hasattr(schema, 'dict') else dict(schema)
            approvals.append({
                'id': schema_dict.get('id'),
                'type': 'schema',
                'title': f"Schema: {schema_dict.get('table_name')}",
                'description': schema_dict.get('reasoning', ''),
                'confidence': schema_dict.get('confidence', 0.0),
                'submitted_at': schema_dict.get('submitted_at', '')
            })
        
        return {'approvals': approvals}
        
    except Exception as e:
        logger.error(f"Failed to get pending approvals: {e}")
        return {'approvals': []}


def get_kernel_instance():
    """Get the global kernel instance (for use in other modules)"""
    return _librarian_kernel
