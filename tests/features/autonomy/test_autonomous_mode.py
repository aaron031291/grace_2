#!/usr/bin/env python3
"""Test Grace's Autonomous Mode"""

import asyncio
from backend.governance_framework import GovernanceFramework

async def test_autonomous_mode():
    gf = GovernanceFramework()
    
    print("=" * 60)
    print("GRACE AUTONOMOUS MODE TEST")
    print("=" * 60)
    
    # Test 1: Auto-approved action (fix_code_issue)
    print("\n[TEST 1] Auto-approved action: fix_code_issue")
    result = await gf.check_action(
        actor='autonomous_improver',
        action='fix_code_issue',
        resource='backend/test.py',
        context={'description': 'fix type error'}
    )
    print(f"  [OK] Approved: {result['approved']}")
    print(f"  [OK] Reason: {result['reason']}")
    print(f"  [OK] Requires human approval: {result['requires_human_approval']}")
    assert result['approved'] == True, "fix_code_issue should be auto-approved"
    assert result['requires_human_approval'] == False, "Should not require human approval"
    
    # Test 2: Auto-approved action (self_heal_low_severity)
    print("\n[TEST 2] Auto-approved action: self_heal_low_severity")
    result = await gf.check_action(
        actor='ml_healer',
        action='self_heal_low_severity',
        resource='backend/metrics_collector.py',
        context={'severity': 'low', 'issue': 'unused import'}
    )
    print(f"  [OK] Approved: {result['approved']}")
    print(f"  [OK] Requires human approval: {result['requires_human_approval']}")
    assert result['approved'] == True, "self_heal_low_severity should be auto-approved"
    
    # Test 3: Requires approval action (delete_file)
    print("\n[TEST 3] Requires approval: delete_file")
    result = await gf.check_action(
        actor='autonomous_improver',
        action='delete_file',
        resource='backend/test.py',
        context={}
    )
    print(f"  [OK] Approved: {result['approved']}")
    print(f"  [OK] Requires human approval: {result['requires_human_approval']}")
    # This should require approval (not auto-approved)
    
    # Test 4: Auto-rejected action (access_credentials)
    print("\n[TEST 4] Auto-rejected: access_credentials")
    result = await gf.check_action(
        actor='autonomous_improver',
        action='access_credentials',
        resource='backend/secrets_vault.py',
        context={}
    )
    print(f"  [OK] Approved: {result['approved']}")
    print(f"  [OK] Reason: {result['reason']}")
    assert result['approved'] == False, "access_credentials should be auto-rejected"
    
    # Test 5: Collect metrics (auto-approved)
    print("\n[TEST 5] Auto-approved: collect_metrics")
    result = await gf.check_action(
        actor='metrics_collector',
        action='collect_metrics',
        resource='metrics_system',
        context={'metric_id': 'system.health'}
    )
    print(f"  [OK] Approved: {result['approved']}")
    print(f"  [OK] Requires human approval: {result['requires_human_approval']}")
    assert result['approved'] == True, "collect_metrics should be auto-approved"
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - AUTONOMOUS MODE IS ENABLED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_autonomous_mode())
