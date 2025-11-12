import os
from pathlib import Path

def show_python_files():
    """Show available Python files in the project"""
    print("🐍 Python files in your Grace project:")
    print("=" * 50)
    
    # Key directories to check
    dirs_to_check = [
        "backend",
        "scripts", 
        "tests",
        "."
    ]
    
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists():
            py_files = list(dir_path.glob("*.py"))
            if py_files:
                print(f"\n📁 {dir_name}/")
                for py_file in py_files[:10]:  # Show first 10
                    print(f"   - {py_file.name}")
                if len(py_files) > 10:
                    print(f"   ... and {len(py_files) - 10} more")
    
    print(f"\n💡 To open a Python file, use:")
    print(f"   code backend/main.py")
    print(f"   code backend/unified_grace_orchestrator.py")

if __name__ == "__main__":
    show_python_files()