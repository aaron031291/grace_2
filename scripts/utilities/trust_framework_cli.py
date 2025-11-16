#!/usr/bin/env python3
"""
TRUST Framework CLI - Production Tool
Manage and monitor Grace's complete trust and governance systems
"""

import asyncio
import sys
import httpx
from pathlib import Path
from typing import Optional
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

API_BASE = "http://localhost:8000"


class TrustFrameworkCLI:
    """CLI for TRUST framework management"""
    
    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
    
    async def check_status(self):
        """Check complete TRUST framework status"""
        
        print("=" * 80)
        print("TRUST FRAMEWORK STATUS")
        print("=" * 80)
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_base}/api/trust/status", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"Framework: {data['framework']}")
                    print(f"Status: {data['status']}")
                    print()
                    
                    print("Systems Active:")
                    for system, stats in data['systems'].items():
                        print(f"  - {system}: {self._format_stats(stats)}")
                    
                    print()
                    print(f"Models: {data['models']['total_registered']} registered")
                else:
                    print(f"[ERROR] API returned status {response.status_code}")
            
            except Exception as e:
                print(f"[ERROR] Could not connect to Grace: {e}")
                print("Make sure Grace is running: python serve.py")
    
    async def check_dashboard(self):
        """Check complete dashboard"""
        
        print("=" * 80)
        print("TRUST FRAMEWORK DASHBOARD")
        print("=" * 80)
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_base}/api/trust/dashboard", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    summary = data['summary']
                    alerts = data['alerts']
                    
                    print(f"Overall Health Score: {summary['overall_health_score']:.0%}")
                    print()
                    
                    print("Models:")
                    print(f"  Total: {summary['total_models']}")
                    print(f"  Healthy: {summary['healthy_models']}")
                    print(f"  Unhealthy: {summary['unhealthy_models']}")
                    print(f"  Quarantined: {summary['quarantined_models']}")
                    print()
                    
                    print("Hallucinations:")
                    print(f"  Total: {summary['total_hallucinations']}")
                    print(f"  Models needing retraining: {summary['models_needing_retraining']}")
                    print()
                    
                    if alerts['unhealthy_models']:
                        print("[WARNING] Unhealthy models:")
                        for model in alerts['unhealthy_models']:
                            print(f"  - {model}")
                        print()
                    
                    if alerts['quarantined_models']:
                        print("[CRITICAL] Quarantined models:")
                        for model in alerts['quarantined_models']:
                            print(f"  - {model}")
                        print()
                    
                    if alerts['retraining_priorities']:
                        print("Retraining Priorities (Top 5):")
                        for item in alerts['retraining_priorities'][:5]:
                            print(f"  - {item['model']}: Priority {item['priority']}")
                
                else:
                    print(f"[ERROR] API returned status {response.status_code}")
            
            except Exception as e:
                print(f"[ERROR] Could not connect to Grace: {e}")
    
    async def check_model_health(self, model_name: str):
        """Check health of specific model"""
        
        print("=" * 80)
        print(f"MODEL HEALTH: {model_name}")
        print("=" * 80)
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base}/api/trust/models/{model_name}/health",
                    timeout=10
                )
                
                if response.status_code == 200:
                    health = response.json()
                    
                    print(f"Status: {health['status']}")
                    print(f"Current Tokens: {health['current_tokens']}")
                    print()
                    
                    print("Metrics:")
                    print(f"  Perplexity: {health['metrics']['avg_perplexity']:.2f}")
                    print(f"  Entropy: {health['metrics']['avg_entropy']:.2f}")
                    print(f"  Latency: {health['metrics']['avg_latency_ms']:.0f}ms")
                    print()
                    
                    print("Trends:")
                    print(f"  Perplexity: {health['trends']['perplexity']}")
                    print(f"  Entropy: {health['trends']['entropy']}")
                    print(f"  Latency: {health['trends']['latency']}")
                    print()
                    
                    if health['warnings']:
                        print("Warnings:")
                        for warning in health['warnings']:
                            print(f"  - {warning}")
                        print()
                    
                    if health['critical_issues']:
                        print("[CRITICAL] Issues:")
                        for issue in health['critical_issues']:
                            print(f"  - {issue}")
                        print()
                    
                    if health['recommended_action']:
                        print(f"Recommended: {health['recommended_action']}")
                
                else:
                    print(f"[ERROR] API returned status {response.status_code}")
            
            except Exception as e:
                print(f"[ERROR] {e}")
    
    async def verify_model_integrity(self, model_name: str):
        """Verify integrity of model"""
        
        print("=" * 80)
        print(f"MODEL INTEGRITY VERIFICATION: {model_name}")
        print("=" * 80)
        print()
        print("Running integrity checks...")
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base}/api/trust/models/{model_name}/integrity",
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"Overall Status: {result['overall_status']}")
                    print()
                    
                    print("Checks:")
                    for check_name, check_result in result['checks'].items():
                        status_icon = "[OK]" if check_result.get('exists') or check_result.get('matches') or check_result.get('consistent') else "[FAIL]"
                        print(f"  {status_icon} {check_name}")
                    print()
                    
                    if result['violations']:
                        print("Violations:")
                        for violation in result['violations']:
                            print(f"  [{violation['severity'].upper()}] {violation['description']}")
                        print()
                
                else:
                    print(f"[ERROR] API returned status {response.status_code}")
            
            except Exception as e:
                print(f"[ERROR] {e}")
    
    async def run_stress_test(self, model_name: str):
        """Run stress test on model"""
        
        print("=" * 80)
        print(f"STRESS TEST: {model_name}")
        print("=" * 80)
        print()
        print("Running token-step ramp test...")
        print("This will take several minutes...")
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base}/api/trust/models/{model_name}/stress-test",
                    timeout=300  # 5 minutes
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"[OK] Stress test complete")
                    print()
                    print(f"Safe max tokens: {result['safe_max_tokens']}")
                    print(f"Grey zone onset: {result['grey_zone_tokens']}")
                    print(f"Critical limit: {result['critical_tokens']}")
                    print()
                    
                    if result['hallucination_patterns']:
                        print("Hallucination signatures detected:")
                        for pattern in result['hallucination_patterns']:
                            print(f"  - {pattern}")
                        print()
                    
                    print(f"Quality curve mapped: {len(result['quality_curve'])} data points")
                
                else:
                    print(f"[ERROR] API returned status {response.status_code}")
            
            except Exception as e:
                print(f"[ERROR] {e}")
    
    async def list_all_models_health(self):
        """List health status for all models"""
        
        print("=" * 80)
        print("ALL MODELS HEALTH STATUS")
        print("=" * 80)
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base}/api/trust/models/health/all",
                    timeout=10
                )
                
                if response.status_code == 200:
                    all_health = response.json()
                    
                    for model_name, health in all_health.items():
                        status_icon = {
                            'healthy': '[OK]',
                            'degraded': '[WARN]',
                            'grey_zone': '[WARN]',
                            'critical': '[CRIT]',
                            'quarantined': '[QUAR]'
                        }.get(health['status'], '[????]')
                        
                        print(f"{status_icon} {model_name:30s} - {health['status']}")
                        
                        if health['warnings']:
                            for warning in health['warnings']:
                                print(f"      └─ {warning}")
                
                else:
                    print(f"[ERROR] API returned status {response.status_code}")
            
            except Exception as e:
                print(f"[ERROR] {e}")
    
    def _format_stats(self, stats: dict) -> str:
        """Format statistics for display"""
        
        if isinstance(stats, dict):
            # Try to find key metrics
            if 'total' in stats:
                return f"{stats['total']} total"
            elif 'count' in stats:
                return f"{stats['count']} items"
            else:
                return f"{len(stats)} items"
        else:
            return str(stats)


async def main():
    """Main CLI entry point"""
    
    if len(sys.argv) < 2:
        print("TRUST Framework CLI")
        print()
        print("Usage:")
        print("  python trust_framework_cli.py status              - Check framework status")
        print("  python trust_framework_cli.py dashboard           - View dashboard")
        print("  python trust_framework_cli.py health <model>      - Check model health")
        print("  python trust_framework_cli.py integrity <model>   - Verify model integrity")
        print("  python trust_framework_cli.py stress-test <model> - Run stress test")
        print("  python trust_framework_cli.py list-health         - List all models health")
        print()
        print("Examples:")
        print("  python trust_framework_cli.py dashboard")
        print("  python trust_framework_cli.py health qwen2.5:72b")
        print("  python trust_framework_cli.py integrity llama3.1:70b")
        print("  python trust_framework_cli.py stress-test deepseek-r1:70b")
        sys.exit(0)
    
    command = sys.argv[1]
    cli = TrustFrameworkCLI()
    
    if command == "status":
        await cli.check_status()
    
    elif command == "dashboard":
        await cli.check_dashboard()
    
    elif command == "health" and len(sys.argv) > 2:
        model_name = sys.argv[2]
        await cli.check_model_health(model_name)
    
    elif command == "integrity" and len(sys.argv) > 2:
        model_name = sys.argv[2]
        await cli.verify_model_integrity(model_name)
    
    elif command == "stress-test" and len(sys.argv) > 2:
        model_name = sys.argv[2]
        await cli.run_stress_test(model_name)
    
    elif command == "list-health":
        await cli.list_all_models_health()
    
    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
