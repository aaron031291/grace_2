"""Script to replace hardcoded API URLs with config.ts imports in frontend.

Replaces all instances of:
- http://localhost:8054
- http://localhost:8000
- ws://localhost:8000

With imports from config.ts
"""

import re
from pathlib import Path

# Frontend source directory
FRONTEND_SRC = Path(__file__).parent.parent / 'frontend' / 'src'

# Patterns to replace
PATTERNS = [
    (r"'http://localhost:8054", "apiUrl('"),
    (r'"http://localhost:8054', 'apiUrl("'),
    (r"'http://localhost:8000", "apiUrl('"),
    (r'"http://localhost:8000', 'apiUrl("'),
    (r"'ws://localhost:8000", "'${WS_BASE_URL}"),
    (r'"ws://localhost:8000', '"${WS_BASE_URL}'),
    (r"`ws://localhost:8000", "`${WS_BASE_URL}"),
]

def needs_import(content: str) -> bool:
    """Check if file needs apiUrl import."""
    return 'apiUrl' in content or 'WS_BASE_URL' in content

def add_import(content: str) -> str:
    """Add config.ts import if not present."""
    if "from './config'" in content or 'from "../config"' in content or "from '@/config'" in content:
        return content
    
    # Find first import statement
    lines = content.split('\n')
    insert_idx = 0
    
    for i, line in enumerate(lines):
        if line.startswith('import '):
            insert_idx = i + 1
            break
    
    # Insert import after other imports
    import_line = "import { apiUrl, WS_BASE_URL } from './config';"
    lines.insert(insert_idx, import_line)
    
    return '\n'.join(lines)

def fix_file(filepath: Path) -> bool:
    """Fix URLs in a single file. Returns True if changed."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Apply replacements
        for pattern, replacement in PATTERNS:
            content = re.sub(pattern, replacement, content)
        
        # Add import if needed
        if content != original_content and needs_import(content):
            content = add_import(content)
        
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            print(f"[OK] Fixed: {filepath.relative_to(FRONTEND_SRC.parent)}")
            return True
        
        return False
    
    except Exception as e:
        print(f"[ERROR] Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all TypeScript/TSX files in frontend/src."""
    print("[*] Fixing hardcoded API URLs in frontend...")
    print(f"    Searching: {FRONTEND_SRC}")
    print()
    
    fixed_count = 0
    total_files = 0
    
    # Process all .ts and .tsx files
    for ext in ['*.ts', '*.tsx']:
        for filepath in FRONTEND_SRC.rglob(ext):
            total_files += 1
            if fix_file(filepath):
                fixed_count += 1
    
    print()
    print(f"[SUMMARY]")
    print(f"    Total files scanned: {total_files}")
    print(f"    Files modified: {fixed_count}")
    print(f"    Files unchanged: {total_files - fixed_count}")
    print()
    print("[OK] Done! All hardcoded URLs replaced with config.ts imports.")

if __name__ == '__main__':
    main()
