#!/usr/bin/env python3
"""
Quick fix script to remove all database dependencies from new routers
Run this to stabilize the system quickly
"""

import re
from pathlib import Path

def fix_router_file(filepath: Path):
    """Fix a single router file"""
    print(f"Fixing {filepath}...")
    
    content = filepath.read_text(encoding='utf-8')
    
    # Remove Session and get_db imports
    content = re.sub(r'from sqlalchemy\.orm import Session\n', '', content)
    content = re.sub(r', Session\n', '\n', content)
    content = re.sub(r'from \.\.database import get_db\n', '', content)
    content = re.sub(r'from backend\.database import get_db\n', '', content)
    
    # Remove db: Session = Depends(get_db) parameters
    content = re.sub(r', db: Session = Depends\(get_db\)', '', content)
    content = re.sub(r'db: Session = Depends\(get_db\), ', '', content)
    content = re.sub(r'\n\s+db: Session = Depends\(get_db\)\n', '\n', content)
    
    # Remove standalone Depends import if it's now unused
    # (Keep this simple - manual review may be needed)
    
    filepath.write_text(content, encoding='utf-8')
    print(f"✓ Fixed {filepath}")

def main():
    """Fix all router files"""
    backend_dir = Path(__file__).parent / "backend" / "routers"
    
    router_files = [
        backend_dir / "transcendence_domain.py",
        backend_dir / "security_domain.py",
        # core_domain.py already fixed
        # cognition.py already fixed
    ]
    
    for filepath in router_files:
        if filepath.exists():
            fix_router_file(filepath)
        else:
            print(f"⚠ File not found: {filepath}")
    
    print("\n✅ All routers fixed!")
    print("Next steps:")
    print("1. Start backend: python -m uvicorn backend.main:app --reload")
    print("2. Test endpoints: curl http://localhost:8000/api/cognition/status")
    print("3. Run CLI: cd cli && python grace_unified.py cognition")

if __name__ == "__main__":
    main()
