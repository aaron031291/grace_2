from fastapi import APIRouter, Depends
from sqlalchemy import select
from ..auth import get_current_user
from ..summaries import Summary, summary_generator, async_session
from ..schemas_extended import SummariesListResponse, SummaryGenerateResponse

router = APIRouter(prefix="/api/summaries", tags=["summaries"])

@router.get("/", response_model=SummariesListResponse)
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
        summary_list = [
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
        return SummariesListResponse(
            summaries=summary_list,
            count=len(summary_list),
            execution_trace=None,
            data_provenance=[]
        )

@router.post("/generate", response_model=SummaryGenerateResponse)
async def generate_summary(current_user: str = Depends(get_current_user)):
    summary = await summary_generator.generate_daily_summary()
    return SummaryGenerateResponse(
        status="generated",
        summary=summary,
        execution_trace=None,
        data_provenance=[]
    )
