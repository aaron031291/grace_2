"""
Crypto Key Manager
Centralized cryptographic key generation, signing, and verification

Features:
- Ed25519 key generation for all components
- Automatic key rotation
- Signature generation and verification
- Integration with immutable log
- Integration with trigger mesh
- Component registry
- Mission Control integration
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
import base64
import hashlib
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization

from backend.models.base_models import async_session
from backend.logging.immutable_log import immutable_log
from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent

logger = logging.getLogger(__name__)


@dataclass
class CryptoKey:
    """Cryptographic key pair"""
    key_id: str
    component_id: str
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    created_at: datetime
    expires_at: Optional[datetime] = None
    rotated: bool = False
    
    def sign(self, data: str) -> str:
        """Sign data with Ed25519"""
        data_bytes = data.encode('utf-8')
        signature = self.private_key.sign(data_bytes)
        return base64.b64encode(signature).decode('utf-8')
    
    def verify(self, data: str, signature: str) -> bool:
        """Verify Ed25519 signature"""
        try:
            data_bytes = data.encode('utf-8')
            sig_bytes = base64.b64decode(signature)
            self.public_key.verify(sig_bytes, data_bytes)
            return True
        except Exception:
            return False
    
    def get_public_key_pem(self) -> str:
        """Get public key in PEM format"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def get_private_key_pem(self) -> str:
        """Get private key in PEM format"""
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')


@dataclass
class SignedMessage:
    """A cryptographically signed message"""
    message: Dict[str, Any]
    signature: str
    key_id: str
    component_id: str
    signed_at: datetime
    verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message": self.message,
            "signature": self.signature,
            "key_id": self.key_id,
            "component_id": self.component_id,
            "signed_at": self.signed_at.isoformat(),
            "verified": self.verified
        }


class CryptoKeyManager:
    """
    Centralized cryptographic key management
    
    Manages Ed25519 keys for all Grace components with:
    - Automatic key generation
    - Key rotation
    - Signature generation/verification
    - Immutable log integration
    - Trigger mesh integration
    """
    
    def __init__(self):
        self.running = False
        
        # Key storage
        self.keys: Dict[str, CryptoKey] = {}  # key_id -> CryptoKey
        self.component_keys: Dict[str, str] = {}  # component_id -> key_id
        
        # Public key registry (for verification)
        self.public_keys: Dict[str, Ed25519PublicKey] = {}  # key_id -> public_key
        
        # Key rotation settings
        self.key_lifetime_days = 90  # Rotate keys every 90 days
        self.auto_rotate = True
        
        # Statistics
        self.signatures_generated = 0
        self.signatures_verified = 0
        self.verification_failures = 0
    
    async def start(self):
        """Start crypto key manager"""
        if self.running:
            return
        
        self.running = True
        
        logger.info("=" * 80)
        logger.info("CRYPTO KEY MANAGER - STARTING")
        logger.info("=" * 80)
        
        # Load existing keys from database
        await self._load_keys_from_database()
        logger.info(f"[CRYPTO] Loaded {len(self.keys)} existing keys")
        
        # Start key rotation monitor
        if self.auto_rotate:
            asyncio.create_task(self._key_rotation_loop())
        
        logger.info("[CRYPTO] ✅ Crypto Key Manager OPERATIONAL")
        logger.info("=" * 80)
        
        # Log to immutable log
        await immutable_log.append(
            actor="crypto_key_manager",
            action="system_start",
            resource="crypto_keys",
            subsystem="crypto",
            payload={"keys_loaded": len(self.keys)},
            result="started"
        )
    
    async def stop(self):
        """Stop crypto key manager"""
        self.running = False
        logger.info("[CRYPTO] Crypto Key Manager stopped")
    
    async def generate_key_for_component(
        self,
        component_id: str,
        force_new: bool = False
    ) -> CryptoKey:
        """
        Generate Ed25519 key pair for a component
        
        Args:
            component_id: Component identifier
            force_new: Force generation of new key even if one exists
        
        Returns:
            CryptoKey instance
        """
        # Check if component already has a key
        if not force_new and component_id in self.component_keys:
            key_id = self.component_keys[component_id]
            existing_key = self.keys.get(key_id)
            if existing_key and not existing_key.rotated:
                logger.info(f"[CRYPTO] Component {component_id} already has key: {key_id}")
                return existing_key
        
        # Generate new Ed25519 key pair
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Create key ID
        key_id = f"key_{component_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.key_lifetime_days)
        
        # Create CryptoKey
        crypto_key = CryptoKey(
            key_id=key_id,
            component_id=component_id,
            private_key=private_key,
            public_key=public_key,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        
        # Store key
        self.keys[key_id] = crypto_key
        self.component_keys[component_id] = key_id
        self.public_keys[key_id] = public_key
        
        # Save to database
        await self._save_key_to_database(crypto_key)
        
        # Log to immutable log
        await immutable_log.append(
            actor="crypto_key_manager",
            action="key_generated",
            resource=component_id,
            subsystem="crypto",
            payload={
                "key_id": key_id,
                "component_id": component_id,
                "expires_at": expires_at.isoformat()
            },
            result="generated"
        )
        
        # Publish event
        await trigger_mesh.publish(TriggerEvent(
            event_type="crypto.key_generated",
            source="crypto_key_manager",
            actor="crypto_key_manager",
            resource=component_id,
            payload={
                "key_id": key_id,
                "component_id": component_id,
                "public_key_pem": crypto_key.get_public_key_pem()
            }
        ))
        
        logger.info(f"[CRYPTO] Generated key for {component_id}: {key_id}")
        
        return crypto_key
    
    async def sign_message(
        self,
        component_id: str,
        message: Dict[str, Any]
    ) -> SignedMessage:
        """
        Sign a message with component's key
        
        Args:
            component_id: Component identifier
            message: Message to sign
        
        Returns:
            SignedMessage instance
        """
        # Get or generate key for component
        if component_id not in self.component_keys:
            await self.generate_key_for_component(component_id)
        
        key_id = self.component_keys[component_id]
        crypto_key = self.keys[key_id]
        
        # Serialize message
        message_json = json.dumps(message, sort_keys=True)
        
        # Sign message
        signature = crypto_key.sign(message_json)
        
        # Create signed message
        signed_message = SignedMessage(
            message=message,
            signature=signature,
            key_id=key_id,
            component_id=component_id,
            signed_at=datetime.now(timezone.utc)
        )
        
        self.signatures_generated += 1
        
        logger.debug(f"[CRYPTO] Signed message for {component_id}")
        
        return signed_message
    
    async def verify_message(
        self,
        signed_message: SignedMessage
    ) -> bool:
        """
        Verify a signed message
        
        Args:
            signed_message: SignedMessage to verify
        
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Get public key
            key_id = signed_message.key_id
            public_key = self.public_keys.get(key_id)
            
            if not public_key:
                logger.warning(f"[CRYPTO] Unknown key ID: {key_id}")
                self.verification_failures += 1
                return False
            
            # Serialize message
            message_json = json.dumps(signed_message.message, sort_keys=True)
            
            # Verify signature
            data_bytes = message_json.encode('utf-8')
            sig_bytes = base64.b64decode(signed_message.signature)
            
            public_key.verify(sig_bytes, data_bytes)
            
            signed_message.verified = True
            self.signatures_verified += 1
            
            logger.debug(f"[CRYPTO] Verified message from {signed_message.component_id}")
            
            return True
            
        except Exception as e:
            logger.warning(f"[CRYPTO] Verification failed: {e}")
            self.verification_failures += 1
            return False
    
    async def rotate_key(self, component_id: str) -> CryptoKey:
        """
        Rotate key for a component
        
        Args:
            component_id: Component identifier
        
        Returns:
            New CryptoKey instance
        """
        # Mark old key as rotated
        if component_id in self.component_keys:
            old_key_id = self.component_keys[component_id]
            old_key = self.keys.get(old_key_id)
            if old_key:
                old_key.rotated = True
        
        # Generate new key
        new_key = await self.generate_key_for_component(component_id, force_new=True)
        
        logger.info(f"[CRYPTO] Rotated key for {component_id}: {new_key.key_id}")
        
        # Log rotation to immutable log
        old_key_id = self.component_keys.get(component_id, "none")
        await immutable_log.append(
            actor="crypto_key_manager",
            action="key_rotated",
            resource=component_id,
            subsystem="crypto",
            payload={
                "old_key_id": old_key_id,
                "new_key_id": new_key.key_id,
                "component_id": component_id,
                "rotation_reason": "scheduled_rotation"
            },
            result="rotated"
        )
        
        return new_key
    
    async def _key_rotation_loop(self):
        """Monitor and rotate expiring keys"""
        while self.running:
            try:
                now = datetime.now(timezone.utc)
                
                for key_id, crypto_key in list(self.keys.items()):
                    if crypto_key.rotated:
                        continue
                    
                    # Fix: Ensure both datetimes are timezone-aware
                    expires_at = crypto_key.expires_at
                    if expires_at:
                        # If expires_at is naive, make it UTC-aware
                        if expires_at.tzinfo is None:
                            from datetime import timezone as dt_timezone
                            expires_at = expires_at.replace(tzinfo=dt_timezone.utc)
                        
                        if expires_at <= now:
                            logger.info(f"[CRYPTO] Key expired: {key_id}, rotating...")
                            await self.rotate_key(crypto_key.component_id)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CRYPTO] Error in key rotation loop: {e}", exc_info=True)
                await asyncio.sleep(3600)
    
    async def _load_keys_from_database(self):
        """Load existing keys from database - IMPLEMENTED"""
        try:
            from backend.models.crypto_models import CryptoKeyStore, ComponentCryptoIdentity
            from backend.models.base_models import async_session
            from sqlalchemy import select
            
            async with async_session() as session:
                # Load all active keys
                result = await session.execute(
                    select(CryptoKeyStore)
                    .where(CryptoKeyStore.is_active == True)
                    .where(CryptoKeyStore.is_rotated == False)
                )
                key_records = result.scalars().all()
                
                for record in key_records:
                    try:
                        # Decrypt and load private key
                        private_key_pem = self._decrypt_key(record.private_key_encrypted)
                        private_key = serialization.load_pem_private_key(
                            private_key_pem.encode('utf-8'),
                            password=None
                        )
                        
                        # Load public key
                        public_key = serialization.load_pem_public_key(
                            record.public_key_pem.encode('utf-8')
                        )
                        
                        # Ensure datetimes are timezone-aware
                        created_at = record.created_at
                        if created_at and created_at.tzinfo is None:
                            created_at = created_at.replace(tzinfo=timezone.utc)
                        
                        expires_at = record.expires_at
                        if expires_at and expires_at.tzinfo is None:
                            expires_at = expires_at.replace(tzinfo=timezone.utc)
                        
                        # Reconstruct CryptoKey object
                        crypto_key = CryptoKey(
                            key_id=record.key_id,
                            component_id=record.component_id,
                            private_key=private_key,
                            public_key=public_key,
                            created_at=created_at,
                            expires_at=expires_at,
                            rotated=record.is_rotated
                        )
                        
                        # Store in memory
                        self.keys[record.key_id] = crypto_key
                        self.component_keys[record.component_id] = record.key_id  # Store key_id, not object
                        
                        logger.info(f"[CRYPTO] Loaded key {record.key_id} for {record.component_id}")
                        
                    except Exception as e:
                        logger.error(f"[CRYPTO] Failed to load key {record.key_id}: {e}")
                
                logger.info(f"[CRYPTO] Loaded {len(key_records)} keys from database")
        
        except Exception as e:
            logger.warning(f"[CRYPTO] Database load failed (tables may not exist yet): {e}")
    
    async def _save_key_to_database(self, crypto_key: CryptoKey):
        """Save key to database with encryption - IMPLEMENTED"""
        try:
            from backend.models.crypto_models import CryptoKeyStore, ComponentCryptoIdentity
            from backend.models.base_models import async_session
            
            # Encrypt private key before storage
            private_key_pem = crypto_key.get_private_key_pem()
            encrypted_private_key = self._encrypt_key(private_key_pem)
            
            # Get public key PEM
            public_key_pem = crypto_key.get_public_key_pem()
            
            async with async_session() as session:
                # Save key store entry
                key_store = CryptoKeyStore(
                    key_id=crypto_key.key_id,
                    component_id=crypto_key.component_id,
                    key_type="ed25519",
                    private_key_encrypted=encrypted_private_key,
                    public_key_pem=public_key_pem,
                    encryption_algorithm="fernet",
                    key_derivation="master_key",
                    created_at=crypto_key.created_at,
                    expires_at=crypto_key.expires_at,
                    is_active=True,
                    is_rotated=crypto_key.rotated,
                    purpose="signing",
                    created_by="crypto_key_manager",
                    use_count=0
                )
                session.add(key_store)
                
                # Save to component identity registry
                identity_hash = hashlib.sha256(public_key_pem.encode()).hexdigest()
                
                identity = ComponentCryptoIdentity(
                    component_id=crypto_key.component_id,
                    current_key_id=crypto_key.key_id,
                    public_key_pem=public_key_pem,
                    identity_hash=identity_hash,
                    verified=True,
                    component_type="kernel",  # Could be enhanced
                    registered_at=crypto_key.created_at,
                    is_active=True,
                    total_signatures=0
                )
                session.add(identity)
                
                await session.commit()
                
                logger.info(f"[CRYPTO] Saved key {crypto_key.key_id} to database")
        
        except Exception as e:
            logger.error(f"[CRYPTO] Failed to save key to database: {e}")
    
    def _encrypt_key(self, key_pem: str) -> str:
        """Encrypt private key using Fernet (symmetric encryption)"""
        try:
            from cryptography.fernet import Fernet
            import os
            
            # Get or create master encryption key
            master_key = self._get_master_key()
            f = Fernet(master_key)
            
            # Encrypt the PEM
            encrypted = f.encrypt(key_pem.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        
        except Exception as e:
            logger.error(f"[CRYPTO] Encryption failed: {e}")
            # Fallback: return unencrypted (not ideal, but prevents data loss)
            return key_pem
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt private key"""
        try:
            from cryptography.fernet import Fernet
            
            # Get master encryption key
            master_key = self._get_master_key()
            f = Fernet(master_key)
            
            # Decrypt
            encrypted_bytes = base64.b64decode(encrypted_key)
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        
        except Exception as e:
            logger.error(f"[CRYPTO] Decryption failed: {e}")
            # Assume unencrypted fallback
            return encrypted_key
    
    def _get_master_key(self) -> bytes:
        """Get or create master encryption key"""
        import os
        
        # Check environment variable first
        env_key = os.getenv("GRACE_CRYPTO_MASTER_KEY")
        if env_key:
            return base64.b64decode(env_key)
        
        # Check file
        key_file = os.path.join(os.path.expanduser("~"), ".grace", "master.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        
        # Generate new master key
        from cryptography.fernet import Fernet
        master_key = Fernet.generate_key()
        
        # Save to file
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(master_key)
        
        logger.info(f"[CRYPTO] Generated new master key: {key_file}")
        
        return master_key
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get crypto statistics"""
        return {
            "total_keys": len(self.keys),
            "active_keys": len([k for k in self.keys.values() if not k.rotated]),
            "rotated_keys": len([k for k in self.keys.values() if k.rotated]),
            "signatures_generated": self.signatures_generated,
            "signatures_verified": self.signatures_verified,
            "verification_failures": self.verification_failures,
            "components_with_keys": len(self.component_keys)
        }


# Singleton instance
crypto_key_manager = CryptoKeyManager()

