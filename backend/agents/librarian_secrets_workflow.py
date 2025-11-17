"""
Librarian Secrets Workflow
Handles secret validation, rotation reminders, and governance integration

Triggered when secrets_service publishes "secrets.stored" event
"""

import asyncio
from typing import Dict, Any, Optional

from backend.core.message_bus import message_bus, MessagePriority
from backend.security.secrets_service import secrets_service


class LibrarianSecretsWorkflow:
    """
    Librarian agent for secret lifecycle management
    
    Responsibilities:
    - Validate new secrets (test API calls)
    - Schedule rotation reminders
    - Monitor expiration
    - Update governance on permission changes
    - Create HTM tasks for secret operations
    """
    
    def __init__(self):
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.secrets_validated = 0
        self.validation_failures = 0
    
    async def start(self):
        """Start Librarian secrets workflow"""
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to secrets.stored events
        try:
            queue = await message_bus.subscribe(
                subscriber="librarian_secrets",
                topic="secrets.stored"
            )
            self._task = asyncio.create_task(self._process_secret_events(queue))
            
            print("[LIBRARIAN-SECRETS] Workflow started, subscribed to secret events")
        except Exception as e:
            print(f"[LIBRARIAN-SECRETS] Failed to start: {e}")
    
    async def stop(self):
        """Stop workflow"""
        self.running = False
        if self._task:
            self._task.cancel()
    
    async def _process_secret_events(self, queue):
        """Process new secret events"""
        while self.running:
            try:
                msg = await queue.get()
                payload = msg.payload
                
                secret_id = payload.get("secret_id")
                secret_type = payload.get("type")
                scope = payload.get("scope")
                
                print(f"[LIBRARIAN-SECRETS] New secret detected: {payload.get('name')}")
                
                # Trigger validation workflow
                if payload.get("requires_validation"):
                    await self._validate_secret(secret_id, secret_type, scope)
                
                # Check if governance approval needed
                if payload.get("requires_approval"):
                    await self._request_governance_approval(secret_id, scope)
                
                # Schedule rotation reminder
                await self._schedule_rotation_reminder(secret_id)
                
            except Exception as e:
                print(f"[LIBRARIAN-SECRETS] Error processing event: {e}")
                await asyncio.sleep(1)
    
    async def _validate_secret(
        self,
        secret_id: str,
        secret_type: str,
        scope: str
    ):
        """
        Validate that secret works via test API call
        
        Creates sandbox test based on secret type
        """
        test_endpoints = {
            "api_key": {
                "stripe": "https://api.stripe.com/v1/charges",
                "openai": "https://api.openai.com/v1/models",
                "github": "https://api.github.com/user"
            }
        }
        
        # Determine test endpoint
        test_endpoint = None
        if secret_type == "api_key" and scope:
            for service, endpoint in test_endpoints.get("api_key", {}).items():
                if service.lower() in scope.lower():
                    test_endpoint = endpoint
                    break
        
        print(f"[LIBRARIAN-SECRETS] Validating {secret_id}...")
        
        try:
            # Perform validation
            validation_passed = await secrets_service.validate_secret(
                secret_id=secret_id,
                validation_method="test_api_call" if test_endpoint else "basic",
                test_endpoint=test_endpoint
            )
            
            if validation_passed:
                self.secrets_validated += 1
                print(f"[LIBRARIAN-SECRETS] Validation PASSED: {secret_id}")
                
                # Notify user
                await message_bus.publish(
                    source="librarian_secrets",
                    topic="secrets.validated",
                    payload={
                        "secret_id": secret_id,
                        "validation_passed": True,
                        "tested_endpoint": test_endpoint
                    },
                    priority=MessagePriority.NORMAL
                )
            else:
                self.validation_failures += 1
                print(f"[LIBRARIAN-SECRETS] Validation FAILED: {secret_id}")
                
                # Alert user
                await message_bus.publish(
                    source="librarian_secrets",
                    topic="secrets.validation_failed",
                    payload={
                        "secret_id": secret_id,
                        "validation_passed": False,
                        "action_required": "check_secret_value"
                    },
                    priority=MessagePriority.HIGH
                )
        
        except Exception as e:
            print(f"[LIBRARIAN-SECRETS] Validation error: {e}")
            self.validation_failures += 1
    
    async def _request_governance_approval(self, secret_id: str, scope: str):
        """
        Request governance approval for secret storage
        
        High-privilege secrets require explicit approval
        """
        print(f"[LIBRARIAN-SECRETS] Requesting governance approval for {secret_id}")
        
        # Create governance check
        try:
            from backend.governance.governance_engine import governance_engine
            
            decision = await governance_engine.check(
                actor="librarian",
                action="secret_storage",
                resource=secret_id,
                payload={
                    "scope": scope,
                    "requires_approval": True
                }
            )
            
            if decision.get("decision") == "allow":
                print(f"[LIBRARIAN-SECRETS] Governance approved: {secret_id}")
            else:
                print(f"[LIBRARIAN-SECRETS] Governance requires review: {secret_id}")
        
        except Exception as e:
            print(f"[LIBRARIAN-SECRETS] Governance check error: {e}")
    
    async def _schedule_rotation_reminder(self, secret_id: str):
        """
        Schedule reminder to rotate secret before expiration
        
        Creates HTM task for future rotation
        """
        # TODO: Create HTM task scheduled 80 days from now (if 90-day rotation)
        # This would integrate with HTM's scheduling system
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        return {
            "running": self.running,
            "secrets_validated": self.secrets_validated,
            "validation_failures": self.validation_failures,
            "success_rate": self.secrets_validated / (self.secrets_validated + self.validation_failures)
                if (self.secrets_validated + self.validation_failures) > 0 else 0
        }


# Global instance
librarian_secrets_workflow = LibrarianSecretsWorkflow()
