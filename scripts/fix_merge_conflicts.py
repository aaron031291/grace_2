"""Fix merge conflicts in backend files"""

import re
from pathlib import Path

def fix_merge_conflict(file_path: Path) -> bool:
    """Fix merge conflicts by keeping both sides intelligently"""
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check if file has merge conflicts
    if '<<<<<<< HEAD' not in content:
        return False
    
    print(f"Fixing: {file_path}")
    
    # Pattern to match merge conflict blocks
    pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/main'
    
    def resolve_conflict(match):
        head_content = match.group(1).strip()
        origin_content = match.group(2).strip()
        
        # If one side is empty, use the other
        if not head_content:
            return origin_content
        if not origin_content:
            return head_content
        
        # If both are imports, merge them
        if 'import' in head_content and 'import' in origin_content:
            # Combine unique imports
            head_lines = set(head_content.split('\n'))
            origin_lines = set(origin_content.split('\n'))
            all_imports = sorted(head_lines | origin_lines)
            return '\n'.join(all_imports)
        
        # Default: keep both with comment
        return f"{head_content}\n# Also from origin:\n{origin_content}"
    
    # Fix all conflicts
    fixed_content = re.sub(pattern, resolve_conflict, content, flags=re.DOTALL)
    
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

