"""
Pre-flight Validation System
Grace validates code BEFORE systems start to catch errors early
"""

import ast
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import logging

from .code_understanding import code_understanding
from .immutable_log import ImmutableLog

logger = logging.getLogger(__name__)


class PreflightValidator:
    """
    Validates code before startup to catch errors early
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.validation_rules = []
        self._load_validation_rules()
    
    def _load_validation_rules(self):
        """Load validation rules"""
        self.validation_rules = [
            {
                'name': 'syntax_check',
                'description': 'Check Python syntax is valid',
                'severity': 'critical',
                'validator': self._check_syntax
            },
            {
                'name': 'import_check',
                'description': 'Verify all imports exist',
                'severity': 'high',
                'validator': self._check_imports
            },
            {
                'name': 'await_async_check',
                'description': 'Verify await is only used on async functions',
                'severity': 'high',
                'validator': self._check_await_usage
            },
            {
                'name': 'dangerous_patterns',
                'description': 'Detect dangerous code patterns',
                'severity': 'high',
                'validator': self._check_dangerous_patterns
            }
        ]
    
    async def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a single Python file
        
        Returns:
            {
                'valid': bool,
                'errors': [...],
                'warnings': [...],
                'suggestions': [...]
            }
        """
        result = {
            'file': file_path,
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Run all validators
            for rule in self.validation_rules:
                try:
                    violations = await rule['validator'](code, file_path)
                    
                    if violations:
                        if rule['severity'] in ['critical', 'high']:
                            result['errors'].extend(violations)
                            result['valid'] = False
                        elif rule['severity'] == 'medium':
                            result['warnings'].extend(violations)
                        else:
                            result['suggestions'].extend(violations)
                
                except Exception as e:
                    logger.warning(f"Validator {rule['name']} failed: {e}")
        
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'rule': 'file_read',
                'message': f"Cannot read file: {e}"
            })
        
        return result
    
    async def validate_directory(self, directory: str, pattern: str = "*.py") -> Dict[str, Any]:
        """
        Validate all Python files in directory
        
        Returns summary of validation results
        """
        dir_path = Path(directory)
        files = list(dir_path.glob(f"**/{pattern}"))
        
        results = {
            'directory': directory,
            'files_scanned': 0,
            'files_valid': 0,
            'files_invalid': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'file_results': []
        }
        
        for file_path in files:
            file_result = await self.validate_file(str(file_path))
            results['file_results'].append(file_result)
            results['files_scanned'] += 1
            
            if file_result['valid']:
                results['files_valid'] += 1
            else:
                results['files_invalid'] += 1
            
            results['total_errors'] += len(file_result['errors'])
            results['total_warnings'] += len(file_result['warnings'])
        
        logger.info(f"[PREFLIGHT] Validated {results['files_scanned']} files: "
                   f"{results['files_invalid']} invalid, {results['total_errors']} errors")
        
        return results
    
    async def _check_syntax(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Check if Python syntax is valid"""
        violations = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            violations.append({
                'rule': 'syntax_check',
                'line': e.lineno,
                'message': f"Syntax error: {e.msg}",
                'fix_suggestion': 'Check syntax at indicated line'
            })
        
        return violations
    
    async def _check_imports(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Check if imports exist (basic check)"""
        violations = []
        
        # Parse imports
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check if module looks suspicious
                        if 'eval' in alias.name or 'exec' in alias.name:
                            violations.append({
                                'rule': 'dangerous_import',
                                'line': node.lineno,
                                'message': f"Dangerous import: {alias.name}",
                                'fix_suggestion': 'Remove dangerous import'
                            })
        
        except:
            pass
        
        return violations
    
    async def _check_await_usage(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Check for incorrect await usage"""
        violations = []
        
        # Look for 'await' used on non-async calls
        # This is complex - simplified version
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for common patterns of incorrect await
            if 'await' in line:
                # Check for patterns like: await some_function.subscribe(
                if re.search(r'await\s+\w+\.subscribe\(', line):
                    violations.append({
                        'rule': 'incorrect_await',
                        'line': i,
                        'message': 'Possible incorrect await on sync function (subscribe)',
                        'fix_suggestion': 'Check if subscribe() is actually async'
                    })
                
                # Check for: await get_something()  where get_something returns an object
                if re.search(r'await\s+get_\w+\(\)\s*$', line.strip()):
                    violations.append({
                        'rule': 'possible_incorrect_await',
                        'line': i,
                        'message': 'Possible await on non-async getter function',
                        'fix_suggestion': 'Verify function is async'
                    })
        
        return violations
    
    async def _check_dangerous_patterns(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Check for dangerous code patterns"""
        violations = []
        
        dangerous = [
            (r'rm\s+-rf', 'Dangerous deletion command'),
            (r'DROP\s+TABLE', 'Destructive SQL'),
            (r'eval\(', 'Use of eval()'),
            (r'exec\(', 'Use of exec()'),
            (r'__import__\(', 'Dynamic import'),
            (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded password')
        ]
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, message in dangerous:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        'rule': 'dangerous_pattern',
                        'line': i,
                        'message': message,
                        'fix_suggestion': f'Remove or refactor: {line.strip()[:50]}'
                    })
        
        return violations
    
    async def validate_before_startup(self, directories: List[str]) -> bool:
        """
        Validate all code before startup
        
        Returns True if all valid, False if errors found
        """
        logger.info("[PREFLIGHT] Running pre-flight validation...")
        
        all_valid = True
        total_errors = 0
        
        for directory in directories:
            result = await self.validate_directory(directory)
            
            if result['files_invalid'] > 0:
                all_valid = False
                total_errors += result['total_errors']
                
                logger.warning(f"[PREFLIGHT] WARNING - {directory}: {result['files_invalid']} invalid files")
        
        if all_valid:
            logger.info("[PREFLIGHT] OK - All pre-flight checks passed")
        else:
            logger.error(f"[PREFLIGHT] FAILED - Pre-flight validation failed: {total_errors} errors")
        
        return all_valid


# Global instance
preflight_validator = PreflightValidator()
