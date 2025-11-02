"""Test IDE WebSocket Integration"""

import asyncio
import pytest
from backend.ide_websocket_handler import ide_ws_handler
from backend.models import async_session
from backend.verification import VerificationEnvelope
from backend.governance_models import AuditLog
from sqlalchemy import select

@pytest.mark.asyncio
async def test_file_open():
    """Test file open with verification"""
    from backend.sandbox_manager import sandbox_manager
    
    await sandbox_manager.write_file("test_user", "test_open.py", "print('hello')")
    
    message = {"type": "file_open", "path": "test_open.py"}
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] == "file_opened"
    assert result["path"] == "test_open.py"
    assert "hello" in result["content"]
    assert result["size"] > 0
    print("✓ Test file_open passed")

@pytest.mark.asyncio
async def test_file_save_with_verification():
    """Test file save with governance + verification"""
    
    message = {
        "type": "file_save",
        "path": "test_save.py",
        "content": "print('test save')"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] in ["file_saved", "file_save_pending"]
    
    if result["type"] == "file_saved":
        assert result["path"] == "test_save.py"
        assert "verified" in result
        assert "verification_id" in result
        print(f"✓ Test file_save passed - verified: {result['verified']}")
    else:
        print(f"✓ Test file_save passed - pending review")

@pytest.mark.asyncio
async def test_file_create():
    """Test file creation with governance"""
    
    message = {
        "type": "file_create",
        "path": "new_test.py",
        "content": "# New file"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] in ["file_created", "file_create_blocked"]
    
    if result["type"] == "file_created":
        assert result["path"] == "new_test.py"
        assert "verified" in result
        print("✓ Test file_create passed")
    else:
        print(f"✓ Test file_create blocked: {result['reason']}")

@pytest.mark.asyncio
async def test_directory_list():
    """Test directory listing"""
    
    message = {"type": "directory_list"}
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] == "directory_tree"
    assert "tree" in result
    assert "file_count" in result
    print(f"✓ Test directory_list passed - {result['file_count']} files")

@pytest.mark.asyncio
async def test_code_execute():
    """Test code execution with sandbox"""
    
    message = {
        "type": "code_execute",
        "language": "python",
        "code": "print('hello from test')"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] in ["execution_result", "execution_blocked"]
    
    if result["type"] == "execution_result":
        assert "stdout" in result
        assert "exit_code" in result
        assert "verified" in result
        print(f"✓ Test code_execute passed - exit code: {result['exit_code']}")
    else:
        print(f"✓ Test code_execute blocked: {result['reason']}")

@pytest.mark.asyncio
async def test_security_scan():
    """Test security scanning with Hunter"""
    from backend.sandbox_manager import sandbox_manager
    
    dangerous_code = """
import os
password = "hardcoded123"
os.system('rm -rf /')
eval(user_input)
    """
    
    await sandbox_manager.write_file("test_user", "dangerous.py", dangerous_code)
    
    message = {
        "type": "security_scan",
        "file_path": "dangerous.py"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] == "security_scan_result"
    assert "risk_score" in result
    assert "recommendation" in result
    print(f"✓ Test security_scan passed - risk score: {result['risk_score']}")

@pytest.mark.asyncio
async def test_auto_fix():
    """Test automated fixes"""
    from backend.sandbox_manager import sandbox_manager
    
    code_with_issue = 'password = "test123"'
    await sandbox_manager.write_file("test_user", "fixable.py", code_with_issue)
    
    message = {
        "type": "auto_fix",
        "file_path": "fixable.py",
        "issue": "hardcoded password"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] == "auto_fix_applied"
    assert result["verified"] is not None
    print("✓ Test auto_fix passed")

@pytest.mark.asyncio
async def test_auto_quarantine():
    """Test file quarantine"""
    from backend.sandbox_manager import sandbox_manager
    
    malicious_code = "import os; os.system('rm -rf /')"
    await sandbox_manager.write_file("test_user", "malicious.py", malicious_code)
    
    message = {
        "type": "auto_quarantine",
        "file_path": "malicious.py"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] in ["file_quarantined", "quarantine_blocked"]
    
    if result["type"] == "file_quarantined":
        assert "quarantine_path" in result
        assert "verified" in result
        print(f"✓ Test auto_quarantine passed - moved to {result['quarantine_path']}")
    else:
        print(f"✓ Test auto_quarantine blocked: {result['reason']}")

@pytest.mark.asyncio
async def test_file_rename():
    """Test file rename"""
    from backend.sandbox_manager import sandbox_manager
    
    await sandbox_manager.write_file("test_user", "old_name.py", "# test")
    
    message = {
        "type": "file_rename",
        "old_path": "old_name.py",
        "new_path": "new_name.py"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] in ["file_renamed", "file_rename_blocked"]
    
    if result["type"] == "file_renamed":
        assert result["new_path"] == "new_name.py"
        assert "verified" in result
        print("✓ Test file_rename passed")
    else:
        print(f"✓ Test file_rename blocked: {result['reason']}")

@pytest.mark.asyncio
async def test_file_delete():
    """Test file deletion"""
    from backend.sandbox_manager import sandbox_manager
    
    await sandbox_manager.write_file("test_user", "to_delete.py", "# delete me")
    
    message = {
        "type": "file_delete",
        "path": "to_delete.py"
    }
    result = await ide_ws_handler.handle_message("test_user", message)
    
    assert result["type"] in ["file_deleted", "file_delete_blocked", "file_delete_pending"]
    
    if result["type"] == "file_deleted":
        assert "verified" in result
        print("✓ Test file_delete passed")
    else:
        print(f"✓ Test file_delete status: {result.get('reason', 'pending')}")

async def run_all_tests():
    """Run all tests in sequence"""
    print("\n=== IDE WebSocket Integration Tests ===\n")
    
    tests = [
        test_file_open,
        test_file_save_with_verification,
        test_file_create,
        test_directory_list,
        test_code_execute,
        test_security_scan,
        test_auto_fix,
        test_auto_quarantine,
        test_file_rename,
        test_file_delete
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n=== Results: {passed} passed, {failed} failed ===\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
