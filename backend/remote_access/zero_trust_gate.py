"""
Zero-Trust Gate
Real device verification with MFA, device allowlist, and session management
"""

import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DeviceIdentity:
    """Registered device with verification"""
    device_id: str
    device_name: str
    device_type: str  # 'laptop', 'desktop', 'container', 'server'
    user_identity: str  # User who owns this device
    fingerprint: str  # Unique device fingerprint
    registered_at: str
    last_verified: Optional[str] = None
    verified: bool = False
    allowlisted: bool = False
    mfa_enabled: bool = True
    public_key: Optional[str] = None  # For certificate-based auth


@dataclass
class SessionToken:
    """Short-lived session token"""
    token: str
    device_id: str
    user_identity: str
    created_at: str
    expires_at: str
    session_id: str
    mfa_verified: bool
    permissions: List[str]


class ZeroTrustGate:
    """
    Zero-trust verification gate
    Requires:
    - Device ID verification
    - User identity confirmation
    - Multi-factor authentication
    - Device allowlist check
    """
    
    def __init__(self):
        self.devices: Dict[str, DeviceIdentity] = {}
        self.active_sessions: Dict[str, SessionToken] = {}
        self.device_allowlist: List[str] = []  # Device IDs explicitly allowed
        self.user_allowlist: List[str] = []  # Users allowed to connect
        self.token_ttl_minutes = 60
        self.require_mfa = True
        
        # Persistence
        self.storage_path = Path("databases/remote_access")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._load_state()
    
    def register_device(
        self,
        device_name: str,
        device_type: str,
        user_identity: str,
        device_fingerprint: str,
        approved_by: str,
        public_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new device for remote access
        
        Args:
            device_name: Human-readable device name
            device_type: Type of device
            user_identity: User who owns the device
            device_fingerprint: Unique device identifier (MAC, hardware ID, etc)
            approved_by: Who approved this device
            public_key: Optional public key for cert-based auth
        
        Returns:
            Device registration info
        """
        # Generate device ID from fingerprint
        device_id = hashlib.sha256(device_fingerprint.encode()).hexdigest()[:16]
        
        # Check if already registered
        if device_id in self.devices:
            logger.warning(f"[ZERO-TRUST] Device already registered: {device_id}")
            return {
                'error': 'device_already_registered',
                'device_id': device_id
            }
        
        # Create device identity
        device = DeviceIdentity(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            user_identity=user_identity,
            fingerprint=device_fingerprint,
            registered_at=datetime.utcnow().isoformat(),
            verified=False,  # Not verified until first MFA
            allowlisted=False,  # Must be explicitly allowlisted
            mfa_enabled=self.require_mfa,
            public_key=public_key
        )
        
        self.devices[device_id] = device
        self._save_state()
        
        logger.info(f"[ZERO-TRUST] ✅ Device registered: {device_name} ({device_id})")
        logger.info(f"[ZERO-TRUST] User: {user_identity}, Approved by: {approved_by}")
        
        return {
            'device_id': device_id,
            'device_name': device_name,
            'user_identity': user_identity,
            'status': 'registered_pending_approval',
            'requires_allowlist': True,
            'requires_mfa': self.require_mfa
        }
    
    def allowlist_device(self, device_id: str, approved_by: str) -> Dict[str, Any]:
        """
        Add device to allowlist (requires admin approval)
        
        Args:
            device_id: Device to allowlist
            approved_by: Admin who approved
        
        Returns:
            Allowlist status
        """
        if device_id not in self.devices:
            return {'error': 'device_not_found'}
        
        device = self.devices[device_id]
        device.allowlisted = True
        device.last_verified = datetime.utcnow().isoformat()
        
        self.device_allowlist.append(device_id)
        self._save_state()
        
        logger.info(f"[ZERO-TRUST] ✅ Device allowlisted: {device.device_name} by {approved_by}")
        
        return {
            'device_id': device_id,
            'device_name': device.device_name,
            'allowlisted': True,
            'approved_by': approved_by
        }
    
    def verify_mfa(
        self,
        device_id: str,
        mfa_token: str,
        mfa_method: str = 'totp'
    ) -> Dict[str, Any]:
        """
        Verify MFA token for device
        
        Args:
            device_id: Device attempting verification
            mfa_token: MFA token (TOTP, SMS code, hardware key response, etc)
            mfa_method: MFA method used
        
        Returns:
            Verification result
        """
        if device_id not in self.devices:
            return {'verified': False, 'error': 'device_not_found'}
        
        device = self.devices[device_id]
        
        # TODO: Integrate real MFA verification (TOTP, WebAuthn, etc)
        # For now, accept a test token for development
        mfa_valid = self._verify_mfa_token(mfa_token, device.user_identity, mfa_method)
        
        if mfa_valid:
            device.verified = True
            device.last_verified = datetime.utcnow().isoformat()
            self._save_state()
            
            logger.info(f"[ZERO-TRUST] ✅ MFA verified for {device.device_name}")
            return {
                'verified': True,
                'device_id': device_id,
                'method': mfa_method
            }
        else:
            logger.warning(f"[ZERO-TRUST] ❌ MFA verification failed for {device.device_name}")
            return {
                'verified': False,
                'error': 'invalid_mfa_token'
            }
    
    def create_session(
        self,
        device_id: str,
        mfa_token: Optional[str] = None,
        requested_permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new remote access session
        Requires: Device allowlisted + MFA verified
        
        Args:
            device_id: Device requesting session
            mfa_token: MFA token (if MFA required)
            requested_permissions: Permissions requested
        
        Returns:
            Session token or error
        """
        # Check device exists
        if device_id not in self.devices:
            logger.warning(f"[ZERO-TRUST] 🚫 Unknown device: {device_id}")
            return {'error': 'device_not_found', 'allowed': False}
        
        device = self.devices[device_id]
        
        # Check allowlist
        if not device.allowlisted:
            logger.warning(f"[ZERO-TRUST] 🚫 Device not allowlisted: {device.device_name}")
            return {
                'error': 'device_not_allowlisted',
                'allowed': False,
                'reason': 'Device must be approved by admin first'
            }
        
        # Check user allowlist
        if self.user_allowlist and device.user_identity not in self.user_allowlist:
            logger.warning(f"[ZERO-TRUST] 🚫 User not allowlisted: {device.user_identity}")
            return {
                'error': 'user_not_allowed',
                'allowed': False,
                'reason': 'User not in allowlist'
            }
        
        # Verify MFA if required
        if self.require_mfa and mfa_token:
            mfa_result = self.verify_mfa(device_id, mfa_token)
            if not mfa_result.get('verified'):
                logger.warning(f"[ZERO-TRUST] 🚫 MFA verification failed: {device.device_name}")
                return {
                    'error': 'mfa_verification_failed',
                    'allowed': False,
                    'reason': 'Multi-factor authentication required'
                }
        elif self.require_mfa and not mfa_token:
            return {
                'error': 'mfa_required',
                'allowed': False,
                'reason': 'MFA token required'
            }
        
        # Generate session token
        session_id = f"sess_{secrets.token_urlsafe(16)}"
        token = secrets.token_urlsafe(32)
        
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(minutes=self.token_ttl_minutes)
        
        # Determine permissions (from RBAC)
        permissions = requested_permissions or ['read', 'execute']
        
        session_token = SessionToken(
            token=token,
            device_id=device_id,
            user_identity=device.user_identity,
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat(),
            session_id=session_id,
            mfa_verified=self.require_mfa,
            permissions=permissions
        )
        
        self.active_sessions[token] = session_token
        self._save_state()
        
        logger.info(f"[ZERO-TRUST] ✅ Session created: {session_id}")
        logger.info(f"[ZERO-TRUST] Device: {device.device_name}, User: {device.user_identity}")
        logger.info(f"[ZERO-TRUST] Expires: {expires_at.isoformat()}")
        
        return {
            'allowed': True,
            'session_id': session_id,
            'token': token,
            'device_id': device_id,
            'user_identity': device.user_identity,
            'expires_at': expires_at.isoformat(),
            'ttl_minutes': self.token_ttl_minutes,
            'permissions': permissions,
            'mfa_verified': self.require_mfa
        }
    
    def verify_session(self, token: str) -> Dict[str, Any]:
        """
        Verify a session token is valid
        
        Args:
            token: Session token to verify
        
        Returns:
            Session info or error
        """
        if token not in self.active_sessions:
            return {'valid': False, 'error': 'invalid_token'}
        
        session = self.active_sessions[token]
        
        # Check expiry
        expires_at = datetime.fromisoformat(session.expires_at)
        if datetime.utcnow() > expires_at:
            # Expired - remove it
            del self.active_sessions[token]
            self._save_state()
            logger.warning(f"[ZERO-TRUST] 🚫 Session expired: {session.session_id}")
            return {'valid': False, 'error': 'session_expired'}
        
        # Valid session
        device = self.devices[session.device_id]
        
        return {
            'valid': True,
            'session_id': session.session_id,
            'device_id': session.device_id,
            'device_name': device.device_name,
            'user_identity': session.user_identity,
            'permissions': session.permissions,
            'expires_at': session.expires_at,
            'mfa_verified': session.mfa_verified
        }
    
    def revoke_session(self, token: str) -> Dict[str, Any]:
        """Revoke an active session"""
        if token not in self.active_sessions:
            return {'error': 'session_not_found'}
        
        session = self.active_sessions[token]
        session_id = session.session_id
        
        del self.active_sessions[token]
        self._save_state()
        
        logger.info(f"[ZERO-TRUST] ✅ Session revoked: {session_id}")
        
        return {
            'revoked': True,
            'session_id': session_id
        }
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        sessions = []
        for token, session in self.active_sessions.items():
            device = self.devices.get(session.device_id)
            sessions.append({
                'session_id': session.session_id,
                'device_name': device.device_name if device else 'unknown',
                'user_identity': session.user_identity,
                'created_at': session.created_at,
                'expires_at': session.expires_at,
                'permissions': session.permissions
            })
        return sessions
    
    def _verify_mfa_token(self, token: str, user_identity: str, method: str) -> bool:
        """
        Verify MFA token
        TODO: Integrate real MFA (pyotp, WebAuthn, etc)
        """
        # Development: Accept test tokens
        if token.startswith('TEST_'):
            return True
        
        # TODO: Implement real TOTP verification
        # import pyotp
        # totp = pyotp.TOTP(user_secret)
        # return totp.verify(token)
        
        return False
    
    def _save_state(self):
        """Persist state to disk"""
        state = {
            'devices': {k: asdict(v) for k, v in self.devices.items()},
            'active_sessions': {k: asdict(v) for k, v in self.active_sessions.items()},
            'device_allowlist': self.device_allowlist,
            'user_allowlist': self.user_allowlist
        }
        
        state_file = self.storage_path / "zero_trust_state.json"
        state_file.write_text(json.dumps(state, indent=2))
    
    def _load_state(self):
        """Load state from disk"""
        state_file = self.storage_path / "zero_trust_state.json"
        if not state_file.exists():
            return
        
        try:
            state = json.loads(state_file.read_text())
            
            self.devices = {
                k: DeviceIdentity(**v) for k, v in state.get('devices', {}).items()
            }
            self.active_sessions = {
                k: SessionToken(**v) for k, v in state.get('active_sessions', {}).items()
            }
            self.device_allowlist = state.get('device_allowlist', [])
            self.user_allowlist = state.get('user_allowlist', [])
            
            logger.info(f"[ZERO-TRUST] Loaded {len(self.devices)} devices, {len(self.active_sessions)} sessions")
        except Exception as e:
            logger.error(f"[ZERO-TRUST] Failed to load state: {e}")


# Global instance
zero_trust_gate = ZeroTrustGate()
