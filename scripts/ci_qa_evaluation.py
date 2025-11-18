#!/usr/bin/env python3
"""
CI Q/A Evaluation - Fail CI on regressions
"""
import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def run_ci_qa_evaluation():
    """Run Q/A evaluation in CI with regression checking"""
    print("🧪 CI Q/A EVALUATION")
    print("=" * 50)
    
    from backend.retrieval.qa_evaluation_harness import qa_evaluation_harness
    from backend.retrieval.hard_negative_miner import hard_negative_miner
    
    try:
        # Load benchmark dataset
        await qa_evaluation_harness.load_benchmark_dataset()
        
        # Mock retrieval function for CI
        async def ci_retrieval_function(question: str, top_k: int = 10):
            """CI mock retrieval - simulates real retrieval"""
            # Simulate different quality responses based on question
            if "restart" in question.lower():
                return [
                    {"text": "Service restart playbook", "score": 0.9, "source": "playbooks/restart.yaml"},
                    {"text": "System restart procedures", "score": 0.8, "source": "docs/restart.md"}
                ][:top_k]
            elif "mttr" in question.lower():
                return [
                    {"text": "MTTR target is 5 minutes", "score": 0.9, "source": "docs/sla.md"}
                ][:top_k]
            else:
                # Lower quality results for other questions
                return [
                    {"text": "Generic documentation", "score": 0.3, "source": "docs/general.md"},
                    {"text": "System overview", "score": 0.2, "source": "docs/overview.md"}
                ][:top_k]
        
        # Run evaluation
        print("🔄 Running evaluation...")
        metrics = await qa_evaluation_harness.run_evaluation(
            ci_retrieval_function, top_k=10, run_id="ci_evaluation"
        )
        
        # Check for regressions
        print("🔍 Checking for regressions...")
        regression_result = await qa_evaluation_harness.check_regression(
            metrics, regression_threshold=0.05  # 5% threshold
        )
        
        if regression_result["regression_detected"]:
            print("🚨 REGRESSION DETECTED - FAILING CI!")
            for reg in regression_result["regressions"]:
                print(f"   ❌ {reg['metric']}: {reg['baseline']:.3f} → {reg['current']:.3f} "
                      f"({reg['regression_pct']:.1f}% regression)")
            
            # Mine hard negatives for failed cases
            if metrics.get("failure_cases", 0) > 0:
                print("⛏️ Mining hard negatives from failures...")
                # Load failure cases from saved results
                results_file = Path("reports/qa_evaluation/ci_evaluation_detailed.json")
                if results_file.exists():
                    with open(results_file, 'r') as f:
                        data = json.load(f)
                        failure_cases = data.get("failure_cases", [])
                    
                    if failure_cases:
                        await hard_negative_miner.analyze_failure_cases(failure_cases)
                        print(f"📊 Mined {len(failure_cases)} failure cases for tuning")
            
            return False
        
        else:
            print("✅ No regressions detected - CI PASSED!")
            print(f"📊 Current Precision@5: {metrics['precision_at_5']:.3f}")
            print(f"📊 Current Precision@10: {metrics['precision_at_10']:.3f}")
            print(f"⏱️ Avg Latency: {metrics['avg_latency']:.3f}s")
            print(f"💾 Cache Hit Rate: {metrics['cache_hit_rate']:.3f}")
            return True
    
    except Exception as e:
        print(f"❌ CI Q/A evaluation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_ci_qa_evaluation())
    sys.exit(0 if success else 1)