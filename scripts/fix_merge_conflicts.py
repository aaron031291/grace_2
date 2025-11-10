"""Fix merge conflicts in backend files"""

import re
from pathlib import Path

def fix_merge_conflict(file_path: Path) -> bool:
    """Fix merge conflicts by keeping origin/main version (most recent)"""

    content = file_path.read_text(encoding='utf-8')

    # Check if file has merge conflicts
    if '<<<<<<< HEAD' not in content:
        return False

    print(f"Fixing: {file_path}")

    # Pattern to match merge conflict blocks - more flexible
    pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n'

    def resolve_conflict(match):
        head_content = match.group(1)
        origin_content = match.group(2)

        # Always prefer origin/main (most recent code)
        # Remove trailing newlines to avoid double spacing
        return origin_content.rstrip('\n') + '\n'

    # Fix all conflicts
    fixed_content = re.sub(pattern, resolve_conflict, content, flags=re.DOTALL)

    # Also handle conflicts without trailing newline
    pattern2 = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?$'
    fixed_content = re.sub(pattern2, resolve_conflict, fixed_content, flags=re.DOTALL | re.MULTILINE)

    # Write back
    file_path.write_text(fixed_content, encoding='utf-8')
    print(f"  ✓ Fixed {file_path}")
    return True

def main():
    """Fix all merge conflicts in backend"""
    backend_dir = Path('backend')
    
    fixed_count = 0
    for py_file in backend_dir.rglob('*.py'):
        if fix_merge_conflict(py_file):
            fixed_count += 1
    
    print(f"\n✓ Fixed {fixed_count} files with merge conflicts")

if __name__ == '__main__':
    main()

