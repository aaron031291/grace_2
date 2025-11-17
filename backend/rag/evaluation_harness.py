"""
RAG Evaluation Harness
Measures retrieval quality with Precision@K metrics
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
import asyncio

@dataclass
class EvaluationQuestion:
    """A question with ground truth answer and relevant doc IDs"""
    question_id: str
    question: str
    ground_truth_answer: str
    relevant_doc_ids: List[str]
    domain: str
    difficulty: str  # 'easy', 'medium', 'hard'

@dataclass
class RetrievalResult:
    """Result of a retrieval attempt"""
    question_id: str
    retrieved_doc_ids: List[str]
    scores: List[float]
    latency_ms: float

@dataclass
class EvaluationMetrics:
    """Evaluation metrics for RAG system"""
    precision_at_1: float
    precision_at_5: float
    precision_at_10: float
    mean_reciprocal_rank: float
    average_latency_ms: float
    total_questions: int
    by_domain: Dict[str, Dict[str, float]]
    by_difficulty: Dict[str, Dict[str, float]]

class RAGEvaluationHarness:
    """Evaluation harness for RAG retrieval quality"""
    
    def __init__(self, dataset_path: Optional[Path] = None):
        self.dataset_path = dataset_path or Path("data/rag_eval_dataset.json")
        self.questions: List[EvaluationQuestion] = []
        self.results: List[Tuple[EvaluationQuestion, RetrievalResult]] = []
        
    def load_dataset(self) -> int:
        """Load evaluation dataset from JSON"""
        if not self.dataset_path.exists():
            print(f"[WARN] Evaluation dataset not found: {self.dataset_path}")
            print("[INFO] Generating synthetic dataset...")
            self._generate_synthetic_dataset()
            return len(self.questions)
        
        with open(self.dataset_path, 'r') as f:
            data = json.load(f)
        
        self.questions = [
            EvaluationQuestion(**q) for q in data.get('questions', [])
        ]
        
        print(f"[OK] Loaded {len(self.questions)} evaluation questions")
        return len(self.questions)
    
    def _generate_synthetic_dataset(self):
        """Generate synthetic evaluation dataset"""
        synthetic_questions = [
            {
                "question_id": "q001",
                "question": "How does Grace handle self-healing?",
                "ground_truth_answer": "Grace uses Guardian playbooks to detect and remediate issues automatically",
                "relevant_doc_ids": ["doc_guardian", "doc_self_heal", "doc_playbooks"],
                "domain": "core",
                "difficulty": "medium"
            },
            {
                "question_id": "q002",
                "question": "What is the governance approval process?",
                "ground_truth_answer": "Tier 2/3 actions require whitelist approval before execution",
                "relevant_doc_ids": ["doc_governance", "doc_whitelist", "doc_constitutional"],
                "domain": "governance",
                "difficulty": "easy"
            },
            {
                "question_id": "q003",
                "question": "How does RAG ingestion work?",
                "ground_truth_answer": "Content is chunked, embedded, and stored with provenance tracking",
                "relevant_doc_ids": ["doc_rag", "doc_ingestion", "doc_embeddings"],
                "domain": "knowledge",
                "difficulty": "medium"
            },
            {
                "question_id": "q004",
                "question": "What metrics does Grace track?",
                "ground_truth_answer": "Grace tracks health, trust, confidence across 10 domains",
                "relevant_doc_ids": ["doc_metrics", "doc_cognition", "doc_domains"],
                "domain": "cognition",
                "difficulty": "easy"
            },
            {
                "question_id": "q005",
                "question": "How does autonomous learning work?",
                "ground_truth_answer": "Grace detects knowledge gaps and learns from whitelisted sources with approval gates",
                "relevant_doc_ids": ["doc_learning", "doc_whitelist", "doc_autonomy"],
                "domain": "transcendence",
                "difficulty": "hard"
            }
        ]
        
        self.questions = [EvaluationQuestion(**q) for q in synthetic_questions]
        
        # Save to file
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.dataset_path, 'w') as f:
            json.dump({"questions": synthetic_questions}, f, indent=2)
        
        print(f"[OK] Generated {len(self.questions)} synthetic questions")
    
    async def evaluate_retrieval(
        self,
        retrieval_fn: callable,
        k_values: List[int] = [1, 5, 10]
    ) -> EvaluationMetrics:
        """
        Evaluate retrieval function
        
        Args:
            retrieval_fn: async function that takes (question: str, k: int) -> List[str] doc_ids
            k_values: List of k values to test (default [1, 5, 10])
        
        Returns:
            EvaluationMetrics with precision@k and other metrics
        """
        if not self.questions:
            self.load_dataset()
        
        print(f"\n[EVAL] Evaluating retrieval on {len(self.questions)} questions...")
        print(f"[EVAL] K values: {k_values}")
        
        results = []
        
        for question in self.questions:
            start_time = asyncio.get_event_loop().time()
            
            # Retrieve with max k
            max_k = max(k_values)
            retrieved_docs = await retrieval_fn(question.question, max_k)
            
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            result = RetrievalResult(
                question_id=question.question_id,
                retrieved_doc_ids=retrieved_docs,
                scores=[1.0] * len(retrieved_docs),  # Placeholder scores
                latency_ms=latency_ms
            )
            
            results.append((question, result))
        
        self.results = results
        
        # Calculate metrics
        return self._calculate_metrics(k_values)
    
    def _calculate_metrics(self, k_values: List[int]) -> EvaluationMetrics:
        """Calculate evaluation metrics"""
        precision_at_k = {}
        
        for k in k_values:
            precisions = []
            
            for question, result in self.results:
                retrieved_k = result.retrieved_doc_ids[:k]
                relevant = question.relevant_doc_ids
                
                # Count how many retrieved docs are relevant
                relevant_retrieved = sum(1 for doc in retrieved_k if doc in relevant)
                precision = relevant_retrieved / k if k > 0 else 0
                precisions.append(precision)
            
            precision_at_k[k] = sum(precisions) / len(precisions) if precisions else 0
        
        # Calculate MRR (Mean Reciprocal Rank)
        reciprocal_ranks = []
        for question, result in self.results:
            relevant = question.relevant_doc_ids
            
            # Find rank of first relevant document
            for i, doc_id in enumerate(result.retrieved_doc_ids):
                if doc_id in relevant:
                    reciprocal_ranks.append(1.0 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0.0)
        
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
        
        # Average latency
        avg_latency = sum(r.latency_ms for _, r in self.results) / len(self.results) if self.results else 0
        
        # By domain
        by_domain = self._calculate_by_category('domain')
        
        # By difficulty
        by_difficulty = self._calculate_by_category('difficulty')
        
        metrics = EvaluationMetrics(
            precision_at_1=precision_at_k.get(1, 0),
            precision_at_5=precision_at_k.get(5, 0),
            precision_at_10=precision_at_k.get(10, 0),
            mean_reciprocal_rank=mrr,
            average_latency_ms=avg_latency,
            total_questions=len(self.results),
            by_domain=by_domain,
            by_difficulty=by_difficulty
        )
        
        return metrics
    
    def _calculate_by_category(self, category: str) -> Dict[str, Dict[str, float]]:
        """Calculate metrics broken down by category"""
        category_results = {}
        
        for question, result in self.results:
            cat_value = getattr(question, category)
            
            if cat_value not in category_results:
                category_results[cat_value] = []
            
            category_results[cat_value].append((question, result))
        
        metrics_by_category = {}
        
        for cat_value, cat_results in category_results.items():
            # Calculate precision@5 for this category
            precisions = []
            for question, result in cat_results:
                retrieved_5 = result.retrieved_doc_ids[:5]
                relevant = question.relevant_doc_ids
                relevant_retrieved = sum(1 for doc in retrieved_5 if doc in relevant)
                precision = relevant_retrieved / 5 if 5 > 0 else 0
                precisions.append(precision)
            
            metrics_by_category[cat_value] = {
                "precision_at_5": sum(precisions) / len(precisions) if precisions else 0,
                "count": len(cat_results)
            }
        
        return metrics_by_category
    
    def print_report(self, metrics: EvaluationMetrics):
        """Print evaluation report"""
        print("\n" + "=" * 80)
        print("RAG EVALUATION REPORT")
        print("=" * 80)
        print(f"Total Questions: {metrics.total_questions}")
        print(f"\nRetrieval Quality:")
        print(f"  Precision@1:  {metrics.precision_at_1:.3f}")
        print(f"  Precision@5:  {metrics.precision_at_5:.3f} {'[PASS]' if metrics.precision_at_5 >= 0.85 else '[FAIL]'}")
        print(f"  Precision@10: {metrics.precision_at_10:.3f}")
        print(f"  MRR:          {metrics.mean_reciprocal_rank:.3f}")
        print(f"\nLatency:")
        print(f"  Average: {metrics.average_latency_ms:.1f}ms")
        print(f"\nBy Domain:")
        for domain, stats in metrics.by_domain.items():
            print(f"  {domain}: P@5={stats['precision_at_5']:.3f} (n={stats['count']})")
        print("=" * 80)
    
    def save_report(self, metrics: EvaluationMetrics, output_path: Path):
        """Save evaluation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": asdict(metrics),
            "questions_evaluated": len(self.results),
            "target_precision_at_5": 0.85,
            "target_met": metrics.precision_at_5 >= 0.85
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved: {output_path}")

async def mock_retrieval_function(question: str, k: int) -> List[str]:
    """Mock retrieval function for testing"""
    await asyncio.sleep(0.01)  # Simulate latency
    
    # Return mock doc IDs based on keywords
    if "self-healing" in question.lower() or "guardian" in question.lower():
        return ["doc_guardian", "doc_self_heal", "doc_playbooks", "doc_other1", "doc_other2"][:k]
    elif "governance" in question.lower() or "approval" in question.lower():
        return ["doc_governance", "doc_whitelist", "doc_constitutional", "doc_other3", "doc_other4"][:k]
    elif "rag" in question.lower() or "ingestion" in question.lower():
        return ["doc_rag", "doc_ingestion", "doc_embeddings", "doc_other5", "doc_other6"][:k]
    elif "metrics" in question.lower():
        return ["doc_metrics", "doc_cognition", "doc_domains", "doc_other7", "doc_other8"][:k]
    elif "learning" in question.lower():
        return ["doc_learning", "doc_whitelist", "doc_autonomy", "doc_other9", "doc_other10"][:k]
    else:
        return [f"doc_{i}" for i in range(k)]

if __name__ == "__main__":
    import sys
    
    async def main():
        harness = RAGEvaluationHarness()
        harness.load_dataset()
        
        metrics = await harness.evaluate_retrieval(mock_retrieval_function)
        harness.print_report(metrics)
        
        report_dir = Path(__file__).parent.parent.parent / "reports"
        harness.save_report(metrics, report_dir / "rag_evaluation.json")
        
        return 0 if metrics.precision_at_5 >= 0.85 else 1
    
    sys.exit(asyncio.run(main()))
