"""
RAG Evaluation API Endpoints
Provides access to RAG quality metrics and evaluation
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel

from ..rag.evaluation_harness import RAGEvaluationHarness, EvaluationMetrics

router = APIRouter(prefix="/api/rag", tags=["rag-evaluation"])

harness = RAGEvaluationHarness()

class EvaluationRequest(BaseModel):
    """Request to run RAG evaluation"""
    k_values: List[int] = [1, 5, 10]

@router.get("/health")
async def get_rag_health():
    """Get RAG evaluation system health"""
    return {
        "status": "operational",
        "harness": "active",
        "dataset_loaded": len(harness.questions) > 0,
        "questions_count": len(harness.questions)
    }

@router.get("/dataset")
async def get_evaluation_dataset():
    """Get the evaluation dataset"""
    if not harness.questions:
        harness.load_dataset()
    
    return {
        "questions": [
            {
                "question_id": q.question_id,
                "question": q.question,
                "domain": q.domain,
                "difficulty": q.difficulty,
                "relevant_doc_count": len(q.relevant_doc_ids)
            }
            for q in harness.questions
        ],
        "total": len(harness.questions)
    }

@router.post("/evaluate")
async def run_evaluation(request: EvaluationRequest):
    """Run RAG evaluation with mock retrieval function"""
    from ..rag.evaluation_harness import mock_retrieval_function
    
    if not harness.questions:
        harness.load_dataset()
    
    metrics = await harness.evaluate_retrieval(
        mock_retrieval_function,
        k_values=request.k_values
    )
    
    report_dir = Path("reports")
    harness.save_report(metrics, report_dir / "rag_evaluation_latest.json")
    
    return {
        "metrics": {
            "precision_at_1": metrics.precision_at_1,
            "precision_at_5": metrics.precision_at_5,
            "precision_at_10": metrics.precision_at_10,
            "mean_reciprocal_rank": metrics.mean_reciprocal_rank,
            "average_latency_ms": metrics.average_latency_ms,
            "total_questions": metrics.total_questions
        },
        "by_domain": metrics.by_domain,
        "by_difficulty": metrics.by_difficulty,
        "target_met": metrics.precision_at_5 >= 0.85,
        "target_precision_at_5": 0.85
    }

@router.get("/metrics")
async def get_latest_metrics():
    """Get latest RAG evaluation metrics"""
    report_path = Path("reports/rag_evaluation_latest.json")
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="No evaluation results found. Run /evaluate first.")
    
    import json
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    return report

@router.get("/history")
async def get_evaluation_history():
    """Get historical RAG evaluation results"""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        return {"history": [], "total": 0}
    
    report_files = list(reports_dir.glob("rag_evaluation*.json"))
    
    history = []
    for report_file in sorted(report_files, key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
        try:
            import json
            with open(report_file, 'r') as f:
                report = json.load(f)
                history.append({
                    "timestamp": report.get("timestamp"),
                    "precision_at_5": report.get("metrics", {}).get("precision_at_5"),
                    "target_met": report.get("target_met"),
                    "file": report_file.name
                })
        except Exception:
            pass
    
    return {
        "history": history,
        "total": len(history)
    }
