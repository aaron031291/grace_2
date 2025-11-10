from fastapi import APIRouter, Depends
from sqlalchemy import select
from ..auth import get_current_user
from ..summaries import Summary, summary_generator, async_session
router = APIRouter(prefix="/api/summaries", tags=["summaries"])

@router.get("/")
async def get_summaries(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        result = await session.execute(
            select(Summary)
            .order_by(Summary.generated_at.desc())
            .limit(limit)
        )
        summaries = result.scalars().all()
        return [
            {
                "id": s.id,
                "period": s.period,
                "period_start": s.period_start,
                "period_end": s.period_end,
                "summary_text": s.summary_text,
                "key_topics": s.key_topics,
                "tasks_created": s.tasks_created,
                "generated_at": s.generated_at
            }
            for s in summaries
        ]
@router.post("/generate")
async def generate_summary(current_user: str = Depends(get_current_user)):
    summary = await summary_generator.generate_daily_summary()
    return {"status": "generated", "summary": summary}
