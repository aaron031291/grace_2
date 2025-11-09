"""
Autonomous System Improver
Proactively hunts for errors, warnings, and improvements in the codebase
Fixes issues and commits to GitHub automatically
"""

import asyncio
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

from .action_contract import contract_verifier
from .governance import governance_engine
from .logging_utils import log_event

logger = logging.getLogger(__name__)

class AutonomousImprover:
    """Proactive system improvement agent"""
    
    def __init__(self):
        self.running = False
        self.scan_interval = 300  # 5 minutes
        self.fixes_applied = 0
        self.errors_found = 0
        
    async def start(self):
        """Start autonomous improvement loop"""
        self.running = True
        logger.info("[AUTONOMOUS] Starting proactive improvement loop...")
        asyncio.create_task(self._improvement_loop())
        
    async def stop(self):
        """Stop improvement loop"""
        self.running = False
        logger.info("[AUTONOMOUS] Stopping improvement loop")
        
    async def _improvement_loop(self):
        """Main autonomous loop"""
        while self.running:
            try:
                await self._run_improvement_cycle()
            except Exception as e:
                logger.error(f"[AUTONOMOUS] Error in improvement cycle: {e}")
            
            await asyncio.sleep(self.scan_interval)
    
    async def _run_improvement_cycle(self):
        """Single improvement cycle"""
        logger.info("[AUTONOMOUS] 🔍 Starting improvement scan...")
        
        issues = []
        
        # 1. Scan for Python errors/warnings
        logger.info("[AUTONOMOUS] Checking Python codebase...")
        python_issues = await self._scan_python_errors()
        issues.extend(python_issues)
        
        # 2. Scan for TypeScript errors
        logger.info("[AUTONOMOUS] Checking TypeScript frontend...")
        ts_issues = await self._scan_typescript_errors()
        issues.extend(ts_issues)
        
        # 3. Check for security vulnerabilities
        logger.info("[AUTONOMOUS] Scanning for security issues...")
        security_issues = await self._scan_security()
        issues.extend(security_issues)
        
        # 4. Check for optimization opportunities
        logger.info("[AUTONOMOUS] Looking for optimizations...")
        optimizations = await self._find_optimizations()
        issues.extend(optimizations)
        
        self.errors_found += len(issues)
        
        if not issues:
            logger.info("[AUTONOMOUS] ✅ No issues found. System is healthy!")
            return
        
        logger.info(f"[AUTONOMOUS] ⚠️ Found {len(issues)} issues")
        
        # 5. Apply fixes autonomously
        fixes_applied = await self._apply_fixes(issues)
        
        if fixes_applied > 0:
            # 6. Commit and push to GitHub
            await self._commit_and_push(fixes_applied, issues)
    
    async def _scan_python_errors(self) -> List[Dict[str, Any]]:
        """Scan Python code for errors"""
        issues = []
        
        try:
            # Run mypy type checking
            result = subprocess.run(
                ['python', '-m', 'mypy', 'backend', '--ignore-missing-imports'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                for line in result.stdout.split('\n'):
                    if 'error:' in line.lower():
                        issues.append({
                            'type': 'python_error',
                            'severity': 'high',
                            'description': line.strip(),
                            'fixable': True
                        })
        except Exception as e:
            logger.warning(f"[AUTONOMOUS] Mypy scan failed: {e}")
        
        # Check for common issues
        backend_path = Path(__file__).parent
        for py_file in backend_path.rglob('*.py'):
            try:
                content = py_file.read_text()
                
                # Check for TODO comments (skip safe/intentional tags)
                if 'TODO:' in content:
                    # Skip if TODO is tagged as safe/intentional
                    safe_todo_tags = ['TODO(SAFE)', 'TODO(ROADMAP)', 'TODO(DESIGN)', 'TODO(FUTURE)']
                    
                    # Patterns that are safe even without tags
                    safe_patterns = [
                        'pass  # TODO:',  # Code generator stubs
                        '# TODO: Implement function logic',  # Generator output
                        '# TODO: Add assertions',  # Test generator
                        "if 'TODO:' in",  # Detection code itself
                        'TODO:' in line',  # Detection code
                    ]
                    
                    # Check if any TODOs in file are unsafe
                    has_unsafe_todo = False
                    for line in content.split('\n'):
                        if 'TODO:' in line:
                            # Skip if has safe tag
                            if any(tag in line for tag in safe_todo_tags):
                                continue
                            # Skip if matches safe pattern
                            if any(pattern in line for pattern in safe_patterns):
                                continue
                            # This TODO is untagged and not a safe pattern
                            has_unsafe_todo = True
                            break
                    
                    if has_unsafe_todo:
                        issues.append({
                            'type': 'todo',
                            'severity': 'low',
                            'file': str(py_file),
                            'description': 'Untagged TODO comment found',
                            'fixable': False
                        })
                
                # Note: print() check disabled - too noisy for script files
                # Many files legitimately use print() for CLI output
            except:
                pass
        
        return issues
    
    async def _scan_typescript_errors(self) -> List[Dict[str, Any]]:
        """Scan TypeScript for errors"""
        issues = []
        
        # Check if frontend directory exists
        frontend_path = Path(__file__).parent.parent / 'frontend'
        if not frontend_path.exists():
            logger.debug(f"[AUTONOMOUS] No frontend directory, skipping TypeScript scan")
            return issues
        
        # Check if npm is available
        try:
            npm_check = subprocess.run(['npm', '--version'], capture_output=True, timeout=5)
            if npm_check.returncode != 0:
                logger.debug(f"[AUTONOMOUS] npm not available, skipping TypeScript scan")
                return issues
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.debug(f"[AUTONOMOUS] npm command not found, skipping TypeScript scan")
            return issues
        
        try:
            result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=str(frontend_path),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                for line in result.stderr.split('\n'):
                    if 'error' in line.lower():
                        issues.append({
                            'type': 'typescript_error',
                            'severity': 'high',
                            'description': line.strip(),
                            'fixable': True
                        })
        except Exception as e:
            logger.debug(f"[AUTONOMOUS] TypeScript scan skipped: {e}")
        
        return issues
    
    async def _scan_security(self) -> List[Dict[str, Any]]:
        """Scan for security vulnerabilities"""
        issues = []
        
        # Check for hardcoded secrets
        backend_path = Path(__file__).parent
        dangerous_patterns = ['password =', 'api_key =', 'secret =', 'token =']
        
        for py_file in backend_path.rglob('*.py'):
            try:
                content = py_file.read_text()
                for pattern in dangerous_patterns:
                    if pattern in content.lower() and 'example' not in content.lower():
                        issues.append({
                            'type': 'security',
                            'severity': 'critical',
                            'file': str(py_file),
                            'description': f'Possible hardcoded secret: {pattern}',
                            'fixable': False  # Manual review needed
                        })
            except:
                pass
        
        return issues
    
    async def _find_optimizations(self) -> List[Dict[str, Any]]:
        """Find optimization opportunities"""
        issues = []
        
        # Check for missing response_model (we already fixed most but check for new ones)
        # Check for missing indexes on database columns
        # Check for N+1 query patterns
        # etc.
        
        return issues
    
    async def _apply_fixes(self, issues: List[Dict[str, Any]]) -> int:
        """Apply autonomous fixes"""
        fixes_applied = 0
        
        for issue in issues:
            if not issue.get('fixable'):
                logger.info(f"[AUTONOMOUS] ⏭️ Skipping non-fixable: {issue['description']}")
                continue
            
            # Check governance approval
            can_fix = await self._check_governance(issue)
            if not can_fix:
                logger.info(f"[AUTONOMOUS] 🚫 Governance blocked fix: {issue['description']}")
                continue
            
            # Apply fix based on type
            if issue['type'] == 'code_quality':
                fixed = await self._fix_code_quality(issue)
            elif issue['type'] == 'python_error':
                fixed = await self._fix_python_error(issue)
            elif issue['type'] == 'typescript_error':
                fixed = await self._fix_typescript_error(issue)
            else:
                fixed = False
            
            if fixed:
                fixes_applied += 1
                self.fixes_applied += 1
                logger.info(f"[AUTONOMOUS] ✅ Fixed: {issue['description']}")
        
        return fixes_applied
    
    async def _check_governance(self, issue: Dict[str, Any]) -> bool:
        """Check if fix is allowed by governance"""
        result = await governance_engine.check_action(
            actor="autonomous_improver",
            action="fix_code_issue",
            resource=issue.get('file', 'codebase'),
            context=issue
        )
        return result.get('approved', False)
    
    async def _fix_code_quality(self, issue: Dict[str, Any]) -> bool:
        """Fix code quality issues"""
        try:
            file_path = issue.get('file')
            if not file_path:
                return False
            
            # Replace print() with logger
            if 'print()' in issue['description']:
                content = Path(file_path).read_text()
                # Simple replacement (real implementation would be smarter)
                # This is a stub - actual implementation would parse AST
                logger.info(f"[AUTONOMOUS] Would fix print() in {file_path}")
                return False  # Don't actually fix yet
            
            return False
        except Exception as e:
            logger.error(f"[AUTONOMOUS] Fix failed: {e}")
            return False
    
    async def _fix_python_error(self, issue: Dict[str, Any]) -> bool:
        """Fix Python errors"""
        # Stub for now - would use AST manipulation
        return False
    
    async def _fix_typescript_error(self, issue: Dict[str, Any]) -> bool:
        """Fix TypeScript errors"""
        # Stub for now
        return False
    
    async def _commit_and_push(self, fixes_count: int, issues: List[Dict[str, Any]]):
        """Commit fixes and push to GitHub"""
        try:
            # Create contract for this action
            contract = await contract_verifier.create_contract(
                action_type="autonomous_code_improvement",
                expected_effect={
                    "fixes_applied": fixes_count,
                    "issues_addressed": [i['description'] for i in issues[:5]]
                }
            )
            
            # Git operations
            repo_path = Path(__file__).parent.parent
            
            # Add changes
            result = subprocess.run(
                ['git', 'add', '-A'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"[AUTONOMOUS] Git add failed: {result.stderr}")
                return
            
            # Commit
            commit_msg = f"""[AUTONOMOUS] Applied {fixes_count} fixes

Issues addressed:
{chr(10).join(f'- {i["description"][:80]}' for i in issues[:5])}

Generated by: Grace Autonomous Improver
Contract ID: {contract.id if contract else 'N/A'}
Timestamp: {datetime.utcnow().isoformat()}
"""
            
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                if 'nothing to commit' not in result.stdout:
                    logger.error(f"[AUTONOMOUS] Git commit failed: {result.stderr}")
                return
            
            # Push to GitHub
            result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"[AUTONOMOUS] 🚀 Pushed {fixes_count} fixes to GitHub!")
                await log_event(
                    "autonomous_git_push",
                    "autonomous_improver",
                    {"fixes": fixes_count, "contract_id": contract.id if contract else None}
                )
            else:
                logger.error(f"[AUTONOMOUS] Git push failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"[AUTONOMOUS] Commit/push failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "running": self.running,
            "scan_interval_seconds": self.scan_interval,
            "fixes_applied": self.fixes_applied,
            "errors_found": self.errors_found,
            "mode": "proactive_hunter"
        }

# Global instance
autonomous_improver = AutonomousImprover()
