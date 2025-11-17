"""Cryptographic verification system for all Grace actions"""

import hashlib
import json
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from backend.models import async_session
from ..models.verification_models import VerificationEnvelope

class VerificationEngine:
    """Sign and verify all actions cryptographically"""
    
    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        # Pre-bind methods to reduce attribute lookup overhead in hot path
        self._sign = self.private_key.sign
        self._verify = self.public_key.verify
    
    def create_envelope(
        self,
        action_id: str,
        actor: str,
        action_type: str,
        resource: str,
        input_data: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Create signed envelope for action"""
        
        # Use compact separators to reduce serialization overhead
        input_str = json.dumps(input_data, sort_keys=True, separators=(",", ":"))
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()
        
        message = f"{action_id}:{actor}:{action_type}:{resource}:{input_hash}"
        signature = self._sign(message.encode())
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
            self._verify(signature, message.encode())
            return True
        except Exception:
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
        
        print(f"✓ Verified action: {action_type} by {actor}")

verification_engine = VerificationEngine()
