"""
Hunter Integration for Verification System
Threat detection during action verification
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class HunterIntegration:
    """Integrates threat detection with verification"""
    
    async def scan(
        self,
        action_type: str,
        actor: str,
        input_data: Dict[str, Any]
    ) -> List[str]:
        """
        Scan action for threats
        
        Returns:
            List of threat alerts (empty if clean)
        """
        threats = []
        
        # Basic threat detection patterns
        try:
            # Check for suspicious patterns in input data
            data_str = str(input_data).lower()
            
            # SQL injection patterns
            sql_patterns = ["drop table", "delete from", "'; --", "union select"]
            for pattern in sql_patterns:
                if pattern in data_str:
                    threats.append(f"Potential SQL injection detected: {pattern}")
            
            # Command injection patterns
            cmd_patterns = ["; rm -rf", "| sh", "&& cat", "$(whoami)"]
            for pattern in cmd_patterns:
                if pattern in data_str:
                    threats.append(f"Potential command injection detected: {pattern}")
            
            # Path traversal
            if "../" in data_str or "..%2f" in data_str:
                threats.append("Potential path traversal detected")
            
            # Excessive data size (potential DOS)
            if len(str(input_data)) > 100000:
                threats.append("Excessive input data size detected")
            
            # Log threats if found
            if threats:
                logger.warning(f"Threats detected in {action_type} by {actor}: {threats}")
        
        except Exception as e:
            logger.error(f"Error during threat scan: {e}")
        
        return threats

# Singleton instance
hunter_integration = HunterIntegration()
