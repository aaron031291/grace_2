"""
Persistent Crypto Key Manager
Wires crypto_key_manager to durable storage (DB + vault)

Features:
- Keys survive restarts
- Audit trail in database
- Integration with secrets vault
- Signature verification across reboots
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import base64


class PersistentCryptoManager:
    """
    Persistent crypto key management
    
    Storage:
    - Database: Key metadata, audit trail
    - Vault: Encrypted key material
    - Memory: Hot cache for performance
    """
    
    def __init__(self, db_path: str = "databases/crypto_keys.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self.keys_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize
        self._init_database()
        self._load_keys_from_db()
        
        print("[CRYPTO] Persistent crypto manager initialized")
    
    def _init_database(self):
        """Initialize crypto database"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Crypto keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crypto_keys (
                key_id TEXT PRIMARY KEY,
                key_type TEXT,
                algorithm TEXT,
                key_material_encrypted TEXT,
                created_at TEXT,
                last_used TEXT,
                usage_count INTEGER DEFAULT 0,
                metadata_json TEXT
            )
        """)
        
        # Audit trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crypto_audit (
                audit_id TEXT PRIMARY KEY,
                key_id TEXT,
                operation TEXT,
                actor TEXT,
                timestamp TEXT,
                details_json TEXT
            )
        """)
        
        # Signatures table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signatures (
                signature_id TEXT PRIMARY KEY,
                data_hash TEXT,
                key_id TEXT,
                signature TEXT,
                created_at TEXT,
                verified BOOLEAN DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_keys_from_db(self):
        """Load keys from database to cache"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT key_id, key_type, algorithm, key_material_encrypted, metadata_json FROM crypto_keys")
        rows = cursor.fetchall()
        
        for row in rows:
            self.keys_cache[row[0]] = {
                "key_id": row[0],
                "key_type": row[1],
                "algorithm": row[2],
                "key_material": self._decrypt_key_material(row[3]),
                "metadata": json.loads(row[4]) if row[4] else {}
            }
        
        conn.close()
        
        print(f"[CRYPTO] Loaded {len(self.keys_cache)} keys from database")
    
    def _decrypt_key_material(self, encrypted: str) -> str:
        """Decrypt key material (would use vault)"""
        # In production, decrypt using vault key
        # For now, simple base64
        try:
            return base64.b64decode(encrypted).decode('utf-8')
        except:
            return encrypted
    
    def _encrypt_key_material(self, key_material: str) -> str:
        """Encrypt key material (would use vault)"""
        # In production, encrypt using vault key
        # For now, simple base64
        return base64.b64encode(key_material.encode('utf-8')).decode('utf-8')
    
    def store_key(
        self,
        key_id: str,
        key_type: str,
        algorithm: str,
        key_material: str,
        metadata: Dict[str, Any] = None
    ):
        """Store crypto key persistently"""
        
        # Encrypt key material
        encrypted = self._encrypt_key_material(key_material)
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO crypto_keys
            (key_id, key_type, algorithm, key_material_encrypted, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            key_id,
            key_type,
            algorithm,
            encrypted,
            datetime.utcnow().isoformat(),
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        # Cache it
        self.keys_cache[key_id] = {
            "key_id": key_id,
            "key_type": key_type,
            "algorithm": algorithm,
            "key_material": key_material,
            "metadata": metadata or {}
        }
        
        # Audit
        self._audit("key_stored", key_id, "system", {"key_type": key_type})
        
        print(f"[CRYPTO] Key stored: {key_id} ({key_type})")
    
    def retrieve_key(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve crypto key"""
        
        # Check cache
        if key_id in self.keys_cache:
            self._record_usage(key_id)
            return self.keys_cache[key_id]
        
        # Not found
        return None
    
    def sign_data(self, key_id: str, data: str) -> Optional[str]:
        """Sign data and persist signature"""
        
        key = self.retrieve_key(key_id)
        if not key:
            return None
        
        # Create signature (simple hash for now)
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        signature = hashlib.sha256(f"{data_hash}{key['key_material']}".encode()).hexdigest()
        
        # Store signature
        signature_id = f"sig_{datetime.utcnow().timestamp()}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO signatures
            (signature_id, data_hash, key_id, signature, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            signature_id,
            data_hash,
            key_id,
            signature,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self._audit("data_signed", key_id, "system", {"signature_id": signature_id})
        
        return signature
    
    def verify_signature(self, data: str, signature: str, key_id: str) -> bool:
        """Verify signature (survives restart!)"""
        
        # Re-compute signature
        expected = self.sign_data(key_id, data)
        
        # Compare
        verified = (expected == signature)
        
        # Update signature verification status
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE signatures SET verified = ? WHERE signature = ?
        """, (verified, signature))
        
        conn.commit()
        conn.close()
        
        return verified
    
    def _record_usage(self, key_id: str):
        """Record key usage"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE crypto_keys
            SET usage_count = usage_count + 1,
                last_used = ?
            WHERE key_id = ?
        """, (datetime.utcnow().isoformat(), key_id))
        
        conn.commit()
        conn.close()
    
    def _audit(self, operation: str, key_id: str, actor: str, details: Dict[str, Any]):
        """Record audit trail"""
        
        audit_id = f"audit_{datetime.utcnow().timestamp()}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO crypto_audit
            (audit_id, key_id, operation, actor, timestamp, details_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            audit_id,
            key_id,
            operation,
            actor,
            datetime.utcnow().isoformat(),
            json.dumps(details)
        ))
        
        conn.commit()
        conn.close()
    
    def get_audit_trail(self, key_id: str) -> List[Dict[str, Any]]:
        """Get complete audit trail for key"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT operation, actor, timestamp, details_json
            FROM crypto_audit
            WHERE key_id = ?
            ORDER BY timestamp DESC
        """, (key_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "operation": row[0],
                "actor": row[1],
                "timestamp": row[2],
                "details": json.loads(row[3])
            }
            for row in rows
        ]


# Global instance
persistent_crypto_manager = PersistentCryptoManager()
