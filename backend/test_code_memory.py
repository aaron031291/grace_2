"""Test Code Memory System

Quick test to verify code memory parsing and recall works
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backend.code_memory import code_memory

async def test_parse_single_file():
    """Test parsing a single Python file"""
    
    print("Testing code memory on a single file...\n")
    
    # Parse this test file itself
    test_file = Path(__file__)
    
    result = await code_memory.parse_file(
        file_path=test_file,
        language='python',
        project='test_project'
    )
    
    print(f"[OK] Parsed {test_file.name}")
    print(f"  Functions: {len(result.get('functions', []))}")
    print(f"  Classes: {len(result.get('classes', []))}")
    print()
    
    return result

async def test_pattern_recall():
    """Test pattern recall system"""
    
    print("Testing pattern recall...\n")
    
    # Try to recall patterns related to "testing"
    patterns = await code_memory.recall_patterns(
        intent="test function",
        language="python",
        limit=5
    )
    
    print(f"[OK] Found {len(patterns)} patterns for 'test function'")
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. {pattern['name']} ({pattern['type']})")
        print(f"   Confidence: {pattern['confidence']:.2f}")
        print(f"   Tags: {', '.join(pattern['tags'][:5])}")
        if pattern['description']:
            print(f"   Description: {pattern['description'][:80]}...")
    
    return patterns

async def main():
    """Run all tests"""
    
    print("=" * 60)
    print("GRACE CODE MEMORY TEST")
    print("=" * 60)
    print()
    
    # Test 1: Parse a file
    try:
        await test_parse_single_file()
    except Exception as e:
        print(f"[FAIL] Parse test failed: {e}\n")
    
    # Test 2: Recall patterns
    try:
        await test_pattern_recall()
    except Exception as e:
        print(f"[FAIL] Recall test failed: {e}\n")
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
