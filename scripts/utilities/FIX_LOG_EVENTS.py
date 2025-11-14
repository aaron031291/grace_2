"""
Quick fix for log_event calls in infrastructure_manager_kernel.py
"""

import re

file_path = "backend/core/infrastructure_manager_kernel.py"

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all log_event calls with simple print statements for now
# This is a quick fix to get the system running

replacements = [
    ('from backend.logging_utils import log_event', '# from backend.logging_utils import log_event'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Add simple log_event function at top
log_func = '''
def log_event(action=None, **kwargs):
    """Simple logging function"""
    print(f"[LOG] {action}: {kwargs}")

'''

# Insert after imports
import_end = content.find('class HostOS')
if import_end > 0:
    content = content[:import_end] + log_func + content[import_end:]

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed log_event calls in infrastructure_manager_kernel.py")
