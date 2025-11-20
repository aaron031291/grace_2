"""
Verification System - Real implementation without stubs
Provides code verification, static analysis, and unit testing
"""

from .verification import VerificationEngine, verification_engine
from .code_verification_engine import (
    CodeVerificationEngine,
    Hypothesis,
    VerificationResult,
    VerificationStatus,
    VerificationIssue,
    SeverityLevel,
    StaticAnalysisResult,
    UnitTestResult,
    verification_engine as code_verification_engine
)
from .verification_api import VerificationAPI, verification_api
from .verification_integration import VerificationIntegration, get_verification_integration

__all__ = [
    'VerificationEngine',
    'verification_engine',
    'CodeVerificationEngine',
    'code_verification_engine',
    'Hypothesis',
    'VerificationResult',
    'VerificationStatus',
    'VerificationIssue',
    'SeverityLevel',
    'StaticAnalysisResult',
    'UnitTestResult',
    'VerificationAPI',
    'verification_api',
    'VerificationIntegration',
    'get_verification_integration',
]
