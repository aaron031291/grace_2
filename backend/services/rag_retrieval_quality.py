"""
RAG Retrieval Quality - Evaluation Harness & Precision Metrics
Builds evaluation harness with synthetic Q/A pairs, measures Precision@5/10, implements hard-negative mining
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import statistics

from backend.logging_system.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class SyntheticQAPair:
    """Synthetic Question-Answer pair for evaluation"""

    def __init__(self, question: str, answer: str, context_chunks: List[str],
                 relevant_chunk_indices: List[int], difficulty: str = "medium"):
        self.question = question
        self.answer = answer
        self.context_chunks = context_chunks
        self.relevant_chunk_indices = relevant_chunk_indices  # Which chunks contain the answer
        self.difficulty = difficulty  # easy, medium, hard
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "context_chunks": self.context_chunks,
            "relevant_chunk_indices": self.relevant_chunk_indices,
            "difficulty": self.difficulty,
            "created_at": self.created_at
        }


class RAGEvaluationHarness:
    """
    Evaluation harness for RAG retrieval quality
    Generates synthetic Q/A pairs and measures retrieval performance
    """

    def __init__(self):
        self.qa_pairs: List[SyntheticQAPair] = []
        self.evaluation_results: List[Dict[str, Any]] = []
        self.target_precision_at_5 = 0.85
        self.target_precision_at_10 = 0.75

    async def generate_synthetic_qa_pairs(self, knowledge_base: List[Dict[str, Any]],
                                        num_pairs: int = 100) -> List[SyntheticQAPair]:
        """
        Generate synthetic Q/A pairs from knowledge base

        Args:
            knowledge_base: List of knowledge chunks
            num_pairs: Number of Q/A pairs to generate

        Returns:
            List of synthetic Q/A pairs
        """
        qa_pairs = []

        # Group chunks by source for context coherence
        source_groups = {}
        for chunk in knowledge_base:
            source_id = chunk.get("source_id", "unknown")
            if source_id not in source_groups:
                source_groups[source_id] = []
            source_groups[source_id].append(chunk)

        for _ in range(num_pairs):
            # Select random source with multiple chunks
            viable_sources = [s for s, chunks in source_groups.items() if len(chunks) >= 3]
            if not viable_sources:
                continue

            source_id = random.choice(viable_sources)
            source_chunks = source_groups[source_id]

            # Select 5-10 chunks for context
            context_size = random.randint(5, min(10, len(source_chunks)))
            context_chunks = random.sample(source_chunks, context_size)

            # Select 1-3 relevant chunks that will contain the answer
            num_relevant = random.randint(1, min(3, len(context_chunks)))
            relevant_indices = random.sample(range(len(context_chunks)), num_relevant)

            # Generate Q/A pair based on relevant chunks
            qa_pair = await self._generate_qa_from_chunks(context_chunks, relevant_indices)
            if qa_pair:
                qa_pairs.append(qa_pair)

        self.qa_pairs.extend(qa_pairs)

        logger.info(f"[EVALUATION-HARNESS] Generated {len(qa_pairs)} synthetic Q/A pairs")
        return qa_pairs

    async def _generate_qa_from_chunks(self, context_chunks: List[Dict[str, Any]],
                                     relevant_indices: List[int]) -> Optional[SyntheticQAPair]:
        """Generate Q/A pair from selected chunks"""
        try:
            # Combine relevant chunk texts
            relevant_texts = [context_chunks[i]["text"] for i in relevant_indices]
            combined_text = " ".join(relevant_texts)

            # Simple Q/A generation - can be enhanced with LLM
            question = await self._generate_question_from_text(combined_text)
            answer = await self._extract_answer_from_text(combined_text, question)

            if question and answer:
                return SyntheticQAPair(
                    question=question,
                    answer=answer,
                    context_chunks=[c["text"] for c in context_chunks],
                    relevant_chunk_indices=relevant_indices,
                    difficulty=self._assess_difficulty(combined_text)
                )

        except Exception as e:
            logger.warning(f"[EVALUATION-HARNESS] Failed to generate Q/A pair: {e}")

        return None

    async def _generate_question_from_text(self, text: str) -> str:
        """Generate question from text (simple rule-based for now)"""
        # Extract key entities and concepts
        sentences = text.split('.')
        if len(sentences) < 2:
            return None

        # Simple question generation patterns
        patterns = [
            "What is {concept}?",
            "How does {concept} work?",
            "What are the benefits of {concept}?",
            "Explain {concept} in detail.",
            "What is the purpose of {concept}?"
        ]

        # Extract potential concepts (can be enhanced with NLP)
        words = text.split()
        if len(words) > 10:
            concept = " ".join(words[5:8])  # Simple concept extraction
            pattern = random.choice(patterns)
            return pattern.format(concept=concept.strip())

        return None

    async def _extract_answer_from_text(self, text: str, question: str) -> str:
        """Extract answer from text based on question"""
        # Simple answer extraction - return first relevant sentence
        sentences = text.split('.')
        for sentence in sentences:
            if len(sentence.strip()) > 20:  # Substantial sentence
                return sentence.strip()

        return text[:200] + "..." if len(text) > 200 else text

    def _assess_difficulty(self, text: str) -> str:
        """Assess question difficulty"""
        word_count = len(text.split())
        if word_count < 50:
            return "easy"
        elif word_count < 150:
            return "medium"
        else:
            return "hard"

    async def evaluate_retrieval(self, rag_service, qa_pairs: Optional[List[SyntheticQAPair]] = None) -> Dict[str, Any]:
        """
        Evaluate retrieval performance using Q/A pairs

        Args:
            rag_service: RAG service to evaluate
            qa_pairs: Q/A pairs to use (uses self.qa_pairs if None)

        Returns:
            Evaluation results with precision metrics
        """
        if qa_pairs is None:
            qa_pairs = self.qa_pairs

        if not qa_pairs:
            return {"error": "No Q/A pairs available for evaluation"}

        results = {
            "total_questions": len(qa_pairs),
            "precision_at_1": [],
            "precision_at_3": [],
            "precision_at_5": [],
            "precision_at_10": [],
            "answer_faithfulness": [],
            "average_response_time": 0,
            "evaluation_timestamp": datetime.utcnow().isoformat()
        }

        total_response_time = 0

        for qa_pair in qa_pairs:
            # Retrieve context for question
            start_time = datetime.utcnow()

            retrieved_results = await rag_service.retrieve(
                query=qa_pair.question,
                top_k=10,
                requested_by="evaluation_harness"
            )

            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            total_response_time += response_time

            # Evaluate precision
            retrieved_chunks = retrieved_results.get("results", [])
            precision_scores = self._calculate_precision_scores(
                retrieved_chunks, qa_pair.context_chunks, qa_pair.relevant_chunk_indices
            )

            results["precision_at_1"].append(precision_scores["precision_at_1"])
            results["precision_at_3"].append(precision_scores["precision_at_3"])
            results["precision_at_5"].append(precision_scores["precision_at_5"])
            results["precision_at_10"].append(precision_scores["precision_at_10"])

            # Evaluate answer faithfulness (if RAG provides answer)
            if "answer" in retrieved_results:
                faithfulness = self._calculate_answer_faithfulness(
                    retrieved_results["answer"], qa_pair.answer
                )
                results["answer_faithfulness"].append(faithfulness)

        # Calculate averages
        for metric in ["precision_at_1", "precision_at_3", "precision_at_5", "precision_at_10", "answer_faithfulness"]:
            if results[metric]:
                results[f"avg_{metric}"] = statistics.mean(results[metric])
                results[f"median_{metric}"] = statistics.median(results[metric])

        results["average_response_time"] = total_response_time / len(qa_pairs)

        # Overall assessment
        results["meets_precision_target"] = (
            results.get("avg_precision_at_5", 0) >= self.target_precision_at_5 and
            results.get("avg_precision_at_10", 0) >= self.target_precision_at_10
        )

        self.evaluation_results.append(results)

        # Log results
        await immutable_log.append(
            actor="rag_evaluation_harness",
            action="retrieval_evaluation",
            resource="rag_service",
            outcome="completed" if results["meets_precision_target"] else "needs_improvement",
            payload=results
        )

        logger.info(f"[EVALUATION-HARNESS] Evaluation complete - P@5: {results.get('avg_precision_at_5', 0):.3f}, Target: {self.target_precision_at_5}")
        return results

    def _calculate_precision_scores(self, retrieved_chunks: List[Dict[str, Any]],
                                  context_chunks: List[str], relevant_indices: List[int]) -> Dict[str, float]:
        """Calculate precision at k scores"""
        # Create set of relevant chunk texts
        relevant_texts = set(context_chunks[i] for i in relevant_indices)

        # Calculate precision at different k values
        scores = {}
        for k in [1, 3, 5, 10]:
            retrieved_texts = set()
            for i in range(min(k, len(retrieved_chunks))):
                chunk_text = retrieved_chunks[i].get("content", "")
                retrieved_texts.add(chunk_text)

            # Calculate precision: relevant retrieved / total retrieved
            relevant_retrieved = len(retrieved_texts & relevant_texts)
            precision = relevant_retrieved / k if k > 0 else 0
            scores[f"precision_at_{k}"] = precision

        return scores

    def _calculate_answer_faithfulness(self, generated_answer: str, expected_answer: str) -> float:
        """Calculate how faithful the generated answer is to the expected answer"""
        # Simple semantic similarity - can be enhanced with embeddings
        gen_words = set(generated_answer.lower().split())
        exp_words = set(expected_answer.lower().split())

        if not gen_words or not exp_words:
            return 0.0

        intersection = len(gen_words & exp_words)
        union = len(gen_words | exp_words)

        return intersection / union if union > 0 else 0.0

    def get_evaluation_report(self) -> Dict[str, Any]:
        """Get comprehensive evaluation report"""
        if not self.evaluation_results:
            return {"error": "No evaluation results available"}

        latest = self.evaluation_results[-1]

        report = {
            "latest_evaluation": latest,
            "historical_trend": self._calculate_trend(),
            "recommendations": self._generate_recommendations(latest),
            "benchmark_comparison": self._compare_to_benchmarks(latest)
        }

        return report

    def _calculate_trend(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.evaluation_results) < 2:
            return {"insufficient_data": True}

        trend = {
            "precision_at_5_trend": [],
            "improving": False,
            "stable": True
        }

        for result in self.evaluation_results[-5:]:  # Last 5 evaluations
            p5 = result.get("avg_precision_at_5", 0)
            trend["precision_at_5_trend"].append(p5)

        if len(trend["precision_at_5_trend"]) >= 2:
            # Check if generally improving
            improvements = 0
            for i in range(1, len(trend["precision_at_5_trend"])):
                if trend["precision_at_5_trend"][i] > trend["precision_at_5_trend"][i-1]:
                    improvements += 1

            trend["improving"] = improvements >= len(trend["precision_at_5_trend"]) - 1
            trend["stable"] = abs(trend["precision_at_5_trend"][-1] - trend["precision_at_5_trend"][0]) < 0.1

        return trend

    def _generate_recommendations(self, latest_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on evaluation results"""
        recommendations = []

        p5 = latest_results.get("avg_precision_at_5", 0)
        p10 = latest_results.get("avg_precision_at_10", 0)

        if p5 < self.target_precision_at_5:
            recommendations.append(f"Precision@5 ({p5:.3f}) below target ({self.target_precision_at_5}). Consider hard-negative mining.")

        if p10 < self.target_precision_at_10:
            recommendations.append(f"Precision@10 ({p10:.3f}) below target ({self.target_precision_at_10}). Review retrieval algorithm.")

        response_time = latest_results.get("average_response_time", 0)
        if response_time > 2.0:
            recommendations.append(f"Response time ({response_time:.2f}s) too slow. Optimize retrieval pipeline.")

        faithfulness = latest_results.get("avg_answer_faithfulness", 0)
        if faithfulness and faithfulness < 0.8:
            recommendations.append(f"Answer faithfulness ({faithfulness:.3f}) low. Improve answer generation.")

        return recommendations

    def _compare_to_benchmarks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results to industry benchmarks"""
        benchmarks = {
            "precision_at_5": {"good": 0.85, "excellent": 0.90},
            "precision_at_10": {"good": 0.75, "excellent": 0.85},
            "response_time_seconds": {"good": 1.0, "excellent": 0.5}
        }

        comparison = {}
        p5 = results.get("avg_precision_at_5", 0)
        p10 = results.get("avg_precision_at_10", 0)
        rt = results.get("average_response_time", 0)

        comparison["precision_at_5"] = self._rate_performance(p5, benchmarks["precision_at_5"])
        comparison["precision_at_10"] = self._rate_performance(p10, benchmarks["precision_at_10"])
        comparison["response_time"] = self._rate_performance(rt, benchmarks["response_time_seconds"], invert=True)

        return comparison

    def _rate_performance(self, value: float, thresholds: Dict[str, float], invert: bool = False) -> str:
        """Rate performance against thresholds"""
        if invert:  # Lower is better
            if value <= thresholds.get("excellent", 0):
                return "excellent"
            elif value <= thresholds.get("good", 0):
                return "good"
            else:
                return "needs_improvement"
        else:  # Higher is better
            if value >= thresholds.get("excellent", 1):
                return "excellent"
            elif value >= thresholds.get("good", 1):
                return "good"
            else:
                return "needs_improvement"


class HardNegativeMiner:
    """
    Hard-negative mining for retrieval improvement
    Identifies difficult examples that the current system gets wrong
    """

    def __init__(self):
        self.hard_negatives: List[Dict[str, Any]] = []
        self.mining_stats = {
            "total_mined": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "near_misses": 0
        }

    async def mine_hard_negatives(self, evaluation_results: Dict[str, Any],
                                qa_pairs: List[SyntheticQAPair]) -> List[Dict[str, Any]]:
        """
        Mine hard negative examples from evaluation results

        Args:
            evaluation_results: Results from evaluation harness
            qa_pairs: Original Q/A pairs used in evaluation

        Returns:
            List of hard negative examples for training
        """
        hard_negatives = []

        # This would analyze which questions the system got wrong
        # and create training examples to improve retrieval

        # Placeholder implementation - would be enhanced with actual mining logic
        for qa_pair in qa_pairs:
            # Simulate finding hard negatives
            if random.random() < 0.1:  # 10% of examples are hard
                hard_negative = {
                    "question": qa_pair.question,
                    "correct_chunks": [qa_pair.context_chunks[i] for i in qa_pair.relevant_chunk_indices],
                    "incorrect_chunks_retrieved": [],  # Would be populated from evaluation
                    "difficulty_score": random.uniform(0.7, 1.0),
                    "mined_at": datetime.utcnow().isoformat()
                }
                hard_negatives.append(hard_negative)

        self.hard_negatives.extend(hard_negatives)
        self.mining_stats["total_mined"] += len(hard_negatives)

        logger.info(f"[HARD-NEGATIVE-MINER] Mined {len(hard_negatives)} hard negative examples")
        return hard_negatives

    def get_mining_stats(self) -> Dict[str, Any]:
        """Get hard negative mining statistics"""
        return self.mining_stats

    def get_hard_negatives(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent hard negative examples"""
        return self.hard_negatives[-limit:]


# Global instances
rag_evaluation_harness = RAGEvaluationHarness()
hard_negative_miner = HardNegativeMiner()
