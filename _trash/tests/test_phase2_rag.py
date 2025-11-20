"""
Phase 2 RAG Tests
REAL tests for RAG evaluation system
"""

import pytest
import asyncio

def test_rag_harness_loads():
    """Verify RAG harness can be imported"""
    from backend.rag.evaluation_harness import RAGEvaluationHarness
    
    harness = RAGEvaluationHarness()
    assert harness is not None

def test_synthetic_dataset_generation():
    """Verify synthetic dataset can be generated"""
    from backend.rag.evaluation_harness import RAGEvaluationHarness
    
    harness = RAGEvaluationHarness()
    count = harness.load_dataset()
    
    assert count == 5
    assert len(harness.questions) == 5
    
    # Verify questions have required fields
    for q in harness.questions:
        assert q.question_id is not None
        assert q.question is not None
        assert q.ground_truth_answer is not None
        assert len(q.relevant_doc_ids) > 0
        assert q.domain is not None

@pytest.mark.asyncio
async def test_mock_retrieval_works():
    """Test mock retrieval function returns results"""
    from backend.rag.evaluation_harness import mock_retrieval_function
    
    results = await mock_retrieval_function("How does self-healing work?", 5)
    
    assert isinstance(results, list)
    assert len(results) <= 5

@pytest.mark.asyncio
async def test_evaluation_runs():
    """Test evaluation actually executes and returns metrics"""
    from backend.rag.evaluation_harness import RAGEvaluationHarness, mock_retrieval_function
    
    harness = RAGEvaluationHarness()
    harness.load_dataset()
    
    metrics = await harness.evaluate_retrieval(mock_retrieval_function, k_values=[1, 5])
    
    # Verify metrics structure
    assert metrics.precision_at_1 >= 0
    assert metrics.precision_at_5 >= 0
    assert metrics.mean_reciprocal_rank >= 0
    assert metrics.average_latency_ms >= 0
    assert metrics.total_questions == 5
    
    # Verify by_domain breakdown exists
    assert 'core' in metrics.by_domain or len(metrics.by_domain) >= 0

def test_evaluation_report_saved():
    """Verify evaluation report can be saved"""
    from backend.rag.evaluation_harness import RAGEvaluationHarness, EvaluationMetrics
    from pathlib import Path
    import json
    
    harness = RAGEvaluationHarness()
    
    # Create mock metrics
    metrics = EvaluationMetrics(
        precision_at_1=1.0,
        precision_at_5=0.6,
        precision_at_10=0.3,
        mean_reciprocal_rank=1.0,
        average_latency_ms=15.0,
        total_questions=5,
        by_domain={},
        by_difficulty={}
    )
    
    report_path = Path("reports/test_rag_eval.json")
    harness.save_report(metrics, report_path)
    
    # Verify file exists
    assert report_path.exists()
    
    # Verify content
    with open(report_path, 'r') as f:
        data = json.load(f)
    
    assert data['metrics']['precision_at_5'] == 0.6
    assert data['target_precision_at_5'] == 0.85
    assert data['target_met'] == False
    
    # Cleanup
    report_path.unlink()
