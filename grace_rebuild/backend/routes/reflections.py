from fastapi import APIRouter
from sqlalchemy import select
from ..reflection import Reflection, reflection_service
from ..models import async_session

router = APIRouter(prefix="/api/reflections", tags=["reflections"])

@router.get("/")
async def list_reflections(limit: int = 10):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Reflection)
                .order_by(Reflection.generated_at.desc())
                .limit(limit)
            )
            reflections = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "generated_at": r.generated_at,
                    "summary": r.summary,
                    "insight": r.insight,
                    "confidence": r.confidence,
                }
                for r in reflections
            ]
    except Exception as e:
        return {"error": str(e), "reflections": []}

@router.post("/trigger")
async def trigger_reflection():
    try:
        await reflection_service.generate_reflection()
        return {"status": "triggered", "message": "Reflection generated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
