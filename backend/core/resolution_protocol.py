"""
Resolution Protocol - handles issue resolution logic for the healing orchestrator
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ResolutionProtocol:
    """
    Protocol for resolving system issues in a structured manner.
    Provides utilities for issue classification, escalation, and resolution tracking.
    """

    def __init__(self):
        self.resolution_history: list[Dict[str, Any]] = []

    async def resolve_issue(
        self,
        issue_type: str,
        issue_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resolve an issue using the appropriate resolution strategy.
        
        Args:
            issue_type: Type of issue to resolve
            issue_data: Data about the issue
            context: Additional context for resolution
            
        Returns:
            Resolution result with status and details
        """
        logger.info(f"Resolving issue of type: {issue_type}")
        
        resolution_result = {
            "issue_type": issue_type,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending",
            "details": issue_data,
            "context": context or {}
        }
        
        self.resolution_history.append(resolution_result)
        
        return resolution_result

    def classify_issue(self, error_message: str) -> str:
        """
        Classify an issue based on error message patterns.
        
        Args:
            error_message: The error message to classify
            
        Returns:
            Issue type classification
        """
        error_lower = error_message.lower()
        
        if "import" in error_lower or "module" in error_lower:
            return "import_error"
        elif "network" in error_lower or "connection" in error_lower:
            return "network_fault"
        elif "config" in error_lower or "configuration" in error_lower:
            return "config_error"
        elif "dependency" in error_lower or "package" in error_lower:
            return "missing_dependency"
        else:
            return "unknown"

    def get_resolution_history(self) -> list[Dict[str, Any]]:
        """Get the history of all resolutions."""
        return self.resolution_history
