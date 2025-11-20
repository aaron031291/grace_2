"""
Mentor API - Local Model Orchestration Endpoints

Provides endpoints for triggering mentor roundtables, viewing results,
and running benchmarks.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.kernels.mentor_harness import get_mentor_harness
from backend.learning_memory import query_category

router = APIRouter()


class RoundtableRequest(BaseModel):
    task_description: str
    task_type: str = "general"
    context: Optional[Dict[str, Any]] = None
    models: Optional[List[str]] = None
    store_results: bool = True
    task_id: Optional[str] = None


class BenchmarkRequest(BaseModel):
    description: str
    context: Optional[Dict[str, Any]] = None
    expected_output: Optional[Any] = None
    models: Optional[List[str]] = None


@router.get("/status")
async def get_mentor_status() -> Dict[str, Any]:
    """Get mentor harness status and available models"""
    
    harness = get_mentor_harness()
    await harness.activate()
    
    status = await harness.get_status()
    
    return {
        "status": "active",
        "harness_info": status,
        "model_profiles": harness.MODEL_PROFILES
    }


@router.post("/roundtable")
async def run_roundtable(request: RoundtableRequest) -> Dict[str, Any]:
    """
    Run a mentor roundtable discussion
    
    Example:
        POST /api/mentor/roundtable
        {
            "task_description": "Design a mobile app architecture for iOS/Android",
            "task_type": "architecture",
            "context": {
                "platforms": ["iOS", "Android"],
                "features": ["auth", "realtime-chat", "media-upload"]
            },
            "models": ["qwen2.5-coder:14b", "deepseek-coder:6.7b"]
        }
    """
    
    harness = get_mentor_harness()
    await harness.activate()
    
    try:
        result = await harness.run_roundtable(
            task_description=request.task_description,
            task_type=request.task_type,
            context=request.context,
            models=request.models,
            store_results=request.store_results,
            task_id=request.task_id
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark")
async def run_benchmark(request: BenchmarkRequest) -> Dict[str, Any]:
    """
    Run a benchmark test across models
    
    Example:
        POST /api/mentor/benchmark
        {
            "description": "Implement a binary search function in Python",
            "expected_output": "def binary_search(arr, target): ...",
            "models": ["qwen2.5-coder:14b", "deepseek-coder:6.7b"]
        }
    """
    
    harness = get_mentor_harness()
    await harness.activate()
    
    try:
        benchmark_task = {
            "description": request.description,
            "context": request.context
        }
        
        if request.expected_output:
            benchmark_task["expected_output"] = request.expected_output
        
        result = await harness.run_benchmark(
            benchmark_task=benchmark_task,
            models=request.models
        )
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{task_id}")
async def get_roundtable_results(task_id: str) -> Dict[str, Any]:
    """Get stored roundtable results from Learning Memory"""
    
    try:
        # Query Learning Memory for this task
        files = await query_category("mentors", subcategory=task_id)
        
        if not files:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Load results
        import json
        results = []
        
        for file_path in files:
            with open(file_path) as f:
                data = json.load(f)
                results.append({
                    "file": file_path,
                    "data": data
                })
        
        return {
            "task_id": task_id,
            "files_found": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_roundtables(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent mentor roundtable sessions"""
    
    try:
        files = await query_category("mentors", limit=limit * 2)  # Get more to filter
        
        # Group by task (summary files)
        summaries = [f for f in files if "summary" in f][:limit]
        
        import json
        results = []
        
        for file_path in summaries:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    results.append({
                        "task_id": data.get("task_id"),
                        "task_type": data.get("task", {}).get("type"),
                        "models_queried": data.get("aggregated", {}).get("total_mentors"),
                        "consensus_confidence": data.get("aggregated", {}).get("average_confidence"),
                        "timestamp": data.get("timestamp"),
                        "file_path": file_path
                    })
            except:
                pass
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_available_models() -> Dict[str, Any]:
    """List all available local models with their profiles"""
    
    harness = get_mentor_harness()
    await harness.activate()
    
    return {
        "available_models": harness.available_models,
        "total": len(harness.available_models),
        "profiles": harness.MODEL_PROFILES
    }


@router.get("/stats")
async def get_mentor_stats() -> Dict[str, Any]:
    """Get mentor usage statistics"""
    
    try:
        # Count files in mentors category
        all_mentor_files = await query_category("mentors", limit=10000)
        
        # Count summaries (roundtables)
        summaries = [f for f in all_mentor_files if "summary" in f]
        
        # Count individual responses
        responses = [f for f in all_mentor_files if "summary" not in f]
        
        return {
            "total_roundtables": len(summaries),
            "total_mentor_responses": len(responses),
            "avg_responses_per_roundtable": len(responses) / len(summaries) if summaries else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
