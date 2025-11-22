"""Extract line number from error"""
import re

with open("error_full.txt", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()
    
# Write to a new file with better formatting
with open("error_readable.txt", "w", encoding="utf-8") as f:
    f.write(content)
    
# Print line by line
lines = content.split("\n")
for i, line in enumerate(lines, 1):
    print(f"{i:3d}: {line}")
