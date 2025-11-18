#!/usr/bin/env python3
"""
Comprehensive Syntax Error Fixer
Scans entire codebase and fixes all Python syntax errors
"""

import ast
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import subprocess

class SyntaxErrorFixer:
    def __init__(self):
        self.fixed_files = []
        self.errors_found = 0
        self.errors_fixed = 0
        
    def scan_and_fix_all(self) -> Dict[str, Any]:
        """Scan entire codebase and fix all syntax errors"""
        print("🔍 COMPREHENSIVE SYNTAX ERROR SCAN & FIX")
        print("=" * 60)
        
        # Directories to scan
        scan_dirs = ['backend', 'scripts', 'tests', 'cli']
        
        all_files = []
        for scan_dir in scan_dirs:
            if Path(scan_dir).exists():
                all_files.extend(Path(scan_dir).rglob("*.py"))
        
        print(f"📁 Scanning {len(all_files)} Python files...")
        
        for py_file in all_files:
            self._check_and_fix_file(py_file)
        
        # Final verification
        print(f"\n🔍 Running final syntax verification...")
        remaining_errors = self._verify_all_syntax()
        
        return {
            'files_scanned': len(all_files),
            'errors_found': self.errors_found,
            'errors_fixed': self.errors_fixed,
            'files_fixed': len(self.fixed_files),
            'remaining_errors': remaining_errors,
            'success': remaining_errors == 0
        }
    
    def _check_and_fix_file(self, file_path: Path) -> bool:
        """Check and fix syntax errors in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for syntax errors
            try:
                ast.parse(content)
                return True  # No syntax errors
            except SyntaxError as e:
                print(f"\n❌ {file_path} - Line {e.lineno}: {e.msg}")
                self.errors_found += 1
                
                # Try to fix the error
                fixed_content = self._fix_syntax_error(content, e, file_path)
                
                if fixed_content != content:
                    # Write fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    # Verify fix worked
                    try:
                        ast.parse(fixed_content)
                        print(f"✅ Fixed: {file_path}")
                        self.errors_fixed += 1
                        self.fixed_files.append(str(file_path))
                        return True
                    except SyntaxError:
                        print(f"⚠️ Could not auto-fix: {file_path}")
                        return False
                
        except Exception as e:
            print(f"⚠️ Could not process {file_path}: {e}")
            return False
        
        return True
    
    def _fix_syntax_error(self, content: str, error: SyntaxError, file_path: Path) -> str:
        """Apply common syntax error fixes"""
        lines = content.split('\n')
        error_line_idx = error.lineno - 1 if error.lineno else 0
        
        # Common fixes
        if error_line_idx < len(lines):
            line = lines[error_line_idx]
            
            # Fix 1: Remove XML edit tags left in code
            if '</code></edit_file>' in line:
                lines[error_line_idx] = line.replace('</code></edit_file>', '')
                return '\n'.join(lines)
            
            # Fix 2: Missing colons after if/for/while/def/class
            if re.search(r'(if|for|while|def|class|try|except|finally|with)\s+.*[^:]$', line.strip()):
                if not line.strip().endswith(':'):
                    lines[error_line_idx] = line + ':'
                    return '\n'.join(lines)
            
            # Fix 3: Unclosed parentheses/brackets
            if '(' in line and line.count('(') > line.count(')'):
                lines[error_line_idx] = line + ')'
                return '\n'.join(lines)
            
            # Fix 4: Missing quotes
            if line.count('"') % 2 == 1:
                lines[error_line_idx] = line + '"'
                return '\n'.join(lines)
            
            # Fix 5: Concatenated statements (missing newline)
            if re.search(r'\)\s*[a-zA-Z_]', line):
                # Split at the boundary
                match = re.search(r'(\))\s*([a-zA-Z_].*)', line)
                if match:
                    lines[error_line_idx] = line[:match.start(2)]
                    lines.insert(error_line_idx + 1, match.group(2))
                    return '\n'.join(lines)
        
        # Fix 6: Try block without except
        if 'try' in content and error.msg and 'expected' in error.msg:
            # Add basic except block
            try_pattern = r'(\s*try:\s*\n(?:\s+.*\n)*)'
            match = re.search(try_pattern, content)
            if match:
                try_block = match.group(1)
                indent = len(match.group(1).split('\n')[0]) - len(match.group(1).split('\n')[0].lstrip())
                except_block = f"{' ' * indent}except Exception as e:\n{' ' * (indent + 4)}pass\n"
                content = content.replace(try_block, try_block + except_block)
                return content
        
        return content
    
    def _verify_all_syntax(self) -> int:
        """Verify all Python files have valid syntax"""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'compileall', '-q', 
                'backend', 'scripts', 'tests', 'cli'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ All files have valid syntax!")
                return 0
            else:
                # Count remaining errors
                error_lines = [line for line in result.stderr.split('\n') if 'SyntaxError' in line]
                print(f"❌ {len(error_lines)} syntax errors remain")
                return len(error_lines)
                
        except Exception as e:
            print(f"⚠️ Could not verify syntax: {e}")
            return -1

def main():
    """Run comprehensive syntax fix"""
    fixer = SyntaxErrorFixer()
    results = fixer.scan_and_fix_all()
    
    print("\n" + "=" * 60)
    print("SYNTAX FIX SUMMARY")
    print("=" * 60)
    print(f"Files scanned: {results['files_scanned']}")
    print(f"Errors found: {results['errors_found']}")
    print(f"Errors fixed: {results['errors_fixed']}")
    print(f"Files modified: {results['files_fixed']}")
    print(f"Remaining errors: {results['remaining_errors']}")
    
    if results['success']:
        print("\n🎉 ALL SYNTAX ERRORS FIXED!")
        return True
    else:
        print(f"\n⚠️ {results['remaining_errors']} errors need manual review")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)