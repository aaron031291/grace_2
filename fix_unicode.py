#!/usr/bin/env python3
"""Fix all unicode characters in serve.py for Windows compatibility"""

with open('serve.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace checkmarks, crosses, warnings
content = content.replace('✓', '[OK]')
content = content.replace('✗', '[FAIL]')
content = content.replace('⚠', '[WARN]')
content = content.replace('❌', '[ERROR]')
content = content.replace('→', '->')
content = content.replace('📡', '')
content = content.replace('📖', '')
content = content.replace('❤️', '')
content = content.replace('❤', '')

# Replace box drawing characters
box_chars = {
    '█': '#',
    '╔': '+',
    '╗': '+',
    '╚': '+',
    '╝': '+',
    '║': '|',
    '═': '=',
    '╒': '+',
    '╕': '+',
    '╘': '+',
    '╛': '+',
    '╓': '+',
    '╖': '+',
    '╙': '+',
    '╜': '+',
}

for old, new in box_chars.items():
    content = content.replace(old, new)

with open('serve.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed all unicode characters in serve.py')
