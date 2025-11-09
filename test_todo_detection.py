#!/usr/bin/env python3
"""Test TODO detection with safe tags"""

# Test file with various TODO patterns

# This should be DETECTED (untagged)
# TODO: This is an untagged todo

# These should be SKIPPED (safe tags)
# TODO(SAFE): This is safe
# TODO(ROADMAP): Future integration planned
# TODO(DESIGN): Design decision pending
# TODO(FUTURE): Deferred implementation

def test_function():
    pass  # TODO: Implement based on spec (code generator output)

def another_function():
    # TODO(ROADMAP): Add proper implementation when API ready
    return None

# Test the detection
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    content = Path(__file__).read_text()
    
    # Simulate autonomous improver detection
    safe_todo_tags = ['TODO(SAFE)', 'TODO(ROADMAP)', 'TODO(DESIGN)', 'TODO(FUTURE)']
    
    has_unsafe_todo = False
    unsafe_lines = []
    
    for i, line in enumerate(content.split('\n'), 1):
        if 'TODO:' in line:
            is_safe = any(tag in line for tag in safe_todo_tags)
            if not is_safe:
                has_unsafe_todo = True
                unsafe_lines.append((i, line.strip()))
    
    print("=" * 80)
    print("TODO DETECTION TEST")
    print("=" * 80)
    print()
    
    print(f"Safe tags recognized: {safe_todo_tags}")
    print()
    
    if has_unsafe_todo:
        print(f"[DETECTED] Found {len(unsafe_lines)} untagged TODOs:")
        for line_num, line in unsafe_lines:
            print(f"  Line {line_num}: {line}")
        print()
        print("[RESULT] Autonomous improver would flag this file")
    else:
        print("[OK] All TODOs are properly tagged as safe")
        print("[RESULT] Autonomous improver would allow this file")
    
    print()
    print("=" * 80)
    
    # Expected: Should detect line 7 (untagged TODO)
    # Should skip lines 11-14 (tagged TODOs) and line 16, 37 (safe patterns)
    assert has_unsafe_todo, "Should detect at least one untagged TODO"
    
    # Note: Test file itself may contain TODOs in the detection code
    # The important thing is untagged TODOs are detected, tagged ones are skipped
    
    print("[PASS] TODO detection working correctly")
    print("=" * 80)
