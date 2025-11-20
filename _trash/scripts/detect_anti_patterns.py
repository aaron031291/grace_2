#!/usr/bin/env python3
"""
Anti-Pattern Detection Script
Scans codebase for performance/architecture issues found by Devin
Run: python scripts/detect_anti_patterns.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

class AntiPatternDetector:
    def __init__(self, root_path: Path):
        self.root = root_path
        self.issues = []
        
    def scan_all(self):
        """Run all anti-pattern checks"""
        print("[SCAN] Scanning for anti-patterns...\n")
        
        self.check_unbounded_queries()
        self.check_sync_sleep()
        self.check_python_filtering()
        self.check_json_parsing()
        self.check_import_paths()
        
        return self.report()
    
    def check_unbounded_queries(self):
        """Detect .all() without pagination"""
        print("[CHECK] Checking for unbounded database queries...")
        pattern = re.compile(r'\.all\(\)')
        
        for py_file in self.root.glob('backend/**/*.py'):
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line) and ('scalars' in line or 'execute' in line or 'query' in line):
                        # Check if .limit() is on same or previous line
                        if '.limit(' not in line:
                            self.issues.append({
                                'severity': 'HIGH',
                                'type': 'Unbounded Query',
                                'file': str(py_file.relative_to(self.root)),
                                'line': i,
                                'code': line.strip(),
                                'fix': 'Add .limit() before .all() or use pagination'
                            })
    
    def check_sync_sleep(self):
        """Detect time.sleep() in async code"""
        print("[CHECK] Checking for sync sleep in async contexts...")
        
        for py_file in self.root.glob('backend/**/*.py'):
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if 'time.sleep' in line:
                        # Check previous 5 lines for async def
                        context = ''.join(lines[max(0, i-5):i+1])
                        if 'async def' in context:
                            self.issues.append({
                                'severity': 'MEDIUM',
                                'type': 'Sync Sleep in Async',
                                'file': str(py_file.relative_to(self.root)),
                                'line': i + 1,
                                'code': line.strip(),
                                'fix': 'Use await asyncio.sleep() instead'
                            })
    
    def check_python_filtering(self):
        """Detect Python-level date filtering after queries"""
        print("[CHECK] Checking for Python-level filtering...")
        
        for py_file in self.root.glob('backend/**/*.py'):
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if re.search(r'for .* in .*\.all\(\):', line):
                        # Check next 10 lines for datetime operations
                        context = ''.join(lines[i:min(len(lines), i+10)])
                        if 'datetime' in context or 'timedelta' in context:
                            self.issues.append({
                                'severity': 'MEDIUM',
                                'type': 'Python-level Filtering',
                                'file': str(py_file.relative_to(self.root)),
                                'line': i + 1,
                                'code': line.strip(),
                                'fix': 'Move date filtering to SQL with .where() clauses'
                            })
    
    def check_json_parsing(self):
        """Detect inefficient JSON parsing"""
        print("[CHECK] Checking for inefficient JSON parsing...")
        pattern = re.compile(r'json\.loads\(.*\.read\(\)\)')
        
        for py_file in self.root.glob('backend/**/*.py'):
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        self.issues.append({
                            'severity': 'LOW',
                            'type': 'Inefficient JSON Parse',
                            'file': str(py_file.relative_to(self.root)),
                            'line': i,
                            'code': line.strip(),
                            'fix': 'Use json.load(stream) for streaming'
                        })
    
    def check_import_paths(self):
        """Verify canonical import paths"""
        print("[CHECK] Checking import paths...")
        bad_imports = [
            (r'from backend\.monitoring\.metrics_service import', 'Use: from backend.metrics_service import'),
            (r'from backend\.misc\.cognition_metrics import', 'Use: from backend.cognition_metrics import'),
        ]
        
        for py_file in self.root.glob('backend/**/*.py'):
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    for pattern_str, fix in bad_imports:
                        if re.search(pattern_str, line):
                            self.issues.append({
                                'severity': 'HIGH',
                                'type': 'Wrong Import Path',
                                'file': str(py_file.relative_to(self.root)),
                                'line': i,
                                'code': line.strip(),
                                'fix': fix
                            })
    
    def report(self) -> int:
        """Generate report and return exit code"""
        print("\n" + "="*80)
        print("ANTI-PATTERN DETECTION REPORT")
        print("="*80 + "\n")
        
        if not self.issues:
            print("[OK] No anti-patterns detected!\n")
            return 0
        
        # Group by severity
        high = [i for i in self.issues if i['severity'] == 'HIGH']
        medium = [i for i in self.issues if i['severity'] == 'MEDIUM']
        low = [i for i in self.issues if i['severity'] == 'LOW']
        
        print(f"Found {len(self.issues)} issues:")
        print(f"  [HIGH]: {len(high)}")
        print(f"  [MEDIUM]: {len(medium)}")
        print(f"  [LOW]: {len(low)}\n")
        
        for severity, issues in [('HIGH', high), ('MEDIUM', medium), ('LOW', low)]:
            if issues:
                print(f"\n{'='*80}")
                print(f"{severity} SEVERITY ISSUES")
                print('='*80)
                
                for issue in issues:
                    print(f"\nFile: {issue['file']}:{issue['line']}")
                    print(f"   Type: {issue['type']}")
                    print(f"   Code: {issue['code']}")
                    print(f"   Fix:  {issue['fix']}")
        
        print("\n" + "="*80)
        print(f"TOTAL ISSUES: {len(self.issues)}")
        print("="*80 + "\n")
        
        return 1 if high else 0  # Fail on HIGH severity


if __name__ == '__main__':
    root = Path(__file__).parent.parent
    detector = AntiPatternDetector(root)
    exit_code = detector.scan_all()
    sys.exit(exit_code)
