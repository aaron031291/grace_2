"""
Hard Negative Miner - Mine failed queries for tuning jobs
"""
import json
import asyncio
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class HardNegativeMiner:
    """Mine hard negatives from failed queries for model tuning"""
    
    def __init__(self):
        self.failed_queries = []
        self.hard_negatives = []
        self.mining_stats = {
            "total_failures_analyzed": 0,
            "hard_negatives_mined": 0,
            "categories_identified": 0,
            "tuning_jobs_created": 0
        }
    
    async def analyze_failure_cases(self, failure_cases: List[Dict]) -> Dict[str, Any]:
        """Analyze failure cases to identify patterns"""
        print(f"🔍 Analyzing {len(failure_cases)} failure cases...")
        
        # Group failures by category and pattern
        failure_patterns = defaultdict(list)
        category_failures = defaultdict(list)
        
        for failure in failure_cases:
            category = failure.get("category", "unknown")
            question = failure["question"]
            precision = failure.get("precision_at_5", 0.0)
            
            category_failures[category].append(failure)
            
            # Identify failure patterns
            pattern = self._identify_failure_pattern(failure)
            failure_patterns[pattern].append(failure)
        
        # Mine hard negatives
        hard_negatives = await self._mine_hard_negatives(failure_cases)
        
        # Generate tuning recommendations
        tuning_jobs = await self._generate_tuning_jobs(failure_patterns, hard_negatives)
        
        analysis_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_failures": len(failure_cases),
            "failure_patterns": dict(failure_patterns),
            "category_breakdown": {k: len(v) for k, v in category_failures.items()},
            "hard_negatives": hard_negatives,
            "tuning_jobs": tuning_jobs,
            "recommendations": self._generate_recommendations(failure_patterns)
        }
        
        # Save analysis
        await self._save_analysis(analysis_result)
        
        self.mining_stats["total_failures_analyzed"] += len(failure_cases)
        self.mining_stats["hard_negatives_mined"] += len(hard_negatives)
        self.mining_stats["categories_identified"] = len(category_failures)
        self.mining_stats["tuning_jobs_created"] += len(tuning_jobs)
        
        return analysis_result
    
    def _identify_failure_pattern(self, failure: Dict) -> str:
        """Identify failure pattern type"""
        precision = failure.get("precision_at_5", 0.0)
        latency = failure.get("latency", 0.0)
        question = failure["question"].lower()
        
        # Pattern classification
        if precision == 0.0:
            return "zero_precision"
        elif precision < 0.1:
            return "very_low_precision"
        elif latency > 2.0:
            return "high_latency"
        elif len(question.split()) < 3:
            return "short_query"
        elif len(question.split()) > 20:
            return "long_query"
        elif any(word in question for word in ["how", "what", "why", "when", "where"]):
            return "question_word_query"
        else:
            return "general_failure"
    
    async def _mine_hard_negatives(self, failure_cases: List[Dict]) -> List[Dict]:
        """Mine hard negatives from failure cases"""
        hard_negatives = []
        
        for failure in failure_cases:
            if failure.get("precision_at_5", 0.0) < 0.2:  # Very low precision
                retrieved_docs = failure.get("retrieved_docs", [])
                
                # Create hard negative examples
                for doc in retrieved_docs[:3]:  # Top 3 irrelevant docs
                    hard_negative = {
                        "query": failure["question"],
                        "negative_doc": doc.get("text", ""),
                        "negative_source": doc.get("source", ""),
                        "relevance_score": doc.get("score", 0.0),
                        "expected_answer": failure["expected_answer"],
                        "failure_reason": self._identify_failure_pattern(failure),
                        "category": failure.get("category", "unknown"),
                        "mined_at": datetime.utcnow().isoformat()
                    }
                    hard_negatives.append(hard_negative)
        
        return hard_negatives
    
    async def _generate_tuning_jobs(self, failure_patterns: Dict, 
                                  hard_negatives: List[Dict]) -> List[Dict]:
        """Generate tuning job recommendations"""
        tuning_jobs = []
        
        # Job 1: Hard negative training
        if len(hard_negatives) >= 10:
            tuning_jobs.append({
                "job_type": "hard_negative_training",
                "description": "Train model to better distinguish relevant from irrelevant documents",
                "data_size": len(hard_negatives),
                "priority": "high",
                "estimated_improvement": "10-15% precision gain",
                "training_data": hard_negatives[:50],  # Limit for efficiency
                "hyperparameters": {
                    "learning_rate": 0.0001,
                    "batch_size": 16,
                    "epochs": 5,
                    "negative_sampling_ratio": 3
                }
            })
        
        # Job 2: Category-specific fine-tuning
        category_counts = defaultdict(int)
        for neg in hard_negatives:
            category_counts[neg["category"]] += 1
        
        for category, count in category_counts.items():
            if count >= 5:
                tuning_jobs.append({
                    "job_type": "category_fine_tuning",
                    "category": category,
                    "description": f"Fine-tune retrieval for {category} queries",
                    "data_size": count,
                    "priority": "medium",
                    "estimated_improvement": "5-8% precision gain for category"
                })
        
        # Job 3: Query expansion for failed patterns
        if "short_query" in failure_patterns and len(failure_patterns["short_query"]) >= 5:
            tuning_jobs.append({
                "job_type": "query_expansion",
                "description": "Improve handling of short queries through expansion",
                "data_size": len(failure_patterns["short_query"]),
                "priority": "medium",
                "technique": "semantic_expansion"
            })
        
        return tuning_jobs
    
    def _generate_recommendations(self, failure_patterns: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if "zero_precision" in failure_patterns:
            count = len(failure_patterns["zero_precision"])
            recommendations.append(
                f"Critical: {count} queries returned zero relevant results. "
                "Consider expanding knowledge base or improving indexing."
            )
        
        if "high_latency" in failure_patterns:
            count = len(failure_patterns["high_latency"])
            recommendations.append(
                f"Performance: {count} queries had high latency (>2s). "
                "Consider caching or index optimization."
            )
        
        if "short_query" in failure_patterns:
            count = len(failure_patterns["short_query"])
            recommendations.append(
                f"Query Quality: {count} short queries failed. "
                "Implement query expansion or suggest related terms."
            )
        
        return recommendations
    
    async def _save_analysis(self, analysis: Dict):
        """Save hard negative analysis"""
        reports_dir = Path("reports/hard_negatives")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Save full analysis
        with open(reports_dir / f"analysis_{timestamp}.json", 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save tuning jobs for ML pipeline
        tuning_dir = Path("ml_training/tuning_jobs")
        tuning_dir.mkdir(parents=True, exist_ok=True)
        
        for i, job in enumerate(analysis["tuning_jobs"]):
            job_file = tuning_dir / f"tuning_job_{timestamp}_{i}.json"
            with open(job_file, 'w') as f:
                json.dump(job, f, indent=2)
        
        print(f"💾 Hard negative analysis saved: {len(analysis['tuning_jobs'])} tuning jobs created")
    
    def get_mining_stats(self) -> Dict:
        """Get mining statistics"""
        return self.mining_stats

# Global instance
hard_negative_miner = HardNegativeMiner()
