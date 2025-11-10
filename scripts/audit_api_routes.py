"""
API Route Audit Script
Analyzes all route files to identify missing response_model declarations
"""

import os
import re
from pathlib import Path
from collections import defaultdict

ROUTES_DIR = Path(__file__).parent.parent / "backend" / "routes"

def extract_endpoints(file_path):
    """Extract all endpoint definitions from a route file"""
    endpoints = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = r'@router\.(get|post|put|delete|patch)\([^)]*\)'
    matches = re.finditer(pattern, content, re.MULTILINE)
    
    for match in matches:
        decorator = match.group(0)
        has_response_model = 'response_model' in decorator
        
        line_num = content[:match.start()].count('\n') + 1
        
        path_match = re.search(r'["\']([^"\']+)["\']', decorator)
        path = path_match.group(1) if path_match else "unknown"
        
        method = match.group(1).upper()
        
        endpoints.append({
            'file': file_path.name,
            'line': line_num,
            'method': method,
            'path': path,
            'has_response_model': has_response_model,
            'decorator': decorator
        })
    
    return endpoints

def main():
    all_endpoints = []
    
    for py_file in ROUTES_DIR.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        
        endpoints = extract_endpoints(py_file)
        all_endpoints.extend(endpoints)
    
    missing_response_model = [ep for ep in all_endpoints if not ep['has_response_model']]
    has_response_model = [ep for ep in all_endpoints if ep['has_response_model']]
    
    print("=" * 80)
    print("API ROUTE AUDIT REPORT")
    print("=" * 80)
    print(f"\nTotal Endpoints: {len(all_endpoints)}")
    print(f"With response_model: {len(has_response_model)} ({len(has_response_model)/len(all_endpoints)*100:.1f}%)")
    print(f"Missing response_model: {len(missing_response_model)} ({len(missing_response_model)/len(all_endpoints)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("ENDPOINTS MISSING response_model (Priority Order)")
    print("=" * 80)
    
    by_file = defaultdict(list)
    for ep in missing_response_model:
        by_file[ep['file']].append(ep)
    
    for file_name in sorted(by_file.keys()):
        print(f"\n{file_name}:")
        for ep in by_file[file_name]:
            print(f"  Line {ep['line']}: {ep['method']} {ep['path']}")
    
    print("\n" + "=" * 80)
    print("FILES WITH COMPLETE COVERAGE")
    print("=" * 80)
    
    files_with_endpoints = defaultdict(lambda: {'total': 0, 'with_model': 0})
    for ep in all_endpoints:
        files_with_endpoints[ep['file']]['total'] += 1
        if ep['has_response_model']:
            files_with_endpoints[ep['file']]['with_model'] += 1
    
    for file_name in sorted(files_with_endpoints.keys()):
        stats = files_with_endpoints[file_name]
        coverage = stats['with_model'] / stats['total'] * 100
        if coverage == 100:
            print(f"  [OK] {file_name} ({stats['total']} endpoints)")
    
    print("\n" + "=" * 80)
    print("PRIORITY FIXES (Files with <50% coverage)")
    print("=" * 80)
    
    priority_files = []
    for file_name, stats in files_with_endpoints.items():
        coverage = stats['with_model'] / stats['total'] * 100
        if coverage < 50:
            priority_files.append((file_name, coverage, stats['total'], stats['with_model']))
    
    for file_name, coverage, total, with_model in sorted(priority_files, key=lambda x: x[1]):
        print(f"  {file_name}: {with_model}/{total} ({coverage:.0f}%)")

if __name__ == "__main__":
    main()
