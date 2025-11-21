"""
Constitutional Verifier for Verification System
Checks actions against constitutional principles
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ConstitutionalVerifier:
    """Verifies actions comply with constitutional principles"""
    
    def __init__(self):
        # Define constitutional principles
        self.principles = {
            "transparency": "Actions must be transparent and auditable",
            "user_consent": "User data operations require consent",
            "minimal_privilege": "Use minimum necessary permissions",
            "data_privacy": "Protect user privacy and data",
            "accountability": "All actions must be attributable",
            "reversibility": "Destructive actions should be reversible",
            "human_oversight": "Critical actions require human approval"
        }
    
    async def verify(
        self,
        action_type: str,
        actor: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify action against constitutional principles
        
        Returns:
            {
                'compliant': bool,
                'violations': list,
                'principles_checked': list
            }
        """
        violations: List[str] = []
        principles_checked: List[str] = []
        
        try:
            # Check transparency (all actions must have source)
            principles_checked.append("transparency")
            if not actor or actor == "unknown":
                violations.append("Transparency violation: Unknown actor")
            
            # Check for destructive operations
            destructive_actions = ["delete", "remove", "drop", "destroy", "wipe"]
            if any(word in action_type.lower() for word in destructive_actions):
                principles_checked.append("reversibility")
                
                # Check if backup/rollback is mentioned
                if not input_data.get("backup") and not input_data.get("reversible"):
                    violations.append("Reversibility violation: Destructive action without backup")
            
            # Check user data operations
            if "user" in action_type.lower() or input_data.get("user_id"):
                principles_checked.append("user_consent")
                principles_checked.append("data_privacy")
                
                # Check for consent flag
                if not input_data.get("user_consent") and action_type != "read":
                    violations.append("User consent violation: Missing consent for user data operation")
            
            # Check privilege escalation
            if "admin" in action_type.lower() or "sudo" in action_type.lower():
                principles_checked.append("minimal_privilege")
                principles_checked.append("human_oversight")
                
                if not input_data.get("approved_by"):
                    violations.append("Human oversight violation: Admin action without approval")
            
            # Log verification result
            if violations:
                logger.warning(f"Constitutional violations in {action_type}: {violations}")
            else:
                logger.debug(f"Constitutional verification passed for {action_type}")
        
        except Exception as e:
            logger.error(f"Error during constitutional verification: {e}")
            violations.append(f"Verification error: {str(e)}")
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'principles_checked': principles_checked
        }

# Singleton instance
constitutional_verifier = ConstitutionalVerifier()
