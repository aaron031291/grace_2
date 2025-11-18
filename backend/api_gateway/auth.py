"""
Authentication - API Key and JWT authentication
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pydantic import BaseModel


class APIKey(BaseModel):
    """API Key model"""
    key_id: str
    key_hash: str
    tenant_id: str
    name: str
    scopes: list[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True


class APIKeyAuth:
    """API Key authentication and management"""
    
    def __init__(self):
        self.keys: dict[str, APIKey] = {}  # key_id -> APIKey
        self.key_hashes: dict[str, str] = {}  # key_hash -> key_id
    
    def generate_key(
        self,
        tenant_id: str,
        name: str,
        scopes: list[str],
        expires_in_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """
        Generate a new API key.
        Returns (raw_key, api_key_object)
        """
        raw_key = f"grace_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(raw_key)
        key_id = f"key_{secrets.token_urlsafe(16)}"
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            tenant_id=tenant_id,
            name=name,
            scopes=scopes,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        self.keys[key_id] = api_key
        self.key_hashes[key_hash] = key_id
        
        return raw_key, api_key
    
    def validate_key(self, raw_key: str) -> Optional[APIKey]:
        """Validate API key and return associated data"""
        key_hash = self._hash_key(raw_key)
        key_id = self.key_hashes.get(key_hash)
        
        if not key_id:
            return None
        
        api_key = self.keys.get(key_id)
        if not api_key:
            return None
        
        if not api_key.is_active:
            return None
        
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            return None
        
        api_key.last_used_at = datetime.utcnow()
        
        return api_key
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        if key_id in self.keys:
            self.keys[key_id].is_active = False
            return True
        return False
    
    def list_keys(self, tenant_id: str) -> list[APIKey]:
        """List all keys for a tenant"""
        return [
            key for key in self.keys.values()
            if key.tenant_id == tenant_id
        ]
    
    @staticmethod
    def _hash_key(raw_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(raw_key.encode()).hexdigest()


class JWTAuth:
    """JWT authentication"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(
        self,
        tenant_id: str,
        user_id: str,
        scopes: list[str],
        expires_in_minutes: int = 60
    ) -> str:
        """Create JWT token"""
        payload = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "scopes": scopes,
            "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_token(self, token: str) -> Optional[dict]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
