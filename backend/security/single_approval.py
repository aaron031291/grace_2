"""
Single Approval Point for Grace Development

Instead of 6 separate approvals, provide ONE approval for all operations.
"""
import os
from typing import Optional

class SingleApprovalManager:
    """Manage single approval point for all Grace operations"""
    
    def __init__(self):
        self.approval_granted = False
        self.approval_method = "not_approved"
        
    def grant_approval(self, method: str = "user_consent") -> bool:
        """
        Grant single approval for all operations
        
        Args:
            method: How approval was granted (user_consent, auto, env_var)
            
        Returns:
            bool: True if approval was granted
        """
        self.approval_granted = True
        self.approval_method = method
        print(f"[OK] Single approval granted via {method}")
        print("[OK] All operations are now authorized")
        return True
        
    def check_approval(self, operation: str = "any") -> bool:
        """
        Check if operation is approved
        
        In single approval mode, once approved, all operations are approved.
        
        Args:
            operation: The operation being requested (ignored in single mode)
            
        Returns:
            bool: True if approved
        """
        return self.approval_granted
        
    def revoke_approval(self, reason: str = "user_request"):
        """Revoke the single approval"""
        self.approval_granted = False
        print(f"[!] Approval revoked: {reason}")
        
    def get_status(self) -> dict:
        """Get approval status"""
        return {
            "approved": self.approval_granted,
            "method": self.approval_method,
            "mode": "single_approval"
        }


# Global instance
single_approval = SingleApprovalManager()


def auto_approve_from_env():
    """Auto-approve if environment variable is set"""
    if os.getenv("GRACE_AUTO_APPROVE", "").lower() == "true":
        single_approval.grant_approval(method="environment_variable")
        return True
        
    if os.getenv("GRACE_ENV") == "development":
        single_approval.grant_approval(method="development_mode")
        return True
        
    if os.getenv("GRACE_SINGLE_APPROVAL", "").lower() == "true":
        single_approval.grant_approval(method="single_approval_mode")
        return True
        
    return False


# Auto-approve on module load if configured
auto_approve_from_env()
