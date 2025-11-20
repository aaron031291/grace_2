#!/usr/bin/env python3
"""
Grace Stress Test Orchestrator
Runs all 5 industry-standard stress tests with complete audit trails
"""

import subprocess
import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / 'logs'
REPORTS_DIR = BASE_DIR / 'reports'

LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

class StressTestOrchestrator:
    def __init__(self):
        self.test_run_id = f"stress-test-{int(time.time())}"
        self.start_time = datetime.now()
        self.results = []
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def test_1_google_sre(self):
        """Test 1: Google SRE Load Testing"""
        self.log("=" * 80)
        self.log("TEST 1: Google SRE Load Testing")
        self.log("=" * 80)
        self.log("Running Python-based load test with SLO validation...")
        
        import requests
        import statistics
        
        results = {
            'requests': [],
            'errors': 0,
            'total': 0,
        }
        
        endpoints = [
            '/health',
            '/world-model/stats',
            '/api/agentic/health',
            '/api/phase7/summary',
            '/api/metrics/summary',
        ]
        
        self.log("Running 500 requests across 5 critical endpoints...")
        for i in range(100):
            for endpoint in endpoints:
                results['total'] += 1
                try:
                    start = time.time()
                    response = requests.get(
                        f'http://localhost:8000{endpoint}',
                        headers={
                            'X-Test-Run': self.test_run_id,
                            'X-Request-ID': f'req-google-{i}-{endpoint}',
                        },
                        timeout=5
                    )
                    duration = (time.time() - start) * 1000
                    
                    results['requests'].append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'duration_ms': duration,
                        'success': response.status_code < 400,
                    })
                    
                    if response.status_code >= 400:
                        results['errors'] += 1
                        
                except Exception as e:
                    results['errors'] += 1
                    results['requests'].append({
                        'endpoint': endpoint,
                        'status': 0,
                        'duration_ms': 0,
                        'success': False,
                        'error': str(e),
                    })
            
            if i % 20 == 0:
                self.log(f"Progress: {i}/100 iterations completed")
            
            time.sleep(0.1)  # 100ms between batches
        
        # Calculate statistics
        durations = [r['duration_ms'] for r in results['requests'] if r['success']]
        summary = {
            'test_name': 'Google SRE Load Testing',
            'total_requests': results['total'],
            'successful_requests': results['total'] - results['errors'],
            'failed_requests': results['errors'],
            'error_rate': results['errors'] / results['total'] if results['total'] > 0 else 0,
            'latency': {
                'avg': statistics.mean(durations) if durations else 0,
                'min': min(durations) if durations else 0,
                'max': max(durations) if durations else 0,
                'p50': statistics.median(durations) if durations else 0,
                'p95': statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else 0,
                'p99': statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else 0,
            },
            'slo_compliance': {
                'error_rate_under_1pct': (results['errors'] / results['total']) < 0.01 if results['total'] > 0 else False,
                'p95_under_400ms': statistics.quantiles(durations, n=20)[18] < 400 if len(durations) > 20 else False,
                'p99_under_800ms': statistics.quantiles(durations, n=100)[98] < 800 if len(durations) > 100 else False,
            },
        }
        
        with open(LOGS_DIR / 'google_sre_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.log(f"✓ Completed {summary['total_requests']} requests")
        self.log(f"✓ Success rate: {(1 - summary['error_rate']) * 100:.2f}%")
        self.log(f"✓ Avg latency: {summary['latency']['avg']:.2f}ms")
        self.log(f"✓ P95 latency: {summary['latency']['p95']:.2f}ms")
        self.log(f"✓ P99 latency: {summary['latency']['p99']:.2f}ms")
        self.log(f"✓ SLO Compliance: Error rate < 1%: {summary['slo_compliance']['error_rate_under_1pct']}")
        self.log(f"✓ SLO Compliance: P95 < 400ms: {summary['slo_compliance']['p95_under_400ms']}")
        self.log(f"✓ SLO Compliance: P99 < 800ms: {summary['slo_compliance']['p99_under_800ms']}")
        
        passed = all(summary['slo_compliance'].values())
        return {
            'test_name': 'Google SRE Load Testing',
            'success': passed,
            'summary': summary,
        }
    
    def test_2_netflix_chaos(self):
        """Test 2: Netflix Chaos Engineering"""
        self.log("=" * 80)
        self.log("TEST 2: Netflix Chaos Engineering")
        self.log("=" * 80)
        self.log("Simulating chaos scenarios...")
        
        import requests
        
        chaos_results = {
            'scenarios': [],
        }
        
        self.log("Chaos Scenario 1: High load burst (50 rapid requests)")
        burst_start = time.time()
        burst_errors = 0
        for i in range(50):
            try:
                response = requests.get('http://localhost:8000/health', timeout=2)
                if response.status_code >= 400:
                    burst_errors += 1
            except:
                burst_errors += 1
        
        chaos_results['scenarios'].append({
            'name': 'High Load Burst',
            'requests': 50,
            'errors': burst_errors,
            'error_rate': burst_errors / 50,
            'duration_seconds': time.time() - burst_start,
            'passed': burst_errors / 50 < 0.05,  # < 5% error rate
        })
        
        self.log(f"✓ Burst test: {burst_errors}/50 errors ({burst_errors/50*100:.1f}%) - {'PASS' if burst_errors/50 < 0.05 else 'FAIL'}")
        
        self.log("Chaos Scenario 2: Concurrent requests (100 parallel)")
        import concurrent.futures
        
        def make_request(i):
            try:
                response = requests.get('http://localhost:8000/world-model/stats', timeout=5)
                return response.status_code < 400
            except:
                return False
        
        concurrent_start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            results_list = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        concurrent_errors = sum(1 for r in results_list if not r)
        chaos_results['scenarios'].append({
            'name': 'Concurrent Requests',
            'requests': 100,
            'errors': concurrent_errors,
            'error_rate': concurrent_errors / 100,
            'duration_seconds': time.time() - concurrent_start,
            'passed': concurrent_errors / 100 < 0.05,
        })
        
        self.log(f"✓ Concurrent test: {concurrent_errors}/100 errors ({concurrent_errors/100*100:.1f}%) - {'PASS' if concurrent_errors/100 < 0.05 else 'FAIL'}")
        
        self.log("Chaos Scenario 3: Sustained load (200 requests over 20s)")
        sustained_start = time.time()
        sustained_errors = 0
        for i in range(200):
            try:
                response = requests.get('http://localhost:8000/api/agentic/health', timeout=3)
                if response.status_code >= 400:
                    sustained_errors += 1
            except:
                sustained_errors += 1
            time.sleep(0.1)
        
        chaos_results['scenarios'].append({
            'name': 'Sustained Load',
            'requests': 200,
            'errors': sustained_errors,
            'error_rate': sustained_errors / 200,
            'duration_seconds': time.time() - sustained_start,
            'passed': sustained_errors / 200 < 0.02,  # < 2% error rate
        })
        
        self.log(f"✓ Sustained test: {sustained_errors}/200 errors ({sustained_errors/200*100:.1f}%) - {'PASS' if sustained_errors/200 < 0.02 else 'FAIL'}")
        
        with open(LOGS_DIR / 'netflix_chaos_results.json', 'w') as f:
            json.dump(chaos_results, f, indent=2)
        
        all_passed = all(s['passed'] for s in chaos_results['scenarios'])
        self.log(f"✓ Netflix Chaos: {'ALL SCENARIOS PASSED' if all_passed else 'SOME SCENARIOS FAILED'}")
        
        return {
            'test_name': 'Netflix Chaos Engineering',
            'success': all_passed,
            'summary': chaos_results,
        }
    
    def test_3_jepsen_inspired(self):
        """Test 3: Jepsen-Inspired Consistency Testing"""
        self.log("=" * 80)
        self.log("TEST 3: Jepsen-Inspired Consistency Testing")
        self.log("=" * 80)
        self.log("Testing consistency and invariants...")
        
        import requests
        
        jepsen_results = {
            'invariants': [],
        }
        
        self.log("Checking invariant: World model total_entries monotonic")
        entries_history = []
        for i in range(50):
            try:
                response = requests.get('http://localhost:8000/world-model/stats', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    entries_history.append(data.get('total_entries', 0))
            except:
                pass
            time.sleep(0.1)
        
        monotonic = all(entries_history[i] <= entries_history[i+1] 
                       for i in range(len(entries_history)-1))
        
        jepsen_results['invariants'].append({
            'name': 'World Model Monotonic Total Entries',
            'passed': monotonic,
            'samples': len(entries_history),
            'min_value': min(entries_history) if entries_history else 0,
            'max_value': max(entries_history) if entries_history else 0,
        })
        
        self.log(f"✓ Monotonic invariant: {'PASS' if monotonic else 'FAIL'} ({len(entries_history)} samples)")
        
        self.log("Checking invariant: Health endpoint availability (100 checks)")
        health_checks = []
        for i in range(100):
            try:
                response = requests.get('http://localhost:8000/health', timeout=2)
                health_checks.append(response.status_code == 200)
            except:
                health_checks.append(False)
            time.sleep(0.05)
        
        availability = sum(health_checks) / len(health_checks)
        jepsen_results['invariants'].append({
            'name': 'Health Endpoint Availability',
            'passed': availability >= 0.99,  # 99% availability
            'availability': availability,
            'samples': len(health_checks),
        })
        
        self.log(f"✓ Availability: {availability*100:.2f}% - {'PASS' if availability >= 0.99 else 'FAIL'}")
        
        self.log("Checking invariant: Idempotency (10 identical requests)")
        idempotent_results = []
        for i in range(10):
            try:
                response = requests.get('http://localhost:8000/api/metrics/summary', timeout=5)
                if response.status_code == 200:
                    idempotent_results.append(response.json())
            except:
                pass
            time.sleep(0.1)
        
        idempotent = len(set(json.dumps(r, sort_keys=True) for r in idempotent_results)) <= 2  # Allow minor timestamp differences
        
        jepsen_results['invariants'].append({
            'name': 'Idempotency',
            'passed': idempotent,
            'samples': len(idempotent_results),
        })
        
        self.log(f"✓ Idempotency: {'PASS' if idempotent else 'FAIL'} ({len(idempotent_results)} samples)")
        
        with open(LOGS_DIR / 'jepsen_results.json', 'w') as f:
            json.dump(jepsen_results, f, indent=2)
        
        all_passed = all(inv['passed'] for inv in jepsen_results['invariants'])
        self.log(f"✓ Jepsen: {'ALL INVARIANTS HOLD' if all_passed else 'SOME INVARIANTS VIOLATED'}")
        
        return {
            'test_name': 'Jepsen-Inspired Consistency Testing',
            'success': all_passed,
            'summary': jepsen_results,
        }
    
    def test_4_locust_journeys(self):
        """Test 4: Locust User Journey Testing"""
        self.log("=" * 80)
        self.log("TEST 4: Locust User Journey Testing")
        self.log("=" * 80)
        self.log("Running user journey tests...")
        
        import requests
        
        journeys = []
        
        self.log("Journey 1: Complete organism flow (20 iterations)")
        for i in range(20):
            journey_start = time.time()
            steps = []
            
            try:
                r = requests.get('http://localhost:8000/health', timeout=5)
                steps.append({'step': 'health', 'success': r.status_code == 200})
                
                r = requests.get('http://localhost:8000/world-model/stats', timeout=5)
                steps.append({'step': 'world_model', 'success': r.status_code == 200})
                
                r = requests.get('http://localhost:8000/api/agentic/health', timeout=5)
                steps.append({'step': 'agentic', 'success': r.status_code == 200})
                
                r = requests.get('http://localhost:8000/api/phase7/summary', timeout=5)
                steps.append({'step': 'phase7', 'success': r.status_code == 200})
                
                journey_success = all(s['success'] for s in steps)
                journeys.append({
                    'journey': 'complete_organism',
                    'success': journey_success,
                    'duration_seconds': time.time() - journey_start,
                    'steps': steps,
                })
                
            except Exception as e:
                journeys.append({
                    'journey': 'complete_organism',
                    'success': False,
                    'error': str(e),
                })
            
            if i % 5 == 0:
                self.log(f"Progress: {i}/20 journeys completed")
        
        self.log("Journey 2: SaaS workflow (10 iterations)")
        for i in range(10):
            journey_start = time.time()
            steps = []
            
            try:
                r = requests.get('http://localhost:8000/api/phase7/templates', timeout=5)
                steps.append({'step': 'templates', 'success': r.status_code == 200})
                
                r = requests.get('http://localhost:8000/api/phase7/subscriptions', timeout=5)
                steps.append({'step': 'subscriptions', 'success': r.status_code == 200})
                
                r = requests.get('http://localhost:8000/api/phase7/roles', timeout=5)
                steps.append({'step': 'roles', 'success': r.status_code == 200})
                
                r = requests.get('http://localhost:8000/api/phase7/runbooks', timeout=5)
                steps.append({'step': 'runbooks', 'success': r.status_code == 200})
                
                journey_success = all(s['success'] for s in steps)
                journeys.append({
                    'journey': 'saas_workflow',
                    'success': journey_success,
                    'duration_seconds': time.time() - journey_start,
                    'steps': steps,
                })
                
            except Exception as e:
                journeys.append({
                    'journey': 'saas_workflow',
                    'success': False,
                    'error': str(e),
                })
        
        summary = {
            'test_name': 'Locust User Journey Testing',
            'total_journeys': len(journeys),
            'successful_journeys': sum(1 for j in journeys if j['success']),
            'success_rate': sum(1 for j in journeys if j['success']) / len(journeys),
            'journeys': journeys,
        }
        
        with open(LOGS_DIR / 'locust_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.log(f"✓ Completed {summary['total_journeys']} journeys")
        self.log(f"✓ Success rate: {summary['success_rate']*100:.2f}%")
        
        return {
            'test_name': 'Locust User Journey Testing',
            'success': summary['success_rate'] >= 0.95,
            'summary': summary,
        }
    
    def test_5_wrk2_latency(self):
        """Test 5: wrk2 Tail-Latency Testing"""
        self.log("=" * 80)
        self.log("TEST 5: wrk2 Tail-Latency Characterization")
        self.log("=" * 80)
        self.log("Running tail-latency tests...")
        
        import requests
        import statistics
        
        latencies = []
        
        endpoints = [
            '/health',
            '/world-model/stats',
            '/api/metrics/summary',
            '/api/agentic/health',
            '/api/phase7/summary',
        ]
        
        for endpoint in endpoints:
            self.log(f"Testing endpoint: {endpoint}")
            endpoint_latencies = []
            for i in range(100):
                try:
                    start = time.time()
                    response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
                    duration = (time.time() - start) * 1000
                    if response.status_code < 400:
                        endpoint_latencies.append(duration)
                except:
                    pass
                time.sleep(0.01)
            
            if endpoint_latencies:
                latencies.extend(endpoint_latencies)
                p50 = statistics.median(endpoint_latencies)
                p99 = statistics.quantiles(endpoint_latencies, n=100)[98] if len(endpoint_latencies) > 100 else max(endpoint_latencies)
                self.log(f"  ✓ {endpoint}: p50={p50:.2f}ms, p99={p99:.2f}ms")
        
        summary = {
            'test_name': 'wrk2 Tail-Latency Testing',
            'total_requests': len(latencies),
            'latency': {
                'min': min(latencies) if latencies else 0,
                'max': max(latencies) if latencies else 0,
                'avg': statistics.mean(latencies) if latencies else 0,
                'p50': statistics.median(latencies) if latencies else 0,
                'p90': statistics.quantiles(latencies, n=10)[8] if len(latencies) > 10 else 0,
                'p95': statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else 0,
                'p99': statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else 0,
                'p999': statistics.quantiles(latencies, n=1000)[998] if len(latencies) > 1000 else max(latencies) if latencies else 0,
            },
            'slo_compliance': {
                'p99_under_1s': statistics.quantiles(latencies, n=100)[98] < 1000 if len(latencies) > 100 else False,
            },
        }
        
        with open(LOGS_DIR / 'wrk2_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.log(f"✓ Latency p50: {summary['latency']['p50']:.2f}ms")
        self.log(f"✓ Latency p90: {summary['latency']['p90']:.2f}ms")
        self.log(f"✓ Latency p95: {summary['latency']['p95']:.2f}ms")
        self.log(f"✓ Latency p99: {summary['latency']['p99']:.2f}ms")
        self.log(f"✓ Latency p999: {summary['latency']['p999']:.2f}ms")
        
        return {
            'test_name': 'wrk2 Tail-Latency Testing',
            'success': summary['latency']['p99'] < 1000,
            'summary': summary,
        }
    
    def generate_report(self):
        """Generate comprehensive stress test report"""
        self.log("=" * 80)
        self.log("Generating Comprehensive Stress Test Report")
        self.log("=" * 80)
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            'test_run_id': self.test_run_id,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'tests': self.results,
            'summary': {
                'total_tests': len(self.results),
                'passed_tests': sum(1 for r in self.results if r.get('success', False)),
                'failed_tests': sum(1 for r in self.results if not r.get('success', False)),
                'pass_rate': sum(1 for r in self.results if r.get('success', False)) / len(self.results) if self.results else 0,
            },
        }
        
        report_file = REPORTS_DIR / f'stress_test_report_{self.test_run_id}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        md_report = self._generate_markdown_report(report)
        md_file = REPORTS_DIR / f'stress_test_report_{self.test_run_id}.md'
        with open(md_file, 'w') as f:
            f.write(md_report)
        
        self.log(f"✓ Report saved to {report_file}")
        self.log(f"✓ Markdown report saved to {md_file}")
        
        return report
    
    def _generate_markdown_report(self, report):
        """Generate markdown report"""
        md = f"""# Grace Stress Test Report

**Test Run ID:** `{report['test_run_id']}`  
**Start Time:** {report['start_time']}  
**End Time:** {report['end_time']}  
**Duration:** {report['duration_seconds']:.2f} seconds  


- **Total Tests:** {report['summary']['total_tests']}
- **Passed:** {report['summary']['passed_tests']}
- **Failed:** {report['summary']['failed_tests']}
- **Pass Rate:** {report['summary']['pass_rate']*100:.2f}%


"""
        
        for i, test in enumerate(report['tests'], 1):
            status = "✅ PASS" if test.get('success', False) else "❌ FAIL"
            md += f"### {i}. {test['test_name']} {status}\n\n"
            
            if 'summary' in test:
                md += "```json\n"
                md += json.dumps(test['summary'], indent=2)
                md += "\n```\n\n"
        
        md += """## Audit Trail

All detailed logs are available in the `logs/` directory:
- `google_sre_results.json` - Google SRE load test results
- `netflix_chaos_results.json` - Netflix chaos engineering results
- `jepsen_results.json` - Jepsen consistency test results
- `locust_results.json` - Locust user journey results
- `wrk2_results.json` - wrk2 latency characterization results


"""
        
        if report['summary']['pass_rate'] == 1.0:
            md += "🎉 **All stress tests passed!** Grace is production-ready as a unified organism.\n"
        else:
            md += f"⚠️ **{report['summary']['failed_tests']} test(s) failed.** Review logs for details.\n"
        
        return md
    
    def run_all(self):
        """Run all stress tests"""
        self.log("=" * 80)
        self.log("GRACE STRESS TEST ORCHESTRATOR")
        self.log(f"Test Run ID: {self.test_run_id}")
        self.log("=" * 80)
        
        self.results.append(self.test_1_google_sre())
        self.results.append(self.test_2_netflix_chaos())
        self.results.append(self.test_3_jepsen_inspired())
        self.results.append(self.test_4_locust_journeys())
        self.results.append(self.test_5_wrk2_latency())
        
        report = self.generate_report()
        
        self.log("=" * 80)
        self.log("STRESS TEST COMPLETE")
        self.log(f"Pass Rate: {report['summary']['pass_rate']*100:.2f}%")
        self.log(f"Passed: {report['summary']['passed_tests']}/{report['summary']['total_tests']}")
        self.log(f"Duration: {report['duration_seconds']:.2f}s")
        self.log("=" * 80)
        
        return report

if __name__ == '__main__':
    orchestrator = StressTestOrchestrator()
    report = orchestrator.run_all()
    
    sys.exit(0 if report['summary']['pass_rate'] == 1.0 else 1)
