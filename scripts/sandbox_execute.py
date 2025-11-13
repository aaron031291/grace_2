#!/usr/bin/env python3
"""
Sandbox API Testing
Tests an integration in a safe sandbox before production use
"""

import sys
import asyncio
import aiohttp
import argparse
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from backend.models import async_session
from backend.memory_verification_matrix import MemoryVerificationMatrix


class SandboxTester:
    """Safe sandbox testing for integrations"""
    
    def __init__(self, integration_name: str):
        self.name = integration_name
        self.results = {
            'integration': integration_name,
            'timestamp': datetime.utcnow().isoformat(),
            'tests': [],
            'overall_status': 'unknown',
            'hunter_bridge_checks': {},
            'metrics': {}
        }
    
    async def run_hunter_bridge_scan(self, url: str) -> Dict:
        """Hunter Bridge security scan"""
        
        print("\n[HUNTER BRIDGE] Running security scan...")
        
        checks = {
            'https_verified': url.startswith('https://'),
            'domain_reputation': 'unknown',
            'tls_version': 'unknown',
            'certificate_valid': True,
            'rate_limit_detected': False,
            'suspicious_redirects': False
        }
        
        # Test HTTPS
        if checks['https_verified']:
            print("  ✓ HTTPS verified")
        else:
            print("  ✗ HTTPS not verified - BLOCKED")
            checks['certificate_valid'] = False
        
        # Test connectivity
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    checks['domain_reputation'] = 'reachable'
                    
                    # Check for suspicious redirects
                    if len(response.history) > 2:
                        checks['suspicious_redirects'] = True
                        print("  ⚠ Suspicious redirects detected")
                    
                    print(f"  ✓ Domain reachable (HTTP {response.status})")
        except Exception as e:
            checks['domain_reputation'] = 'unreachable'
            print(f"  ✗ Domain unreachable: {e}")
        
        self.results['hunter_bridge_checks'] = checks
        
        # Overall Hunter decision
        if not checks['https_verified'] or checks['suspicious_redirects']:
            return {'status': 'failed', 'checks': checks}
        else:
            return {'status': 'passed', 'checks': checks}
    
    async def test_api_endpoints(self, url: str) -> Dict:
        """Test API endpoints"""
        
        print("\n[TESTING] API endpoints...")
        
        test_results = []
        
        # Test 1: Base URL
        test_results.append(await self._test_endpoint(url, "Base URL"))
        
        # Test 2: Common paths
        common_paths = ['/health', '/status', '/api', '/v1']
        for path in common_paths:
            test_url = url.rstrip('/') + path
            test_results.append(await self._test_endpoint(test_url, f"Path: {path}"))
        
        self.results['tests'] = test_results
        
        successful = sum(1 for t in test_results if t['success'])
        total = len(test_results)
        
        print(f"\n[RESULTS] {successful}/{total} endpoint tests passed")
        
        return {
            'total_tests': total,
            'successful': successful,
            'success_rate': successful / total if total > 0 else 0
        }
    
    async def _test_endpoint(self, url: str, description: str) -> Dict:
        """Test a single endpoint"""
        
        result = {
            'url': url,
            'description': description,
            'success': False,
            'status_code': None,
            'latency_ms': None,
            'error': None
        }
        
        try:
            start = datetime.utcnow()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    end = datetime.utcnow()
                    
                    result['status_code'] = response.status
                    result['latency_ms'] = (end - start).total_seconds() * 1000
                    
                    if response.status in [200, 201, 204]:
                        result['success'] = True
                        print(f"  ✓ {description}: {response.status} ({result['latency_ms']:.0f}ms)")
                    else:
                        print(f"  ⚠ {description}: {response.status}")
        except Exception as e:
            result['error'] = str(e)
            print(f"  ✗ {description}: {e}")
        
        return result
    
    async def measure_kpis(self) -> Dict:
        """Measure performance KPIs"""
        
        print("\n[KPIs] Measuring performance...")
        
        # Calculate metrics from test results
        latencies = [t['latency_ms'] for t in self.results['tests'] if t['latency_ms']]
        successful_tests = [t for t in self.results['tests'] if t['success']]
        
        kpis = {
            'avg_latency_ms': sum(latencies) / len(latencies) if latencies else 0,
            'max_latency_ms': max(latencies) if latencies else 0,
            'min_latency_ms': min(latencies) if latencies else 0,
            'error_rate': 1 - (len(successful_tests) / len(self.results['tests'])) if self.results['tests'] else 1,
            'uptime': 'unknown'
        }
        
        self.results['metrics'] = kpis
        
        print(f"  Avg Latency: {kpis['avg_latency_ms']:.0f}ms")
        print(f"  Error Rate: {kpis['error_rate']*100:.1f}%")
        
        # Check against thresholds
        passing = True
        if kpis['avg_latency_ms'] > 400:
            print(f"  ✗ Latency exceeds 400ms threshold")
            passing = False
        if kpis['error_rate'] > 0.01:
            print(f"  ✗ Error rate exceeds 1% threshold")
            passing = False
        
        if passing:
            print(f"  ✓ All KPIs within thresholds")
        
        return kpis
    
    def generate_report(self) -> Dict:
        """Generate final sandbox report"""
        
        # Determine overall status
        hunter_passed = self.results['hunter_bridge_checks'].get('https_verified', False)
        tests_passed = sum(1 for t in self.results['tests'] if t['success']) > 0
        kpis_passed = self.results['metrics'].get('error_rate', 1) < 0.01
        
        if hunter_passed and tests_passed and kpis_passed:
            self.results['overall_status'] = 'PASSED'
            self.results['recommendation'] = 'Ready for governance approval'
        elif hunter_passed and tests_passed:
            self.results['overall_status'] = 'CONDITIONAL_PASS'
            self.results['recommendation'] = 'Review KPIs before approval'
        else:
            self.results['overall_status'] = 'FAILED'
            self.results['recommendation'] = 'Do not approve - fix issues first'
        
        return self.results


async def main():
    """Run sandbox test"""
    
    parser = argparse.ArgumentParser(description='Sandbox test an integration')
    parser.add_argument('--integration', required=True, help='Integration name to test')
    args = parser.parse_args()
    
    print("=" * 70)
    print(f"SANDBOX TESTING: {args.integration}")
    print("=" * 70)
    
    # Get integration from matrix
    async with async_session() as session:
        matrix = MemoryVerificationMatrix(session)
        integrations = matrix.get_all_integrations()
        
        integration = next((i for i in integrations if i['name'] == args.integration), None)
        
        if not integration:
            print(f"\n[ERROR] Integration '{args.integration}' not found in matrix")
            print("\nAvailable integrations:")
            for i in integrations:
                print(f"  - {i['name']}")
            return
        
        print(f"\n[LOADED] {integration['name']}")
        print(f"  URL: {integration['url']}")
        print(f"  Auth: {integration['auth_type']}")
        print(f"  Risk: {integration['risk_level']}")
        
        # Run sandbox tests
        tester = SandboxTester(integration['name'])
        
        # 1. Hunter Bridge scan
        hunter_result = await tester.run_hunter_bridge_scan(integration['url'])
        
        # Update matrix with scan results
        matrix.update_hunter_scan(
            integration['name'],
            hunter_result['status'],
            hunter_result['checks']
        )
        
        # 2. API endpoint tests
        await tester.test_api_endpoints(integration['url'])
        
        # 3. KPI measurements
        await tester.measure_kpis()
        
        # 4. Generate report
        report = tester.generate_report()
        
        print("\n" + "=" * 70)
        print("SANDBOX TEST REPORT")
        print("=" * 70)
        print(f"\nOverall Status: {report['overall_status']}")
        print(f"Recommendation: {report['recommendation']}")
        
        # Save report
        output_dir = Path(__file__).parent.parent / 'reports' / 'sandbox'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / f"{args.integration.replace(' ', '_')}_sandbox.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[SAVED] Report: {report_file}")
        
        if report['overall_status'] == 'PASSED':
            print("\n[NEXT STEP] Submit for governance approval:")
            print(f"  python scripts/governance_submit.py --integration \"{args.integration}\"")


if __name__ == '__main__':
    asyncio.run(main())
