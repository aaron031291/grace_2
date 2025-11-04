from fastapi import APIRouter, Request
from sqlalchemy import func, select
from datetime import datetime, timedelta
from ..models import ChatMessage, User, async_session
from ..metrics_models import MetricEvent as MetricEventDB
from ..metrics_service import get_metrics_collector

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/summary")
async def summary():
    async with async_session() as session:
        total_messages = await session.scalar(select(func.count(ChatMessage.id)))
        distinct_users = await session.scalar(
            select(func.count(func.distinct(ChatMessage.user)))
        )
        
        user_count = await session.scalar(select(func.count(User.id)))
        
    return {
        "total_messages": total_messages or 0,
        "active_users": distinct_users or 0,
        "registered_users": user_count or 0
    }

@router.get("/user/{username}")
async def user_stats(username: str):
    async with async_session() as session:
        user_messages = await session.scalar(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.user == username)
        )
        
        grace_responses = await session.scalar(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.user == username, ChatMessage.role == "grace")
        )
        
    return {
        "username": username,
        "total_messages": user_messages or 0,
        "grace_responses": grace_responses or 0,
        "user_messages": (user_messages or 0) - (grace_responses or 0)
    }

@router.get("/history")
async def history(request: Request, domain: str, kpi: str, hours: int = 24):
    """
    Historical metric events.
    - If metrics persistence is enabled, reads from DB
    - Otherwise falls back to in-memory collector window
    """
    cutoff = datetime.now() - timedelta(hours=hours)

    # Prefer DB if a metrics sessionmaker is available
    sessionmaker = getattr(request.app.state, "metrics_sessionmaker", None)
    if sessionmaker:
        async with sessionmaker() as session:
            result = await session.execute(
                select(MetricEventDB)
                .where(MetricEventDB.domain == domain)
                .where(MetricEventDB.kpi == kpi)
                .where(MetricEventDB.timestamp > cutoff)
                .order_by(MetricEventDB.timestamp.asc())
            )
            events = []
            for e in result.scalars().all():
                events.append({
                    "domain": e.domain,
                    "kpi": e.kpi,
                    "value": e.value,
                    "timestamp": e.timestamp.isoformat(),
                    "metadata": e.metric_metadata or {},
                })
            return {"domain": domain, "kpi": kpi, "count": len(events), "events": events}

    # Fallback: in-memory
    collector = get_metrics_collector()
    events = collector.get_metric_history(domain, kpi, hours=hours)
    return {
        "domain": domain,
        "kpi": kpi,
        "count": len(events),
        "events": [
            {
                "domain": e.domain,
                "kpi": e.kpi,
                "value": e.value,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata or {},
            }
            for e in events
        ],
    }
