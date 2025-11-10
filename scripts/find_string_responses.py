"""
Find all API endpoints returning raw strings/dicts (no response_model)
"""
import os
import re
from pathlib import Path
from collections import defaultdict

ROUTES_DIR = Path(__file__).parent.parent / "backend" / "routes"

def analyze_endpoint(file_path, decorator_line, function_lines):
    """Analyze if endpoint returns raw dict/string"""
    has_response_model = 'response_model' in decorator_line
    
    # Find return statements
    returns = []
    for line in function_lines:
        if 'return' in line:
            returns.append(line.strip())
    
    # Classify return type
    return_type = "unknown"
    if any('return {' in r or 'return Dict' in r for r in returns):
        return_type = "raw_dict"
    elif any('return "' in r or "return '" in r for r in returns):
        return_type = "raw_string"
    elif any('return [' in r or 'return List' in r for r in returns):
        return_type = "raw_list"
    elif returns:
        return_type = "object"
    
    return {
        'has_response_model': has_response_model,
        'return_type': return_type,
        'returns': returns[:3]  # First 3 return statements
    }

def extract_endpoints_from_file(file_path):
    """Extract all endpoints and their return types"""
    endpoints = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for router decorator
        if re.match(r'@router\.(get|post|put|delete|patch)\(', line):
            decorator = line.strip()
            method = re.search(r'@router\.(get|post|put|delete|patch)', line).group(1).upper()
            
            # Extract path
            path_match = re.search(r'["\']([^"\']+)["\']', line)
            path = path_match.group(1) if path_match else "unknown"
            
            # Get function definition
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('async def'):
                decorator += ' ' + lines[i].strip()
                i += 1
            
            if i >= len(lines):
                break
                
            func_line = lines[i].strip()
            func_name = re.search(r'async def (\w+)', func_line).group(1) if 'async def' in func_line else "unknown"
            
            # Collect function body (next 50 lines or until next decorator)
            function_lines = []
            i += 1
            lines_collected = 0
            while i < len(lines) and lines_collected < 50:
                if lines[i].strip().startswith('@router.'):
                    break
                function_lines.append(lines[i])
                i += 1
                lines_collected += 1
            
            # Analyze endpoint
            analysis = analyze_endpoint(file_path, decorator, function_lines)
            
            endpoints.append({
                'file': file_path.name,
                'line': lines.index(line) + 1 if line in lines else 0,
                'method': method,
                'path': path,
                'function': func_name,
                **analysis
            })
        else:
            i += 1
    
    return endpoints

def main():
    all_endpoints = []
    
    for py_file in ROUTES_DIR.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        
        endpoints = extract_endpoints_from_file(py_file)
        all_endpoints.extend(endpoints)
    
    # Filter to problematic endpoints
    string_responses = [
        ep for ep in all_endpoints 
        if not ep['has_response_model'] and ep['return_type'] in ['raw_dict', 'raw_string', 'raw_list']
    ]
    
    print("=" * 100)
    print("ENDPOINTS RETURNING RAW STRINGS/DICTS (Will show as 'string' in API docs)")
    print("=" * 100)
    print(f"\nTotal endpoints: {len(all_endpoints)}")
    print(f"Endpoints with response_model: {len([e for e in all_endpoints if e['has_response_model']])}")
    print(f"Endpoints returning raw data: {len(string_responses)}")
    
    # Group by return type
    by_type = defaultdict(list)
    for ep in string_responses:
        by_type[ep['return_type']].append(ep)
    
    for return_type, endpoints in sorted(by_type.items()):
        print(f"\n{'=' * 100}")
        print(f"{return_type.upper()} - {len(endpoints)} endpoints")
        print("=" * 100)
        
        # Group by file
        by_file = defaultdict(list)
        for ep in endpoints:
            by_file[ep['file']].append(ep)
        
        for file_name in sorted(by_file.keys()):
            print(f"\n{file_name}:")
            for ep in by_file[file_name]:
                print(f"  Line {ep['line']}: {ep['method']} {ep['path']} -> {ep['function']}()")
                if ep['returns']:
                    print(f"    Returns: {ep['returns'][0][:80]}...")
    
    # Summary by file
    print("\n" + "=" * 100)
    print("SUMMARY BY FILE (Files needing fixes)")
    print("=" * 100)
    
    files_needing_fixes = defaultdict(int)
    for ep in string_responses:
        files_needing_fixes[ep['file']] += 1
    
    for file_name, count in sorted(files_needing_fixes.items(), key=lambda x: -x[1]):
        print(f"  {file_name}: {count} endpoints")
    
    # Save detailed report
    report_path = Path(__file__).parent.parent / "reports" / "string_responses_audit.txt"
    with open(report_path, 'w') as f:
        f.write("ENDPOINTS RETURNING RAW STRINGS/DICTS\n")
        f.write("=" * 100 + "\n\n")
        
        for ep in sorted(string_responses, key=lambda x: (x['file'], x['line'])):
            f.write(f"{ep['file']}:{ep['line']} - {ep['method']} {ep['path']}\n")
            f.write(f"  Function: {ep['function']}()\n")
            f.write(f"  Return type: {ep['return_type']}\n")
            if ep['returns']:
                f.write(f"  Returns: {ep['returns'][0]}\n")
            f.write("\n")
    
    print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    main()
