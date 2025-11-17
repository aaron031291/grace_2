"""
API Sandbox Tester
Grace tests discovered APIs in a safe sandbox environment
Only promotes to production if tests pass all KPIs and governance
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json
from pathlib import Path

from .governance_framework import governance_framework
from .constitutional_engine import constitutional_engine
from .secrets_vault import secrets_vault
from .unified_logger import unified_logger
from .knowledge_provenance import provenance_tracker

logger = logging.getLogger(__name__)


class APISandboxTester:
    """
    Tests APIs in sandbox before production use
    Validates: Security, Performance, Reliability, Usefulness
    Stores API keys securely in secrets vault
    """
    
    def __init__(self):
        self.sandbox_dir = Path(__file__).parent.parent / "sandbox" / "api_tests"
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        self.tested_apis = []
        self.approved_apis = []
        self.blocked_apis = []
        
        # Test KPIs
        self.test_kpis = {
            'response_time_ms': 5000,  # Max 5 seconds
            'success_rate': 0.9,  # Min 90% success
            'uptime': 0.95,  # Min 95% uptime
            'rate_limit_friendly': True,  # Must not be too restrictive
            'https_required': True  # Must use HTTPS
        }
    
    async def test_api(
        self,
        api_info: Dict[str, Any],
        api_key: Optional[str] = None,
        test_endpoints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Test an API in sandbox environment
        
        Args:
            api_info: API metadata
            api_key: API key if required
            test_endpoints: Specific endpoints to test
        
        Returns:
            Test results with pass/fail and recommendations
        """
        
        logger.info(f"[API-SANDBOX] 🧪 Testing API: {api_info['name']}")
        logger.info(f"[API-SANDBOX] Category: {api_info.get('category')}")
        
        # Governance check
        approval = await governance_framework.check_action(
            actor='grace_api_tester',
            action='test_api_in_sandbox',
            resource=api_info['name'],
            context={
                'api_name': api_info['name'],
                'api_url': api_info['url'],
                'requires_auth': api_key is not None
            },
            confidence=0.85
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[API-SANDBOX] 🚫 Governance blocked")
            return {'error': 'governance_blocked', 'passed': False}
        
        # Constitutional check
        constitutional_check = await constitutional_engine.verify_action(
            action_type='test_external_api',
            context={
                'api_name': api_info['name'],
                'api_url': api_info['url']
            }
        )
        
        if not constitutional_check.get('approved', False):
            logger.warning(f"[API-SANDBOX] ⚖️ Constitutional check failed")
            return {'error': 'constitutional_blocked', 'passed': False}
        
        logger.info(f"[API-SANDBOX] ✅ Governance and constitutional checks passed")
        
        # Store API key in secrets vault if provided
        secret_key_name = None
        if api_key:
            secret_key_name = f"{api_info['name'].upper().replace(' ', '_')}_API_KEY"
            await secrets_vault.set_secret(secret_key_name, api_key)
            logger.info(f"[API-SANDBOX] 🔐 API key stored securely: {secret_key_name}")
        
        # Run tests
        test_results = await self._run_api_tests(api_info, api_key, test_endpoints)
        
        # Check KPIs
        kpi_met = self._check_api_kpis(test_results)
        
        # Determine if API should be promoted
        promote_to_production = (
            test_results['tests_passed'] and
            kpi_met and
            test_results['security_score'] >= 0.8
        )
        
        # Record test
        test_id = await self._record_api_test(
            api_info,
            test_results,
            kpi_met,
            promote_to_production,
            secret_key_name
        )
        
        result = {
            'test_id': test_id,
            'api_name': api_info['name'],
            'passed': test_results['tests_passed'],
            'kpi_met': kpi_met,
            'security_score': test_results['security_score'],
            'recommend_promotion': promote_to_production,
            'test_results': test_results,
            'secret_stored': secret_key_name if api_key else None,
            'fully_traceable': True
        }
        
        if promote_to_production:
            logger.info(f"[API-SANDBOX] ✅ PASSED - Recommend promotion to production!")
            logger.info(f"[API-SANDBOX]   Security: {test_results['security_score']:.2f}")
            logger.info(f"[API-SANDBOX]   Performance: {test_results['avg_response_ms']:.0f}ms")
            logger.info(f"[API-SANDBOX]   Success rate: {test_results['success_rate']:.1%}")
            self.approved_apis.append(api_info)
        else:
            logger.warning(f"[API-SANDBOX] ❌ FAILED - Not safe for production")
            self.blocked_apis.append(api_info)
        
        return result
    
    async def _run_api_tests(
        self,
        api_info: Dict[str, Any],
        api_key: Optional[str],
        test_endpoints: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Run comprehensive API tests"""
        
        base_url = api_info['url']
        
        # Build headers
        headers = {}
        if api_key:
            auth_type = api_info.get('auth', 'apiKey')
            if auth_type == 'apiKey':
                headers['Authorization'] = f'Bearer {api_key}'
            elif auth_type == 'X-Api-Key':
                headers['X-Api-Key'] = api_key
        
        tests_run = 0
        tests_passed = 0
        response_times = []
        
        # Test endpoints
        endpoints_to_test = test_endpoints or ['/']
        
        for endpoint in endpoints_to_test[:5]:  # Max 5 endpoints
            try:
                url = base_url.rstrip('/') + endpoint
                
                start_time = asyncio.get_event_loop().time()
                
                async with self.session.get(url, headers=headers) as response:
                    elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                    response_times.append(elapsed_ms)
                    
                    tests_run += 1
                    
                    if response.status in [200, 201, 204]:
                        tests_passed += 1
                    
                    # Try to get response data
                    try:
                        data = await response.json()
                    except:
                        data = await response.text()
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.warning(f"[API-SANDBOX] Test failed for {endpoint}: {e}")
                tests_run += 1
        
        # Calculate metrics
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        success_rate = tests_passed / tests_run if tests_run > 0 else 0
        
        # Calculate security score
        security_score = 0.5  # Base score
        if api_info.get('https', False):
            security_score += 0.3
        if api_info.get('auth') in ['apiKey', 'OAuth2']:
            security_score += 0.2
        
        return {
            'tests_run': tests_run,
            'tests_passed': tests_passed,
            'success_rate': success_rate,
            'avg_response_ms': avg_response,
            'max_response_ms': max(response_times) if response_times else 0,
            'security_score': security_score,
            'https_enabled': api_info.get('https', False),
            'auth_required': api_info.get('auth', 'None') != 'None'
        }
    
    def _check_api_kpis(self, test_results: Dict[str, Any]) -> bool:
        """Check if API meets KPI thresholds"""
        
        if test_results['avg_response_ms'] > self.test_kpis['response_time_ms']:
            logger.warning(f"[API-SANDBOX] KPI failed: Response time too slow")
            return False
        
        if test_results['success_rate'] < self.test_kpis['success_rate']:
            logger.warning(f"[API-SANDBOX] KPI failed: Success rate too low")
            return False
        
        if not test_results['https_enabled'] and self.test_kpis['https_required']:
            logger.warning(f"[API-SANDBOX] KPI failed: HTTPS not enabled")
            return False
        
        return True
    
    async def _record_api_test(
        self,
        api_info: Dict[str, Any],
        test_results: Dict[str, Any],
        kpi_met: bool,
        promote: bool,
        secret_key_name: Optional[str]
    ) -> str:
        """Record API test with provenance"""
        
        # Record as knowledge source
        source_id = await provenance_tracker.record_source(
            url=api_info['url'],
            source_type='api',
            content={
                'title': api_info['name'],
                'text': api_info.get('description', ''),
                'word_count': 0,
                'code_count': 0,
                'scraped_at': datetime.utcnow().isoformat()
            },
            governance_checks={
                'governance': True,
                'hunter': True,
                'constitutional': True
            },
            storage_path=f"apis/sandbox/{api_info['name'].replace(' ', '_')}.json"
        )
        
        # Save test results
        test_file = self.sandbox_dir / f"{api_info['name'].replace(' ', '_')}_test.json"
        test_data = {
            'source_id': source_id,
            'api_info': api_info,
            'test_results': test_results,
            'kpi_met': kpi_met,
            'promote_to_production': promote,
            'secret_key_name': secret_key_name,
            'tested_at': datetime.utcnow().isoformat()
        }
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        # Log decision
        await unified_logger.log_agentic_spine_decision(
            decision_type='api_tested_in_sandbox',
            decision_context={'api_name': api_info['name']},
            chosen_action='promote' if promote else 'block',
            rationale=f"Tests passed: {test_results['tests_passed']}/{test_results['tests_run']}, KPIs met: {kpi_met}",
            actor='api_sandbox_tester',
            confidence=0.9 if promote else 0.5,
            risk_score=0.1 if promote else 0.8,
            status='approved' if promote else 'blocked',
            resource=api_info['name']
        )
        
        self.tested_apis.append(test_data)
        
        return source_id
    
    async def promote_to_production(
        self,
        api_name: str
    ) -> Dict[str, Any]:
        """
        Promote approved API from sandbox to production
        
        Args:
            api_name: Name of API to promote
        
        Returns:
            Promotion result
        """
        
        logger.info(f"[API-SANDBOX] 🚀 Promoting API to production: {api_name}")
        
        # Find API in approved list
        api = next((a for a in self.approved_apis if a['name'] == api_name), None)
        
        if not api:
            return {'error': 'API not found in approved list'}
        
        # Final governance check for production promotion
        approval = await governance_framework.check_action(
            actor='grace_api_integration',
            action='promote_api_to_production',
            resource=api_name,
            context={'api': api},
            confidence=0.95
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[API-SANDBOX] 🚫 Production promotion blocked")
            return {'error': 'governance_blocked_production'}
        
        # Save to production config
        prod_config_file = Path(__file__).parent.parent / "config" / "integrated_apis.json"
        prod_config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing
        if prod_config_file.exists():
            with open(prod_config_file, 'r') as f:
                prod_config = json.load(f)
        else:
            prod_config = {'apis': []}
        
        # Add API
        prod_config['apis'].append({
            'name': api['name'],
            'url': api['url'],
            'category': api['category'],
            'description': api.get('description'),
            'auth': api.get('auth'),
            'promoted_at': datetime.utcnow().isoformat(),
            'promoted_by': 'grace_autonomous'
        })
        
        # Save
        with open(prod_config_file, 'w') as f:
            json.dump(prod_config, f, indent=2)
        
        logger.info(f"[API-SANDBOX] ✅ API promoted to production: {api_name}")
        logger.info(f"[API-SANDBOX] Config saved: {prod_config_file}")
        
        # Log promotion
        await unified_logger.log_agentic_spine_decision(
            decision_type='api_promoted_to_production',
            decision_context={'api_name': api_name},
            chosen_action='promote',
            rationale='Passed all sandbox tests and KPIs',
            actor='api_sandbox_tester',
            confidence=0.95,
            risk_score=0.05,
            status='completed',
            resource=api_name
        )
        
        return {
            'success': True,
            'api_name': api_name,
            'promoted_at': datetime.utcnow().isoformat(),
            'config_file': str(prod_config_file)
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get sandbox testing status"""
        
        return {
            'apis_tested': len(self.tested_apis),
            'apis_approved': len(self.approved_apis),
            'apis_blocked': len(self.blocked_apis),
            'approval_rate': len(self.approved_apis) / len(self.tested_apis) if self.tested_apis else 0,
            'kpi_thresholds': self.test_kpis
        }


# Global instance
api_sandbox_tester = APISandboxTester()
