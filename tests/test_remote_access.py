"""
Remote Access System Tests
Tests zero-trust gate, RBAC, session management, and recording
"""

import pytest
import asyncio
from backend.remote_access.zero_trust_gate import ZeroTrustGate
from backend.remote_access.rbac_enforcer import RBACEnforcer
from backend.remote_access.remote_session_manager import RemoteSessionManager
from backend.remote_access.session_recorder import SessionRecorder


@pytest.fixture
def zero_trust():
    """Fresh zero-trust instance"""
    zt = ZeroTrustGate()
    zt.devices = {}
    zt.active_sessions = {}
    zt.device_allowlist = []
    zt.user_allowlist = ['aaron', 'test_user']
    return zt


@pytest.fixture
def rbac():
    """Fresh RBAC instance"""
    rbac = RBACEnforcer()
    rbac.device_roles = {}
    return rbac


@pytest.fixture
def session_manager():
    """Fresh session manager"""
    return RemoteSessionManager()


@pytest.fixture
def session_recorder():
    """Fresh session recorder"""
    return SessionRecorder()


class TestZeroTrustGate:
    """Test zero-trust authentication"""
    
    def test_register_device(self, zero_trust):
        """Test device registration"""
        result = zero_trust.register_device(
            device_name="test_laptop",
            device_type="laptop",
            user_identity="aaron",
            device_fingerprint="AA:BB:CC:DD:EE:FF",
            approved_by="admin"
        )
        
        assert 'device_id' in result
        assert result['status'] == 'registered_pending_approval'
        assert result['requires_allowlist'] == True
    
    def test_allowlist_device(self, zero_trust):
        """Test device allowlisting"""
        # Register first
        reg_result = zero_trust.register_device(
            device_name="test_laptop",
            device_type="laptop",
            user_identity="aaron",
            device_fingerprint="AA:BB:CC:DD:EE:FF",
            approved_by="admin"
        )
        
        device_id = reg_result['device_id']
        
        # Allowlist
        result = zero_trust.allowlist_device(device_id, "admin")
        
        assert result['allowlisted'] == True
        assert device_id in zero_trust.device_allowlist
    
    def test_mfa_verification(self, zero_trust):
        """Test MFA verification"""
        # Register device
        reg_result = zero_trust.register_device(
            device_name="test_laptop",
            device_type="laptop",
            user_identity="aaron",
            device_fingerprint="AA:BB:CC:DD:EE:FF",
            approved_by="admin"
        )
        
        device_id = reg_result['device_id']
        
        # Verify MFA with test token
        result = zero_trust.verify_mfa(device_id, "TEST_123456")
        
        assert result['verified'] == True
    
    def test_create_session_success(self, zero_trust):
        """Test successful session creation"""
        # Register and allowlist device
        reg_result = zero_trust.register_device(
            device_name="test_laptop",
            device_type="laptop",
            user_identity="aaron",
            device_fingerprint="AA:BB:CC:DD:EE:FF",
            approved_by="admin"
        )
        
        device_id = reg_result['device_id']
        zero_trust.allowlist_device(device_id, "admin")
        
        # Create session
        result = zero_trust.create_session(
            device_id=device_id,
            mfa_token="TEST_123456"
        )
        
        assert result['allowed'] == True
        assert 'token' in result
        assert 'session_id' in result
        assert result['mfa_verified'] == True
    
    def test_create_session_not_allowlisted(self, zero_trust):
        """Test session creation fails without allowlist"""
        # Register but don't allowlist
        reg_result = zero_trust.register_device(
            device_name="test_laptop",
            device_type="laptop",
            user_identity="aaron",
            device_fingerprint="AA:BB:CC:DD:EE:FF",
            approved_by="admin"
        )
        
        device_id = reg_result['device_id']
        
        # Try to create session
        result = zero_trust.create_session(
            device_id=device_id,
            mfa_token="TEST_123456"
        )
        
        assert result['allowed'] == False
        assert result['error'] == 'device_not_allowlisted'
    
    def test_verify_session_valid(self, zero_trust):
        """Test valid session verification"""
        # Create session
        reg_result = zero_trust.register_device(
            device_name="test_laptop",
            device_type="laptop",
            user_identity="aaron",
            device_fingerprint="AA:BB:CC:DD:EE:FF",
            approved_by="admin"
        )
        
        device_id = reg_result['device_id']
        zero_trust.allowlist_device(device_id, "admin")
        
        session_result = zero_trust.create_session(
            device_id=device_id,
            mfa_token="TEST_123456"
        )
        
        token = session_result['token']
        
        # Verify token
        result = zero_trust.verify_session(token)
        
        assert result['valid'] == True
        assert result['device_id'] == device_id
    
    def test_verify_session_invalid(self, zero_trust):
        """Test invalid session verification"""
        result = zero_trust.verify_session("invalid_token")
        
        assert result['valid'] == False
        assert result['error'] == 'invalid_token'


class TestRBAC:
    """Test RBAC enforcement"""
    
    def test_assign_role(self, rbac):
        """Test role assignment"""
        result = rbac.assign_role("device_123", "developer", "admin")
        
        assert result['role'] == 'developer'
        assert 'read_code' in result['permissions']
        assert 'write_code' in result['permissions']
    
    def test_check_permission_allowed(self, rbac):
        """Test permission check - allowed"""
        rbac.assign_role("device_123", "developer", "admin")
        
        result = rbac.check_permission("device_123", "execute", "test.py")
        
        assert result['allowed'] == True
    
    def test_check_permission_denied(self, rbac):
        """Test permission check - denied"""
        rbac.assign_role("device_123", "observer", "admin")
        
        result = rbac.check_permission("device_123", "execute", "test.py")
        
        assert result['allowed'] == False
        assert result['reason'] == 'insufficient_permissions'
    
    def test_blocked_permission(self, rbac):
        """Test globally blocked permission"""
        rbac.assign_role("device_123", "admin", "admin")
        
        result = rbac.check_permission("device_123", "sudo_escalation", "system")
        
        assert result['allowed'] == False
        assert result['reason'] == 'action_globally_blocked'
    
    def test_list_roles(self, rbac):
        """Test listing roles"""
        roles = rbac.list_roles()
        
        assert len(roles) > 0
        role_names = [r['name'] for r in roles]
        assert 'observer' in role_names
        assert 'developer' in role_names
        assert 'admin' in role_names


@pytest.mark.asyncio
class TestSessionRecorder:
    """Test session recording"""
    
    async def test_start_recording(self, session_recorder):
        """Test start recording"""
        await session_recorder.start()
        
        recording_id = await session_recorder.start_recording(
            session_id="sess_123",
            device_id="device_123",
            device_name="test_laptop"
        )
        
        assert recording_id.startswith("rec_")
        assert recording_id in session_recorder.active_recordings
    
    async def test_record_command(self, session_recorder):
        """Test recording command"""
        await session_recorder.start()
        
        recording_id = await session_recorder.start_recording(
            session_id="sess_123",
            device_id="device_123",
            device_name="test_laptop"
        )
        
        await session_recorder.record_command(
            recording_id=recording_id,
            command="ls -la",
            output="total 100\ndrwxr-xr-x ...",
            exit_code=0,
            execution_time_ms=50.0
        )
        
        recording = session_recorder.active_recordings[recording_id]
        assert len(recording['commands']) == 1
        assert recording['commands'][0]['command'] == "ls -la"
    
    async def test_suspicious_command_detection(self, session_recorder):
        """Test suspicious command detection"""
        await session_recorder.start()
        
        recording_id = await session_recorder.start_recording(
            session_id="sess_123",
            device_id="device_123",
            device_name="test_laptop"
        )
        
        await session_recorder.record_command(
            recording_id=recording_id,
            command="rm -rf /",
            output="",
            exit_code=0,
            execution_time_ms=10.0
        )
        
        recording = session_recorder.active_recordings[recording_id]
        assert len(recording['suspicious_activity']) > 0


@pytest.mark.asyncio
class TestSessionManager:
    """Test session management"""
    
    async def test_execute_command(self, session_manager, zero_trust, rbac):
        """Test command execution"""
        # Setup: Register device, create session
        reg_result = zero_trust.register_device(
            device_name="test_laptop",
            device_type="laptop",
            user_identity="aaron",
            device_fingerprint="AA:BB:CC:DD:EE:FF",
            approved_by="admin"
        )
        
        device_id = reg_result['device_id']
        zero_trust.allowlist_device(device_id, "admin")
        rbac.assign_role(device_id, "developer", "admin")
        
        session_result = zero_trust.create_session(
            device_id=device_id,
            mfa_token="TEST_123456"
        )
        
        token = session_result['token']
        
        # Create session in manager
        await session_manager.create_session(token)
        
        session_id = session_result['session_id']
        
        # Execute command
        result = await session_manager.execute_command(
            session_id=session_id,
            command="echo 'Hello World'",
            timeout=5
        )
        
        assert result.get('success') == True
        assert 'Hello World' in result.get('stdout', '')


def test_integration_full_flow():
    """Test full remote access flow"""
    # This tests the complete workflow
    zt = ZeroTrustGate()
    zt.devices = {}
    zt.active_sessions = {}
    zt.user_allowlist = ['aaron']
    
    rbac = RBACEnforcer()
    rbac.device_roles = {}
    
    print("\n[TEST] Full Remote Access Flow")
    
    # Step 1: Register device
    print("[1] Registering device...")
    reg_result = zt.register_device(
        device_name="aaron_laptop",
        device_type="laptop",
        user_identity="aaron",
        device_fingerprint="AA:BB:CC:DD:EE:FF:00",
        approved_by="admin"
    )
    assert 'device_id' in reg_result
    device_id = reg_result['device_id']
    print(f"    ✅ Device registered: {device_id}")
    
    # Step 2: Allowlist device
    print("[2] Allowlisting device...")
    allowlist_result = zt.allowlist_device(device_id, "admin")
    assert allowlist_result['allowlisted'] == True
    print(f"    ✅ Device allowlisted")
    
    # Step 3: Assign role
    print("[3] Assigning RBAC role...")
    role_result = rbac.assign_role(device_id, "developer", "admin")
    assert role_result['role'] == 'developer'
    print(f"    ✅ Role assigned: developer")
    
    # Step 4: Create session
    print("[4] Creating session...")
    session_result = zt.create_session(
        device_id=device_id,
        mfa_token="TEST_123456"
    )
    assert session_result['allowed'] == True
    token = session_result['token']
    print(f"    ✅ Session created: {session_result['session_id']}")
    
    # Step 5: Verify session
    print("[5] Verifying session...")
    verify_result = zt.verify_session(token)
    assert verify_result['valid'] == True
    print(f"    ✅ Session valid")
    
    # Step 6: Check permission
    print("[6] Checking permissions...")
    perm_result = rbac.check_permission(device_id, "execute", "test.py")
    assert perm_result['allowed'] == True
    print(f"    ✅ Permission granted")
    
    print("\n✅ Full flow successful!")


if __name__ == "__main__":
    # Run integration test
    test_integration_full_flow()
    
    print("\nRun full test suite with: pytest tests/test_remote_access.py -v")
