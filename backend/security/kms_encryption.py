"""
KMS-Backed Encryption for Artifacts at Rest
"""
import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

from backend.config.environment import GraceEnvironment
from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)

class KMSEncryption:
    """KMS-backed encryption for artifacts at rest"""
    
    def __init__(self):
        self.master_key_id = os.getenv("GRACE_KMS_KEY_ID", "grace-master-key")
        self.key_cache = {}
        self.encryption_stats = {
            "artifacts_encrypted": 0,
            "artifacts_decrypted": 0,
            "key_rotations": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def encrypt_artifact(self, data: Any, domain: str, 
                             artifact_type: str, metadata: Dict = None) -> Dict[str, Any]:
        """Encrypt artifact with domain-specific key"""
        try:
            # Get or create domain key
            domain_key = await self._get_domain_key(domain)
            
            # Serialize data
            if isinstance(data, (dict, list)):
                plaintext = json.dumps(data, sort_keys=True).encode()
            elif isinstance(data, str):
                plaintext = data.encode()
            else:
                plaintext = str(data).encode()
            
            # Encrypt with Fernet
            fernet = Fernet(domain_key)
            encrypted_data = fernet.encrypt(plaintext)
            
            # Create encrypted artifact envelope
            artifact = {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "domain": domain,
                "artifact_type": artifact_type,
                "encryption_version": "v1",
                "key_id": f"{domain}_key",
                "encrypted_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
                "integrity_hash": self._calculate_integrity_hash(encrypted_data)
            }
            
            # Log encryption
            await immutable_log.append(
                actor="kms_encryption",
                action="artifact_encrypted",
                resource=f"{domain}/{artifact_type}",
                outcome="success",
                payload={
                    "domain": domain,
                    "artifact_type": artifact_type,
                    "size_bytes": len(plaintext)
                }
            )
            
            self.encryption_stats["artifacts_encrypted"] += 1
            return artifact
            
        except Exception as e:
            logger.error(f"Encryption failed for {domain}/{artifact_type}: {e}")
            raise
    
    async def decrypt_artifact(self, encrypted_artifact: Dict[str, Any]) -> Any:
        """Decrypt artifact using domain key"""
        try:
            domain = encrypted_artifact["domain"]
            artifact_type = encrypted_artifact["artifact_type"]
            
            # Get domain key
            domain_key = await self._get_domain_key(domain)
            
            # Verify integrity
            encrypted_data = base64.b64decode(encrypted_artifact["encrypted_data"])
            expected_hash = encrypted_artifact.get("integrity_hash")
            actual_hash = self._calculate_integrity_hash(encrypted_data)
            
            if expected_hash and expected_hash != actual_hash:
                raise ValueError("Integrity check failed - artifact may be corrupted")
            
            # Decrypt
            fernet = Fernet(domain_key)
            plaintext = fernet.decrypt(encrypted_data)
            
            # Deserialize
            try:
                data = json.loads(plaintext.decode())
            except json.JSONDecodeError:
                data = plaintext.decode()
            
            # Log decryption
            await immutable_log.append(
                actor="kms_encryption",
                action="artifact_decrypted",
                resource=f"{domain}/{artifact_type}",
                outcome="success"
            )
            
            self.encryption_stats["artifacts_decrypted"] += 1
            return data
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    async def _get_domain_key(self, domain: str) -> bytes:
        """Get or create domain-specific encryption key"""
        cache_key = f"{domain}_key"
        
        # Check cache first
        if cache_key in self.key_cache:
            self.encryption_stats["cache_hits"] += 1
            return self.key_cache[cache_key]
        
        self.encryption_stats["cache_misses"] += 1
        
        # In production, this would call AWS KMS or similar
        # For now, derive from master key + domain
        if GraceEnvironment.is_offline_mode():
            # Offline mode - use deterministic key derivation
            master_key = os.getenv("GRACE_MASTER_KEY", "default-master-key-for-testing")
            domain_salt = f"grace-domain-{domain}".encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=domain_salt,
                iterations=100000,
            )
            domain_key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        else:
            # Production mode - would integrate with real KMS
            domain_key = await self._kms_derive_key(domain)
        
        # Cache the key
        self.key_cache[cache_key] = domain_key
        
        return domain_key
    
    async def _kms_derive_key(self, domain: str) -> bytes:
        """Derive domain key from KMS (production implementation)"""
        # This would integrate with AWS KMS, Azure Key Vault, etc.
        # For demo, simulate KMS call
        await asyncio.sleep(0.01)  # Simulate network call
        
        # Generate deterministic key for demo
        key_material = f"{self.master_key_id}-{domain}-{datetime.utcnow().date()}"
        return base64.urlsafe_b64encode(hashlib.sha256(key_material.encode()).digest())
    
    def _calculate_integrity_hash(self, data: bytes) -> str:
        """Calculate SHA-256 integrity hash"""
        return hashlib.sha256(data).hexdigest()
    
    async def rotate_domain_key(self, domain: str):
        """Rotate encryption key for domain"""
        old_key = self.key_cache.get(f"{domain}_key")
        
        # Clear cache to force new key generation
        cache_key = f"{domain}_key"
        if cache_key in self.key_cache:
            del self.key_cache[cache_key]
        
        # Generate new key
        new_key = await self._get_domain_key(domain)
        
        # Log rotation
        await immutable_log.append(
            actor="kms_encryption",
            action="key_rotated",
            resource=f"domain/{domain}",
            outcome="success",
            payload={"domain": domain}
        )
        
        self.encryption_stats["key_rotations"] += 1
        logger.info(f"Rotated encryption key for domain: {domain}")
    
    def get_encryption_stats(self) -> Dict[str, int]:
        """Get encryption statistics"""
        return self.encryption_stats.copy()

# Global instance
kms_encryption = KMSEncryption()