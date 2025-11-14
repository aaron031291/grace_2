"""
Run backend and capture output with proper encoding
"""

import subprocess
import sys

print("="*70)
print("Starting GRACE Backend with UTF-8 encoding...")
print("="*70)
print()

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Run serve.py
try:
    subprocess.run(
        [sys.executable, "serve.py"],
        cwd=r"C:\Users\aaron\grace_2",
        encoding='utf-8',
        errors='replace'
    )
except KeyboardInterrupt:
    print("\n\nBackend stopped by user")
except Exception as e:
    print(f"\n\nError: {e}")
