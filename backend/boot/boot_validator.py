"""
Boot Validator - Comprehensive validation system
Validates schema, secrets, tooling, and configuration before boot
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple


class BootValidator:
    """Validates all critical systems before boot"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validations_run = []
        self.failures = []
        
    def validate_all(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Run all validations
        
        Returns:
            (all_passed, validation_results)
        """
        
        validations = [
            ("Database Schema", self._validate_schema),
            ("Required Secrets", self._validate_secrets),
            ("Optional Secrets", self._validate_optional_secrets),
            ("UTF-8 Encoding", self._validate_encoding),
            ("Python Packages", self._validate_packages),
            ("TypeScript Tooling", self._validate_typescript),
            ("File Permissions", self._validate_permissions),
            ("Port Availability", self._validate_ports),
        ]
        
        results = []
        
        for name, validator in validations:
            result = validator()
            result["name"] = name
            results.append(result)
            
            if not result["passed"]:
                self.failures.append(name)
        
        all_passed = len(self.failures) == 0
        
        return all_passed, results
    
    def _validate_schema(self) -> Dict[str, Any]:
        """Validate database schema is up to date"""
        
        db_path = self.project_root / "backend" / "grace.db"
        
        if not db_path.exists():
            return {
                "passed": False,
                "critical": True,
                "issue": "Database file missing",
                "fix": "Run: .venv\\Scripts\\python.exe -m alembic upgrade head"
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            
            # Check critical columns
            required_checks = [
                ("verification_events", "passed", "Boolean column for verification results"),
                ("playbooks", "risk_level", "Risk level for governance"),
                ("playbooks", "autonomy_tier", "Autonomy tier for execution control"),
            ]
            
            missing = []
            
            for table, column, description in required_checks:
                cursor = conn.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                
                if column not in columns:
                    missing.append(f"{table}.{column} - {description}")
            
            conn.close()
            
            if missing:
                return {
                    "passed": False,
                    "critical": True,
                    "issue": f"Missing columns: {', '.join(missing)}",
                    "fix": "Run: .venv\\Scripts\\python.exe scripts\\fix_schema.py"
                }
            
            return {"passed": True, "critical": True}
            
        except Exception as e:
            return {
                "passed": False,
                "critical": True,
                "issue": f"Schema check failed: {e}",
                "fix": "Check database integrity"
            }
    
    def _validate_secrets(self) -> Dict[str, Any]:
        """Validate required secrets are present"""
        
        required = {
            "SECRET_KEY": "Application secret key",
            "DATABASE_URL": "Database connection string"
        }
        
        missing = []
        
        for secret, description in required.items():
            if not os.getenv(secret):
                missing.append(f"{secret} - {description}")
        
        if missing:
            return {
                "passed": False,
                "critical": True,
                "issue": f"Missing secrets: {', '.join(missing)}",
                "fix": "Add to .env file (see .env.example)"
            }
        
        return {"passed": True, "critical": True}
    
    def _validate_optional_secrets(self) -> Dict[str, Any]:
        """Check optional secrets (warns but doesn't fail)"""
        
        optional = {
            "GITHUB_TOKEN": "GitHub API access (60/hr without, 5000/hr with)",
            "AMP_API_KEY": "Amp AI integration",
            "OPENAI_API_KEY": "OpenAI models",
            "ANTHROPIC_API_KEY": "Claude models"
        }
        
        missing = []
        
        for secret, description in optional.items():
            if not os.getenv(secret):
                missing.append(f"{secret} - {description}")
        
        if missing:
            return {
                "passed": True,  # Don't fail boot
                "critical": False,
                "warning": f"Optional secrets missing: {len(missing)}",
                "details": missing
            }
        
        return {"passed": True, "critical": False}
    
    def _validate_encoding(self) -> Dict[str, Any]:
        """Validate UTF-8 encoding is configured"""
        
        try:
            # Test emoji output
            test_output = "✅"
            sys.stdout.write(test_output)
            sys.stdout.flush()
            
            # Check environment variable
            if os.getenv("PYTHONIOENCODING") != "utf-8":
                return {
                    "passed": True,  # Works but could be better
                    "critical": False,
                    "warning": "PYTHONIOENCODING not set to utf-8",
                    "fix": "Set $env:PYTHONIOENCODING='utf-8' in PowerShell"
                }
            
            return {"passed": True, "critical": True}
            
        except UnicodeEncodeError:
            return {
                "passed": False,
                "critical": True,
                "issue": "UTF-8 encoding not working",
                "fix": "Run: chcp 65001 in PowerShell and set PYTHONIOENCODING=utf-8"
            }
    
    def _validate_packages(self) -> Dict[str, Any]:
        """Validate critical Python packages"""
        
        critical = ["fastapi", "sqlalchemy", "uvicorn", "pydantic"]
        
        missing = []
        
        for package in critical:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            return {
                "passed": False,
                "critical": True,
                "issue": f"Missing packages: {', '.join(missing)}",
                "fix": "Run: .venv\\Scripts\\pip install -r backend\\requirements.txt"
            }
        
        return {"passed": True, "critical": True}
    
    def _validate_typescript(self) -> Dict[str, Any]:
        """Check TypeScript tooling availability"""
        
        frontend_path = self.project_root / "frontend"
        
        if not frontend_path.exists():
            return {
                "passed": True,
                "critical": False,
                "info": "No frontend directory - TypeScript checks skipped"
            }
        
        # Check if npm is available
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {
                    "passed": True,  # Don't fail boot
                    "critical": False,
                    "warning": "npm not available - TypeScript scans will be skipped"
                }
            
            return {"passed": True, "critical": False}
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {
                "passed": True,  # Don't fail boot
                "critical": False,
                "warning": "npm command not found - TypeScript scans disabled",
                "fix": "Install Node.js if you need TypeScript validation"
            }
    
    def _validate_permissions(self) -> Dict[str, Any]:
        """Check file system permissions"""
        
        critical_dirs = ["logs", "storage", "ml_artifacts"]
        
        issues = []
        
        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
            
            if not os.access(dir_path, os.W_OK):
                issues.append(f"{dir_name} not writable")
        
        if issues:
            return {
                "passed": False,
                "critical": True,
                "issue": f"Permission issues: {', '.join(issues)}",
                "fix": "Check directory permissions"
            }
        
        return {"passed": True, "critical": True}
    
    def _validate_ports(self) -> Dict[str, Any]:
        """Check if required ports are available"""
        
        import socket
        
        port = 8000
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            return {
                "passed": False,
                "critical": True,
                "issue": f"Port {port} already in use",
                "fix": "Stop existing Grace instance or use different port"
            }
        
        return {"passed": True, "critical": True}
    
    def generate_validation_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate human-readable validation report"""
        
        report = []
        report.append("=" * 80)
        report.append("BOOT VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append(f"Validations: {len(results)}")
        report.append(f"Passed: {len([r for r in results if r['passed']])}")
        report.append(f"Failed: {len([r for r in results if not r['passed']])}")
        report.append("")
        
        # Critical failures
        critical_failures = [r for r in results if not r["passed"] and r.get("critical")]
        if critical_failures:
            report.append("CRITICAL FAILURES:")
            report.append("-" * 40)
            for result in critical_failures:
                report.append(f"  ✗ {result['name']}")
                report.append(f"    Issue: {result['issue']}")
                report.append(f"    Fix: {result['fix']}")
                report.append("")
        
        # Warnings
        warnings = [r for r in results if r.get("warning")]
        if warnings:
            report.append("WARNINGS:")
            report.append("-" * 40)
            for result in warnings:
                report.append(f"  ⚠ {result['name']}")
                report.append(f"    {result['warning']}")
                if "fix" in result:
                    report.append(f"    Fix: {result['fix']}")
                report.append("")
        
        # Passed
        passed = [r for r in results if r["passed"] and not r.get("warning")]
        if passed:
            report.append(f"PASSED: {len(passed)} checks")
            report.append("-" * 40)
            for result in passed:
                report.append(f"  ✓ {result['name']}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


# Global instance
boot_validator = BootValidator()
