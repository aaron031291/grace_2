#!/usr/bin/env python3
"""Scan for remaining untagged TODOs that would block autonomous improver"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Simulate autonomous improver logic
safe_todo_tags = ['TODO(SAFE)', 'TODO(ROADMAP)', 'TODO(DESIGN)', 'TODO(FUTURE)']
safe_patterns = [
    'pass  # TODO:',
    '# TODO: Implement function logic',
    '# TODO: Add assertions',
    "if 'TODO:' in",
    "'TODO:' in line",
    "'TODO:' in content",
]

backend_path = Path(__file__).parent / 'backend'
files_with_unsafe_todos = []

for py_file in backend_path.rglob('*.py'):
    try:
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        
        if 'TODO:' not in content and 'TODO(' not in content:
            continue
        
        has_unsafe_todo = False
        unsafe_lines = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            if 'TODO:' in line:
                # Skip if has safe tag
                if any(tag in line for tag in safe_todo_tags):
                    continue
                # Skip if matches safe pattern
                if any(pattern in line for pattern in safe_patterns):
                    continue
                # Untagged TODO
                has_unsafe_todo = True
                unsafe_lines.append((line_num, line.strip()[:100]))
        
        if has_unsafe_todo:
            rel_path = py_file.relative_to(Path(__file__).parent)
            files_with_unsafe_todos.append((str(rel_path), unsafe_lines))
    
    except Exception as e:
        pass

print("=" * 80)
print("REMAINING UNTAGGED TODOs")
print("=" * 80)
print()

if not files_with_unsafe_todos:
    print("[OK] No untagged TODOs found!")
    print("[OK] All TODOs are properly tagged with ROADMAP/FUTURE/DESIGN/SAFE")
    print()
    print("Autonomous improver is fully unblocked.")
else:
    print(f"[FOUND] {len(files_with_unsafe_todos)} files with untagged TODOs:")
    print()
    
    for file_path, unsafe_lines in files_with_unsafe_todos[:20]:  # Show first 20
        print(f"  {file_path}:")
        for line_num, line_text in unsafe_lines[:3]:  # Show first 3 TODOs per file
            print(f"    Line {line_num}: {line_text}")
        if len(unsafe_lines) > 3:
            print(f"    ... and {len(unsafe_lines) - 3} more")
        print()
    
    if len(files_with_unsafe_todos) > 20:
        print(f"  ... and {len(files_with_unsafe_todos) - 20} more files")
        print()
    
    print("=" * 80)
    print("RECOMMENDED ACTIONS")
    print("=" * 80)
    print()
    print("Option 1: Tag as safe (if intentional roadmap items)")
    print("  Change: # TODO: Something")
    print("  To:     # TODO(ROADMAP): Something")
    print()
    print("Option 2: Add to whitelist")
    print("  Edit: config/autonomous_improver_whitelist.yaml")
    print("  Add to design_decision_todos list")
    print()
    print("Option 3: Implement or remove")
    print("  Either implement the TODO or remove it")
    print()

print("=" * 80)
