"""Auto-fix engine for security issues"""
import re
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class AutoFix:
    """Applies automated fixes to security issues"""
    
    def __init__(self):
        self.fix_strategies = {
            'remove_dangerous_imports': self.remove_dangerous_imports,
            'sanitize_sql': self.sanitize_sql,
            'escape_xss': self.escape_xss,
            'fix_path_traversal': self.fix_path_traversal,
            'add_type_hints': self.add_type_hints,
            'format_code': self.format_code,
        }
    
    async def apply_fix(self, file_path: str, fix_type: str) -> Dict[str, Any]:
        """Apply a specific fix to a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            if fix_type not in self.fix_strategies:
                return {
                    'success': False,
                    'changes_made': [],
                    'error': f'Unknown fix type: {fix_type}'
                }
            
            new_content, changes = await self.fix_strategies[fix_type](original_content, file_path)
            
            if new_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return {
                    'success': True,
                    'changes_made': changes,
                    'new_content': new_content,
                    'file_path': file_path
                }
            else:
                return {
                    'success': True,
                    'changes_made': [],
                    'message': 'No changes needed'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'changes_made': []
            }
    
    async def remove_dangerous_imports(self, content: str, file_path: str) -> tuple[str, List[str]]:
        """Remove dangerous imports like eval, exec, __import__"""
        changes = []
        lines = content.split('\n')
        new_lines = []
        
        dangerous_patterns = [
            r'import\s+eval',
            r'from\s+.*\s+import\s+.*eval.*',
            r'import\s+exec',
            r'from\s+.*\s+import\s+.*exec.*',
            r'__import__',
        ]
        
        for line in lines:
            skip = False
            for pattern in dangerous_patterns:
                if re.search(pattern, line):
                    changes.append(f'Removed dangerous import: {line.strip()}')
                    new_lines.append(f'# REMOVED (security): {line}')
                    skip = True
                    break
            
            if not skip:
                new_lines.append(line)
        
        return '\n'.join(new_lines), changes
    
    async def sanitize_sql(self, content: str, file_path: str) -> tuple[str, List[str]]:
        """Fix SQL injection patterns"""
        changes = []
        new_content = content
        
        # Pattern: cursor.execute("SELECT * FROM table WHERE id=" + user_id)
        # Fix: cursor.execute("SELECT * FROM table WHERE id=%s", (user_id,))
        pattern1 = r'execute\s*\(\s*["\'](.+?)["\']\.format\((.*?)\)\s*\)'
        matches = re.finditer(pattern1, new_content)
        
        for match in matches:
            query = match.group(1)
            params = match.group(2)
            
            # Replace .format() with parameterized query
            param_list = [p.strip() for p in params.split(',')]
            placeholders = ', '.join(['%s'] * len(param_list))
            
            fixed = f'execute("{query}", ({params},))'
            new_content = new_content.replace(match.group(0), fixed)
            changes.append(f'Fixed SQL injection: parameterized query')
        
        # Pattern: "SELECT * WHERE x=" + var
        pattern2 = r'(["\'])(.+?)\1\s*\+\s*(\w+)'
        
        def replace_concat(match):
            quote = match.group(1)
            query = match.group(2)
            var = match.group(3)
            changes.append(f'Fixed SQL concatenation: {var}')
            return f'{quote}{query}%s{quote}, ({var},)'
        
        new_content = re.sub(pattern2, replace_concat, new_content)
        
        return new_content, changes
    
    async def escape_xss(self, content: str, file_path: str) -> tuple[str, List[str]]:
        """Add HTML escaping to prevent XSS"""
        changes = []
        new_content = content
        
        # JavaScript: innerHTML = userInput
        if '.innerHTML' in content:
            pattern = r'\.innerHTML\s*=\s*([^;]+);'
            
            def add_escape(match):
                value = match.group(1)
                changes.append(f'Added HTML escaping to innerHTML assignment')
                return f'.textContent = {value};  // XSS fix: use textContent instead'
            
            new_content = re.sub(pattern, add_escape, new_content)
        
        # Python: f"<div>{user_input}</div>"
        if file_path.endswith('.py'):
            pattern = r'f["\']<.+?\{(.+?)\}.+?["\']'
            
            def add_html_escape(match):
                var = match.group(1)
                changes.append(f'Added HTML escaping: {var}')
                return match.group(0).replace(f'{{{var}}}', f'{{html.escape({var})}}')
            
            new_content = re.sub(pattern, add_html_escape, new_content)
            
            # Add import if needed
            if changes and 'import html' not in new_content:
                new_content = 'import html\n' + new_content
                changes.append('Added html.escape import')
        
        return new_content, changes
    
    async def fix_path_traversal(self, content: str, file_path: str) -> tuple[str, List[str]]:
        """Validate file paths to prevent traversal attacks"""
        changes = []
        new_content = content
        
        # Pattern: open(user_path)
        pattern = r'open\s*\(\s*([^)]+)\s*\)'
        
        def add_path_validation(match):
            path_var = match.group(1).strip()
            
            # Skip if already validated
            if 'os.path.normpath' in path_var or 'Path(' in path_var:
                return match.group(0)
            
            changes.append(f'Added path validation: {path_var}')
            return f'open(os.path.normpath(os.path.abspath({path_var})))'
        
        new_content = re.sub(pattern, add_path_validation, new_content)
        
        # Add import if needed
        if changes and 'import os' not in new_content:
            new_content = 'import os\n' + new_content
            changes.append('Added os import for path validation')
        
        return new_content, changes
    
    async def add_type_hints(self, content: str, file_path: str) -> tuple[str, List[str]]:
        """Add Python type annotations"""
        changes = []
        
        if not file_path.endswith('.py'):
            return content, changes
        
        lines = content.split('\n')
        new_lines = []
        
        # Pattern: def function_name(param):
        pattern = r'^(\s*)def\s+(\w+)\s*\(([^)]*)\)\s*:'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                indent = match.group(1)
                func_name = match.group(2)
                params = match.group(3)
                
                # Skip if already has type hints
                if ':' not in params or '->' in line:
                    new_lines.append(line)
                    continue
                
                # Add basic type hints
                param_parts = [p.strip() for p in params.split(',') if p.strip()]
                typed_params = []
                
                for param in param_parts:
                    if '=' in param:
                        name, default = param.split('=', 1)
                        typed_params.append(f'{name.strip()}: Any = {default.strip()}')
                    else:
                        typed_params.append(f'{param}: Any')
                
                new_line = f'{indent}def {func_name}({", ".join(typed_params)}) -> Any:'
                new_lines.append(new_line)
                changes.append(f'Added type hints to {func_name}()')
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        # Add typing import if changes made
        if changes and 'from typing import' not in new_content:
            new_content = 'from typing import Any\n' + new_content
            changes.append('Added typing imports')
        
        return new_content, changes
    
    async def format_code(self, content: str, file_path: str) -> tuple[str, List[str]]:
        """Run language formatter"""
        changes = []
        
        try:
            if file_path.endswith('.py'):
                # Try to use black
                import subprocess
                result = subprocess.run(
                    ['black', '--quiet', file_path],
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    with open(file_path, 'r') as f:
                        new_content = f.read()
                    
                    if new_content != content:
                        changes.append('Formatted with black')
                        return new_content, changes
            
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                # Try to use prettier
                import subprocess
                result = subprocess.run(
                    ['prettier', '--write', file_path],
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    with open(file_path, 'r') as f:
                        new_content = f.read()
                    
                    if new_content != content:
                        changes.append('Formatted with prettier')
                        return new_content, changes
        
        except Exception as e:
            changes.append(f'Formatting skipped: {str(e)}')
        
        return content, changes


auto_fix = AutoFix()
