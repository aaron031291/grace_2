#!/usr/bin/env python3
"""
Grace Installation Verification Script
Run this to verify all components are properly installed and working
"""

import sys
import os
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Need 3.9+")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    print_header("Required Packages Check")
    
    packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'sqlalchemy': 'SQLAlchemy',
        'pydantic': 'Pydantic',
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("Install missing packages: pip install -r requirements.txt")
    
    return all_installed

def check_file_structure():
    """Check if all required files exist"""
    print_header("File Structure Check")
    
    base_dir = Path(__file__).parent
    
    required_files = [
        'backend/main.py',
        'backend/metrics_service.py',
        'backend/cognition_metrics.py',
        'backend/routers/cognition.py',
        'backend/routers/core_domain.py',
        'backend/routers/transcendence_domain.py',
        'backend/routers/security_domain.py',
        'cli/grace_unified.py',
        'cli/commands/cognition_status.py',
        'cli/commands/domain_commands.py',
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_syntax():
    """Check Python syntax of main files"""
    print_header("Syntax Check")
    
    base_dir = Path(__file__).parent
    
    files_to_check = [
        'backend/metrics_service.py',
        'backend/cognition_metrics.py',
        'backend/routers/cognition.py',
        'backend/routers/core_domain.py',
        'backend/routers/transcendence_domain.py',
        'backend/routers/security_domain.py',
    ]
    
    all_valid = True
    for file_path in files_to_check:
        full_path = base_dir / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(full_path), 'exec')
                print_success(f"{file_path}")
            except SyntaxError as e:
                print_error(f"{file_path} - Line {e.lineno}: {e.msg}")
                all_valid = False
        else:
            print_warning(f"{file_path} - File not found")
    
    return all_valid

def check_imports():
    """Test if modules can be imported"""
    print_header("Import Check")
    
    # Add backend to path
    base_dir = Path(__file__).parent
    sys.path.insert(0, str(base_dir))
    
    imports_to_test = [
        ('backend.metrics_service', 'get_metrics_collector'),
        ('backend.cognition_metrics', 'get_metrics_engine'),
        ('backend.routers.cognition', 'router'),
        ('backend.routers.core_domain', 'router'),
    ]
    
    all_imported = True
    for module_name, attr in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[attr])
            if hasattr(module, attr):
                print_success(f"{module_name}.{attr}")
            else:
                print_error(f"{module_name}.{attr} - Attribute not found")
                all_imported = False
        except Exception as e:
            print_error(f"{module_name} - {str(e)}")
            all_imported = False
    
    return all_imported

def test_metrics_service():
    """Test metrics service functionality"""
    print_header("Metrics Service Test")
    
    try:
        from backend.metrics_service import get_metrics_collector
        import asyncio
        
        collector = get_metrics_collector()
        print_success("Metrics collector initialized")
        
        # Test publishing a metric
        async def test_publish():
            await collector.publish("test_domain", "test_kpi", 0.95, {"test": True})
            return True
        
        result = asyncio.run(test_publish())
        if result:
            print_success("Metric publishing works")
        
        # Test aggregation
        kpis = collector.get_domain_kpis("test_domain")
        if "test_kpi" in kpis:
            print_success(f"Metric aggregation works (test_kpi = {kpis['test_kpi']:.2f})")
        
        return True
        
    except Exception as e:
        print_error(f"Metrics service test failed: {e}")
        return False

def test_cognition_engine():
    """Test cognition engine functionality"""
    print_header("Cognition Engine Test")
    
    try:
        from backend.cognition_metrics import get_metrics_engine
        
        engine = get_metrics_engine()
        print_success("Cognition engine initialized")
        
        # Test status
        status = engine.get_status()
        if "domains" in status:
            print_success(f"Status report works ({len(status['domains'])} domains)")
        
        # Test readiness
        readiness = engine.get_readiness_report()
        if "ready" in readiness:
            print_success(f"Readiness report works (ready: {readiness['ready']})")
        
        return True
        
    except Exception as e:
        print_error(f"Cognition engine test failed: {e}")
        return False

def print_summary(results):
    """Print summary of all checks"""
    print_header("Summary")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"Total checks: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.END}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.END}")
    print()
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED - System is ready!{Colors.END}")
        print()
        print_info("Next steps:")
        print("  1. Start backend: python -m uvicorn backend.main:app --reload")
        print("  2. Test API: curl http://localhost:8000/api/cognition/status")
        print("  3. Run CLI: cd cli && python grace_unified.py cognition")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed - See errors above{Colors.END}")
        print()
        print_info("Fix the errors and run this script again")
        return False

def main():
    """Run all verification checks"""
    print(f"{Colors.BOLD}Grace Installation Verification{Colors.END}")
    print(f"Version: 1.0")
    print(f"Path: {Path(__file__).parent}")
    
    results = {}
    
    # Run all checks
    results['Python Version'] = check_python_version()
    results['Required Packages'] = check_required_packages()
    results['File Structure'] = check_file_structure()
    results['Syntax'] = check_syntax()
    results['Imports'] = check_imports()
    results['Metrics Service'] = test_metrics_service()
    results['Cognition Engine'] = test_cognition_engine()
    
    # Print summary
    all_passed = print_summary(results)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
