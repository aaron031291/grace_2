"""Observatory Dashboard - Backend API for Real-Time Cognitive State

Provides APIs for:
- Current cognitive state
- Learning progress (8-stage cycles)
- Reasoning chains
- Memory formation
- Pending proposals
- WebSocket streaming
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import asyncio
import json

from ...models import async_session
from ...auth import get_current_user
from ..cognitive_observatory import CognitiveStep
from ...cognition.GraceLoopOutput import GraceLoopOutput, OutputType
from ...meta_loop import MetaAnalysis, meta_loop_engine
from ...memory_models import MemoryArtifact
# Prefer a dedicated Proposal model; fallback to GovernanceSession if not present
try:
    from ...parliament_models import Proposal  # type: ignore
except Exception:  # pragma: no cover - compatibility
    from ...parliament_models import GovernanceSession as Proposal

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class ObservatoryDashboard:
    """Backend API for cognitive observatory"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def get_cognitive_state(self) -> Dict[str, Any]:
        """Get current cognitive state"""
        async with async_session() as session:
            # Get most recent cognitive step (ordered by started_at)
            result = await session.execute(
                select(CognitiveStep)
                .order_by(desc(CognitiveStep.started_at))
                .limit(1)
            )
            latest_step = result.scalar_one_or_none()
            
            if not latest_step:
                return {
                    "status": "idle",
                    "current_stage": None,
                    "message": "No active cognitive process"
                }
            
            # Get current cycle steps
            cycle_result = await session.execute(
                select(CognitiveStep)
                .where(CognitiveStep.cycle_id == latest_step.cycle_id)
                .order_by(CognitiveStep.sequence)
            )
            cycle_steps = cycle_result.scalars().all()

            # Derive completed count (completed_at present or success True)
            completed_steps = len([s for s in cycle_steps if (getattr(s, 'completed_at', None) is not None) or (getattr(s, 'success', None) is True)])
            
            return {
                "status": "active",
                "cycle_id": latest_step.cycle_id,
                "current_stage": latest_step.stage,
                "current_substage": latest_step.substage,
                "reasoning": latest_step.reasoning,
                "confidence": latest_step.confidence,
                "evidence": latest_step.evidence,
                "alternatives": latest_step.alternatives_considered,
                "decision": latest_step.decision_made,
                "progress": {
                    "completed_steps": completed_steps,
                    "total_steps": len(cycle_steps),
                    "stages": list(set([s.stage for s in cycle_steps]))
                },
                "timestamp": (latest_step.started_at.isoformat() if getattr(latest_step, 'started_at', None) else None)
            }
    
    async def get_learning_progress(self, cycle_id: Optional[str] = None) -> Dict[str, Any]:
        """Get 8-stage learning cycle progress"""
        async with async_session() as session:
            if not cycle_id:
                # Get latest cycle
                result = await session.execute(
                    select(CognitiveStep.cycle_id)
                    .order_by(desc(CognitiveStep.created_at))
                    .limit(1)
                )
                row = result.first()
                if not row:
                    return {"error": "No learning cycles found"}
                cycle_id = row[0]
            
            # Get all steps in cycle
            result = await session.execute(
                select(CognitiveStep)
                .where(CognitiveStep.cycle_id == cycle_id)
                .order_by(CognitiveStep.sequence)
            )
            steps = result.scalars().all()
            
            # Group by stage
            stages = {}
            for step in steps:
                if step.stage not in stages:
                    stages[step.stage] = []
                stages[step.stage].append({
                    "substage": step.substage,
                    "reasoning": step.reasoning,
                    "confidence": step.confidence,
                    "completed": step.completed,
                    "timestamp": step.created_at.isoformat() if step.created_at else None
                })
            
            # Calculate overall progress
            completed = len([s for s in steps if s.completed])
            total = len(steps)
            
            return {
                "cycle_id": cycle_id,
                "stages": stages,
                "progress": {
                    "completed": completed,
                    "total": total,
                    "percentage": (completed / total * 100) if total > 0 else 0
                },
                "started_at": steps[0].created_at.isoformat() if steps else None,
                "status": "completed" if completed == total else "in_progress"
            }
    
    async def get_reasoning_chains(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decision-making chains"""
        async with async_session() as session:
            result = await session.execute(
                select(CognitiveStep)
                .where(CognitiveStep.decision_made.isnot(None))
                .order_by(desc(CognitiveStep.created_at))
                .limit(limit)
            )
            steps = result.scalars().all()
            
            chains = []
            for step in steps:
                chains.append({
                    "cycle_id": step.cycle_id,
                    "stage": step.stage,
                    "decision": step.decision_made,
                    "reasoning": step.reasoning,
                    "confidence": step.confidence,
                    "evidence": step.evidence,
                    "alternatives": step.alternatives_considered,
                    "timestamp": step.created_at.isoformat() if step.created_at else None
                })
            
            return chains
    
    async def get_memory_formation(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get what's being stored in memory"""
        async with async_session() as session:
            result = await session.execute(
                select(MemoryArtifact)
                .order_by(desc(MemoryArtifact.created_at))
                .limit(limit)
            )
            artifacts = result.scalars().all()
            
            memories = []
            for artifact in artifacts:
                memories.append({
                    "artifact_id": artifact.artifact_id,
                    "type": artifact.artifact_type,
                    "modality": artifact.modality,
                    "importance": artifact.importance_score,
                    "access_count": artifact.access_count,
                    "tags": artifact.tags if hasattr(artifact, 'tags') else [],
                    "created_at": artifact.created_at.isoformat() if artifact.created_at else None
                })
            
            return memories
    
    async def get_proposals_pending(self) -> List[Dict[str, Any]]:
        """Get Grace's pending proposals"""
        async with async_session() as session:
            result = await session.execute(
                select(Proposal)
                .where(Proposal.status == "pending")
                .order_by(desc(Proposal.created_at))
            )
            proposals = result.scalars().all()
            
            pending = []
            for proposal in proposals:
                pending.append({
                    "proposal_id": proposal.proposal_id,
                    "title": proposal.title,
                    "description": proposal.description,
                    "proposer": proposal.proposer,
                    "category": proposal.category if hasattr(proposal, 'category') else "general",
                    "impact": proposal.impact_score if hasattr(proposal, 'impact_score') else 0.5,
                    "created_at": proposal.created_at.isoformat() if proposal.created_at else None
                })
            
            return pending
    
    async def stream_cognitive_updates(self, websocket: WebSocket):
        """Stream real-time cognitive updates via WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            while True:
                # Get latest state
                state = await self.get_cognitive_state()
                
                # Send to client
                await websocket.send_json({
                    "type": "cognitive_update",
                    "data": state,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Wait before next update
                await asyncio.sleep(1)
                
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            print(f"WebSocket error: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def broadcast_update(self, update_type: str, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        message = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


observatory_dashboard = ObservatoryDashboard()


@router.get("/cognitive/current")
async def get_current_cognitive_state(current_user: str = Depends(get_current_user)):
    """Get real-time cognitive state"""
    return await observatory_dashboard.get_cognitive_state()


@router.get("/cognitive/cycles")
async def get_learning_cycles(
    cycle_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get learning cycle progress"""
    return await observatory_dashboard.get_learning_progress(cycle_id)


@router.get("/cognitive/reasoning")
async def get_reasoning_chains(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    """Get recent reasoning chains"""
    chains = await observatory_dashboard.get_reasoning_chains(limit)
    return {"chains": chains, "count": len(chains)}


@router.get("/cognitive/memory")
async def get_memory_formation(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    """Get memory formation activity"""
    memories = await observatory_dashboard.get_memory_formation(limit)
    return {"memories": memories, "count": len(memories)}


@router.get("/proposals/pending")
async def get_pending_proposals(current_user: str = Depends(get_current_user)):
    """Get pending proposals from Grace"""
    proposals = await observatory_dashboard.get_proposals_pending()
    return {"proposals": proposals, "count": len(proposals)}


@router.get("/business/revenue")
async def get_revenue_data(
    timeframe: str = "month",
    current_user: str = Depends(get_current_user)
):
    """Get revenue data"""
    from ..business.revenue_tracker import revenue_tracker
    
    profit = await revenue_tracker.calculate_profit(timeframe)
    sources = await revenue_tracker.analyze_revenue_sources()
    growth = await revenue_tracker.calculate_growth_rate(timeframe)
    
    return {
        "profit": profit,
        "sources": sources,
        "growth": growth
    }


@router.get("/business/forecast")
async def get_revenue_forecast(
    months: int = 3,
    current_user: str = Depends(get_current_user)
):
    """Get revenue forecast"""
    from ..business.revenue_tracker import revenue_tracker
    
    forecasts = await revenue_tracker.forecast_revenue(months)
    return {"forecasts": forecasts}


@router.get("/business/optimizations")
async def get_optimizations(current_user: str = Depends(get_current_user)):
    """Get Grace's optimization suggestions"""
    from ..business.revenue_tracker import revenue_tracker
    
    suggestions = await revenue_tracker.suggest_optimizations()
    return {"suggestions": suggestions, "count": len(suggestions)}


@router.websocket("/ws/cognitive")
async def cognitive_websocket(websocket: WebSocket):
    """WebSocket for real-time cognitive updates"""
    await observatory_dashboard.stream_cognitive_updates(websocket)
