"""
Verification API - Clean async interface for verification engine
Exposes verify_claim() and verify_code_snippet() to the rest of Grace
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .code_verification_engine import (
    verification_engine,
    Hypothesis,
    VerificationResult,
    VerificationStatus
)


class VerificationAPI:
    """
    Clean async API for verification operations
    
    Usage:
        api = VerificationAPI()
        result = await api.verify_claim(hypothesis)
        result = await api.verify_code_snippet(hypothesis, code)
    """
    
    def __init__(self):
        self.engine = verification_engine
    
    async def verify_claim(
        self,
        hypothesis: Hypothesis
    ) -> VerificationResult:
        """
        Verify a hypothesis/claim
        
        Args:
            hypothesis: The hypothesis to verify
            
        Returns:
            VerificationResult with status, confidence, and recommendations
            
        Example:
            hypothesis = Hypothesis(
                id="hyp_001",
                description="Function correctly validates email addresses",
                code_snippet=email_validator_code,
                expected_behavior="Returns True for valid emails, False otherwise"
            )
            result = await api.verify_claim(hypothesis)
        """
        return await self.engine.verify_claim(hypothesis)
    
    async def verify_code_snippet(
        self,
        hypothesis: Hypothesis,
        code: str,
        run_tests: bool = True
    ) -> VerificationResult:
        """
        Verify a code snippet with static analysis and unit testing
        
        Args:
            hypothesis: The hypothesis describing what the code should do
            code: Python code to verify
            run_tests: Whether to generate and run unit tests
            
        Returns:
            VerificationResult with complete analysis
            
        Example:
            hypothesis = Hypothesis(
                id="code_001",
                description="Safe user input handler",
                expected_behavior="Sanitizes and validates user input"
            )
            result = await api.verify_code_snippet(hypothesis, user_code)
        """
        return await self.engine.verify_code_snippet(hypothesis, code, run_tests)
    
    async def quick_verify(
        self,
        description: str,
        code: str,
        expected_behavior: Optional[str] = None,
        run_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Quick verification helper - creates hypothesis automatically
        
        Args:
            description: What the code should do
            code: Python code to verify
            expected_behavior: Expected behavior description
            run_tests: Whether to run unit tests
            
        Returns:
            Dictionary with verification results
            
        Example:
            result = await api.quick_verify(
                description="Email validator function",
                code=email_code,
                expected_behavior="Returns True for valid emails"
            )
        """
        hypothesis = Hypothesis(
            id=f"quick_{datetime.utcnow().timestamp()}",
            description=description,
            code_snippet=code,
            expected_behavior=expected_behavior
        )
        
        result = await self.verify_code_snippet(hypothesis, code, run_tests)
        
        return result.to_dict()
    
    async def verify_security(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Security-focused verification - only static analysis, no test execution
        
        Args:
            code: Python code to verify
            context: Additional context for verification
            
        Returns:
            Dictionary with security analysis results
            
        Example:
            result = await api.verify_security(untrusted_code)
            if result['status'] == 'verified':
                # Safe to execute
        """
        hypothesis = Hypothesis(
            id=f"security_{datetime.utcnow().timestamp()}",
            description="Security verification",
            code_snippet=code,
            context=context or {}
        )
        
        result = await self.verify_code_snippet(hypothesis, code, run_tests=False)
        
        security_result = {
            'status': result.status.value,
            'confidence': result.confidence,
            'security_score': result.static_analysis.security_score if result.static_analysis else 0.0,
            'critical_issues': [
                {
                    'severity': issue.severity.value,
                    'message': issue.message,
                    'line': issue.line_number,
                    'fix': issue.fix_suggestion
                }
                for issue in result.issues
                if issue.category == "security"
            ],
            'safe_to_execute': (
                result.status == VerificationStatus.VERIFIED and
                result.confidence >= 0.8 and
                len([i for i in result.issues if i.category == "security"]) == 0
            )
        }
        
        return security_result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get verification engine statistics"""
        return {
            'total_verifications': self.engine.verification_count,
            'engine_status': 'active',
            'temp_dir': str(self.engine.temp_dir)
        }


verification_api = VerificationAPI()
