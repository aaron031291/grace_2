"""
RAG Retrieval Quality Harness - PRODUCTION
Benchmark dataset (≥100 Q/A pairs), evaluation runner, nightly CI job
"""

import asyncio
import logging
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import statistics

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class BenchmarkDataset:
    """
    PRODUCTION: Benchmark dataset with ≥100 Q/A pairs and ground-truth citations
    """

    def __init__(self, dataset_path: str = "./config/benchmark_dataset.json"):
        self.dataset_path = Path(dataset_path)
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)

        self.qa_pairs: List[Dict[str, Any]] = []
        self.ground_truth: Dict[str, List[Dict[str, Any]]] = {}

        # Load or generate dataset
        self._load_or_generate_dataset()

    def _load_or_generate_dataset(self):
        """Load existing dataset or generate new one"""
        if self.dataset_path.exists():
            try:
                with open(self.dataset_path, 'r') as f:
                    data = json.load(f)
                    self.qa_pairs = data.get("qa_pairs", [])
                    self.ground_truth = data.get("ground_truth", {})
                    logger.info(f"✓ Loaded benchmark dataset: {len(self.qa_pairs)} Q/A pairs")
            except Exception as e:
                logger.error(f"Failed to load benchmark dataset: {e}")
                self._generate_synthetic_dataset()
        else:
            self._generate_synthetic_dataset()

    def _generate_synthetic_dataset(self):
        """Generate synthetic benchmark dataset with ≥100 Q/A pairs"""
        logger.info("📚 Generating synthetic benchmark dataset...")

        # Knowledge base topics
        topics = {
            "python": [
                "Python is a high-level programming language created by Guido van Rossum in 1991.",
                "Python uses indentation for code blocks instead of curly braces.",
                "Python has built-in data structures like lists, dictionaries, and tuples.",
                "Python supports object-oriented, imperative, and functional programming paradigms.",
                "The Python standard library includes modules for file I/O, networking, and data processing."
            ],
            "machine_learning": [
                "Machine learning algorithms learn patterns from data without being explicitly programmed.",
                "Supervised learning uses labeled training data to make predictions.",
                "Unsupervised learning finds hidden patterns in data without labels.",
                "Neural networks are inspired by biological neural systems in the brain.",
                "Deep learning uses multiple layers of neural networks for complex pattern recognition."
            ],
            "databases": [
                "Relational databases store data in tables with rows and columns.",
                "SQL is the standard language for querying relational databases.",
                "NoSQL databases are designed for large-scale data storage and retrieval.",
                "ACID properties ensure database transactions are reliable.",
                "Database normalization reduces data redundancy and improves integrity."
            ],
            "web_development": [
                "HTTP is the protocol used for communication between web browsers and servers.",
                "HTML defines the structure and content of web pages.",
                "CSS controls the presentation and styling of web pages.",
                "JavaScript adds interactivity and dynamic behavior to web pages.",
                "REST APIs provide programmatic access to web services."
            ],
            "security": [
                "Encryption converts data into a coded format to prevent unauthorized access.",
                "Authentication verifies the identity of users or systems.",
                "Authorization determines what actions authenticated users can perform.",
                "Firewalls monitor and control network traffic based on security rules.",
                "Multi-factor authentication requires multiple forms of verification."
            ]
        }

        # Generate Q/A pairs for each topic
        qa_pairs = []
        ground_truth = {}

        for topic, facts in topics.items():
            # Generate questions for each fact
            for i, fact in enumerate(facts):
                # Create multiple question types
                questions = [
                    f"What is {fact.split()[0].lower()}?",  # Simple what question
                    f"Can you explain {fact.split()[:3] if len(fact.split()) >= 3 else fact.split()}?",  # Explain question
                    f"How does {fact.split()[:2] if len(fact.split()) >= 2 else fact.split()} work?",  # How question
                    f"Why is {fact.split()[:2] if len(fact.split()) >= 2 else fact.split()} important?",  # Why question
                ]

                for j, question in enumerate(questions):
                    qa_id = f"{topic}_{i}_{j}"

                    qa_pair = {
                        "id": qa_id,
                        "question": question,
                        "topic": topic,
                        "difficulty": "easy" if j == 0 else "medium" if j == 1 else "hard",
                        "expected_answer": fact,
                        "source_fact": fact,
                        "created_at": datetime.utcnow().isoformat()
                    }

                    qa_pairs.append(qa_pair)

                    # Ground truth: which documents should contain the answer
                    ground_truth[qa_id] = [{
                        "document_id": f"{topic}_doc_{i}",
                        "content": fact,
                        "relevance_score": 1.0,
                        "citations": [f"Source: {topic.capitalize()} Documentation, Section {i+1}"]
                    }]

        # Ensure we have at least 100 Q/A pairs
        while len(qa_pairs) < 100:
            # Generate additional synthetic pairs
            topic = random.choice(list(topics.keys()))
            fact = random.choice(topics[topic])

            qa_id = f"synthetic_{len(qa_pairs)}"
            question = f"Tell me about {fact.split()[:3] if len(fact.split()) >= 3 else fact.split()}?"

            qa_pair = {
                "id": qa_id,
                "question": question,
                "topic": topic,
                "difficulty": "synthetic",
                "expected_answer": fact,
                "source_fact": fact,
                "created_at": datetime.utcnow().isoformat()
            }

            qa_pairs.append(qa_pair)
            ground_truth[qa_id] = [{
                "document_id": f"{topic}_synthetic_{len(qa_pairs)}",
                "content": fact,
                "relevance_score": 1.0,
                "citations": [f"Source: {topic.capitalize()} Reference"]
            }]

        self.qa_pairs = qa_pairs
        self.ground_truth = ground_truth

        # Save dataset
        self._save_dataset()

        logger.info(f"✓ Generated benchmark dataset: {len(qa_pairs)} Q/A pairs across {len(topics)} topics")

    def _save_dataset(self):
        """Save dataset to disk"""
        data = {
            "qa_pairs": self.qa_pairs,
            "ground_truth": self.ground_truth,
            "metadata": {
                "total_pairs": len(self.qa_pairs),
                "topics": list(set(pair["topic"] for pair in self.qa_pairs)),
                "difficulty_distribution": self._get_difficulty_distribution(),
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        }

        try:
            with open(self.dataset_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"✓ Saved benchmark dataset to {self.dataset_path}")
        except Exception as e:
            logger.error(f"Failed to save benchmark dataset: {e}")

    def _get_difficulty_distribution(self) -> Dict[str, int]:
        """Get difficulty level distribution"""
        distribution = {}
        for pair in self.qa_pairs:
            difficulty = pair.get("difficulty", "unknown")
            distribution[difficulty] = distribution.get(difficulty, 0) + 1
        return distribution

    def get_evaluation_set(self, sample_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get evaluation set (optionally sampled)"""
        if sample_size and sample_size < len(self.qa_pairs):
            return random.sample(self.qa_pairs, sample_size)
        return self.qa_pairs.copy()

    def get_ground_truth(self, qa_id: str) -> List[Dict[str, Any]]:
        """Get ground truth for a Q/A pair"""
        return self.ground_truth.get(qa_id, [])

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        return {
            "total_pairs": len(self.qa_pairs),
            "topics": list(set(pair["topic"] for pair in self.qa_pairs)),
            "difficulty_distribution": self._get_difficulty_distribution(),
            "ground_truth_coverage": len(self.ground_truth),
            "avg_ground_truth_per_question": statistics.mean(len(gt) for gt in self.ground_truth.values()) if self.ground_truth else 0
        }


class RetrievalEvaluationRunner:
    """
    PRODUCTION: Evaluation runner measuring Precision@5/10, faithfulness, latency percentiles
    """

    def __init__(self, benchmark_dataset: BenchmarkDataset):
        self.benchmark_dataset = benchmark_dataset
        self.evaluation_history: List[Dict[str, Any]] = []
        self.performance_thresholds = {
            "precision_at_5_min": 0.85,
            "precision_at_10_min": 0.75,
            "faithfulness_min": 0.9,
            "latency_p95_max": 2.0  # seconds
        }

    async def run_evaluation(self, rag_service, sample_size: Optional[int] = None,
                           run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete retrieval evaluation
        """
        if run_id is None:
            run_id = f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"🎯 Starting retrieval evaluation: {run_id}")

        start_time = datetime.utcnow()
        evaluation_set = self.benchmark_dataset.get_evaluation_set(sample_size)

        results = {
            "run_id": run_id,
            "timestamp": start_time.isoformat(),
            "sample_size": len(evaluation_set),
            "questions_evaluated": [],
            "metrics": {},
            "performance": {},
            "thresholds": self.performance_thresholds
        }

        # Evaluate each question
        latencies = []
        precision_at_5_scores = []
        precision_at_10_scores = []
        faithfulness_scores = []

        for qa_pair in evaluation_set:
            question_start = datetime.utcnow()

            try:
                # Get retrieval results
                retrieval_result = await rag_service.retrieve(
                    query=qa_pair["question"],
                    top_k=10  # Get top 10 for evaluation
                )

                question_end = datetime.utcnow()
                latency = (question_end - question_start).total_seconds()
                latencies.append(latency)

                # Evaluate retrieval quality
                ground_truth = self.benchmark_dataset.get_ground_truth(qa_pair["id"])

                precision_at_5 = self._calculate_precision_at_k(retrieval_result.get("results", []), ground_truth, k=5)
                precision_at_10 = self._calculate_precision_at_k(retrieval_result.get("results", []), ground_truth, k=10)
                faithfulness = self._calculate_faithfulness(retrieval_result.get("results", []), qa_pair)

                precision_at_5_scores.append(precision_at_5)
                precision_at_10_scores.append(precision_at_10)
                faithfulness_scores.append(faithfulness)

                # Store individual question results
                question_result = {
                    "question_id": qa_pair["id"],
                    "question": qa_pair["question"],
                    "topic": qa_pair["topic"],
                    "difficulty": qa_pair["difficulty"],
                    "latency_seconds": latency,
                    "precision_at_5": precision_at_5,
                    "precision_at_10": precision_at_10,
                    "faithfulness": faithfulness,
                    "results_returned": len(retrieval_result.get("results", [])),
                    "ground_truth_available": len(ground_truth)
                }

                results["questions_evaluated"].append(question_result)

            except Exception as e:
                logger.error(f"❌ Evaluation failed for question {qa_pair['id']}: {e}")
                latencies.append(10.0)  # Penalize with high latency
                precision_at_5_scores.append(0.0)
                precision_at_10_scores.append(0.0)
                faithfulness_scores.append(0.0)

        # Calculate aggregate metrics
        results["metrics"] = {
            "avg_precision_at_5": statistics.mean(precision_at_5_scores) if precision_at_5_scores else 0,
            "avg_precision_at_10": statistics.mean(precision_at_10_scores) if precision_at_10_scores else 0,
            "avg_faithfulness": statistics.mean(faithfulness_scores) if faithfulness_scores else 0,
            "precision_at_5_std": statistics.stdev(precision_at_5_scores) if len(precision_at_5_scores) > 1 else 0,
            "precision_at_10_std": statistics.stdev(precision_at_10_scores) if len(precision_at_10_scores) > 1 else 0,
            "faithfulness_std": statistics.stdev(faithfulness_scores) if len(faithfulness_scores) > 1 else 0
        }

        # Calculate performance percentiles
        if latencies:
            latencies.sort()
            results["performance"] = {
                "latency_p50": latencies[len(latencies) // 2],
                "latency_p95": latencies[int(len(latencies) * 0.95)],
                "latency_p99": latencies[int(len(latencies) * 0.99)] if len(latencies) > 100 else latencies[-1],
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "avg_latency": statistics.mean(latencies)
            }

        # Check thresholds
        results["threshold_check"] = self._check_thresholds(results["metrics"], results["performance"])

        end_time = datetime.utcnow()
        results["duration_seconds"] = (end_time - start_time).total_seconds()

        # Store in history
        self.evaluation_history.append(results)
        if len(self.evaluation_history) > 50:  # Keep last 50 runs
            self.evaluation_history = self.evaluation_history[-50:]

        # Log results
        await self._log_evaluation_results(results)

        logger.info(f"✓ Evaluation completed: P@5={results['metrics']['avg_precision_at_5']:.3f}, "
                   f"P@10={results['metrics']['avg_precision_at_10']:.3f}, "
                   f"Faithfulness={results['metrics']['avg_faithfulness']:.3f}")

        return results

    def _calculate_precision_at_k(self, retrieved_results: List[Dict], ground_truth: List[Dict], k: int) -> float:
        """Calculate Precision@K"""
        if not retrieved_results or not ground_truth:
            return 0.0

        # Get top K results
        top_k = retrieved_results[:k]

        # Check how many are relevant (have matching content with ground truth)
        relevant_count = 0
        ground_truth_texts = {gt["content"] for gt in ground_truth}

        for result in top_k:
            result_text = result.get("content", "").lower().strip()
            # Simple relevance check: contains significant overlap with ground truth
            for gt_text in ground_truth_texts:
                if self._text_similarity(result_text, gt_text.lower()) > 0.7:  # 70% similarity threshold
                    relevant_count += 1
                    break

        return relevant_count / k

    def _calculate_faithfulness(self, retrieved_results: List[Dict], qa_pair: Dict) -> float:
        """Calculate faithfulness score (how well results support the expected answer)"""
        if not retrieved_results:
            return 0.0

        expected_answer = qa_pair.get("expected_answer", "").lower()
        total_score = 0.0

        for result in retrieved_results[:5]:  # Check top 5
            result_text = result.get("content", "").lower()
            similarity = self._text_similarity(result_text, expected_answer)
            total_score += similarity

        return min(total_score / 5, 1.0)  # Cap at 1.0

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        if not text1 or not text2:
            return 0.0

        # Simple word overlap similarity
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _check_thresholds(self, metrics: Dict, performance: Dict) -> Dict[str, Any]:
        """Check if metrics meet performance thresholds"""
        results = {
            "all_passed": True,
            "failed_checks": [],
            "passed_checks": []
        }

        # Precision@5 check
        if metrics.get("avg_precision_at_5", 0) >= self.performance_thresholds["precision_at_5_min"]:
            results["passed_checks"].append("precision_at_5")
        else:
            results["failed_checks"].append({
                "check": "precision_at_5",
                "expected": self.performance_thresholds["precision_at_5_min"],
                "actual": metrics.get("avg_precision_at_5", 0)
            })
            results["all_passed"] = False

        # Precision@10 check
        if metrics.get("avg_precision_at_10", 0) >= self.performance_thresholds["precision_at_10_min"]:
            results["passed_checks"].append("precision_at_10")
        else:
            results["failed_checks"].append({
                "check": "precision_at_10",
                "expected": self.performance_thresholds["precision_at_10_min"],
                "actual": metrics.get("avg_precision_at_10", 0)
            })
            results["all_passed"] = False

        # Faithfulness check
        if metrics.get("avg_faithfulness", 0) >= self.performance_thresholds["faithfulness_min"]:
            results["passed_checks"].append("faithfulness")
        else:
            results["failed_checks"].append({
                "check": "faithfulness",
                "expected": self.performance_thresholds["faithfulness_min"],
                "actual": metrics.get("avg_faithfulness", 0)
            })
            results["all_passed"] = False

        # Latency check
        if performance.get("latency_p95", 0) <= self.performance_thresholds["latency_p95_max"]:
            results["passed_checks"].append("latency_p95")
        else:
            results["failed_checks"].append({
                "check": "latency_p95",
                "expected": f"≤{self.performance_thresholds['latency_p95_max']}s",
                "actual": f"{performance.get('latency_p95', 0):.2f}s"
            })
            results["all_passed"] = False

        return results

    async def _log_evaluation_results(self, results: Dict[str, Any]):
        """Log evaluation results to immutable log"""
        await immutable_log.append(
            actor="retrieval_evaluation_runner",
            action="evaluation_completed",
            resource=results["run_id"],
            outcome="success" if results["threshold_check"]["all_passed"] else "thresholds_failed",
            payload={
                "run_id": results["run_id"],
                "metrics": results["metrics"],
                "performance": results["performance"],
                "threshold_check": results["threshold_check"],
                "sample_size": results["sample_size"],
                "duration_seconds": results["duration_seconds"]
            }
        )

    def get_evaluation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent evaluation history"""
        return self.evaluation_history[-limit:] if self.evaluation_history else []

    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time"""
        if len(self.evaluation_history) < 2:
            return {"insufficient_data": True}

        # Calculate trends for key metrics
        recent_runs = self.evaluation_history[-10:]  # Last 10 runs

        trends = {}
        metrics_to_track = ["avg_precision_at_5", "avg_precision_at_10", "avg_faithfulness"]

        for metric in metrics_to_track:
            values = [run["metrics"].get(metric, 0) for run in recent_runs if metric in run["metrics"]]
            if len(values) >= 2:
                trends[f"{metric}_trend"] = values[-1] - values[0]  # Change from first to last
                trends[f"{metric}_avg"] = statistics.mean(values)
                trends[f"{metric}_std"] = statistics.stdev(values) if len(values) > 1 else 0

        return trends


class CIQualityGate:
    """
    PRODUCTION: Nightly CI job comparing runs to targets and failing CI if regressions exceed tolerance
    """

    def __init__(self, evaluation_runner: RetrievalEvaluationRunner):
        self.evaluation_runner = evaluation_runner
        self.regression_tolerance = 0.05  # 5% regression tolerance
        self.baseline_file = Path("./config/retrieval_baseline.json")
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)

    async def run_ci_check(self, rag_service, sample_size: int = 50) -> Dict[str, Any]:
        """
        Run CI quality gate check
        """
        logger.info("🔍 Running CI quality gate check...")

        # Run evaluation
        evaluation_results = await self.evaluation_runner.run_evaluation(
            rag_service, sample_size, run_id=f"ci_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )

        # Load baseline if exists
        baseline = self._load_baseline()

        # Compare with baseline
        comparison = self._compare_with_baseline(evaluation_results, baseline)

        # Determine CI status
        ci_status = self._determine_ci_status(comparison)

        results = {
            "evaluation_results": evaluation_results,
            "baseline_comparison": comparison,
            "ci_status": ci_status,
            "should_fail_ci": ci_status["should_fail"],
            "checked_at": datetime.utcnow().isoformat()
        }

        # Update baseline if this is a good run
        if ci_status["status"] == "improved" or (ci_status["status"] == "stable" and not baseline):
            self._update_baseline(evaluation_results)

        # Log CI results
        await immutable_log.append(
            actor="ci_quality_gate",
            action="ci_check_completed",
            resource=f"ci_{datetime.utcnow().strftime('%Y%m%d')}",
            outcome="passed" if not ci_status["should_fail"] else "failed",
            payload={
                "ci_status": ci_status,
                "comparison": comparison,
                "evaluation_run_id": evaluation_results["run_id"]
            }
        )

        logger.info(f"✅ CI check completed: {ci_status['status']} "
                   f"({'PASS' if not ci_status['should_fail'] else 'FAIL'})")

        return results

    def _load_baseline(self) -> Optional[Dict[str, Any]]:
        """Load baseline metrics"""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load baseline: {e}")
        return None

    def _compare_with_baseline(self, current: Dict, baseline: Optional[Dict]) -> Dict[str, Any]:
        """Compare current results with baseline"""
        if not baseline:
            return {
                "has_baseline": False,
                "comparison": "no_baseline",
                "message": "No baseline available for comparison"
            }

        comparison = {
            "has_baseline": True,
            "baseline_run_id": baseline.get("run_id"),
            "current_run_id": current["run_id"],
            "metric_changes": {}
        }

        # Compare key metrics
        key_metrics = ["avg_precision_at_5", "avg_precision_at_10", "avg_faithfulness"]

        for metric in key_metrics:
            current_value = current["metrics"].get(metric, 0)
            baseline_value = baseline["metrics"].get(metric, 0)

            change = current_value - baseline_value
            change_percent = (change / baseline_value) * 100 if baseline_value > 0 else 0

            comparison["metric_changes"][metric] = {
                "current": current_value,
                "baseline": baseline_value,
                "absolute_change": change,
                "percent_change": change_percent,
                "regression": change < -self.regression_tolerance  # Significant drop
            }

        return comparison

    def _determine_ci_status(self, comparison: Dict) -> Dict[str, Any]:
        """Determine CI status based on comparison"""
        if not comparison.get("has_baseline"):
            return {
                "status": "baseline_established",
                "should_fail": False,
                "message": "First run - establishing baseline"
            }

        # Check for regressions
        regressions = []
        improvements = []

        for metric, changes in comparison["metric_changes"].items():
            if changes["regression"]:
                regressions.append(f"{metric}: {changes['percent_change']:.1f}%")
            elif changes["absolute_change"] > 0.01:  # Small improvement threshold
                improvements.append(f"{metric}: +{changes['percent_change']:.1f}%")

        if regressions:
            return {
                "status": "regressed",
                "should_fail": True,
                "message": f"Performance regression detected: {', '.join(regressions)}",
                "regressions": regressions
            }
        elif improvements:
            return {
                "status": "improved",
                "should_fail": False,
                "message": f"Performance improved: {', '.join(improvements)}",
                "improvements": improvements
            }
        else:
            return {
                "status": "stable",
                "should_fail": False,
                "message": "Performance stable within tolerance"
            }

    def _update_baseline(self, evaluation_results: Dict):
        """Update baseline with current results"""
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(evaluation_results, f, indent=2)
            logger.info("✓ Updated retrieval quality baseline")
        except Exception as e:
            logger.error(f"Failed to update baseline: {e}")


# Global instances
benchmark_dataset = BenchmarkDataset()
retrieval_evaluation_runner = RetrievalEvaluationRunner(benchmark_dataset)
ci_quality_gate = CIQualityGate(retrieval_evaluation_runner)