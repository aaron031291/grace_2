"""
Verification Integration for Immutable Log
Logs all verification results, anomalies, and refutations with full audit trail
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .immutable_log import immutable_log


class VerificationLogger:
    """
    Specialized logger for verification system
    Ensures all verification outcomes are logged to immutable audit trail
    """
    
    def __init__(self):
        self.log = immutable_log
    
    async def log_verification_result(
        self,
        hypothesis_id: str,
        actor: str,
        verification_type: str,
        status: str,
        confidence: float,
        issues: List[Dict[str, Any]],
        recommendations: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log a verification result
        
        Args:
            hypothesis_id: Hypothesis being verified
            actor: Who requested verification
            verification_type: Type of verification (code, claim, security, etc.)
            status: VERIFIED, REFUTED, INCONCLUSIVE, ERROR
            confidence: Confidence score (0.0 - 1.0)
            issues: List of issues found
            recommendations: List of recommended actions
            metadata: Additional context
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "hypothesis_id": hypothesis_id,
            "verification_type": verification_type,
            "status": status,
            "confidence": confidence,
            "issues_count": len(issues),
            "critical_issues": len([i for i in issues if i.get('severity') == 'critical']),
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        # Include issue details if not too many
        if len(issues) <= 10:
            payload["issues"] = issues
        
        action = f"VERIFICATION_{status.upper()}"
        result = status.lower()
        
        return await self.log.append(
            actor=actor,
            action=action,
            resource=f"hypothesis:{hypothesis_id}",
            subsystem="verification",
            payload=payload,
            result=result
        )
    
    async def log_static_analysis(
        self,
        code_id: str,
        actor: str,
        security_score: float,
        complexity_score: float,
        issues_found: int,
        passed: bool
    ) -> int:
        """
        Log static code analysis results
        
        Args:
            code_id: Code identifier
            actor: Who submitted the code
            security_score: Security score (0.0 - 1.0)
            complexity_score: Complexity score (0.0 - 1.0)
            issues_found: Number of issues found
            passed: Whether analysis passed
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "code_id": code_id,
            "security_score": security_score,
            "complexity_score": complexity_score,
            "issues_found": issues_found,
            "passed": passed,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="STATIC_ANALYSIS_COMPLETED",
            resource=f"code:{code_id}",
            subsystem="verification",
            payload=payload,
            result="passed" if passed else "failed"
        )
    
    async def log_unit_test_results(
        self,
        code_id: str,
        actor: str,
        tests_run: int,
        tests_passed: int,
        tests_failed: int,
        coverage_percent: float,
        duration_seconds: float
    ) -> int:
        """
        Log unit test execution results
        
        Args:
            code_id: Code identifier
            actor: Who submitted the code
            tests_run: Number of tests executed
            tests_passed: Number of tests that passed
            tests_failed: Number of tests that failed
            coverage_percent: Code coverage percentage
            duration_seconds: Test execution duration
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "code_id": code_id,
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "coverage_percent": coverage_percent,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        passed = tests_failed == 0
        
        return await self.log.append(
            actor=actor,
            action="UNIT_TESTS_COMPLETED",
            resource=f"code:{code_id}",
            subsystem="verification",
            payload=payload,
            result="passed" if passed else "failed"
        )
    
    async def log_refutation(
        self,
        hypothesis_id: str,
        actor: str,
        refutation_reason: str,
        evidence: List[str],
        severity: str = "medium"
    ) -> int:
        """
        Log a claim/code refutation
        
        Args:
            hypothesis_id: What was refuted
            actor: Who attempted the claim
            refutation_reason: Why it was refuted
            evidence: Evidence of refutation
            severity: Severity of the issue
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "hypothesis_id": hypothesis_id,
            "refutation_reason": refutation_reason,
            "evidence": evidence,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="REFUTED",
            resource=f"hypothesis:{hypothesis_id}",
            subsystem="verification",
            payload=payload,
            result="refuted"
        )
    
    async def log_inconclusive(
        self,
        hypothesis_id: str,
        actor: str,
        reason: str,
        confidence: float,
        missing_data: List[str]
    ) -> int:
        """
        Log an inconclusive verification
        
        Args:
            hypothesis_id: What couldn't be verified
            actor: Who requested verification
            reason: Why verification was inconclusive
            confidence: Partial confidence score
            missing_data: What data/evidence was missing
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "hypothesis_id": hypothesis_id,
            "reason": reason,
            "confidence": confidence,
            "missing_data": missing_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="INCONCLUSIVE",
            resource=f"hypothesis:{hypothesis_id}",
            subsystem="verification",
            payload=payload,
            result="inconclusive"
        )
    
    async def log_security_violation(
        self,
        code_id: str,
        actor: str,
        violation_type: str,
        violation_details: str,
        dangerous_patterns: List[str],
        action_taken: str
    ) -> int:
        """
        Log a security violation detected during verification
        
        Args:
            code_id: Code that violated security rules
            actor: Who submitted the code
            violation_type: Type of violation
            violation_details: Details of what was found
            dangerous_patterns: List of dangerous patterns detected
            action_taken: How it was handled
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "code_id": code_id,
            "violation_type": violation_type,
            "violation_details": violation_details,
            "dangerous_patterns": dangerous_patterns,
            "action_taken": action_taken,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="SECURITY_VIOLATION_DETECTED",
            resource=f"code:{code_id}",
            subsystem="verification",
            payload=payload,
            result="blocked"
        )
    
    async def log_integrity_check(
        self,
        check_id: str,
        check_type: str,
        passed: bool,
        issues_found: List[str],
        corrective_actions: List[str]
    ) -> int:
        """
        Log an integrity check result
        
        Args:
            check_id: Check identifier
            check_type: Type of integrity check
            passed: Whether check passed
            issues_found: Issues discovered
            corrective_actions: Actions taken to fix issues
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "check_id": check_id,
            "check_type": check_type,
            "passed": passed,
            "issues_found": issues_found,
            "corrective_actions": corrective_actions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor="verification_system",
            action="INTEGRITY_CHECK_COMPLETED",
            resource=f"check:{check_id}",
            subsystem="verification",
            payload=payload,
            result="passed" if passed else "failed"
        )
    
    async def get_verification_history(
        self,
        hours_back: int = 168,  # 7 days
        limit: int = 100
    ) -> list:
        """
        Get verification history
        
        Args:
            hours_back: How many hours to look back
            limit: Maximum number of entries to return
            
        Returns:
            List of verification log entries
        """
        
        return await self.log.get_entries(
            subsystem="verification",
            limit=limit
        )
    
    async def get_refutation_history(
        self,
        limit: int = 50
    ) -> list:
        """
        Get history of refuted claims/code
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of refutation log entries
        """
        
        entries = await self.log.get_entries(
            subsystem="verification",
            limit=limit * 2
        )
        
        # Filter for refutations
        refutations = [
            entry for entry in entries
            if 'REFUTED' in entry['action'] or entry['result'] == 'refuted'
        ]
        
        return refutations[:limit]
    
    async def get_security_violations(
        self,
        limit: int = 50
    ) -> list:
        """
        Get history of security violations
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of security violation log entries
        """
        
        entries = await self.log.get_entries(
            subsystem="verification",
            limit=limit * 2
        )
        
        # Filter for security violations
        violations = [
            entry for entry in entries
            if 'SECURITY_VIOLATION' in entry['action']
        ]
        
        return violations[:limit]


verification_logger = VerificationLogger()
