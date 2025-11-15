"""Remove BOM from Python files"""
from pathlib import Path

backend = Path('backend')
fixed = 0

for py_file in backend.rglob('*.py'):
    if not py_file.is_file():
        continue
    
    try:
        content = py_file.read_bytes()
        
        # Check for BOM
        if content.startswith(b'\xef\xbb\xbf'):
            # Remove BOM
            py_file.write_bytes(content[3:])
            print(f"Fixed: {py_file}")
            fixed += 1
    except Exception as e:
        print(f"Error with {py_file}: {e}")

print(f"\nTotal fixed: {fixed} files")
