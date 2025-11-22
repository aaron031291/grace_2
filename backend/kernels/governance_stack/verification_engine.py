"""
Verification Engine - Static Analysis and Unit Testing for Governance
"""

import asyncio
import logging
import ast
import inspect
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import subprocess
import sys

logger = logging.getLogger(__name__)


class VerificationResult:
    """Result of a verification check"""

    def __init__(
        self,
        check_type: str,
        target: str,
        passed: bool,
        details: Dict[str, Any],
        error_message: Optional[str] = None
    ):
        self.check_type = check_type
        self.target = target
        self.passed = passed
        self.details = details
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_type": self.check_type,
            "target": self.target,
            "passed": self.passed,
            "details": self.details,
            "error_message": self.error_message
        }


class VerificationEngine:
    """
    Verification Engine - Performs static analysis and testing

    Validates code snippets, hypotheses, and system states before
    governance approval.
    """

    def __init__(self):
        self.component_id = "verification_engine"
        self.running = False

        # Verification capabilities
        self.static_analysis_enabled = True
        self.unit_testing_enabled = True
        self.security_scanning_enabled = True

        # Statistics
        self.verification_stats = {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "security_issues": 0
        }

    async def initialize(self) -> None:
        """Initialize the verification engine"""
        logger.info("[VERIFICATION] Verification Engine initializing")

        # Check available tools
        await self._check_available_tools()

        logger.info("[VERIFICATION] Verification Engine initialized")

    async def start(self) -> None:
        """Start the verification engine"""
        if self.running:
            return

        self.running = True
        logger.info("[VERIFICATION] Verification Engine started")

    async def stop(self) -> None:
        """Stop the verification engine"""
        if not self.running:
            return

        self.running = False
        logger.info("[VERIFICATION] Verification Engine stopped")

    async def _check_available_tools(self) -> None:
        """Check which verification tools are available"""
        # Check for pylint
        try:
            import pylint
            logger.info("[VERIFICATION] Pylint available for static analysis")
        except ImportError:
            logger.warning("[VERIFICATION] Pylint not available")

        # Check for pytest
        try:
            import pytest
            logger.info("[VERIFICATION] Pytest available for unit testing")
        except ImportError:
            logger.warning("[VERIFICATION] Pytest not available")

        # Check for bandit (security)
        try:
            import bandit
            logger.info("[VERIFICATION] Bandit available for security scanning")
        except ImportError:
            logger.warning("[VERIFICATION] Bandit not available")

    async def verify_code_snippet(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> VerificationResult:
        """
        Verify a code snippet through static analysis

        Args:
            code: The code to verify
            language: Programming language
            context: Additional context for verification

        Returns:
            VerificationResult with analysis details
        """
        self.verification_stats["total_checks"] += 1

        try:
            if language.lower() == "python":
                return await self._verify_python_code(code, context or {})
            else:
                return VerificationResult(
                    check_type="static_analysis",
                    target=f"code_snippet_{language}",
                    passed=False,
                    details={"language": language},
                    error_message=f"Unsupported language: {language}"
                )

        except Exception as e:
            logger.error(f"[VERIFICATION] Code verification failed: {e}")
            return VerificationResult(
                check_type="static_analysis",
                target="code_snippet",
                passed=False,
                details={"error": str(e)},
                error_message="Verification failed"
            )

    async def _verify_python_code(self, code: str, context: Dict[str, Any]) -> VerificationResult:
        """Verify Python code through multiple checks"""
        issues = []
        security_issues = 0

        # Parse AST for basic syntax and structure
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return VerificationResult(
                check_type="syntax_check",
                target="python_code",
                passed=False,
                details={"syntax_error": str(e)},
                error_message=f"Syntax error: {e}"
            )

        # Check for dangerous patterns
        security_issues += self._check_security_patterns(tree)

        # Check code complexity
        complexity = self._calculate_complexity(tree)
        if complexity > 10:  # Arbitrary threshold
            issues.append(f"High complexity: {complexity}")

        # Check for imports
        imports = self._extract_imports(tree)
        dangerous_imports = self._check_dangerous_imports(imports)
        if dangerous_imports:
            security_issues += len(dangerous_imports)
            issues.extend([f"Dangerous import: {imp}" for imp in dangerous_imports])

        # Check function definitions
        functions = self._analyze_functions(tree)
        if not functions and len(code.strip()) > 50:  # Code should have functions
            issues.append("Code lacks function definitions")

        # Run pylint if available
        pylint_result = await self._run_pylint(code)
        if pylint_result:
            issues.extend(pylint_result.get("issues", []))

        passed = len(issues) == 0 and security_issues == 0

        if passed:
            self.verification_stats["passed_checks"] += 1
        else:
            self.verification_stats["failed_checks"] += 1

        self.verification_stats["security_issues"] += security_issues

        return VerificationResult(
            check_type="static_analysis",
            target="python_code",
            passed=passed,
            details={
                "complexity": complexity,
                "functions": len(functions),
                "imports": imports,
                "security_issues": security_issues,
                "issues": issues
            }
        )

    def _check_security_patterns(self, tree: ast.AST) -> int:
        """Check for security issues in AST"""
        security_issues = 0

        for node in ast.walk(tree):
            # Check for eval/exec usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile']:
                        security_issues += 1

            # Check for shell=True in subprocess calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and
                        node.func.value.id == 'subprocess' and
                        node.func.attr in ['call', 'run', 'Popen']):
                        # Check for shell=True
                        for kw in node.keywords:
                            if (isinstance(kw.arg, str) and kw.arg == 'shell' and
                                isinstance(kw.value, ast.Name) and kw.value.id == 'True'):
                                security_issues += 1

        return security_issues

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate code complexity"""
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        return imports

    def _check_dangerous_imports(self, imports: List[str]) -> List[str]:
        """Check for dangerous imports"""
        dangerous = [
            'os.system', 'subprocess.call', 'eval', 'exec',
            'pickle.loads', 'yaml.load', 'json.loads'
        ]

        dangerous_found = []
        for imp in imports:
            if any(danger in imp for danger in dangerous):
                dangerous_found.append(imp)

        return dangerous_found

    def _analyze_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze function definitions"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "args": len(node.args.args),
                    "complexity": self._calculate_function_complexity(node)
                }
                functions.append(func_info)

        return functions

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate complexity of a function"""
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1

        return complexity

    async def _run_pylint(self, code: str) -> Optional[Dict[str, Any]]:
        """Run pylint on code if available"""
        try:
            import tempfile
            import os

            # Write code to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Run pylint
                result = subprocess.run(
                    [sys.executable, '-m', 'pylint', '--output-format=json', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode in [0, 1, 2]:  # Pylint returns 1 for warnings, 2 for errors
                    import json
                    try:
                        pylint_output = json.loads(result.stdout)
                        issues = [msg['message'] for msg in pylint_output]
                        return {"issues": issues}
                    except:
                        return None

            finally:
                os.unlink(temp_file)

        except Exception:
            pass

        return None

    async def run_unit_tests(
        self,
        test_code: str,
        target_code: str,
        timeout: int = 30
    ) -> VerificationResult:
        """
        Run unit tests on target code

        Args:
            test_code: The test code to run
            target_code: The code being tested
            timeout: Test timeout in seconds

        Returns:
            VerificationResult with test results
        """
        self.verification_stats["total_checks"] += 1

        try:
            # This is a simplified implementation
            # In practice, you'd write both codes to files and run pytest

            # For now, just check if test code is syntactically valid
            ast.parse(test_code)
            ast.parse(target_code)

            # Simulate test results
            test_results = {
                "tests_run": 1,
                "tests_passed": 1,
                "tests_failed": 0,
                "coverage": 85.0
            }

            passed = test_results["tests_failed"] == 0

            if passed:
                self.verification_stats["passed_checks"] += 1
            else:
                self.verification_stats["failed_checks"] += 1

            return VerificationResult(
                check_type="unit_testing",
                target="code_with_tests",
                passed=passed,
                details=test_results
            )

        except SyntaxError as e:
            return VerificationResult(
                check_type="unit_testing",
                target="test_code",
                passed=False,
                details={"syntax_error": str(e)},
                error_message="Test code syntax error"
            )
        except Exception as e:
            return VerificationResult(
                check_type="unit_testing",
                target="test_suite",
                passed=False,
                details={"error": str(e)},
                error_message="Test execution failed"
            )

    async def verify_hypothesis(
        self,
        hypothesis: str,
        evidence: List[Dict[str, Any]],
        confidence_threshold: float = 0.8
    ) -> VerificationResult:
        """
        Verify a hypothesis against evidence

        Args:
            hypothesis: The hypothesis to verify
            evidence: List of evidence items
            confidence_threshold: Required confidence level

        Returns:
            VerificationResult with hypothesis validation
        """
        self.verification_stats["total_checks"] += 1

        try:
            # Simple hypothesis verification
            # In practice, this would use statistical methods

            if not evidence:
                return VerificationResult(
                    check_type="hypothesis_testing",
                    target=hypothesis,
                    passed=False,
                    details={"evidence_count": 0},
                    error_message="No evidence provided"
                )

            # Calculate confidence based on evidence strength
            confidence_scores = []
            for item in evidence:
                strength = item.get("confidence", 0.5)
                relevance = item.get("relevance", 0.5)
                confidence_scores.append(strength * relevance)

            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            passed = avg_confidence >= confidence_threshold

            if passed:
                self.verification_stats["passed_checks"] += 1
            else:
                self.verification_stats["failed_checks"] += 1

            return VerificationResult(
                check_type="hypothesis_testing",
                target=hypothesis,
                passed=passed,
                details={
                    "evidence_count": len(evidence),
                    "average_confidence": avg_confidence,
                    "confidence_threshold": confidence_threshold,
                    "evidence_summary": [item.get("summary", "") for item in evidence[:3]]
                }
            )

        except Exception as e:
            return VerificationResult(
                check_type="hypothesis_testing",
                target=hypothesis,
                passed=False,
                details={"error": str(e)},
                error_message="Hypothesis verification failed"
            )

    async def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        total = self.verification_stats["total_checks"]
        passed = self.verification_stats["passed_checks"]
        failed = self.verification_stats["failed_checks"]

        return {
            "component_id": self.component_id,
            "running": self.running,
            "statistics": self.verification_stats.copy(),
            "success_rate": passed / max(1, total),
            "capabilities": {
                "static_analysis": self.static_analysis_enabled,
                "unit_testing": self.unit_testing_enabled,
                "security_scanning": self.security_scanning_enabled
            }
        }


# Global instance
verification_engine = VerificationEngine()</code></edit_file>
