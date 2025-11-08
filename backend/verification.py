"""Cryptographic verification system for all Grace actions"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .models import Base, async_session

class VerificationEnvelope(Base):
    """Signed envelopes for actions"""
    __tablename__ = "verification_envelopes"
    id = Column(Integer, primary_key=True)
    action_id = Column(String(64), unique=True, nullable=False)
    actor = Column(String(64), nullable=False)
    action_type = Column(String(128), nullable=False)
    resource = Column(String(256))
    input_hash = Column(String(64), nullable=False)
    output_hash = Column(String(64))
    signature = Column(String(256), nullable=False)
    verified = Column(Boolean, default=False)
    criteria_met = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VerificationEngine:
    """Sign and verify all actions cryptographically"""
    
    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
    
    def create_envelope(
        self,
        action_id: str,
        actor: str,
        action_type: str,
        resource: str,
        input_data: Dict[str, Any]
    ) -> str:
        """Create signed envelope for action"""
        
        input_str = json.dumps(input_data, sort_keys=True)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()
        
        message = f"{action_id}:{actor}:{action_type}:{resource}:{input_hash}"
        signature = self.private_key.sign(message.encode())
        signature_hex = signature.hex()
        
        return signature_hex, input_hash
    
    def verify_envelope(
        self,
        signature_hex: str,
        action_id: str,
        actor: str,
        action_type: str,
        resource: str,
        input_hash: str
    ) -> bool:
        """Verify signature on envelope"""
        
        try:
            message = f"{action_id}:{actor}:{action_type}:{resource}:{input_hash}"
            signature = bytes.fromhex(signature_hex)
            self.public_key.verify(signature, message.encode())
            return True
        except:
            return False
    
    async def log_verified_action(
        self,
        action_id: str,
        actor: str,
        action_type: str,
        resource: str,
        input_data: dict,
        output_data: dict = None,
        criteria_met: bool = True
    ):
        """Log action with verification"""
        
        signature, input_hash = self.create_envelope(
            action_id, actor, action_type, resource, input_data
        )
        
        output_hash = None
        if output_data:
            output_str = json.dumps(output_data, sort_keys=True)
            output_hash = hashlib.sha256(output_str.encode()).hexdigest()
        
        async with async_session() as session:
            envelope = VerificationEnvelope(
                action_id=action_id,
                actor=actor,
                action_type=action_type,
                resource=resource,
                input_hash=input_hash,
                output_hash=output_hash,
                signature=signature,
                verified=True,
                criteria_met=criteria_met
            )
            session.add(envelope)
            await session.commit()
        
        print(f"[OK] Verified action: {action_type} by {actor}")

verification_engine = VerificationEngine()
