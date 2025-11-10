"""Remove ALL merge conflict markers"""

from pathlib import Path

def remove_all_markers(file_path: Path) -> bool:
    """Remove ALL merge conflict markers"""

    content = file_path.read_text(encoding='utf-8')

    # Check if file has any markers
    markers = ['<<<<<<< HEAD', '=======', '>>>>>>> origin/main', '>>>>>>> main']
    has_markers = any(marker in content for marker in markers)

    if not has_markers:
        return False

    print(f"Cleaning: {file_path}")

    # Remove ALL conflict marker lines
    lines = content.split('\n')
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        # Skip any line that is a conflict marker
        if stripped in markers or stripped.startswith('<<<<<<< ') or stripped.startswith('>>>>>>> '):
            continue
        cleaned_lines.append(line)

    cleaned_content = '\n'.join(cleaned_lines)

    # Write back
    file_path.write_text(cleaned_content, encoding='utf-8')
    print(f"  ✓ Cleaned {file_path}")
    return True

def main():
    """Remove all conflict markers in backend"""
    backend_dir = Path('backend')

    fixed_count = 0
    for py_file in backend_dir.rglob('*.py'):
        if remove_all_markers(py_file):
            fixed_count += 1

    print(f"\n✓ Cleaned {fixed_count} files")

if __name__ == '__main__':
    main()

