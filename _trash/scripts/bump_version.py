#!/usr/bin/env python3
"""
Version Bump Tool
Automatically updates version across all files and generates changelog entry

Usage:
  python scripts/bump_version.py patch  # 2.1.0 -> 2.1.1
  python scripts/bump_version.py minor  # 2.1.0 -> 2.2.0
  python scripts/bump_version.py major  # 2.1.0 -> 3.0.0
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Tuple

def get_current_version() -> str:
    """Read current version from VERSION file"""
    version_file = Path(__file__).parent.parent / "VERSION"
    if not version_file.exists():
        return "2.1.0"
    return version_file.read_text().strip()

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string to tuple"""
    major, minor, patch = version.split('.')
    return int(major), int(minor), int(patch)

def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type"""
    major, minor, patch = parse_version(current)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

def update_file(file_path: Path, old_version: str, new_version: str, pattern: str):
    """Update version in a file"""
    if not file_path.exists():
        print(f"  [SKIP] {file_path} (not found)")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    new_content = re.sub(pattern.format(old_version), pattern.format(new_version), content)
    
    if content != new_content:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"  [OK] {file_path}")
        return True
    else:
        print(f"  [SKIP] {file_path} (no change)")
        return False

def update_all_versions(old_version: str, new_version: str):
    """Update version in all relevant files"""
    root = Path(__file__).parent.parent
    
    files_to_update = [
        (root / "VERSION", old_version, new_version, r"{}"),
        (root / "pyproject.toml", old_version, new_version, r'version = "{}"'),
        (root / "backend" / "__version__.py", old_version, new_version, r'__version__ = "{}"'),
        (root / "backend" / "misc" / "main.py", old_version, new_version, r'version="{}"'),
    ]
    
    print(f"\nUpdating version {old_version} -> {new_version}:")
    print("=" * 60)
    
    updated_count = 0
    for file_path, old, new, pattern in files_to_update:
        if update_file(file_path, old, new, pattern):
            updated_count += 1
    
    print("=" * 60)
    print(f"Updated {updated_count} files\n")
    
    return updated_count

def add_changelog_entry(version: str, bump_type: str):
    """Add entry to CHANGELOG.md"""
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
    
    if not changelog_path.exists():
        print("[WARN] CHANGELOG.md not found")
        return
    
    content = changelog_path.read_text(encoding='utf-8')
    
    # Create new entry
    date = datetime.now().strftime("%Y-%m-%d")
    bump_label = bump_type.upper()
    
    new_entry = f"""
## [{version}] - {date}

### {bump_label} Release

- TODO: Add release notes here

---

"""
    
    # Insert after header
    lines = content.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('## ['):
            insert_pos = i
            break
    
    if insert_pos > 0:
        lines.insert(insert_pos, new_entry.strip())
        new_content = '\n'.join(lines)
        changelog_path.write_text(new_content, encoding='utf-8')
        print(f"[OK] Added changelog entry for {version}")
        print(f"[ACTION] Edit CHANGELOG.md to add release notes")
    else:
        print("[WARN] Could not find insertion point in CHANGELOG.md")

def main():
    """Main version bump process"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/bump_version.py [major|minor|patch]")
        print("\nCurrent version: " + get_current_version())
        sys.exit(1)
    
    bump_type = sys.argv[1].lower()
    
    if bump_type not in ["major", "minor", "patch"]:
        print(f"Error: Invalid bump type '{bump_type}'")
        print("Must be: major, minor, or patch")
        sys.exit(1)
    
    current = get_current_version()
    new = bump_version(current, bump_type)
    
    print("=" * 60)
    print("GRACE VERSION BUMP")
    print("=" * 60)
    print(f"Current: {current}")
    print(f"New:     {new}")
    print(f"Type:    {bump_type}")
    print("=" * 60)
    
    # Confirm
    response = input("\nProceed with version bump? [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Update files
    updated = update_all_versions(current, new)
    
    if updated > 0:
        # Add changelog entry
        add_changelog_entry(new, bump_type)
        
        print("\n" + "=" * 60)
        print("VERSION BUMP COMPLETE")
        print("=" * 60)
        print(f"Version: {new}")
        print(f"Files updated: {updated}")
        print("\nNext steps:")
        print("  1. Edit CHANGELOG.md to add release notes")
        print("  2. git add -A")
        print(f"  3. git commit -m 'Version {new}'")
        print(f"  4. git tag -a v{new} -m 'Release {new}'")
        print("  5. git push origin main && git push origin v{new}")
        print("=" * 60)
    else:
        print("[ERROR] No files updated")
        sys.exit(1)

if __name__ == "__main__":
    main()
