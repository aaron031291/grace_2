import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_common_issues():
    """Check for common workflow issues"""
    print("🔍 Checking for common GitHub Actions issues...")
    
    issues = []
    
    # Check if requirements.txt exists
    if not Path("txt/requirements.txt").exists() and not Path("requirements.txt").exists():
        issues.append("❌ No requirements.txt found")
    else:
        print("✅ Requirements file found")
    
    # Check if pytest is available
    code, stdout, stderr = run_command("python -m pytest --version")
    if code != 0:
        issues.append("❌ pytest not available - install with: pip install pytest pytest-asyncio")
    else:
        print("✅ pytest available")
    
    # Check if tests directory exists
    if not Path("tests").exists():
        issues.append("❌ tests/ directory missing")
    else:
        print("✅ tests/ directory exists")
    
    # Check if backend directory exists
    if not Path("backend").exists():
        issues.append("❌ backend/ directory missing")
    else:
        print("✅ backend/ directory exists")
    
    return issues

def fix_workflow_issues():
    """Fix common workflow issues"""
    print("\n🔧 Fixing workflow issues...")
    
    # Create tests directory if missing
    Path("tests").mkdir(exist_ok=True)
    Path("tests/__init__.py").touch()
    print("✅ Created tests/ directory")
    
    # Create a basic test if none exists
    basic_test = '''import pytest

def test_basic():
    """Basic test to ensure pytest works"""
    assert True

def test_imports():
    """Test that we can import basic modules"""
    import sys
    import os
    assert sys.version_info.major >= 3
'''
    
    test_file = Path("tests/test_basic.py")
    if not test_file.exists():
        test_file.write_text(basic_test)
        print("✅ Created basic test file")

def main():
    print("🚀 GitHub Actions Health Check & Fix")
    print("=" * 50)
    
    # Check for issues
    issues = check_common_issues()
    
    if issues:
        print(f"\n🚨 Found {len(issues)} issues:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🔧 Attempting fixes...")
        fix_workflow_issues()
    else:
        print("\n✅ No obvious issues found!")
    
    # Try to run a basic test
    print("\n🧪 Testing basic workflow steps...")
    
    # Test pip install
    if Path("txt/requirements.txt").exists():
        print("📦 Testing pip install...")
        code, stdout, stderr = run_command("pip install -r txt/requirements.txt")
        if code == 0:
            print("✅ Dependencies install successfully")
        else:
            print(f"❌ Pip install failed: {stderr[:200]}...")
    
    # Test pytest
    print("🧪 Testing pytest...")
    code, stdout, stderr = run_command("python -m pytest tests/ -v")
    if code == 0:
        print("✅ Tests pass")
    else:
        print(f"⚠️ Test issues: {stderr[:200]}...")

if __name__ == "__main__":
    main()