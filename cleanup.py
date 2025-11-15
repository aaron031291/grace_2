"""Remove duplicates - Windows compatible"""
import os
from pathlib import Path

files_to_remove = [
    "serve_simple.py",
    "serve_fixed.py", 
    "serve_debug.py",
    "start_grace_auto_port.py",
    "fix_and_start.py",
    "RUN.cmd",
    "START_FIXED.cmd",
    "START_AUTO_PORT.cmd",
    "START_DEBUG.cmd",
    "GRACE_START.cmd",
    "RUN_SIMPLE.cmd",
    "START_GRACE_LEARNING.cmd",
    "README_START_GRACE.txt",
    "SIMPLE_START.txt",
    "RESTART_INSTRUCTIONS.txt",
    "FIXED_STARTUP.txt",
    "HOWTO_START.md",
    "QUICK_START.md",
    "quick_test.py",
    "test_backend.py",
    "test_imports.py",
    "CLEANUP_DUPLICATES.py"
]

print("Removing duplicates...")
removed = 0
for f in files_to_remove:
    p = Path(f)
    if p.exists():
        p.unlink()
        print(f"Removed: {f}")
        removed += 1

print(f"\nRemoved {removed} duplicate files")
print("\nKept ONLY:")
print("  serve.py")
print("  START.cmd")
print("  README.md")
print("\nNo more confusion!")
