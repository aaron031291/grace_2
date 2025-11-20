#!/usr/bin/env python3
"""
Quick Syntax Check - Find all current syntax errors
"""

import ast
import sys
from pathlib import Path

def check_syntax():
    """Quick syntax check of all Python files"""
    print("QUICK SYNTAX CHECK")
    print("=" * 40)
    
    errors = []
    total_files = 0
    
    for py_file in Path('.').rglob('*.py'):
        if any(part.startswith('.') for part in py_file.parts):
            continue  # Skip hidden directories
            
        total_files += 1
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                ast.parse(content)
            except SyntaxError as e:
                errors.append({
                    'file': str(py_file),
                    'line': e.lineno,
                    'message': e.msg,
                    'text': e.text.strip() if e.text else ''
                })
                
        except Exception as e:
            print(f"Could not read {py_file}: {e}")
    
    print(f"Scanned {total_files} Python files")
    print(f"Found {len(errors)} syntax errors")
    
    if errors:
        print("\nSYNTAX ERRORS FOUND:")
        print("-" * 40)
        
        for error in errors:
            print(f"\n{error['file']}")
            print(f"   Line {error['line']}: {error['message']}")
            if error['text']:
                print(f"   Code: {error['text']}")
    else:
        print("\nNO SYNTAX ERRORS FOUND!")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = check_syntax()
    sys.exit(0 if success else 1)