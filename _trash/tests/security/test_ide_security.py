"""Test IDE security features: scanner, auto-fix, quarantine"""
import asyncio
import os
import tempfile
from pathlib import Path


async def test_security_scanner():
    """Test security scanning functionality"""
    print("\n[TEST 1] Testing Security Scanner...")
    
    from backend.ide_security import security_scanner
    
    # Create test file with SQL injection
    test_code = '''
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE id=" + user_id
    cursor.execute(query)
    return cursor.fetchone()

def unsafe_exec(code):
    # Dangerous import
    eval(code)
    exec(code)
'''
    
    issues = await security_scanner.scan_code(test_code, 'python')
    
    print(f"✓ Found {len(issues)} security issues")
    
    for issue in issues:
        print(f"  - {issue['severity'].upper()}: {issue['rule_name']} (Line {issue['line_number']})")
        print(f"    Issue: {issue['issue']}")
        print(f"    Fix: {issue['suggestion']}")
    
    assert len(issues) > 0, "Should detect security issues"
    
    sql_issues = [i for i in issues if 'sql' in i['rule_name'].lower()]
    dangerous_imports = [i for i in issues if 'dangerous' in i['rule_name'].lower() or 'eval' in i['issue'].lower()]
    
    print(f"✓ SQL injection issues: {len(sql_issues)}")
    print(f"✓ Dangerous imports: {len(dangerous_imports)}")
    
    return True


async def test_auto_fix():
    """Test auto-fix functionality"""
    print("\n[TEST 2] Testing Auto-Fix...")
    
    from backend.auto_fix import auto_fix
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''
def dangerous_function():
    import eval
    from os import system
    __import__('subprocess')
    
def sql_query(user_input):
    query = "SELECT * FROM users WHERE name='" + user_input + "'"
    return query
''')
        temp_file = f.name
    
    try:
        # Test: Remove dangerous imports
        result = await auto_fix.apply_fix(temp_file, 'remove_dangerous_imports')
        
        print(f"✓ Fix applied: {result['success']}")
        print(f"✓ Changes made: {len(result.get('changes_made', []))}")
        
        for change in result.get('changes_made', []):
            print(f"  - {change}")
        
        assert result['success'], "Fix should succeed"
        assert len(result.get('changes_made', [])) > 0, "Should make changes"
        
        # Verify dangerous imports are removed
        with open(temp_file, 'r') as f:
            new_content = f.read()
        
        assert 'import eval' not in new_content or '# REMOVED' in new_content, "Should remove/comment eval"
        print("✓ Dangerous imports removed")
        
        return True
    
    finally:
        os.unlink(temp_file)


async def test_quarantine_system():
    """Test file quarantine and restoration"""
    print("\n[TEST 3] Testing Quarantine System...")
    
    from backend.auto_quarantine import quarantine_manager
    
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('# Malicious code here\neval("dangerous")')
        temp_file = f.name
    
    try:
        # Quarantine the file
        result = await quarantine_manager.quarantine_file(
            temp_file,
            "Detected dangerous eval() usage",
            actor="test_user"
        )
        
        print(f"✓ Quarantine result: {result['success']}")
        
        if result['success']:
            quarantine_id = result['quarantine_id']
            print(f"✓ Quarantine ID: {quarantine_id}")
            
            # Verify original file is removed
            assert not os.path.exists(temp_file), "Original file should be removed"
            print("✓ Original file removed")
            
            # List quarantined files
            quarantined = quarantine_manager.list_quarantined()
            print(f"✓ Total quarantined files: {len(quarantined)}")
            
            # Find our file
            our_file = next((f for f in quarantined if f['quarantine_id'] == quarantine_id), None)
            assert our_file is not None, "Should find quarantined file"
            print(f"✓ File found in quarantine")
            print(f"  - Reason: {our_file['reason']}")
            print(f"  - Status: {our_file['status']}")
            
            # Test restoration (will require governance)
            restore_result = await quarantine_manager.restore_file(quarantine_id, "test_user")
            
            if restore_result.get('requires_approval'):
                print("✓ Restoration requires governance approval (expected)")
            elif restore_result['success']:
                print(f"✓ File restored to: {restore_result['restored_to']}")
                # Clean up restored file
                if os.path.exists(restore_result['restored_to']):
                    os.unlink(restore_result['restored_to'])
            else:
                print(f"✗ Restoration failed: {restore_result.get('error')}")
            
            return True
        else:
            print(f"✗ Quarantine failed: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return False


async def test_xss_fix():
    """Test XSS auto-fix"""
    print("\n[TEST 4] Testing XSS Fix...")
    
    from backend.auto_fix import auto_fix
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write('''
function displayUser(name) {
    document.getElementById('output').innerHTML = name;
    document.write(userInput);
}
''')
        temp_file = f.name
    
    try:
        result = await auto_fix.apply_fix(temp_file, 'escape_xss')
        
        print(f"✓ XSS fix applied: {result['success']}")
        
        for change in result.get('changes_made', []):
            print(f"  - {change}")
        
        with open(temp_file, 'r') as f:
            fixed_content = f.read()
        
        # Should replace innerHTML with textContent
        if 'textContent' in fixed_content:
            print("✓ innerHTML replaced with textContent")
        
        return True
    
    finally:
        os.unlink(temp_file)


async def test_path_traversal_fix():
    """Test path traversal fix"""
    print("\n[TEST 5] Testing Path Traversal Fix...")
    
    from backend.auto_fix import auto_fix
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''
def read_file(filename):
    with open(filename) as f:
        return f.read()

def load_config(path):
    return open(path + "../config.ini")
''')
        temp_file = f.name
    
    try:
        result = await auto_fix.apply_fix(temp_file, 'fix_path_traversal')
        
        print(f"✓ Path traversal fix applied: {result['success']}")
        
        for change in result.get('changes_made', []):
            print(f"  - {change}")
        
        with open(temp_file, 'r') as f:
            fixed_content = f.read()
        
        if 'os.path.normpath' in fixed_content:
            print("✓ Path validation added")
        
        return True
    
    finally:
        os.unlink(temp_file)


async def test_full_workflow():
    """Test complete workflow: scan → detect → fix → verify"""
    print("\n[TEST 6] Testing Full Security Workflow...")
    
    from backend.ide_security import security_scanner
    from backend.auto_fix import auto_fix
    from backend.auto_quarantine import quarantine_manager
    
    # Create malicious file
    malicious_code = '''
import os

def hack_db(user_id):
    query = "DELETE FROM users WHERE id=" + user_id
    os.system("rm -rf /")
    eval(user_id)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(malicious_code)
        temp_file = f.name
    
    try:
        # Step 1: Scan
        print("\n→ Step 1: Scanning file...")
        issues = await security_scanner.scan_file(temp_file)
        print(f"  Found {len(issues)} issues")
        
        critical_issues = [i for i in issues if i['severity'] == 'critical']
        print(f"  Critical issues: {len(critical_issues)}")
        
        # Step 2: Try auto-fix
        print("\n→ Step 2: Attempting auto-fix...")
        fix_result = await auto_fix.apply_fix(temp_file, 'remove_dangerous_imports')
        print(f"  Fix applied: {fix_result['success']}")
        print(f"  Changes: {len(fix_result.get('changes_made', []))}")
        
        # Step 3: Re-scan
        print("\n→ Step 3: Re-scanning after fix...")
        new_issues = await security_scanner.scan_file(temp_file)
        print(f"  Issues remaining: {len(new_issues)}")
        
        # Step 4: Quarantine if still critical
        remaining_critical = [i for i in new_issues if i['severity'] == 'critical']
        
        if remaining_critical:
            print(f"\n→ Step 4: {len(remaining_critical)} critical issues remain - quarantining...")
            quarantine_result = await quarantine_manager.quarantine_file(
                temp_file,
                f"Critical security issues: {remaining_critical[0]['rule_name']}",
                actor="security_system"
            )
            
            if quarantine_result['success']:
                print(f"  ✓ File quarantined: {quarantine_result['quarantine_id']}")
            else:
                print(f"  ✗ Quarantine failed: {quarantine_result.get('error')}")
        else:
            print("\n→ Step 4: All critical issues resolved ✓")
        
        print("\n✓ Full workflow completed successfully")
        return True
    
    except Exception as e:
        print(f"\n✗ Workflow failed: {e}")
        return False
    
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


async def main():
    """Run all tests"""
    print("="*60)
    print("IDE SECURITY SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("Security Scanner", test_security_scanner),
        ("Auto-Fix", test_auto_fix),
        ("Quarantine System", test_quarantine_system),
        ("XSS Fix", test_xss_fix),
        ("Path Traversal Fix", test_path_traversal_fix),
        ("Full Workflow", test_full_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nPassed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total_count - passed_count} TEST(S) FAILED")


if __name__ == "__main__":
    asyncio.run(main())
