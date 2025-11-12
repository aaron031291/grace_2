"""
Grace Co-Pilot API Routes
Context-aware AI assistance
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

router = APIRouter(prefix="/api/copilot", tags=["copilot"])


class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class SuggestSchemaRequest(BaseModel):
    file_path: str


class RecommendPlanRequest(BaseModel):
    file_paths: List[str]


class FlagConflictsRequest(BaseModel):
    table_name: str
    row_data: Dict[str, Any]


@router.post("/chat")
async def chat_with_grace(request: ChatRequest):
    """Chat with Grace about current context"""
    try:
        from backend.collaboration.grace_copilot_engine import grace_copilot
        
        result = await grace_copilot.chat(
            request.user_id,
            request.message,
            request.context
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-schema")
async def suggest_schema(request: SuggestSchemaRequest):
    """Generate schema suggestion from file"""
    try:
        from backend.collaboration.grace_copilot_engine import grace_copilot
        from pathlib import Path
        
        file_path = Path(request.file_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        file_content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        result = await grace_copilot.suggest_schema(
            str(file_path),
            file_content
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-plan")
async def recommend_ingestion_plan(request: RecommendPlanRequest):
    """Recommend ingestion plan for files"""
    try:
        from backend.collaboration.grace_copilot_engine import grace_copilot
        
        result = await grace_copilot.recommend_ingestion_plan(request.file_paths)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flag-conflicts")
async def flag_conflicts(request: FlagConflictsRequest):
    """Flag potential conflicts in data"""
    try:
        from backend.collaboration.grace_copilot_engine import grace_copilot
        
        result = await grace_copilot.flag_conflicts(
            request.table_name,
            request.row_data
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_file(file_path: str, user_id: str):
    """Explain a file"""
    try:
        from backend.collaboration.grace_copilot_engine import grace_copilot
        from pathlib import Path
        
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        file_content = file_path_obj.read_text(encoding='utf-8', errors='ignore')
        
        result = await grace_copilot.explain_file(
            file_path,
            file_content,
            user_id
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft-summary")
async def draft_summary(content: str, context: Optional[str] = None):
    """Draft a summary"""
    try:
        from backend.collaboration.grace_copilot_engine import grace_copilot
        
        result = await grace_copilot.draft_summary(content, context or "")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/identify-missing-fields")
async def identify_missing_fields(table_name: str, row_data: Dict[str, Any]):
    """Identify missing fields in a row"""
    try:
        from backend.collaboration.grace_copilot_engine import grace_copilot
        
        result = await grace_copilot.identify_missing_fields(table_name, row_data)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
