#!/usr/bin/env python3
"""
Comprehensive conflict resolver for Grace repo.
Resolves common merge conflict patterns automatically.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def find_conflict_files(root: Path) -> List[Path]:
    """Find all files with conflict markers."""
    conflict_files = []
    extensions = {'.py', '.md', '.txt', '.yaml', '.yml', '.json', '.js', '.ts', '.tsx', '.jsx', '.sh', '.ps1', '.bat'}
    
    for ext in extensions:
        for filepath in root.rglob(f'*{ext}'):
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                if '<<<<<<< HEAD' in content or '=======' in content or '>>>>>>>' in content:
                    conflict_files.append(filepath)
            except Exception:
                pass
    
    return conflict_files

def resolve_conflicts(content: str) -> Tuple[str, int]:
    """Resolve common conflict patterns. Returns (new_content, num_resolved)."""
    original = content
    resolved_count = 0
    
    # Pattern 1: Arrow style conflicts (→ vs ->)
    def normalize_arrows(match):
        head_line = match.group(1)
        main_line = match.group(2)
        # Normalize both to ->
        head_normalized = head_line.replace('→', '->')
        main_normalized = main_line.replace('→', '->')
        if head_normalized == main_normalized:
            return head_normalized
        return head_line  # Keep HEAD if different
    
    pattern1 = re.compile(r'<<<<<<< HEAD\s*\n(.*?)\n=======\s*\n(.*?)\n>>>>>>> origin/main', re.DOTALL)
    content = pattern1.sub(normalize_arrows, content)
    if content != original:
        resolved_count += 1
        original = content
    
    # Pattern 2: Print statement conflicts (✓ vs [OK])
    pattern2 = re.compile(r'<<<<<<< HEAD\s*\n(\s*)print\(f"✓([^"]+)"\)\n=======\s*\n\s*print\(f"\[OK\]([^"]+)"\)\n>>>>>>> origin/main')
    content = pattern2.sub(r'\1print(f"[OK]\2")', content)
    if content != original:
        resolved_count += original.count('<<<<<<< HEAD') - content.count('<<<<<<< HEAD')
        original = content
    
    # Pattern 3: TODO comment conflicts
    pattern3 = re.compile(r'<<<<<<< HEAD\s*\n(\s*)#\s*TODO:([^\n]+)\n=======\s*\n\s*#\s*TODO\(FUTURE\):([^\n]+)\n>>>>>>> origin/main')
    content = pattern3.sub(r'\1# TODO:\2', content)
    if content != original:
        resolved_count += 1
        original = content
    
    # Pattern 4: Identical lines (keep one)
    pattern4 = re.compile(r'<<<<<<< HEAD\s*\n(.+?)\n=======\s*\n\1\n>>>>>>> origin/main', re.DOTALL)
    content = pattern4.sub(r'\1', content)
    if content != original:
        resolved_count += 1
        original = content
    
    # Pattern 5: Empty vs non-empty (keep non-empty)
    pattern5a = re.compile(r'<<<<<<< HEAD\s*\n\s*\n=======\s*\n([^\n<]+)\n>>>>>>> origin/main')
    content = pattern5a.sub(r'\1', content)
    if content != original:
        resolved_count += 1
        original = content
    
    pattern5b = re.compile(r'<<<<<<< HEAD\s*\n([^\n<]+)\n=======\s*\n\s*\n>>>>>>> origin/main')
    content = pattern5b.sub(r'\1', content)
    if content != original:
        resolved_count += 1
    
    return content, resolved_count

def main():
    root = Path.cwd()
    print("=== Grace Conflict Resolver (Python) ===")
    print(f"Root: {root}")
    print()
    
    conflict_files = find_conflict_files(root)
    print(f"Found {len(conflict_files)} files with conflict markers")
    print()
    
    total_files = 0
    total_conflicts = 0
    errors = []
    
    for filepath in conflict_files:
        try:
            print(f"Processing: {filepath.relative_to(root)}")
            content = filepath.read_text(encoding='utf-8')
            new_content, num_resolved = resolve_conflicts(content)
            
            if num_resolved > 0:
                filepath.write_text(new_content, encoding='utf-8')
                total_files += 1
                total_conflicts += num_resolved
                print(f"  -> Resolved {num_resolved} conflict(s)")
            else:
                print(f"  -> No auto-resolvable conflicts")
        except Exception as e:
            errors.append(f"Error processing {filepath}: {e}")
            print(f"  -> ERROR: {e}")
    
    print()
    print("=== Summary ===")
    print(f"Files processed: {total_files}")
    print(f"Conflicts resolved: {total_conflicts}")
    
    if errors:
        print(f"Errors: {len(errors)}")
        for err in errors:
            print(f"  {err}")
    
    print()
    return 0 if not errors else 1

if __name__ == '__main__':
    sys.exit(main())
