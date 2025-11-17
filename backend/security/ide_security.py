"""IDE Security Scanner - Uses Hunter rules for file and code scanning"""
import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .hunter import hunter
from backend.models.governance_models import SecurityRule
from backend.models import async_session
from sqlalchemy import select


class SecurityScanner:
    """Scans files and code for security issues using Hunter rules"""
    
    def __init__(self):
        self.patterns = {
            'sql_injection': [
                r"execute\s*\(\s*['\"].*%s.*['\"]",
                r"cursor\.execute\s*\(.*\+.*\)",
                r"raw\s*\(.*\+.*\)",
                r"SELECT.*FROM.*WHERE.*\+",
            ],
            'xss': [
                r"innerHTML\s*=",
                r"document\.write\s*\(",
                r"eval\s*\(",
                r"dangerouslySetInnerHTML",
            ],
            'dangerous_imports': [
                r"import\s+eval",
                r"from\s+os\s+import\s+system",
                r"import\s+exec",
                r"__import__\s*\(",
                r"importlib\.import_module",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"os\.path\.join\s*\(.*\.\..*\)",
                r"open\s*\(.*\.\..*\)",
            ],
            'hardcoded_secrets': [
                r"password\s*=\s*['\"][^'\"]{3,}['\"]",
                r"api[_-]?key\s*=\s*['\"][^'\"]{10,}['\"]",
                r"secret\s*=\s*['\"][^'\"]{10,}['\"]",
                r"token\s*=\s*['\"][^'\"]{20,}['\"]",
            ],
            'command_injection': [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(.*shell\s*=\s*True",
                r"eval\s*\(",
                r"exec\s*\(",
            ],
        }
        
        self.severity_map = {
            'sql_injection': 'critical',
            'command_injection': 'critical',
            'xss': 'high',
            'hardcoded_secrets': 'high',
            'path_traversal': 'medium',
            'dangerous_imports': 'medium',
        }
    
    async def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            language = self._detect_language(file_path)
            return await self.scan_code(content, language)
        
        except Exception as e:
            return [{
                'rule_name': 'scan_error',
                'severity': 'low',
                'line_number': 0,
                'issue': f'Failed to scan file: {str(e)}',
                'suggestion': 'Check file permissions and encoding'
            }]
    
    async def scan_code(self, code_string: str, language: str) -> List[Dict[str, Any]]:
        """Scan code string for security issues"""
        issues = []
        lines = code_string.split('\n')
        
        # Pattern-based scanning
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            'rule_name': category,
                            'severity': self.severity_map.get(category, 'medium'),
                            'line_number': line_num,
                            'issue': f'Detected {category.replace("_", " ")}: {line.strip()[:80]}',
                            'suggestion': self._get_suggestion(category),
                            'code_snippet': line.strip()
                        })
        
        # Hunter rule-based scanning
        async with async_session() as session:
            result = await session.execute(select(SecurityRule))
            rules = result.scalars().all()
            
            for rule in rules:
                try:
                    condition = json.loads(rule.condition)
                    keywords = condition.get('keywords', [])
                    
                    for keyword in keywords:
                        for line_num, line in enumerate(lines, 1):
                            if keyword.lower() in line.lower():
                                issues.append({
                                    'rule_name': rule.name,
                                    'severity': rule.severity,
                                    'line_number': line_num,
                                    'issue': f'{rule.description}: {line.strip()[:80]}',
                                    'suggestion': f'Review Hunter rule: {rule.name}',
                                    'code_snippet': line.strip()
                                })
                except:
                    pass
        
        return issues
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.sql': 'sql',
        }
        return lang_map.get(ext, 'unknown')
    
    def _get_suggestion(self, category: str) -> str:
        """Get fix suggestion for a category"""
        suggestions = {
            'sql_injection': 'Use parameterized queries or ORM methods',
            'xss': 'Sanitize user input and use safe DOM methods',
            'dangerous_imports': 'Remove dangerous imports like eval, exec, __import__',
            'path_traversal': 'Validate and sanitize file paths, use os.path.normpath()',
            'hardcoded_secrets': 'Move secrets to environment variables or secret manager',
            'command_injection': 'Avoid shell=True, use subprocess with list arguments',
        }
        return suggestions.get(category, 'Review and fix security issue')


security_scanner = SecurityScanner()
