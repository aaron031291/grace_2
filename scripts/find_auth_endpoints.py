"""
Find all endpoints that require authentication
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).parent.parent / "backend" / "routes"

def analyze_file(file_path):
    """Analyze a route file for auth requirements"""
    content = file_path.read_text(encoding='utf-8')
    
    # Find all route decorators
    route_pattern = r'@router\.(get|post|put|delete|patch)\([^)]*"([^"]+)"[^)]*\)'
    routes = re.finditer(route_pattern, content)
    
    results = []
    
    for match in routes:
        method = match.group(1).upper()
        path = match.group(2)
        start_pos = match.end()
        
        # Look ahead for function definition (next 500 chars)
        lookahead = content[start_pos:start_pos+500]
        
        # Check if Depends(get_current_user) appears
        requires_auth = 'Depends(get_current_user)' in lookahead or 'current_user' in lookahead
        
        results.append({
            'file': file_path.name,
            'method': method,
            'path': path,
            'requires_auth': requires_auth
        })
    
    return results

def main():
    all_endpoints = []
    
    for py_file in ROUTES_DIR.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        
        endpoints = analyze_file(py_file)
        all_endpoints.extend(endpoints)
    
    # Separate by auth requirement
    auth_required = [e for e in all_endpoints if e['requires_auth']]
    no_auth = [e for e in all_endpoints if not e['requires_auth']]
    
    print("=" * 80)
    print("AUTHENTICATION REQUIREMENTS AUDIT")
    print("=" * 80)
    print(f"\nTotal Endpoints: {len(all_endpoints)}")
    print(f"Require Auth: {len(auth_required)} ({len(auth_required)/len(all_endpoints)*100:.1f}%)")
    print(f"No Auth: {len(no_auth)} ({len(no_auth)/len(all_endpoints)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("ENDPOINTS REQUIRING AUTHENTICATION (by file)")
    print("=" * 80)
    
    from collections import defaultdict
    by_file = defaultdict(list)
    
    for e in auth_required:
        by_file[e['file']].append(e)
    
    for file_name in sorted(by_file.keys()):
        endpoints = by_file[file_name]
        print(f"\n{file_name}: {len(endpoints)} endpoints")
        for e in endpoints[:5]:  # Show first 5
            print(f"  {e['method']:6s} {e['path']}")
        if len(endpoints) > 5:
            print(f"  ... and {len(endpoints)-5} more")
    
    print("\n" + "=" * 80)
    print("PUBLIC ENDPOINTS (No Auth Required)")
    print("=" * 80)
    
    by_file_no_auth = defaultdict(list)
    for e in no_auth:
        by_file_no_auth[e['file']].append(e)
    
    for file_name in sorted(by_file_no_auth.keys()):
        endpoints = by_file_no_auth[file_name]
        print(f"\n{file_name}: {len(endpoints)} public endpoints")
        for e in endpoints:
            print(f"  {e['method']:6s} {e['path']}")

if __name__ == "__main__":
    main()
