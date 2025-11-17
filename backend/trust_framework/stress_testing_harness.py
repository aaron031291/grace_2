"""
Stress Testing Harness - PRODUCTION
Automated stress testing with token-step ramps to map execution windows for each model

Maps for EVERY model:
- execution_window: Safe token range
- grey_zone_onset: When quality degrades
- hallucination_signature: Patterns before hallucination
- cost_curve: Token cost vs quality

Stores in model_health_registry for orchestration routing decisions
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from .model_health_telemetry import ExecutionWindow, model_health_registry

logger = logging.getLogger(__name__)


@dataclass
class StressTestResult:
    """Result of stress test at specific token count"""
    
    token_count: int
    
    # Quality metrics
    perplexity: float
    coherence_score: float  # 0-1
    factual_accuracy: float  # 0-1
    
    # Performance
    tokens_per_second: float
    latency_ms: float
    
    # Hallucination indicators
    repetition_rate: float
    contradiction_detected: bool
    confidence_score: float
    
    # Status
    in_safe_zone: bool
    in_grey_zone: bool
    hallucinating: bool
    
    timestamp: float = field(default_factory=time.time)
    
    def overall_quality(self) -> float:
        """Calculate overall quality score"""
        return (
            self.coherence_score * 0.4 +
            self.factual_accuracy * 0.4 +
            (1.0 - self.repetition_rate) * 0.2
        )
    
    def to_dict(self) -> Dict:
        return {
            'token_count': self.token_count,
            'quality': {
                'perplexity': self.perplexity,
                'coherence': self.coherence_score,
                'factual_accuracy': self.factual_accuracy,
                'overall': self.overall_quality()
            },
            'performance': {
                'tokens_per_second': self.tokens_per_second,
                'latency_ms': self.latency_ms
            },
            'hallucination_indicators': {
                'repetition_rate': self.repetition_rate,
                'contradiction': self.contradiction_detected,
                'confidence': self.confidence_score
            },
            'zones': {
                'safe': self.in_safe_zone,
                'grey': self.in_grey_zone,
                'hallucinating': self.hallucinating
            },
            'timestamp': self.timestamp
        }


class StressTestHarness:
    """
    Production stress testing harness
    
    Runs automated token-step ramps:
    - Start at 1K tokens
    - Increment to 2K, 5K, 10K, 20K, 50K, 100K, 128K
    - At each step, measure quality metrics
    - Identify: safe_zone, grey_zone, hallucination_onset
    - Build cost curve (quality vs tokens)
    """
    
    # Token ramp steps
    TOKEN_STEPS = [
        1_000,
        2_000,
        5_000,
        10_000,
        20_000,
        50_000,
        100_000,
        128_000
    ]
    
    # Test scenarios for different token counts
    TEST_SCENARIOS = {
        'factual_qa': "Answer this factual question with citations: {question}",
        'reasoning': "Solve this step by step: {problem}",
        'code_generation': "Write production code for: {requirement}",
        'summarization': "Summarize this in detail: {content}",
        'analysis': "Analyze this data: {data}"
    }
    
    def __init__(self, storage_path: str = "databases/stress_test_results"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Test results cache
        self.test_results: Dict[str, List[StressTestResult]] = {}  # model -> results
        
        # Statistics
        self.tests_completed = 0
        self.models_mapped = 0
        
        logger.info("[STRESS-TEST] Harness initialized")
    
    async def run_full_stress_test(
        self,
        model_name: str,
        scenario: str = 'factual_qa'
    ) -> Dict[str, Any]:
        """
        Run complete stress test across all token steps
        
        Returns:
        - Execution window mapping
        - Grey zone onset point
        - Hallucination signatures
        - Cost curve
        """
        
        logger.info(f"[STRESS-TEST] Starting full stress test for {model_name}")
        
        results = []
        
        # Run test at each token step
        for token_count in self.TOKEN_STEPS:
            logger.info(f"[STRESS-TEST] Testing {model_name} at {token_count} tokens...")
            
            result = await self._test_at_token_count(model_name, token_count, scenario)
            results.append(result)
            
            # Stop if clear hallucination detected
            if result.hallucinating:
                logger.warning(
                    f"[STRESS-TEST] Hallucination detected at {token_count} tokens - stopping test"
                )
                break
            
            # Brief pause between tests
            await asyncio.sleep(2)
        
        # Analyze results
        analysis = self._analyze_stress_test_results(model_name, results)
        
        # Save results
        self.test_results[model_name] = results
        self._save_test_results(model_name, results, analysis)
        
        # Create execution window
        execution_window = self._create_execution_window(model_name, analysis)
        
        # Register with model health registry
        monitor = model_health_registry.get_monitor(model_name)
        monitor.set_execution_window(execution_window)
        
        self.tests_completed += 1
        self.models_mapped += 1
        
        logger.info(
            f"[STRESS-TEST] Completed for {model_name}: "
            f"Safe={execution_window.safe_max_tokens}, "
            f"Grey={execution_window.grey_zone_tokens}, "
            f"Critical={execution_window.critical_tokens}"
        )
        
        return analysis
    
    async def _test_at_token_count(
        self,
        model_name: str,
        target_tokens: int,
        scenario: str
    ) -> StressTestResult:
        """
        Run test at specific token count
        
        Simulates context of target_tokens size and measures quality
        """
        
        # Build prompt to approximate token count
        # (In production, would use actual tokenizer)
        words_needed = target_tokens // 2  # Rough approximation
        test_content = " ".join(["word"] * words_needed)
        
        # Add test question
        template = self.TEST_SCENARIOS.get(scenario, self.TEST_SCENARIOS['factual_qa'])
        prompt = template.format(
            question="What is the capital of France?",
            problem="Calculate 15 * 27",
            requirement="a hello world function",
            content=test_content,
            data="sample data here"
        )
        
        start_time = time.time()
        
        try:
            # Get response from model
            response = await self._query_model(model_name, prompt, max_tokens=100)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Analyze response quality
            quality_metrics = self._analyze_response_quality(response, scenario)
            
            # Determine zones
            overall_quality = quality_metrics['overall_quality']
            
            in_safe_zone = overall_quality >= 0.8
            in_grey_zone = 0.5 <= overall_quality < 0.8
            hallucinating = overall_quality < 0.5 or quality_metrics['contradiction_detected']
            
            return StressTestResult(
                token_count=target_tokens,
                perplexity=quality_metrics.get('perplexity', 10.0),
                coherence_score=quality_metrics['coherence'],
                factual_accuracy=quality_metrics['factual_accuracy'],
                tokens_per_second=100.0 / (latency_ms / 1000) if latency_ms > 0 else 0.0,
                latency_ms=latency_ms,
                repetition_rate=quality_metrics['repetition_rate'],
                contradiction_detected=quality_metrics['contradiction_detected'],
                confidence_score=quality_metrics['confidence'],
                in_safe_zone=in_safe_zone,
                in_grey_zone=in_grey_zone,
                hallucinating=hallucinating
            )
        
        except Exception as e:
            logger.error(f"[STRESS-TEST] Test failed at {target_tokens} tokens: {e}")
            
            # Return failure result
            return StressTestResult(
                token_count=target_tokens,
                perplexity=100.0,
                coherence_score=0.0,
                factual_accuracy=0.0,
                tokens_per_second=0.0,
                latency_ms=30000.0,
                repetition_rate=1.0,
                contradiction_detected=True,
                confidence_score=0.0,
                in_safe_zone=False,
                in_grey_zone=False,
                hallucinating=True
            )
    
    async def _query_model(
        self,
        model_name: str,
        prompt: str,
        max_tokens: int = 100
    ) -> str:
        """Query model via Ollama"""
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('response', '')
        
        except Exception as e:
            logger.error(f"[STRESS-TEST] Model query failed: {e}")
            return ""
    
    def _analyze_response_quality(
        self,
        response: str,
        scenario: str
    ) -> Dict[str, float]:
        """Analyze quality of model response"""
        
        if not response:
            return {
                'overall_quality': 0.0,
                'coherence': 0.0,
                'factual_accuracy': 0.0,
                'perplexity': 100.0,
                'repetition_rate': 1.0,
                'contradiction_detected': True,
                'confidence': 0.0
            }
        
        # Simple quality heuristics
        
        # Coherence: based on sentence structure
        sentences = response.split('.')
        coherence = min(1.0, len([s for s in sentences if len(s.strip()) > 5]) / max(1, len(sentences)))
        
        # Factual accuracy: check for expected answers
        factual_accuracy = 0.7  # Default moderate
        if "paris" in response.lower():
            factual_accuracy = 1.0
        elif "405" in response or "27" in response:  # Math answer
            factual_accuracy = 1.0
        
        # Repetition detection
        words = response.split()
        unique_words = set(words)
        repetition_rate = 1.0 - (len(unique_words) / max(1, len(words)))
        
        # Contradiction detection (simple)
        contradiction_detected = self._detect_contradiction(response)
        
        # Confidence (based on length and structure)
        confidence = min(1.0, len(response) / 200.0)
        
        # Overall quality
        overall = (coherence * 0.4) + (factual_accuracy * 0.4) + ((1.0 - repetition_rate) * 0.2)
        
        return {
            'overall_quality': overall,
            'coherence': coherence,
            'factual_accuracy': factual_accuracy,
            'perplexity': 10.0 if overall > 0.8 else 30.0,  # Estimated
            'repetition_rate': repetition_rate,
            'contradiction_detected': contradiction_detected,
            'confidence': confidence
        }
    
    def _detect_contradiction(self, text: str) -> bool:
        """Simple contradiction detection"""
        
        text_lower = text.lower()
        
        contradiction_pairs = [
            ("yes", "no"),
            ("true", "false"),
            ("correct", "incorrect"),
            ("always", "never")
        ]
        
        for word1, word2 in contradiction_pairs:
            if word1 in text_lower and word2 in text_lower:
                return True
        
        return False
    
    def _analyze_stress_test_results(
        self,
        model_name: str,
        results: List[StressTestResult]
    ) -> Dict[str, Any]:
        """
        Analyze stress test results to determine execution windows
        
        Returns:
        - Safe max tokens
        - Grey zone onset
        - Hallucination onset
        - Quality degradation curve
        """
        
        if not results:
            return {
                'safe_max_tokens': 0,
                'grey_zone_tokens': 0,
                'critical_tokens': 0,
                'error': 'no_test_results'
            }
        
        # Find zone boundaries
        safe_max = 0
        grey_zone = 0
        critical = 0
        
        for result in results:
            if result.in_safe_zone:
                safe_max = max(safe_max, result.token_count)
            elif result.in_grey_zone:
                if grey_zone == 0:
                    grey_zone = result.token_count
                critical = result.token_count
            elif result.hallucinating:
                if critical == 0:
                    critical = result.token_count
                break
        
        # If didn't find boundaries, use defaults
        if grey_zone == 0:
            grey_zone = safe_max + 10_000 if safe_max > 0 else 50_000
        
        if critical == 0:
            critical = grey_zone + 20_000
        
        # Build quality curve
        quality_curve = {
            result.token_count: result.overall_quality()
            for result in results
        }
        
        # Identify hallucination signatures
        hallucination_patterns = []
        for result in results:
            if result.hallucinating or result.in_grey_zone:
                patterns = []
                if result.repetition_rate > 0.3:
                    patterns.append("high_repetition")
                if result.contradiction_detected:
                    patterns.append("contradictions")
                if result.coherence_score < 0.5:
                    patterns.append("incoherence")
                
                hallucination_patterns.extend(patterns)
        
        return {
            'model_name': model_name,
            'safe_max_tokens': safe_max,
            'grey_zone_tokens': grey_zone,
            'critical_tokens': critical,
            'quality_curve': quality_curve,
            'hallucination_patterns': list(set(hallucination_patterns)),
            'total_tests': len(results),
            'test_coverage': {
                'min_tokens': min(r.token_count for r in results),
                'max_tokens': max(r.token_count for r in results)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_execution_window(
        self,
        model_name: str,
        analysis: Dict
    ) -> ExecutionWindow:
        """Create execution window from analysis"""
        
        window = ExecutionWindow(
            model_name=model_name,
            safe_max_tokens=analysis['safe_max_tokens'],
            grey_zone_tokens=analysis['grey_zone_tokens'],
            critical_tokens=analysis['critical_tokens'],
            tokens_to_quality=analysis['quality_curve'],
            hallucination_patterns=analysis['hallucination_patterns'],
            stress_tests_run=1
        )
        
        return window
    
    def _save_test_results(
        self,
        model_name: str,
        results: List[StressTestResult],
        analysis: Dict
    ):
        """Save test results to disk"""
        
        result_file = self.storage_path / f"{model_name.replace(':', '_')}_stress_test.json"
        
        try:
            data = {
                'model_name': model_name,
                'analysis': analysis,
                'detailed_results': [r.to_dict() for r in results],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            with open(result_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"[STRESS-TEST] Results saved: {result_file}")
        
        except Exception as e:
            logger.error(f"[STRESS-TEST] Failed to save results: {e}")
    
    async def run_stress_tests_for_all_models(
        self,
        model_names: List[str]
    ) -> Dict[str, Any]:
        """
        Run stress tests for all models
        
        Can run in parallel for speed
        """
        
        logger.info(f"[STRESS-TEST] Running stress tests for {len(model_names)} models")
        
        # Run tests concurrently (limit concurrency to avoid overload)
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent tests
        
        async def test_with_semaphore(model: str):
            async with semaphore:
                return await self.run_full_stress_test(model)
        
        # Execute all tests
        tasks = [test_with_semaphore(model) for model in model_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        successful = sum(1 for r in results if isinstance(r, dict) and not r.get('error'))
        
        summary = {
            'total_models': len(model_names),
            'tests_completed': successful,
            'tests_failed': len(model_names) - successful,
            'models': {
                model_names[i]: results[i] if not isinstance(results[i], Exception) else {'error': str(results[i])}
                for i in range(len(model_names))
            }
        }
        
        logger.info(
            f"[STRESS-TEST] Batch complete: {successful}/{len(model_names)} successful"
        )
        
        return summary
    
    def get_execution_window(self, model_name: str) -> Optional[ExecutionWindow]:
        """Get execution window for model"""
        
        monitor = model_health_registry.get_monitor(model_name)
        return monitor.execution_window if monitor else None
    
    def get_stats(self) -> Dict:
        """Get harness statistics"""
        
        return {
            'tests_completed': self.tests_completed,
            'models_mapped': self.models_mapped,
            'models_with_results': len(self.test_results),
            'token_steps': self.TOKEN_STEPS
        }


# Global harness
stress_test_harness = StressTestHarness()
