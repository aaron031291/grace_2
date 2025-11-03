"""Quick validation of IDE WebSocket integration"""

import sys
import importlib.util
from pathlib import Path

def check_file(path, description):
    """Check if file exists"""
    if Path(path).exists():
        size = Path(path).stat().st_size
        print(f"✓ {description}: {path} ({size} bytes)")
        return True
    else:
        print(f"✗ {description}: {path} NOT FOUND")
        return False

def check_import(module_path, module_name):
    """Check if module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✓ Module imports: {module_name}")
        return True
    except Exception as e:
        print(f"✗ Import failed {module_name}: {e}")
        return False

def check_handler_functions():
    """Check handler has all required functions"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.ide_websocket_handler import ide_ws_handler
        
        required_methods = [
            'file_open',
            'file_save',
            'file_create',
            'file_delete',
            'file_rename',
            'directory_list',
            'code_execute',
            'security_scan',
            'auto_fix',
            'auto_quarantine'
        ]
        
        missing = []
        for method in required_methods:
            if not hasattr(ide_ws_handler, method):
                missing.append(method)
        
        if missing:
            print(f"✗ Missing handler methods: {', '.join(missing)}")
            return False
        else:
            print(f"✓ All {len(required_methods)} handler methods present")
            return True
            
    except Exception as e:
        print(f"✗ Handler validation failed: {e}")
        return False

def main():
    print("=" * 60)
    print("IDE WebSocket Integration Validation")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check backend files
    print("Backend Files:")
    checks.append(check_file(
        "backend/ide_websocket_handler.py",
        "IDE WebSocket Handler"
    ))
    checks.append(check_file(
        "backend/websocket_manager.py",
        "WebSocket Manager"
    ))
    checks.append(check_file(
        "backend/sandbox_manager.py",
        "Sandbox Manager"
    ))
    checks.append(check_file(
        "backend/governance.py",
        "Governance Engine"
    ))
    checks.append(check_file(
        "backend/hunter.py",
        "Hunter Security"
    ))
    checks.append(check_file(
        "backend/verification_integration.py",
        "Verification Integration"
    ))
    print()
    
    # Check frontend files
    print("Frontend Files:")
    checks.append(check_file(
        "grace_ide/static/websocket_client.js",
        "WebSocket Client JS"
    ))
    checks.append(check_file(
        "grace_ide/static/test_ide.html",
        "Test HTML Page"
    ))
    checks.append(check_file(
        "grace_ide/api/websocket.py",
        "WebSocket API"
    ))
    checks.append(check_file(
        "grace_ide/api/handlers.py",
        "Message Handlers"
    ))
    checks.append(check_file(
        "grace_ide/api/security.py",
        "Security Engine"
    ))
    checks.append(check_file(
        "grace_ide/api/execution.py",
        "Execution Engine"
    ))
    print()
    
    # Check test files
    print("Test Files:")
    checks.append(check_file(
        "tests/test_ide_websocket.py",
        "WebSocket Tests"
    ))
    print()
    
    # Check documentation
    print("Documentation:")
    checks.append(check_file(
        "IDE_WEBSOCKET_INTEGRATION.md",
        "Integration Documentation"
    ))
    print()
    
    # Check handler methods
    print("Handler Methods:")
    checks.append(check_handler_functions())
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✓ ALL CHECKS PASSED ({passed}/{total})")
        print()
        print("Integration Status: COMPLETE ✅")
        print()
        print("Next Steps:")
        print("1. Start backend: python -m uvicorn backend.main:app --reload")
        print("2. Run tests: pytest tests/test_ide_websocket.py -v")
        print("3. Browser test: http://localhost:8000/static/test_ide.html")
    else:
        print(f"✗ SOME CHECKS FAILED ({passed}/{total} passed)")
        print()
        print("Integration Status: INCOMPLETE ⚠️")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
