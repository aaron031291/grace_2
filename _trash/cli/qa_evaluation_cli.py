"""
Q/A Evaluation CLI - Command line interface for evaluation harness
"""
import asyncio
import click
import json
from pathlib import Path
from typing import Optional

from backend.retrieval.qa_evaluation_harness import qa_evaluation_harness
from backend.retrieval.hard_negative_miner import hard_negative_miner
from backend.retrieval.synthetic_qa_benchmark import qa_benchmark_generator

@click.group()
def qa_eval():
    """Q/A Evaluation CLI"""
    pass

@qa_eval.command()
@click.option('--size', default=150, help='Number of Q/A pairs to generate')
@click.option('--output', default='config/qa_benchmark.json', help='Output file path')
async def generate_benchmark(size: int, output: str):
    """Generate synthetic Q/A benchmark dataset"""
    click.echo(f"🔄 Generating {size} Q/A pairs...")
    
    await qa_benchmark_generator.generate_benchmark_dataset(size)
    filepath = await qa_benchmark_generator.save_benchmark(output)
    
    click.echo(f"✅ Benchmark generated: {filepath}")

@qa_eval.command()
@click.option('--benchmark', default='config/qa_benchmark.json', help='Benchmark file')
@click.option('--top-k', default=10, help='Top-K results to evaluate')
@click.option('--run-id', help='Custom run ID')
async def run_evaluation(benchmark: str, top_k: int, run_id: Optional[str]):
    """Run Q/A evaluation"""
    click.echo("🧪 Starting Q/A evaluation...")
    
    # Load benchmark
    await qa_evaluation_harness.load_benchmark_dataset(benchmark)
    
    # Mock retrieval function for demo
    async def mock_retrieval(question: str, top_k: int = 10):
        """Mock retrieval function - replace with real implementation"""
        return [
            {"text": "Service restart playbook documentation", "score": 0.9, "source": "playbooks/restart.yaml"},
            {"text": "MTTR target is 5 minutes for critical incidents", "score": 0.8, "source": "docs/sla.md"},
            {"text": "Guardian runs integrity checks on playbooks", "score": 0.7, "source": "docs/guardian.md"},
            {"text": "System monitoring dashboard shows CPU usage", "score": 0.6, "source": "docs/monitoring.md"},
            {"text": "Database connection pooling configuration", "score": 0.5, "source": "config/db.yaml"}
        ][:top_k]
    
    # Run evaluation
    metrics = await qa_evaluation_harness.run_evaluation(
        mock_retrieval, top_k=top_k, run_id=run_id
    )
    
    click.echo("📊 Evaluation Results:")
    click.echo(f"   Precision@5: {metrics['precision_at_5']:.3f}")
    click.echo(f"   Precision@10: {metrics['precision_at_10']:.3f}")
    click.echo(f"   Avg Latency: {metrics['avg_latency']:.3f}s")
    click.echo(f"   Cache Hit Rate: {metrics['cache_hit_rate']:.3f}")

@qa_eval.command()
@click.option('--threshold', default=0.05, help='Regression threshold (5%)')
async def check_regression(threshold: float):
    """Check for regressions against baseline"""
    click.echo("🔍 Checking for regressions...")
    
    # Load latest results
    latest_file = Path("reports/qa_evaluation/latest_results.json")
    if not latest_file.exists():
        click.echo("❌ No evaluation results found. Run evaluation first.")
        return
    
    with open(latest_file, 'r') as f:
        current_metrics = json.load(f)
    
    regression_result = await qa_evaluation_harness.check_regression(
        current_metrics, threshold
    )
    
    if regression_result["regression_detected"]:
        click.echo("🚨 REGRESSION DETECTED!")
        for reg in regression_result["regressions"]:
            click.echo(f"   {reg['metric']}: {reg['baseline']:.3f} → {reg['current']:.3f} "
                      f"({reg['regression_pct']:.1f}% regression)")
        exit(1)  # Fail CI
    else:
        click.echo("✅ No regressions detected")

@qa_eval.command()
async def mine_hard_negatives():
    """Mine hard negatives from failure cases"""
    click.echo("⛏️ Mining hard negatives...")
    
    # Load latest evaluation results
    results_dir = Path("reports/qa_evaluation")
    latest_files = list(results_dir.glob("*_detailed.json"))
    
    if not latest_files:
        click.echo("❌ No evaluation results found for mining")
        return
    
    # Get most recent results
    latest_file = max(latest_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
        failure_cases = data.get("failure_cases", [])
    
    if not failure_cases:
        click.echo("✅ No failure cases found - system performing well!")
        return
    
    # Mine hard negatives
    analysis = await hard_negative_miner.analyze_failure_cases(failure_cases)
    
    click.echo(f"📊 Mining Results:")
    click.echo(f"   Failure cases analyzed: {analysis['total_failures']}")
    click.echo(f"   Hard negatives mined: {len(analysis['hard_negatives'])}")
    click.echo(f"   Tuning jobs created: {len(analysis['tuning_jobs'])}")
    
    # Show recommendations
    if analysis["recommendations"]:
        click.echo("\n💡 Recommendations:")
        for rec in analysis["recommendations"]:
            click.echo(f"   • {rec}")

@qa_eval.command()
async def show_stats():
    """Show evaluation statistics"""
    click.echo("📊 Q/A Evaluation Statistics")
    click.echo("=" * 40)
    
    # Show latest metrics
    latest_file = Path("reports/qa_evaluation/latest_results.json")
    if latest_file.exists():
        with open(latest_file, 'r') as f:
            metrics = json.load(f)
        
        click.echo("Latest Evaluation:")
        click.echo(f"   Timestamp: {metrics.get('timestamp', 'Unknown')}")
        click.echo(f"   Questions: {metrics.get('total_questions', 0)}")
        click.echo(f"   Precision@5: {metrics.get('precision_at_5', 0):.3f}")
        click.echo(f"   Precision@10: {metrics.get('precision_at_10', 0):.3f}")
        click.echo(f"   Latency P95: {metrics.get('latency_p95', 0):.3f}s")
        click.echo(f"   Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.3f}")
        click.echo(f"   Failure Cases: {metrics.get('failure_cases', 0)}")
    
    # Show mining stats
    mining_stats = hard_negative_miner.get_mining_stats()
    click.echo("\nHard Negative Mining:")
    click.echo(f"   Total failures analyzed: {mining_stats['total_failures_analyzed']}")
    click.echo(f"   Hard negatives mined: {mining_stats['hard_negatives_mined']}")
    click.echo(f"   Tuning jobs created: {mining_stats['tuning_jobs_created']}")

if __name__ == '__main__':
    qa_eval()