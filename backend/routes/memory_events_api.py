"""
Memory Events API
Real-time event streaming for UI updates
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json
from datetime import datetime

router = APIRouter(prefix="/api/memory/events", tags=["memory-events"])


class MemoryEventStream:
    """
    Manages event streaming for real-time UI updates.
    """
    
    def __init__(self):
        self.subscribers = []
        self.event_queue = asyncio.Queue()
    
    async def publish(self, event_type: str, data: dict):
        """Publish an event to all subscribers"""
        event = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.event_queue.put(event)
    
    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Subscribe to event stream"""
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        
        try:
            while True:
                # Wait for new event
                event = await queue.get()
                
                # Format as SSE (Server-Sent Events)
                yield f"data: {json.dumps(event)}\n\n"
        
        except asyncio.CancelledError:
            # Clean up on disconnect
            self.subscribers.remove(queue)
            raise


# Global event stream
memory_event_stream = MemoryEventStream()


@router.get("/stream")
async def stream_events():
    """
    Stream memory events to UI.
    
    Returns Server-Sent Events (SSE) stream for real-time updates.
    Events: file_uploaded, schema_proposed, row_inserted, agent_spawned, etc.
    """
    async def event_generator():
        async for event in memory_event_stream.subscribe():
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/recent")
async def get_recent_events(limit: int = 50):
    """Get recent events (polling alternative to streaming)"""
    try:
        from backend.memory_tables.registry import table_registry
        
        # Get recent activity from various tables
        events = []
        
        # Recent documents
        docs = table_registry.query_rows('memory_documents', limit=10)
        for doc in docs:
            events.append({
                'type': 'document_added',
                'title': doc.title if hasattr(doc, 'title') else 'Unknown',
                'timestamp': doc.created_at if hasattr(doc, 'created_at') else None,
                'trust_score': doc.trust_score if hasattr(doc, 'trust_score') else 0
            })
        
        # Recent agent activity
        from backend.subsystems.sub_agents_integration import sub_agents_integration
        fleet_stats = await sub_agents_integration.get_fleet_stats()
        
        events.append({
            'type': 'fleet_status',
            'total_agents': fleet_stats.get('total_agents', 0),
            'active_agents': fleet_stats.get('by_status', {}).get('active', 0),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Sort by timestamp
        events.sort(key=lambda e: e.get('timestamp', ''), reverse=True)
        
        return {
            'success': True,
            'events': events[:limit]
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'events': []
        }


# Helper functions to emit events from other modules
async def emit_file_uploaded(file_path: str, size: int):
    """Emit file uploaded event"""
    await memory_event_stream.publish('file_uploaded', {
        'file_path': file_path,
        'size': size
    })


async def emit_schema_proposed(proposal_id: str, table_name: str, confidence: float):
    """Emit schema proposed event"""
    await memory_event_stream.publish('schema_proposed', {
        'proposal_id': proposal_id,
        'table_name': table_name,
        'confidence': confidence
    })


async def emit_row_inserted(table_name: str, row_id: str, trust_score: float):
    """Emit row inserted event"""
    await memory_event_stream.publish('row_inserted', {
        'table_name': table_name,
        'row_id': row_id,
        'trust_score': trust_score
    })


async def emit_agent_spawned(agent_id: str, agent_type: str):
    """Emit agent spawned event"""
    await memory_event_stream.publish('agent_spawned', {
        'agent_id': agent_id,
        'agent_type': agent_type
    })
