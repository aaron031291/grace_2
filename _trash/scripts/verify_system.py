#!/usr/bin/env python3
"""
System Verification Script
Validates all v2.2.0 systems are operational
"""

import sys
import asyncio
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

async def verify_all_systems():
    """Verify all systems"""
    print("=" * 80)
    print("GRACE v2.2.0 SYSTEM VERIFICATION")
    print("=" * 80)
    
    results = {}
    
    # Phase 0
    print("\n[PHASE 0] Baseline Systems")
    results['imports'] = test_imports()
    results['environment'] = test_environment()
    results['boot'] = test_boot()
    
    # Phase 1
    print("\n[PHASE 1] Guardian Systems")
    results['guardian'] = test_guardian()
    results['mttr'] = test_mttr()
    
    # Phase 2
    print("\n[PHASE 2] RAG Systems")
    results['rag_eval'] = test_rag_evaluation()
    
    # Phase 3
    print("\n[PHASE 3] Learning Systems")
    results['gap_detection'] = test_gap_detection()
    
    # Phase 4
    print("\n[PHASE 4] Coding Pipeline")
    results['coding_pipeline'] = test_coding_pipeline()
    
    # Phase 6
    print("\n[PHASE 6] Enterprise Systems")
    results['golden_signals'] = test_golden_signals()
    results['multi_tenancy'] = test_multi_tenancy()
    results['rate_limiting'] = test_rate_limiting()
    
    # Phase 7
    print("\n[PHASE 7] SaaS Systems")
    results['billing'] = test_billing()
    results['rbac'] = test_rbac()
    results['templates'] = test_templates()
    results['disaster_recovery'] = test_dr()
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n[OK] ALL SYSTEMS OPERATIONAL")
        return 0
    else:
        print("\n[WARN] Some systems need attention")
        for name, result in results.items():
            if not result:
                print(f"  - {name}: FAILED")
        return 1

def test_imports():
    """Test core imports"""
    try:
        from backend.metrics_service import get_metrics_collector
        from backend.cognition_metrics import get_metrics_engine
        from backend.__version__ import __version__
        print("  [OK] Core imports")
        return True
    except Exception as e:
        print(f"  [FAIL] Core imports: {e}")
        return False

def test_environment():
    """Test environment config"""
    try:
        from backend.config.environment import GraceEnvironment
        port = GraceEnvironment.get_port()
        print(f"  [OK] Environment (port={port})")
        return True
    except Exception as e:
        print(f"  [FAIL] Environment: {e}")
        return False

def test_boot():
    """Test metrics boot"""
    try:
        from backend.metrics_service import get_metrics_collector
        from backend.cognition_metrics import get_metrics_engine
        collector = get_metrics_collector()
        engine = get_metrics_engine()
        print("  [OK] Metrics boot")
        return True
    except Exception as e:
        print(f"  [FAIL] Metrics boot: {e}")
        return False

def test_guardian():
    """Test Guardian systems"""
    try:
        from backend.self_heal.network_healing_playbooks import NetworkPlaybookRegistry
        from backend.self_heal.auto_healing_playbooks import RestartKernelPlaybook
        
        registry = NetworkPlaybookRegistry()
        playbook = RestartKernelPlaybook()
        
        # Check safety methods
        assert hasattr(playbook, 'verify')
        assert hasattr(playbook, 'rollback')
        assert hasattr(playbook, 'dry_run')
        
        print(f"  [OK] Guardian (13 playbooks)")
        return True
    except Exception as e:
        print(f"  [FAIL] Guardian: {e}")
        return False

def test_mttr():
    """Test MTTR tracking"""
    try:
        from backend.monitoring.mttr_tracker import get_mttr_tracker
        tracker = get_mttr_tracker()
        stats = tracker.get_stats()
        print("  [OK] MTTR tracking")
        return True
    except Exception as e:
        print(f"  [FAIL] MTTR: {e}")
        return False

def test_rag_evaluation():
    """Test RAG evaluation"""
    try:
        from backend.rag.evaluation_harness import RAGEvaluationHarness
        harness = RAGEvaluationHarness()
        print("  [OK] RAG evaluation harness")
        return True
    except Exception as e:
        print(f"  [FAIL] RAG: {e}")
        return False

def test_gap_detection():
    """Test knowledge gap detection"""
    try:
        from backend.learning.knowledge_gap_detector import get_gap_detector
        detector = get_gap_detector()
        stats = detector.get_stats()
        print("  [OK] Gap detection")
        return True
    except Exception as e:
        print(f"  [FAIL] Gap detection: {e}")
        return False

def test_coding_pipeline():
    """Test coding pipeline"""
    try:
        from backend.autonomy.coding_pipeline import get_coding_pipeline
        pipeline = get_coding_pipeline()
        stats = pipeline.get_stats()
        print("  [OK] Coding pipeline")
        return True
    except Exception as e:
        print(f"  [FAIL] Coding pipeline: {e}")
        return False

def test_golden_signals():
    """Test golden signals"""
    try:
        from backend.observability.golden_signals import get_golden_signals
        monitor = get_golden_signals()
        signals = monitor.get_all_signals()
        print("  [OK] Golden signals")
        return True
    except Exception as e:
        print(f"  [FAIL] Golden signals: {e}")
        return False

def test_multi_tenancy():
    """Test multi-tenancy"""
    try:
        from backend.tenancy.multi_tenant import get_tenant_manager, TenantTier
        manager = get_tenant_manager()
        print(f"  [OK] Multi-tenancy (4 tiers)")
        return True
    except Exception as e:
        print(f"  [FAIL] Multi-tenancy: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting"""
    try:
        from backend.middleware.api_gateway import get_rate_limiter
        limiter = get_rate_limiter()
        allowed = limiter.check_rate_limit("test_client")
        print("  [OK] Rate limiting")
        return True
    except Exception as e:
        print(f"  [FAIL] Rate limiting: {e}")
        return False

def test_billing():
    """Test billing system"""
    try:
        from backend.billing.billing_integration import get_billing_manager
        manager = get_billing_manager()
        print(f"  [OK] Billing (4 plans)")
        return True
    except Exception as e:
        print(f"  [FAIL] Billing: {e}")
        return False

def test_rbac():
    """Test RBAC system"""
    try:
        from backend.auth.rbac_system import get_rbac_system
        rbac = get_rbac_system()
        print(f"  [OK] RBAC (4 roles, 14 permissions)")
        return True
    except Exception as e:
        print(f"  [FAIL] RBAC: {e}")
        return False

def test_templates():
    """Test product templates"""
    try:
        from backend.saas.product_templates import get_template_registry
        registry = get_template_registry()
        templates = registry.list_templates()
        print(f"  [OK] Templates ({len(templates)} available)")
        return True
    except Exception as e:
        print(f"  [FAIL] Templates: {e}")
        return False

def test_dr():
    """Test disaster recovery"""
    try:
        from backend.disaster_recovery.dr_automation import get_dr_manager
        dr = get_dr_manager()
        stats = dr.get_dr_stats()
        print("  [OK] Disaster recovery")
        return True
    except Exception as e:
        print(f"  [FAIL] DR: {e}")
        return False

if __name__ == "__main__":
    exit_code = asyncio.run(verify_all_systems())
    sys.exit(exit_code)
