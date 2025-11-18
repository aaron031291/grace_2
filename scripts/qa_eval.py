#!/usr/bin/env python3
"""
Q/A Evaluation CLI Launcher
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.qa_evaluation_cli import qa_eval

if __name__ == '__main__':
    # Convert async CLI to sync
    import click
    
    @click.group()
    def main():
        """Q/A Evaluation CLI"""
        pass
    
    @main.command()
    @click.option('--size', default=150, help='Number of Q/A pairs')
    @click.option('--output', default='config/qa_benchmark.json', help='Output file')
    def generate(size, output):
        """Generate benchmark dataset"""
        from backend.retrieval.synthetic_qa_benchmark import qa_benchmark_generator
        
        async def run():
            await qa_benchmark_generator.generate_benchmark_dataset(size)
            await qa_benchmark_generator.save_benchmark(output)
            print(f"✅ Generated {size} Q/A pairs in {output}")
        
        asyncio.run(run())
    
    @main.command()
    @click.option('--benchmark', default='config/qa_benchmark.json')
    @click.option('--top-k', default=10)
    def evaluate(benchmark, top_k):
        """Run evaluation"""
        asyncio.run(run_evaluation_async(benchmark, top_k))
    
    @main.command()
    def check_regression():
        """Check for regressions"""
        asyncio.run(run_regression_check())
    
    @main.command()
    def mine_negatives():
        """Mine hard negatives"""
        asyncio.run(run_mining())
    
    main()

async def run_evaluation_async(benchmark, top_k):
    """Run evaluation async"""
    from backend.retrieval.qa_evaluation_harness import qa_evaluation_harness
    
    await qa_evaluation_harness.load_benchmark_dataset(benchmark)
    
    # Mock retrieval
    async def mock_retrieval(question: str, top_k: int = 10):
        return [
            {"text": "Service restart playbook", "score": 0.9, "source": "playbooks/restart.yaml"},
            {"text": "MTTR target is 5 minutes", "score": 0.8, "source": "docs/sla.md"}
        ][:top_k]
    
    metrics = await qa_evaluation_harness.run_evaluation(mock_retrieval, top_k=top_k)
    print(f"📊 Precision@5: {metrics['precision_at_5']:.3f}")
    print(f"📊 Precision@10: {metrics['precision_at_10']:.3f}")

async def run_regression_check():
    """Check regressions async"""
    from backend.retrieval.qa_evaluation_harness import qa_evaluation_harness
    import json
    
    latest_file = Path("reports/qa_evaluation/latest_results.json")
    if not latest_file.exists():
        print("❌ No results found")
        return
    
    with open(latest_file, 'r') as f:
        metrics = json.load(f)
    
    result = await qa_evaluation_harness.check_regression(metrics)
    if result["regression_detected"]:
        print("🚨 Regression detected!")
        sys.exit(1)
    else:
        print("✅ No regressions")

async def run_mining():
    """Mine hard negatives async"""
    from backend.retrieval.hard_negative_miner import hard_negative_miner
    
    # Mock failure cases for demo
    failure_cases = [
        {
            "qa_id": "qa_001",
            "question": "How to restart service?",
            "expected_answer": "Use systemctl restart",
            "retrieved_docs": [{"text": "Unrelated doc", "score": 0.1}],
            "precision_at_5": 0.0,
            "category": "system_operations"
        }
    ]
    
    analysis = await hard_negative_miner.analyze_failure_cases(failure_cases)
    print(f"⛏️ Mined {len(analysis['hard_negatives'])} hard negatives")
    print(f"🔧 Created {len(analysis['tuning_jobs'])} tuning jobs")