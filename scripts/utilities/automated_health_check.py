#!/usr/bin/env python3
"""
Automated Health Check - PRODUCTION
Runs comprehensive health checks and generates report
Can be scheduled (cron/Task Scheduler) for daily checks
"""

import asyncio
import httpx
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

API_BASE = "http://localhost:8000"


class AutomatedHealthCheck:
    """Automated health checker for TRUST framework"""
    
    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
        self.report = {
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {},
            'issues_found': [],
            'recommendations': [],
            'overall_status': 'healthy'
        }
    
    async def run_all_checks(self):
        """Run all health checks"""
        
        print("=" * 80)
        print("GRACE TRUST FRAMEWORK - AUTOMATED HEALTH CHECK")
        print("=" * 80)
        print(f"Timestamp: {self.report['timestamp']}")
        print()
        
        async with httpx.AsyncClient() as client:
            # Check 1: Framework status
            print("[1/7] Checking framework status...")
            await self._check_framework_status(client)
            
            # Check 2: Model health
            print("[2/7] Checking all models health...")
            await self._check_all_models_health(client)
            
            # Check 3: Hallucination ledger
            print("[3/7] Checking hallucination ledger...")
            await self._check_hallucination_ledger(client)
            
            # Check 4: Guardrails
            print("[4/7] Checking guardrails...")
            await self._check_guardrails(client)
            
            # Check 5: Data hygiene
            print("[5/7] Checking data hygiene...")
            await self._check_data_hygiene(client)
            
            # Check 6: Chaos drills
            print("[6/7] Checking chaos drills...")
            await self._check_chaos_drills(client)
            
            # Check 7: Dashboard
            print("[7/7] Checking dashboard...")
            await self._check_dashboard(client)
        
        # Generate report
        self._generate_report()
    
    async def _check_framework_status(self, client: httpx.AsyncClient):
        """Check framework status"""
        
        try:
            response = await client.get(f"{self.api_base}/api/trust/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.report['checks']['framework_status'] = 'ok'
                print("  [OK] Framework active")
            else:
                self.report['checks']['framework_status'] = 'error'
                self.report['issues_found'].append("Framework API not responding")
                print(f"  [ERROR] Status code: {response.status_code}")
        
        except Exception as e:
            self.report['checks']['framework_status'] = 'error'
            self.report['issues_found'].append(f"Framework unreachable: {e}")
            print(f"  [ERROR] {e}")
    
    async def _check_all_models_health(self, client: httpx.AsyncClient):
        """Check health of all models"""
        
        try:
            response = await client.get(f"{self.api_base}/api/trust/models/health/all", timeout=10)
            
            if response.status_code == 200:
                all_health = response.json()
                
                unhealthy = []
                critical = []
                
                for model_name, health in all_health.items():
                    if health['status'] in ['critical', 'quarantined']:
                        critical.append(model_name)
                    elif health['status'] in ['degraded', 'grey_zone']:
                        unhealthy.append(model_name)
                
                if critical:
                    self.report['checks']['model_health'] = 'critical'
                    self.report['issues_found'].append(f"{len(critical)} models in critical state")
                    self.report['recommendations'].append(f"Investigate critical models: {', '.join(critical)}")
                    print(f"  [CRITICAL] {len(critical)} models in critical state")
                
                elif unhealthy:
                    self.report['checks']['model_health'] = 'warning'
                    self.report['issues_found'].append(f"{len(unhealthy)} models degraded")
                    self.report['recommendations'].append("Monitor degraded models closely")
                    print(f"  [WARNING] {len(unhealthy)} models degraded")
                
                else:
                    self.report['checks']['model_health'] = 'ok'
                    print(f"  [OK] All {len(all_health)} models healthy")
            
            else:
                self.report['checks']['model_health'] = 'error'
                print(f"  [ERROR] Status code: {response.status_code}")
        
        except Exception as e:
            self.report['checks']['model_health'] = 'error'
            print(f"  [ERROR] {e}")
    
    async def _check_hallucination_ledger(self, client: httpx.AsyncClient):
        """Check hallucination ledger"""
        
        try:
            response = await client.get(f"{self.api_base}/api/trust/hallucinations/ledger", timeout=10)
            
            if response.status_code == 200:
                ledger = response.json()
                
                total_hallucinations = ledger.get('total_hallucinations', 0)
                high_risk = ledger.get('highest_risk_models', [])
                
                if high_risk:
                    self.report['checks']['hallucination_ledger'] = 'warning'
                    self.report['issues_found'].append(f"{len(high_risk)} high-risk models")
                    self.report['recommendations'].append(f"Review high-risk models: {', '.join(high_risk)}")
                    print(f"  [WARNING] {len(high_risk)} high-risk models detected")
                
                else:
                    self.report['checks']['hallucination_ledger'] = 'ok'
                    print(f"  [OK] Ledger tracking (total: {total_hallucinations})")
            
            else:
                self.report['checks']['hallucination_ledger'] = 'error'
                print(f"  [ERROR] Status code: {response.status_code}")
        
        except Exception as e:
            self.report['checks']['hallucination_ledger'] = 'error'
            print(f"  [ERROR] {e}")
    
    async def _check_guardrails(self, client: httpx.AsyncClient):
        """Check guardrails"""
        
        try:
            response = await client.get(f"{self.api_base}/api/trust/guardrails/status", timeout=10)
            
            if response.status_code == 200:
                self.report['checks']['guardrails'] = 'ok'
                print("  [OK] Guardrails active")
            else:
                self.report['checks']['guardrails'] = 'error'
                print(f"  [ERROR] Status code: {response.status_code}")
        
        except Exception as e:
            self.report['checks']['guardrails'] = 'error'
            print(f"  [ERROR] {e}")
    
    async def _check_data_hygiene(self, client: httpx.AsyncClient):
        """Check data hygiene"""
        
        try:
            response = await client.get(f"{self.api_base}/api/trust/data-hygiene/stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                
                pass_rate = stats.get('pass_rate', 0.0)
                
                if pass_rate < 0.7:
                    self.report['checks']['data_hygiene'] = 'warning'
                    self.report['issues_found'].append(f"Low data quality pass rate: {pass_rate:.0%}")
                    self.report['recommendations'].append("Review data hygiene failures")
                    print(f"  [WARNING] Pass rate: {pass_rate:.0%}")
                
                else:
                    self.report['checks']['data_hygiene'] = 'ok'
                    print(f"  [OK] Pass rate: {pass_rate:.0%}")
            
            else:
                self.report['checks']['data_hygiene'] = 'error'
                print(f"  [ERROR] Status code: {response.status_code}")
        
        except Exception as e:
            self.report['checks']['data_hygiene'] = 'error'
            print(f"  [ERROR] {e}")
    
    async def _check_chaos_drills(self, client: httpx.AsyncClient):
        """Check chaos drills"""
        
        try:
            response = await client.get(f"{self.api_base}/api/trust/chaos-drills/stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                
                total_drills = stats.get('total_drills', 0)
                vulnerabilities = stats.get('vulnerabilities_found', 0)
                
                if vulnerabilities > 0:
                    self.report['checks']['chaos_drills'] = 'warning'
                    self.report['issues_found'].append(f"{vulnerabilities} vulnerabilities found in drills")
                    self.report['recommendations'].append("Patch security vulnerabilities")
                    print(f"  [WARNING] {vulnerabilities} vulnerabilities found")
                
                else:
                    self.report['checks']['chaos_drills'] = 'ok'
                    print(f"  [OK] {total_drills} drills run, no vulnerabilities")
            
            else:
                self.report['checks']['chaos_drills'] = 'error'
                print(f"  [ERROR] Status code: {response.status_code}")
        
        except Exception as e:
            self.report['checks']['chaos_drills'] = 'error'
            print(f"  [ERROR] {e}")
    
    async def _check_dashboard(self, client: httpx.AsyncClient):
        """Final dashboard check"""
        
        try:
            response = await client.get(f"{self.api_base}/api/trust/dashboard", timeout=10)
            
            if response.status_code == 200:
                self.report['checks']['dashboard'] = 'ok'
                print("  [OK] Dashboard accessible")
            else:
                self.report['checks']['dashboard'] = 'error'
                print(f"  [ERROR] Status code: {response.status_code}")
        
        except Exception as e:
            self.report['checks']['dashboard'] = 'error'
            print(f"  [ERROR] {e}")
    
    def _generate_report(self):
        """Generate final report"""
        
        print()
        print("=" * 80)
        print("HEALTH CHECK REPORT")
        print("=" * 80)
        print()
        
        # Determine overall status
        if any(check == 'critical' for check in self.report['checks'].values()):
            self.report['overall_status'] = 'critical'
        elif any(check == 'error' for check in self.report['checks'].values()):
            self.report['overall_status'] = 'error'
        elif any(check == 'warning' for check in self.report['checks'].values()):
            self.report['overall_status'] = 'warning'
        else:
            self.report['overall_status'] = 'healthy'
        
        status_icons = {
            'healthy': '[OK]',
            'warning': '[WARN]',
            'error': '[ERROR]',
            'critical': '[CRITICAL]'
        }
        
        print(f"Overall Status: {status_icons[self.report['overall_status']]} {self.report['overall_status'].upper()}")
        print()
        
        # Issues
        if self.report['issues_found']:
            print(f"Issues Found ({len(self.report['issues_found'])}):")
            for issue in self.report['issues_found']:
                print(f"  - {issue}")
            print()
        
        # Recommendations
        if self.report['recommendations']:
            print(f"Recommendations ({len(self.report['recommendations'])}):")
            for rec in self.report['recommendations']:
                print(f"  - {rec}")
            print()
        
        # Save report
        report_file = Path(f"reports/trust_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f"Report saved: {report_file}")
        print()
        
        # Exit code based on status
        if self.report['overall_status'] in ['critical', 'error']:
            sys.exit(1)
        elif self.report['overall_status'] == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)


async def main():
    """Main entry point"""
    
    checker = AutomatedHealthCheck()
    await checker.run_all_checks()


if __name__ == "__main__":
    asyncio.run(main())
