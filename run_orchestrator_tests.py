#!/usr/bin/env python3
"""
Run the Grace Unified Orchestrator tests
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run the orchestrator tests with pytest"""
    
    # Change to project root
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("Running Grace Unified Orchestrator Tests")
    print("=" * 60)
    print()
    
    # Run pytest on the specific test file
    test_file = "tests/test_unified_grace_orchestrator.py"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_file, 
            "-v",           # verbose output
            "--tb=short",   # shorter traceback format
            "--no-header",  # cleaner output
        ], 
        cwd=project_root,
        capture_output=True, 
        text=True,
        timeout=60
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print(f"\n❌ Tests failed with code {result.returncode}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)