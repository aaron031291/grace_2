from fastapi import APIRouter
from sqlalchemy import select
from ..reflection import Reflection, reflection_service
from ..models import async_session
from ..schemas_extended import ReflectionsListResponse, ReflectionTriggerResponse

router = APIRouter(prefix="/api/reflections", tags=["reflections"])

@router.get("/", response_model=ReflectionsListResponse)
async def list_reflections(limit: int = 10):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Reflection)
                .order_by(Reflection.generated_at.desc())
                .limit(limit)
            )
            reflections = result.scalars().all()
            reflection_list = [
                {
                    "id": r.id,
                    "generated_at": r.generated_at,
                    "summary": r.summary,
                    "insight": r.insight,
                    "confidence": r.confidence,
                }
                for r in reflections
            ]
            return ReflectionsListResponse(
                reflections=reflection_list,
                count=len(reflection_list),
                execution_trace=None,
                data_provenance=[]
            )
    except Exception as e:
        return ReflectionsListResponse(
            reflections=[],
            count=0,
            execution_trace=None,
            data_provenance=[]
        )

@router.post("/trigger", response_model=ReflectionTriggerResponse)
async def trigger_reflection():
    try:
        await reflection_service.generate_reflection()
        return ReflectionTriggerResponse(
            status="triggered",
            message="Reflection generated",
            execution_trace=None,
            data_provenance=[]
        )
    except Exception as e:
        return ReflectionTriggerResponse(
            status="error",
            message=str(e),
            execution_trace=None,
            data_provenance=[]
        )
