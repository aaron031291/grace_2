"""
Synthetic Q&A Harness - Phase 2
Benchmark retrieval quality with Precision@5/10
"""
import asyncio
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path

class SyntheticQAHarness:
    """Production Q&A evaluation harness"""
    
    def __init__(self):
        self.benchmark_dataset = []
        self.evaluation_results = []
        self.metrics = {
            "precision_at_5": 0.0,
            "precision_at_10": 0.0,
            "recall_at_5": 0.0,
            "recall_at_10": 0.0,
            "mrr": 0.0,  # Mean Reciprocal Rank
            "ndcg_at_10": 0.0  # Normalized Discounted Cumulative Gain
        }
    
    async def load_benchmark_dataset(self, dataset_path: str = "config/qa_benchmark.json"):
        """Load synthetic Q&A benchmark dataset"""
        dataset_file = Path(dataset_path)
        
        if dataset_file.exists():
            with open(dataset_file, 'r') as f:
                self.benchmark_dataset = json.load(f)
        else:
            # Generate synthetic dataset
            self.benchmark_dataset = await self._generate_synthetic_dataset()
            
            # Save for consistency
            dataset_file.parent.mkdir(parents=True, exist_ok=True)
            with open(dataset_file, 'w') as f:
                json.dump(self.benchmark_dataset, f, indent=2)
        
        print(f"📊 Loaded {len(self.benchmark_dataset)} Q&A pairs for evaluation")
    
    async def _generate_synthetic_dataset(self) -> List[Dict[str, Any]]:
        """Generate synthetic Q&A pairs for testing"""
        synthetic_pairs = [
            {
                "question": "How do I restart a failed service?",
                "expected_answers": [
                    "Use the service restart playbook",
                    "Check service status first",
                    "Verify dependencies before restart"
                ],
                "domain": "self_healing",
                "difficulty": "easy"
            },
            {
                "question": "What is the MTTR target for critical incidents?",
                "expected_answers": [
                    "5 minutes for critical incidents",
                    "MTTR target is 300 seconds",
                    "Critical incidents should resolve within 5 minutes"
                ],
                "domain": "observability",
                "difficulty": "medium"
            },
            {
                "question": "How does the Guardian integrity sweep work?",
                "expected_answers": [
                    "Runs checks on all 31 playbooks",
                    "Validates playbook syntax and dependencies",
                    "Reports pass/fail status for each playbook"
                ],
                "domain": "guardian",
                "difficulty": "hard"
            }
            # Add more synthetic pairs...
        ]
        
        # Generate variations
        expanded_pairs = []
        for pair in synthetic_pairs:
            expanded_pairs.append(pair)
            
            # Generate question variations
            variations = await self._generate_question_variations(pair["question"])
            for variation in variations:
                expanded_pairs.append({
                    **pair,
                    "question": variation,
                    "is_variation": True
                })
        
        return expanded_pairs
    
    async def _generate_question_variations(self, question: str) -> List[str]:
        """Generate question variations for robustness testing"""
        # Simple variations - in production, use LLM
        variations = []
        
        if "How do I" in question:
            variations.append(question.replace("How do I", "What's the process to"))
            variations.append(question.replace("How do I", "Can you explain how to"))
        
        if "What is" in question:
            variations.append(question.replace("What is", "What's"))
            variations.append(question.replace("What is", "Can you tell me"))
        
        return variations[:2]  # Limit variations
    
    async def run_evaluation(self, retrieval_function) -> Dict[str, Any]:
        """Run full evaluation against benchmark dataset"""
        if not self.benchmark_dataset:
            await self.load_benchmark_dataset()
        
        evaluation_results = []
        
        for qa_pair in self.benchmark_dataset:
            question = qa_pair["question"]
            expected_answers = qa_pair["expected_answers"]
            
            # Get retrieval results
            retrieved_docs = await retrieval_function(question, top_k=10)
            
            # Evaluate precision and recall
            precision_5 = await self._calculate_precision(retrieved_docs[:5], expected_answers)
            precision_10 = await self._calculate_precision(retrieved_docs[:10], expected_answers)
            
            recall_5 = await self._calculate_recall(retrieved_docs[:5], expected_answers)
            recall_10 = await self._calculate_recall(retrieved_docs[:10], expected_answers)
            
            # Calculate MRR
            mrr = await self._calculate_mrr(retrieved_docs, expected_answers)
            
            result = {
                "question": question,
                "domain": qa_pair["domain"],
                "difficulty": qa_pair["difficulty"],
                "precision_at_5": precision_5,
                "precision_at_10": precision_10,
                "recall_at_5": recall_5,
                "recall_at_10": recall_10,
                "mrr": mrr,
                "retrieved_count": len(retrieved_docs)
            }
            
            evaluation_results.append(result)
        
        # Calculate aggregate metrics
        self.metrics = await self._calculate_aggregate_metrics(evaluation_results)
        
        return {
            "aggregate_metrics": self.metrics,
            "detailed_results": evaluation_results,
            "evaluation_timestamp": datetime.now().isoformat(),
            "dataset_size": len(self.benchmark_dataset)
        }
    
    async def _calculate_precision(self, retrieved_docs: List[Dict], expected_answers: List[str]) -> float:
        """Calculate precision at K"""
        if not retrieved_docs:
            return 0.0
        
        relevant_count = 0
        for doc in retrieved_docs:
            doc_text = doc.get("text", "").lower()
            
            # Check if any expected answer is in the document
            for expected in expected_answers:
                if expected.lower() in doc_text:
                    relevant_count += 1
                    break
        
        return relevant_count / len(retrieved_docs)
    
    async def _calculate_recall(self, retrieved_docs: List[Dict], expected_answers: List[str]) -> float:
        """Calculate recall at K"""
        if not expected_answers:
            return 0.0
        
        found_answers = 0
        for expected in expected_answers:
            for doc in retrieved_docs:
                doc_text = doc.get("text", "").lower()
                if expected.lower() in doc_text:
                    found_answers += 1
                    break
        
        return found_answers / len(expected_answers)
    
    async def _calculate_mrr(self, retrieved_docs: List[Dict], expected_answers: List[str]) -> float:
        """Calculate Mean Reciprocal Rank"""
        for i, doc in enumerate(retrieved_docs):
            doc_text = doc.get("text", "").lower()
            
            for expected in expected_answers:
                if expected.lower() in doc_text:
                    return 1.0 / (i + 1)
        
        return 0.0
    
    async def _calculate_aggregate_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate aggregate metrics across all evaluations"""
        if not results:
            return self.metrics
        
        return {
            "precision_at_5": sum(r["precision_at_5"] for r in results) / len(results),
            "precision_at_10": sum(r["precision_at_10"] for r in results) / len(results),
            "recall_at_5": sum(r["recall_at_5"] for r in results) / len(results),
            "recall_at_10": sum(r["recall_at_10"] for r in results) / len(results),
            "mrr": sum(r["mrr"] for r in results) / len(results),
            "ndcg_at_10": 0.0  # Placeholder for NDCG calculation
        }

qa_harness = SyntheticQAHarness()
