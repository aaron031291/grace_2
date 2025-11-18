"""
Q/A Evaluation Harness - Precision@5/@10 with CI Integration
"""
import asyncio
import json
import time
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path
import logging
import statistics

from backend.logging.immutable_log import immutable_log
from backend.config.environment import GraceEnvironment

logger = logging.getLogger(__name__)

class QAEvaluationHarness:
    """Production Q/A evaluation harness with CI integration"""
    
    def __init__(self):
        self.benchmark_dataset = []
        self.evaluation_results = []
        self.baseline_metrics = {}
        self.failure_cases = []
        self.latency_metrics = {
            "p50": 0.0,
            "p95": 0.0, 
            "p99": 0.0,
            "avg": 0.0
        }
        self.cache_metrics = {
            "hits": 0,
            "misses": 0,
            "hit_rate": 0.0
        }
    
    async def load_benchmark_dataset(self, filepath: str = "config/qa_benchmark.json"):
        """Load Q/A benchmark dataset"""
        if not Path(filepath).exists():
            print(f"⚠️ Benchmark file not found: {filepath}")
            print("🔄 Generating new benchmark...")
            from .synthetic_qa_benchmark import qa_benchmark_generator
            await qa_benchmark_generator.generate_benchmark_dataset(150)
            await qa_benchmark_generator.save_benchmark(filepath)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.benchmark_dataset = data["questions"]
        
        print(f"📚 Loaded {len(self.benchmark_dataset)} Q/A pairs")
        return len(self.benchmark_dataset)
    
    async def run_evaluation(self, retrieval_function, top_k: int = 10, 
                           run_id: Optional[str] = None) -> Dict[str, Any]:
        """Run complete evaluation with metrics"""
        if not run_id:
            run_id = f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🧪 Running Q/A evaluation: {run_id}")
        print(f"📊 Dataset size: {len(self.benchmark_dataset)}")
        
        start_time = time.time()
        evaluation_results = []
        latencies = []
        cache_hits = 0
        cache_misses = 0
        
        for i, qa_pair in enumerate(self.benchmark_dataset):
            if i % 20 == 0:
                print(f"Progress: {i}/{len(self.benchmark_dataset)}")
            
            # Measure retrieval latency
            query_start = time.time()
            
            try:
                # Call retrieval function
                retrieved_docs = await retrieval_function(
                    qa_pair["question"], top_k=top_k
                )
                
                query_latency = time.time() - query_start
                latencies.append(query_latency)
                
                # Simulate cache hit/miss (would be real in production)
                is_cache_hit = query_latency < 0.1  # Fast queries likely cached
                if is_cache_hit:
                    cache_hits += 1
                else:
                    cache_misses += 1
                
                # Evaluate result
                result = await self._evaluate_retrieval(
                    qa_pair, retrieved_docs, top_k, query_latency
                )
                evaluation_results.append(result)
                
                # Track failure cases
                if result["precision_at_5"] < 0.2:  # Low precision threshold
                    self.failure_cases.append({
                        "qa_id": qa_pair.get("qa_id", f"qa_{i}"),
                        "question": qa_pair["question"],
                        "expected_answer": qa_pair["expected_answer"],
                        "retrieved_docs": retrieved_docs[:5],
                        "precision_at_5": result["precision_at_5"],
                        "latency": query_latency,
                        "category": qa_pair.get("category", "unknown")
                    })
                
            except Exception as e:
                logger.error(f"Evaluation failed for question {i}: {e}")
                cache_misses += 1
                evaluation_results.append({
                    "qa_id": qa_pair.get("qa_id", f"qa_{i}"),
                    "precision_at_5": 0.0,
                    "precision_at_10": 0.0,
                    "recall_at_5": 0.0,
                    "recall_at_10": 0.0,
                    "latency": 0.0,
                    "error": str(e)
                })
        
        # Calculate aggregate metrics
        total_time = time.time() - start_time
        metrics = await self._calculate_aggregate_metrics(
            evaluation_results, latencies, cache_hits, cache_misses, total_time
        )
        
        # Save results
        await self._save_evaluation_results(run_id, metrics, evaluation_results)
        
        print(f"✅ Evaluation complete: {run_id}")
        print(f"📊 Precision@5: {metrics['precision_at_5']:.3f}")
        print(f"📊 Precision@10: {metrics['precision_at_10']:.3f}")
        print(f"⏱️ Avg latency: {metrics['avg_latency']:.3f}s")
        print(f"💾 Cache hit rate: {metrics['cache_hit_rate']:.3f}")
        
        return metrics
    
    async def _evaluate_retrieval(self, qa_pair: Dict, retrieved_docs: List[Dict], 
                                top_k: int, latency: float) -> Dict:
        """Evaluate single retrieval result"""
        expected_sources = qa_pair.get("expected_sources", [])
        expected_keywords = qa_pair.get("keywords", [])
        
        # Calculate precision@5 and @10
        precision_at_5 = self._calculate_precision(retrieved_docs[:5], expected_sources, expected_keywords)
        precision_at_10 = self._calculate_precision(retrieved_docs[:10], expected_sources, expected_keywords)
        
        # Calculate recall (simplified)
        recall_at_5 = min(1.0, precision_at_5 * 5 / max(1, len(expected_sources)))
        recall_at_10 = min(1.0, precision_at_10 * 10 / max(1, len(expected_sources)))
        
        return {
            "qa_id": qa_pair.get("qa_id", "unknown"),
            "precision_at_5": precision_at_5,
            "precision_at_10": precision_at_10,
            "recall_at_5": recall_at_5,
            "recall_at_10": recall_at_10,
            "latency": latency,
            "category": qa_pair.get("category", "unknown")
        }
    
    def _calculate_precision(self, retrieved_docs: List[Dict], 
                           expected_sources: List[str], expected_keywords: List[str]) -> float:
        """Calculate precision score"""
        if not retrieved_docs:
            return 0.0
        
        relevant_count = 0
        
        for doc in retrieved_docs:
            doc_text = doc.get("text", "").lower()
            doc_source = doc.get("source", "")
            
            # Check if document matches expected sources
            source_match = any(source in doc_source for source in expected_sources)
            
            # Check if document contains expected keywords
            keyword_match = any(keyword.lower() in doc_text for keyword in expected_keywords)
            
            if source_match or keyword_match:
                relevant_count += 1
        
        return relevant_count / len(retrieved_docs)
    
    async def _calculate_aggregate_metrics(self, results: List[Dict], latencies: List[float],
                                         cache_hits: int, cache_misses: int, total_time: float) -> Dict:
        """Calculate aggregate evaluation metrics"""
        if not results:
            return {}
        
        # Precision metrics
        precision_5_scores = [r.get("precision_at_5", 0.0) for r in results if "precision_at_5" in r]
        precision_10_scores = [r.get("precision_at_10", 0.0) for r in results if "precision_at_10" in r]
        
        # Latency percentiles
        if latencies:
            latencies.sort()
            p50 = statistics.median(latencies)
            p95 = latencies[int(0.95 * len(latencies))] if len(latencies) > 20 else latencies[-1]
            p99 = latencies[int(0.99 * len(latencies))] if len(latencies) > 100 else latencies[-1]
            avg_latency = statistics.mean(latencies)
        else:
            p50 = p95 = p99 = avg_latency = 0.0
        
        # Cache metrics
        total_queries = cache_hits + cache_misses
        cache_hit_rate = cache_hits / max(1, total_queries)
        
        return {
            "run_id": f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "total_questions": len(results),
            "precision_at_5": statistics.mean(precision_5_scores) if precision_5_scores else 0.0,
            "precision_at_10": statistics.mean(precision_10_scores) if precision_10_scores else 0.0,
            "latency_p50": p50,
            "latency_p95": p95,
            "latency_p99": p99,
            "avg_latency": avg_latency,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "total_evaluation_time": total_time,
            "failure_cases": len(self.failure_cases),
            "questions_per_second": len(results) / max(0.001, total_time)
        }
    
    async def _save_evaluation_results(self, run_id: str, metrics: Dict, results: List[Dict]):
        """Save evaluation results"""
        results_dir = Path("reports/qa_evaluation")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        with open(results_dir / f"{run_id}_detailed.json", 'w') as f:
            json.dump({
                "metrics": metrics,
                "individual_results": results,
                "failure_cases": self.failure_cases
            }, f, indent=2)
        
        # Save summary metrics
        with open(results_dir / f"{run_id}_summary.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Update latest results
        with open(results_dir / "latest_results.json", 'w') as f:
            json.dump(metrics, f, indent=2)
    
    async def check_regression(self, current_metrics: Dict, 
                             regression_threshold: float = 0.05) -> Dict[str, Any]:
        """Check for regressions against baseline"""
        baseline_file = Path("config/qa_baseline.json")
        
        if not baseline_file.exists():
            print("⚠️ No baseline found, setting current as baseline")
            with open(baseline_file, 'w') as f:
                json.dump(current_metrics, f, indent=2)
            return {"regression_detected": False, "is_baseline": True}
        
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)
        
        regressions = []
        
        # Check precision regressions
        for metric in ["precision_at_5", "precision_at_10"]:
            current_val = current_metrics.get(metric, 0.0)
            baseline_val = baseline.get(metric, 0.0)
            
            if baseline_val > 0:
                regression = (baseline_val - current_val) / baseline_val
                if regression > regression_threshold:
                    regressions.append({
                        "metric": metric,
                        "baseline": baseline_val,
                        "current": current_val,
                        "regression_pct": regression * 100
                    })
        
        # Check latency regressions (higher is worse)
        for metric in ["avg_latency", "latency_p95"]:
            current_val = current_metrics.get(metric, 0.0)
            baseline_val = baseline.get(metric, 0.0)
            
            if baseline_val > 0:
                regression = (current_val - baseline_val) / baseline_val
                if regression > regression_threshold:
                    regressions.append({
                        "metric": metric,
                        "baseline": baseline_val,
                        "current": current_val,
                        "regression_pct": regression * 100
                    })
        
        return {
            "regression_detected": len(regressions) > 0,
            "regressions": regressions,
            "baseline_metrics": baseline,
            "current_metrics": current_metrics
        }

# Global instance
qa_evaluation_harness = QAEvaluationHarness()