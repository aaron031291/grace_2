from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..causal_graph import CausalGraph
from ..causal_analyzer import causal_analyzer


router = APIRouter(prefix="/api/causal", tags=["causal_graph"])

class BuildGraphRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    user: Optional[str] = None
    days_back: int = 7

class PathRequest(BaseModel):
    event_a_id: int
    event_a_type: str
    event_b_id: int
    event_b_type: str

@router.post("/build-graph")
async def build_graph(request: BuildGraphRequest):
    """Build causal graph from date range"""
    try:
        if request.start_date and request.end_date:
            start = datetime.fromisoformat(request.start_date)
            end = datetime.fromisoformat(request.end_date)
        else:
            end = datetime.utcnow()
            start = end - timedelta(days=request.days_back)
        
        graph = CausalGraph()
        node_count = await graph.build_from_events(start, end, request.user)
        
        stats = {
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "user_filter": request.user
        }
        
        return {
            "success": True,
            "message": f"Built graph with {node_count} nodes",
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build graph: {str(e)}")

@router.get("/causes/{event_id}")
async def get_causes(
    event_id: int,
    event_type: str = Query(..., description="Event type (e.g., 'message_user', 'task_created')"),
    max_depth: int = Query(3, ge=1, le=5),
    days_back: int = Query(7, ge=1, le=30),
    user: Optional[str] = None
):
    """Find what caused this event"""
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        
        graph = CausalGraph()
        await graph.build_from_events(start, end, user)
        
        causes = graph.find_causes(event_id, event_type, max_depth)
        
        return {
            "event_id": event_id,
            "event_type": event_type,
            "causes_found": len(causes),
            "causes": causes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find causes: {str(e)}")

@router.get("/effects/{event_id}")
async def get_effects(
    event_id: int,
    event_type: str = Query(..., description="Event type (e.g., 'message_user', 'task_created')"),
    max_depth: int = Query(3, ge=1, le=5),
    days_back: int = Query(7, ge=1, le=30),
    user: Optional[str] = None
):
    """Find what this event caused"""
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        
        graph = CausalGraph()
        await graph.build_from_events(start, end, user)
        
        effects = graph.find_effects(event_id, event_type, max_depth)
        
        return {
            "event_id": event_id,
            "event_type": event_type,
            "effects_found": len(effects),
            "effects": effects
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find effects: {str(e)}")

@router.post("/path")
async def find_causal_path(
    request: PathRequest,
    days_back: int = Query(7, ge=1, le=30),
    user: Optional[str] = None
):
    """Find causal path between two events"""
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        
        graph = CausalGraph()
        await graph.build_from_events(start, end, user)
        
        path = graph.find_path(
            request.event_a_id, request.event_a_type,
            request.event_b_id, request.event_b_type
        )
        
        if path is None:
            return {
                "path_found": False,
                "message": "No causal path exists between these events",
                "event_a": {"id": request.event_a_id, "type": request.event_a_type},
                "event_b": {"id": request.event_b_id, "type": request.event_b_type}
            }
        
        return {
            "path_found": True,
            "path_length": len(path),
            "path": path,
            "event_a": {"id": request.event_a_id, "type": request.event_a_type},
            "event_b": {"id": request.event_b_id, "type": request.event_b_type}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find path: {str(e)}")

@router.get("/influence")
async def get_influential_events(
    limit: int = Query(10, ge=1, le=50),
    days_back: int = Query(7, ge=1, le=30),
    user: Optional[str] = None
):
    """Get most influential events"""
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        
        graph = CausalGraph()
        await graph.build_from_events(start, end, user)
        
        influential = graph.get_most_influential_events(limit)
        
        return {
            "analysis_period": f"{days_back} days",
            "total_events_analyzed": len(graph.nodes),
            "most_influential": influential
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate influence: {str(e)}")

@router.get("/cycles")
async def detect_feedback_loops(
    days_back: int = Query(7, ge=1, le=30),
    user: Optional[str] = None
):
    """Find feedback loops in the system"""
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        
        graph = CausalGraph()
        await graph.build_from_events(start, end, user)
        
        cycles = graph.detect_cycles()
        
        return {
            "cycles_found": len(cycles),
            "cycles": cycles[:10],
            "analysis_period": f"{days_back} days"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect cycles: {str(e)}")

@router.get("/visualize")
async def get_visualization_data(
    days_back: int = Query(7, ge=1, le=30),
    user: Optional[str] = None,
    prune_threshold: float = Query(0.3, ge=0.0, le=1.0)
):
    """Export graph data for D3.js/Cytoscape visualization"""
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)
        
        graph = CausalGraph()
        await graph.build_from_events(start, end, user)
        
        if prune_threshold > 0:
            graph.prune_weak_edges(prune_threshold)
        
        viz_data = graph.export_for_visualization()
        
        return viz_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate visualization: {str(e)}")

@router.get("/analyze/task-completion")
async def analyze_task_completion(
    user: Optional[str] = None,
    days: int = Query(7, ge=1, le=30)
):
    """Analyze what causes tasks to complete or fail"""
    try:
        analysis = await causal_analyzer.analyze_task_completion(user, days)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analyze/error-chains")
async def analyze_error_chains(
    user: Optional[str] = None,
    days: int = Query(7, ge=1, le=30)
):
    """Trace errors to root cause"""
    try:
        analysis = await causal_analyzer.analyze_error_chains(user, days)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analyze/optimization")
async def analyze_optimization_paths(
    metric: str = Query("task_completion", description="Metric to optimize"),
    user: Optional[str] = None,
    days: int = Query(7, ge=1, le=30)
):
    """Find best ways to improve a metric"""
    try:
        analysis = await causal_analyzer.analyze_optimization_paths(metric, user, days)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analyze/feedback-loops")
async def analyze_feedback_loops(
    user: Optional[str] = None,
    days: int = Query(7, ge=1, le=30)
):
    """Detect and analyze feedback loops"""
    try:
        analysis = await causal_analyzer.analyze_feedback_loops(user, days)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
