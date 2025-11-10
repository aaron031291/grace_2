"""Coding Agent API - Endpoints for AI code assistance"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..code_memory import code_memory
from ..code_understanding import code_understanding
from ..code_generator import code_generator
from ..dev_workflow import dev_workflow
from ..auth import get_current_user
from ..agentic import coding_orchestrator
from ..agentic.orchestrator import OrchestrationPlan
=======
from ..schemas import (
    CodeParseResponse, CodeContextResponse, CodeSuggestionsResponse, CodeIntentResponse,
    CodeGenerateResponse, CodeTaskResponse, CodeTaskProgressResponse, CodeRelatedResponse,
    CodePatternsResponse, CodeOrchestrationPlanResponse, CodeOrchestrationExecuteResponse
)
>>>>>>> origin/main

router = APIRouter(prefix="/api/code", tags=["coding_agent"])

class ParseCodebaseRequest(BaseModel):
    root_path: str
    project_name: str = "grace_2"
    language_filter: Optional[List[str]] = None

class AnalyzeContextRequest(BaseModel):
    file_path: str
    cursor_position: Optional[Dict[str, int]] = None
    file_content: Optional[str] = None
    session_id: str = "default"

class UnderstandIntentRequest(BaseModel):
    description: str
    context: Optional[Dict[str, Any]] = None

class GenerateFunctionRequest(BaseModel):
    name: str
    description: str
    parameters: List[Dict[str, Any]] = []
    return_type: str = "Any"
    language: str = "python"
    use_patterns: bool = True

class GenerateClassRequest(BaseModel):
    name: str
    description: str
    base_classes: List[str] = []
    attributes: List[Dict[str, Any]] = []
    methods: List[Dict[str, Any]] = []
    language: str = "python"

class GenerateTestsRequest(BaseModel):
    code: str
    framework: str = "pytest"
    language: str = "python"

class FixErrorsRequest(BaseModel):
    code: str
    errors: List[Dict[str, Any]]
    language: str = "python"

class RefactorCodeRequest(BaseModel):
    code: str
    style: str
    language: str = "python"

class SearchPatternsRequest(BaseModel):
    query: str
    language: str = "python"
    limit: int = 10

class SubmitTaskRequest(BaseModel):
    description: str
    context: Optional[Dict[str, Any]] = None


class OrchestratePlanRequest(BaseModel):
    description: str
    context: Optional[Dict[str, Any]] = None


class ExecuteOrchestrationRequest(BaseModel):
    description: str
    plan: Dict[str, Any]


def _resolve_user(current_user: Any) -> str:
    if isinstance(current_user, str):
        return current_user
    if isinstance(current_user, dict):
        return current_user.get("username") or current_user.get("user") or "system"
    return "system"


def _plan_to_dict(plan: OrchestrationPlan) -> Dict[str, Any]:
    return {
        "steps": plan.steps,
        "intent": plan.intent,
        "code_context": plan.code_context,
        "rationale": plan.rationale,
        "created_at": plan.created_at.isoformat(),
    }

<<<<<<< HEAD
@router.post("/parse")
async def parse_codebase(
    request: ParseCodebaseRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Parse codebase into Grace's memory
    
    Extract functions, classes, and patterns from a codebase
    """
    
    try:
        result = await code_memory.parse_codebase(
            root_path=request.root_path,
            project_name=request.project_name,
            language_filter=request.language_filter
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/understand")
async def analyze_context(
    request: AnalyzeContextRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze current code context
    
    Understand what user is editing and provide suggestions
    """
    
    try:
        context = await code_understanding.analyze_current_context(
            file_path=request.file_path,
            cursor_position=request.cursor_position,
            file_content=request.file_content,
            session_id=request.session_id
        )
        
        return {
            "status": "success",
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest")
async def get_suggestions(
    request: AnalyzeContextRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get code suggestions based on current context
    """
    
    try:
        # First analyze context
        context = await code_understanding.analyze_current_context(
            file_path=request.file_path,
            cursor_position=request.cursor_position,
            file_content=request.file_content,
            session_id=request.session_id
        )
        
        # Get suggestions
        suggestions = await code_understanding.suggest_next_steps(context)
        
        return {
            "status": "success",
            "suggestions": suggestions,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/intent")
async def understand_intent(
    request: UnderstandIntentRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Parse natural language intent into actionable tasks
    """
    
    try:
        intent = await code_understanding.understand_intent(
            description=request.description,
            context=request.context
        )
        
        return {
            "status": "success",
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/function")
async def generate_function(
    request: GenerateFunctionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate function from specification
    """
    
    try:
        spec = {
            'name': request.name,
            'description': request.description,
            'parameters': request.parameters,
            'return_type': request.return_type
        }
        
        result = await code_generator.generate_function(
            spec=spec,
            language=request.language,
            use_patterns=request.use_patterns
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/class")
async def generate_class(
    request: GenerateClassRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate class from specification
    """
    
    try:
        spec = {
            'name': request.name,
            'description': request.description,
            'base_classes': request.base_classes,
            'attributes': request.attributes,
            'methods': request.methods
        }
        
        result = await code_generator.generate_class(
            spec=spec,
            language=request.language
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/tests")
async def generate_tests(
    request: GenerateTestsRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Auto-generate tests for code
    """
    
    try:
        result = await code_generator.generate_tests(
            code=request.code,
            framework=request.framework,
            language=request.language
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fix")
async def fix_errors(
    request: FixErrorsRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Auto-fix errors in code
    """
    
    try:
        result = await code_generator.fix_errors(
            code=request.code,
            errors=request.errors,
            language=request.language
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refactor")
async def refactor_code(
    request: RefactorCodeRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Refactor code to match style guidelines
    """
    
    try:
        result = await code_generator.refactor_code(
            code=request.code,
            style=request.style,
            language=request.language
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns")
async def search_patterns(
    query: str,
    language: str = "python",
    limit: int = 10,
    current_user: Dict = Depends(get_current_user)
):
    """
    Search for code patterns in memory
    """
    
    try:
        patterns = await code_memory.recall_patterns(
            intent=query,
            language=language,
            limit=limit
        )
        
        return {
            "status": "success",
            "patterns": patterns,
            "count": len(patterns),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/task")
async def submit_task(
    request: SubmitTaskRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Submit development task for automated execution
    """
    
    try:
        # Parse task
        task = await dev_workflow.parse_task(
            natural_language=request.description,
            context=request.context
        )
        
        # Plan implementation
        plan = await dev_workflow.plan_implementation(task)
        
        # Execute plan (async)
        # In production, this would be queued for background execution
        
        return {
            "status": "success",
            "task": task,
            "plan": plan,
            "message": "Task submitted for execution",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}/progress")
async def get_task_progress(
    task_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Track progress of development task
    """
    
    try:
        progress = await dev_workflow.track_progress(task_id)
        
        return {
            "status": "success",
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/related")
async def find_related_code(
    pattern: str,
    context: Optional[Dict[str, Any]] = None,
    threshold: float = 0.7,
    current_user: Dict = Depends(get_current_user)
):
    """
    Find related code in codebase
    """
    
    try:
        related = await code_understanding.find_related_code(
            pattern=pattern,
            context=context,
            similarity_threshold=threshold
        )
        
        return {
            "status": "success",
            "related": related,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orchestrate/plan")
async def orchestrate_plan(
    request: OrchestratePlanRequest,
    current_user: Dict = Depends(get_current_user)
):
    try:
        user = _resolve_user(current_user)
        plan = await coding_orchestrator.plan(
            description=request.description,
            user=user,
            context=request.context,
        )
        return {
            "status": "success",
            "plan": _plan_to_dict(plan),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orchestrate/execute")
async def execute_orchestration(
    request: ExecuteOrchestrationRequest,
    current_user: Dict = Depends(get_current_user)
):
    try:
        user = _resolve_user(current_user)
        payload = request.plan or {}
        created_at = payload.get("created_at")
        plan = OrchestrationPlan(
            steps=payload.get("steps", []),
            intent=payload.get("intent", {}),
            code_context=payload.get("code_context", {}),
            rationale=payload.get("rationale", ""),
            created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
        )
        result = await coding_orchestrator.execute(
            plan,
            description=request.description,
            user=user,
        )
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orchestrate/run")
async def quick_orchestration(
    request: OrchestratePlanRequest,
    current_user: Dict = Depends(get_current_user)
):
    try:
        user = _resolve_user(current_user)
        result = await coding_orchestrator.quick_execute(
            description=request.description,
            user=user,
            context=request.context,
        )
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
