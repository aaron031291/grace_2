#!/usr/bin/env python3
"""
Grace CLI Installation Verification Script

This script verifies that all components are properly installed
and ready to use.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

def check_item(name: str, passed: bool, details: str = "") -> Tuple[str, bool]:
    """Print check result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} - {name}")
    if details:
        print(f"       {Colors.YELLOW}{details}{Colors.RESET}")
    return (name, passed)

def main():
    """Run installation verification"""
    print(f"\n{Colors.BOLD}Grace CLI - Installation Verification{Colors.RESET}")
    
    results: List[Tuple[str, bool]] = []
    
    # 1. Check Python version
    print_header("1. Python Environment")
    
    python_version = sys.version_info
    python_ok = python_version >= (3, 9)
    results.append(check_item(
        "Python version >= 3.9",
        python_ok,
        f"Found: Python {python_version.major}.{python_version.minor}.{python_version.micro}"
    ))
    
    # 2. Check required files
    print_header("2. Required Files")
    
    cli_dir = Path(__file__).parent
    required_files = [
        "grace_client.py",
        "config.py",
        "plugin_manager.py",
        "voice_handler.py",
        "enhanced_grace_cli.py",
        "requirements.txt",
        "setup.py",
        "README.md",
    ]
    
    for file in required_files:
        file_path = cli_dir / file
        results.append(check_item(
            f"File: {file}",
            file_path.exists()
        ))
    
    # 3. Check command modules
    print_header("3. Command Modules")
    
    commands_dir = cli_dir / "commands"
    command_modules = [
        "chat_command.py",
        "tasks_command.py",
        "knowledge_command.py",
        "hunter_command.py",
        "governance_command.py",
        "verification_command.py",
        "ide_command.py",
        "voice_command.py",
    ]
    
    results.append(check_item(
        "Commands directory",
        commands_dir.exists() and commands_dir.is_dir()
    ))
    
    for module in command_modules:
        module_path = commands_dir / module
        results.append(check_item(
            f"Module: {module}",
            module_path.exists()
        ))
    
    # 4. Check dependencies
    print_header("4. Python Dependencies")
    
    required_modules = [
        ("httpx", "HTTP client"),
        ("websockets", "WebSocket support"),
        ("rich", "Terminal UI"),
        ("prompt_toolkit", "Interactive prompts"),
        ("yaml", "Configuration"),
    ]
    
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            results.append(check_item(
                f"{description} ({module_name})",
                True
            ))
        except ImportError:
            results.append(check_item(
                f"{description} ({module_name})",
                False,
                "Install with: pip install -r requirements.txt"
            ))
    
    # 5. Check optional dependencies
    print_header("5. Optional Dependencies")
    
    optional_modules = [
        ("pyaudio", "Audio recording"),
        ("pydub", "Audio playback"),
        ("pytest", "Testing"),
    ]
    
    for module_name, description in optional_modules:
        try:
            __import__(module_name)
            results.append(check_item(
                f"{description} ({module_name})",
                True
            ))
        except ImportError:
            results.append(check_item(
                f"{description} ({module_name}) [OPTIONAL]",
                True,
                "Not installed - feature will be limited"
            ))
    
    # 6. Check test files
    print_header("6. Test Suite")
    
    tests_dir = cli_dir / "tests"
    test_files = [
        "test_cli_basic.py",
        "test_backend_integration.py",
        "test_commands.py",
    ]
    
    results.append(check_item(
        "Tests directory",
        tests_dir.exists() and tests_dir.is_dir()
    ))
    
    for test_file in test_files:
        test_path = tests_dir / test_file
        results.append(check_item(
            f"Test: {test_file}",
            test_path.exists()
        ))
    
    # 7. Check documentation
    print_header("7. Documentation")
    
    doc_files = [
        ("README.md", "User manual"),
        ("INSTALL.md", "Installation guide"),
        ("QUICKSTART.md", "Quick start guide"),
        ("CLI_DELIVERY_SUMMARY.md", "Delivery summary"),
    ]
    
    for doc_file, description in doc_files:
        doc_path = cli_dir / doc_file
        results.append(check_item(
            f"{description} ({doc_file})",
            doc_path.exists()
        ))
    
    # 8. Check configuration directory
    print_header("8. Configuration")
    
    config_dir = Path.home() / ".grace"
    results.append(check_item(
        "Config directory (~/.grace/)",
        True,
        f"Will be created on first run: {config_dir}"
    ))
    
    # 9. Test imports
    print_header("9. Module Imports")
    
    sys.path.insert(0, str(cli_dir))
    
    test_imports = [
        ("grace_client", "GraceAPIClient"),
        ("config", "ConfigManager"),
        ("plugin_manager", "PluginManager"),
        ("voice_handler", "VoiceHandler"),
    ]
    
    for module_name, import_name in test_imports:
        try:
            module = __import__(module_name)
            has_class = hasattr(module, import_name)
            results.append(check_item(
                f"Import {module_name}.{import_name}",
                has_class
            ))
        except Exception as e:
            results.append(check_item(
                f"Import {module_name}.{import_name}",
                False,
                str(e)
            ))
    
    # Summary
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    print(f"Total checks: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Installation verified successfully!{Colors.RESET}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
        print(f"1. Start Grace backend: python -m uvicorn backend.main:app --reload")
        print(f"2. Run CLI: python enhanced_grace_cli.py")
        print(f"3. Read quick start: QUICKSTART.md")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Installation incomplete{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please fix the failed checks above{Colors.RESET}")
        print(f"Run: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
