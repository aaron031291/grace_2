"""
ML Coding Agent API
Endpoints for ML-powered coding assistance using Grace's internal LLM
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from ..kernels.agents.ml_coding_agent import ml_coding_agent

router = APIRouter(prefix="/api/ml-coding", tags=["ML Coding"])


class CodeGenerationRequest(BaseModel):
    description: str
    language: str = 'python'
    context: Optional[str] = None


class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = 'python'


class RefactoringRequest(BaseModel):
    code: str
    language: str = 'python'
    goals: List[str] = ['readability', 'performance']


class DocumentationRequest(BaseModel):
    code: str
    language: str = 'python'
    doc_style: str = 'docstring'


class TestGenerationRequest(BaseModel):
    code: str
    language: str = 'python'
    framework: str = 'pytest'


class ResearchRequest(BaseModel):
    technique: str


class DatasetRequest(BaseModel):
    task: str


@router.on_event("startup")
async def startup():
    """Initialize ML coding agent"""
    await ml_coding_agent.initialize()


@router.post("/generate")
async def generate_code(request: CodeGenerationRequest):
    """
    Generate code from description using Grace's internal LLM
    
    Example:
    ```json
    {
        "description": "Create a binary search function",
        "language": "python"
    }
    ```
    """
    
    result = await ml_coding_agent.generate_code(
        description=request.description,
        language=request.language,
        context=request.context
    )
    
    return result


@router.post("/understand")
async def understand_code(request: CodeAnalysisRequest):
    """
    Analyze and explain code using Grace's learned patterns
    
    Example:
    ```json
    {
        "code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
        "language": "python"
    }
    ```
    """
    
    result = await ml_coding_agent.understand_code(
        code=request.code,
        language=request.language
    )
    
    return result


@router.post("/bugs")
async def detect_bugs(request: CodeAnalysisRequest):
    """
    Detect bugs in code using Grace's analysis capabilities
    """
    
    result = await ml_coding_agent.detect_bugs(
        code=request.code,
        language=request.language
    )
    
    return result


@router.post("/refactor")
async def suggest_refactoring(request: RefactoringRequest):
    """
    Suggest refactoring improvements
    
    Example:
    ```json
    {
        "code": "...",
        "language": "python",
        "goals": ["performance", "readability"]
    }
    ```
    """
    
    result = await ml_coding_agent.suggest_refactoring(
        code=request.code,
        language=request.language,
        goals=request.goals
    )
    
    return result


@router.post("/document")
async def generate_documentation(request: DocumentationRequest):
    """
    Generate documentation for code
    
    Example:
    ```json
    {
        "code": "def add(a, b): return a + b",
        "language": "python",
        "doc_style": "docstring"
    }
    ```
    """
    
    result = await ml_coding_agent.generate_documentation(
        code=request.code,
        language=request.language,
        doc_style=request.doc_style
    )
    
    return result


@router.post("/tests")
async def generate_tests(request: TestGenerationRequest):
    """
    Generate unit tests for code
    
    Example:
    ```json
    {
        "code": "def add(a, b): return a + b",
        "language": "python",
        "framework": "pytest"
    }
    ```
    """
    
    result = await ml_coding_agent.generate_tests(
        code=request.code,
        language=request.language,
        framework=request.framework
    )
    
    return result


@router.post("/research")
async def research_technique(request: ResearchRequest):
    """
    Research ML/coding technique via arXiv papers
    
    Example:
    ```json
    {
        "technique": "transformer architecture"
    }
    ```
    """
    
    result = await ml_coding_agent.research_technique(
        technique=request.technique
    )
    
    return result


@router.post("/datasets")
async def get_datasets(request: DatasetRequest):
    """
    Get datasets for ML task
    
    Example:
    ```json
    {
        "task": "image_classification"
    }
    ```
    """
    
    result = await ml_coding_agent.get_datasets_for_task(
        task=request.task
    )
    
    return result


@router.get("/stats")
async def get_stats():
    """Get ML coding agent statistics"""
    
    stats = await ml_coding_agent.get_stats()
    
    return stats


@router.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities"""
    
    return {
        'name': ml_coding_agent.name,
        'capabilities': ml_coding_agent.capabilities,
        'llm_provider': 'Grace Internal LLM',
        'external_dependency': False,
        'description': 'Uses Grace own learned knowledge and reasoning'
    }


@router.get("/llm-info")
async def get_llm_info():
    """Get information about Grace's internal LLM"""
    
    from ..transcendence.ml_api_integrator import ml_api_integrator
    
    info = await ml_api_integrator.get_grace_llm_info()
    
    return info
