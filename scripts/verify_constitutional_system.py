"""Verification Script for Constitutional AI Framework

Quick test to verify all components are working.
"""

import asyncio
import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(__file__))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def verify_system():
    """Verify constitutional system is operational"""
    
    print("="*70)
    print("CONSTITUTIONAL AI FRAMEWORK - VERIFICATION".center(70))
    print("="*70 + "\n")
    
    from grace_rebuild.backend.models import async_session
    from grace_rebuild.backend.constitutional_models import (
        ConstitutionalPrinciple, ConstitutionalViolation,
        ClarificationRequest, OperationalTenet
    )
    from grace_rebuild.backend.constitutional_verifier import constitutional_verifier
    from grace_rebuild.backend.constitutional_engine import constitutional_engine
    from grace_rebuild.backend.clarifier import clarifier
    from sqlalchemy import select, func
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check principles seeded
    print("[1/7] Checking constitutional principles...")
    try:
        async with async_session() as session:
            result = await session.execute(
                select(func.count(ConstitutionalPrinciple.id))
            )
            count = result.scalar()
            
            if count == 30:
                print(f"    ✓ PASS: {count} principles found (expected 30)")
                tests_passed += 1
            else:
                print(f"    ✗ FAIL: {count} principles found (expected 30)")
                tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 2: Check tenets seeded
    print("\n[2/7] Checking operational tenets...")
    try:
        async with async_session() as session:
            result = await session.execute(
                select(func.count(OperationalTenet.id))
            )
            count = result.scalar()
            
            if count == 10:
                print(f"    ✓ PASS: {count} tenets found (expected 10)")
                tests_passed += 1
            else:
                print(f"    ✗ FAIL: {count} tenets found (expected 10)")
                tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 3: Test compliance checking for allowed action
    print("\n[3/7] Testing compliance check (allowed action)...")
    try:
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="read_file",
            resource="/test/file.txt",
            payload={"operation": "read"},
            confidence=0.95
        )
        
        if result['allowed'] and result['compliant']:
            print(f"    ✓ PASS: Action allowed as expected")
            tests_passed += 1
        else:
            print(f"    ✗ FAIL: Action blocked unexpectedly")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 4: Test compliance checking for blocked action
    print("\n[4/7] Testing compliance check (blocked action)...")
    try:
        result = await constitutional_verifier.verify_action(
            actor="test_user",
            action_type="code_execution",
            resource="shell",
            payload={"command": "rm -rf /"},
            confidence=1.0
        )
        
        if not result['allowed'] and len(result['violations']) > 0:
            print(f"    ✓ PASS: Destructive command blocked as expected")
            print(f"           Violations: {len(result['violations'])}")
            tests_passed += 1
        else:
            print(f"    ✗ FAIL: Destructive command not blocked")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 5: Test clarification detection
    print("\n[5/7] Testing clarification detection...")
    try:
        uncertainty = clarifier.detect_uncertainty(
            user_input="Delete it",
            context={"recent_entities": ["file1.txt", "file2.txt", "folder/"]}
        )
        
        if uncertainty and uncertainty['type'] == 'ambiguous_pronoun':
            print(f"    ✓ PASS: Ambiguous pronoun detected")
            print(f"           Question: {uncertainty['question']}")
            tests_passed += 1
        else:
            print(f"    ✗ FAIL: Ambiguity not detected")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 6: Test clarification request creation
    print("\n[6/7] Testing clarification request...")
    try:
        clarification = await constitutional_engine.request_clarification(
            user="test_user",
            original_input="Fix the bug",
            uncertainty_type="missing_parameter",
            confidence=0.6,
            question="Which bug should I fix?",
            options=["Issue #42", "Issue #53"],
            timeout_minutes=60
        )
        
        if clarification and clarification['request_id']:
            print(f"    ✓ PASS: Clarification request created")
            print(f"           Request ID: {clarification['request_id'][:16]}...")
            tests_passed += 1
        else:
            print(f"    ✗ FAIL: Clarification request not created")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Test 7: Test violation logging
    print("\n[7/7] Testing violation logging...")
    try:
        violation = await constitutional_engine.log_violation(
            principle_name="no_destructive_commands",
            actor="test_user",
            action="shell_command",
            resource="/etc/passwd",
            violation_type="attempt",
            detected_by="test_verification",
            severity="critical",
            details="Test violation for verification",
            blocked=True
        )
        
        if violation and violation['violation_id']:
            print(f"    ✓ PASS: Violation logged successfully")
            print(f"           Violation ID: {violation['violation_id']}")
            tests_passed += 1
        else:
            print(f"    ✗ FAIL: Violation not logged")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ FAIL: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY".center(70))
    print("="*70)
    print(f"\nTests Passed: {tests_passed}/7")
    print(f"Tests Failed: {tests_failed}/7")
    
    if tests_failed == 0:
        print("\n✓ ALL TESTS PASSED - Constitutional AI Framework is operational!")
        print("\nNext steps:")
        print("  1. Start backend: py grace_rebuild/backend/main.py")
        print("  2. View constitution: py -m grace_rebuild.backend.cli.commands.constitution_command show")
        print("  3. Check stats: py -m grace_rebuild.backend.cli.commands.constitution_command stats")
        print("  4. Read docs: grace_rebuild/backend/CONSTITUTIONAL_AI.md")
        return 0
    else:
        print(f"\n✗ {tests_failed} TEST(S) FAILED - Review errors above")
        print("\nTroubleshooting:")
        print("  1. Ensure database is initialized")
        print("  2. Run seed: py grace_rebuild/backend/run_seed_constitution.py")
        print("  3. Check logs for errors")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(verify_system())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
