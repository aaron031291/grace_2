"""
Comprehensive verification script - checks all components are ready
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def check_file(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print(f"{Colors.GREEN}✓{Colors.END} {description}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {description} - NOT FOUND: {path}")
        return False

def check_import(module_path, description):
    """Check if a module can be imported"""
    try:
        __import__(module_path)
        print(f"{Colors.GREEN}✓{Colors.END} {description}")
        return True
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {description} - ERROR: {e}")
        return False

def main():
    print_header("GRACE BOOK SYSTEM - COMPONENT VERIFICATION")
    
    results = {}
    
    # Check backend files
    print(f"{Colors.BOLD}Backend Components:{Colors.END}\n")
    results['backend_db'] = check_file('backend/database.py', 'Database helper')
    results['book_agent'] = check_file('backend/kernels/agents/book_ingestion_agent.py', 'Book ingestion agent')
    results['schema_agent'] = check_file('backend/kernels/agents/schema_agent.py', 'Schema agent')
    results['organizer_agent'] = check_file('backend/kernels/agents/file_organizer_agent.py', 'File organizer agent')
    results['verification'] = check_file('backend/verification/book_verification.py', 'Verification engine')
    results['book_routes'] = check_file('backend/routes/book_dashboard.py', 'Book dashboard routes')
    results['organizer_routes'] = check_file('backend/routes/file_organizer_api.py', 'File organizer routes')
    results['test_routes'] = check_file('backend/routes/test_endpoint.py', 'Test endpoint')
    
    # Check schemas
    print(f"\n{Colors.BOLD}Database Schemas:{Colors.END}\n")
    results['schema_ops'] = check_file('backend/memory_tables/schema/file_operations.yaml', 'File operations schema')
    results['schema_rules'] = check_file('backend/memory_tables/schema/file_organization_rules.yaml', 'Organization rules schema')
    
    # Check frontend components
    print(f"\n{Colors.BOLD}Frontend Components:{Colors.END}\n")
    results['book_panel'] = check_file('frontend/src/components/BookLibraryPanel.tsx', 'Book library panel')
    results['organizer_panel'] = check_file('frontend/src/components/FileOrganizerPanel.tsx', 'File organizer panel')
    results['copilot'] = check_file('frontend/src/components/LibrarianCopilot.tsx', 'Librarian co-pilot')
    results['notifications'] = check_file('frontend/src/components/NotificationToast.tsx', 'Notification toasts')
    results['overview'] = check_file('frontend/src/components/GraceOverview.tsx', 'Overview page')
    results['command_palette'] = check_file('frontend/src/components/CommandPalette.tsx', 'Command palette')
    results['onboarding'] = check_file('frontend/src/components/OnboardingWalkthrough.tsx', 'Onboarding walkthrough')
    
    # Check directories
    print(f"\n{Colors.BOLD}Directory Structure:{Colors.END}\n")
    results['books_dir'] = check_file('grace_training/documents/books', 'Books directory')
    results['backup_dir'] = check_file('.librarian_backups', 'Backup directory')
    
    # Check database
    print(f"\n{Colors.BOLD}Database:{Colors.END}\n")
    results['db_exists'] = check_file('databases/memory_fusion.db', 'Database file')
    
    if results['db_exists']:
        try:
            import sqlite3
            conn = sqlite3.connect('databases/memory_fusion.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'memory_documents',
                'memory_document_chunks',
                'memory_insights',
                'memory_verification_suites',
                'memory_file_operations',
                'memory_librarian_log'
            ]
            
            for table in required_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"{Colors.GREEN}✓{Colors.END} Table '{table}' exists ({count} rows)")
                else:
                    print(f"{Colors.RED}✗{Colors.END} Table '{table}' MISSING")
                    results[f'table_{table}'] = False
            
            conn.close()
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Database check failed: {e}")
    
    # Check Python imports
    print(f"\n{Colors.BOLD}Python Imports:{Colors.END}\n")
    results['import_db'] = check_import('backend.database', 'backend.database')
    results['import_book_routes'] = check_import('backend.routes.book_dashboard', 'Book dashboard routes')
    results['import_org_routes'] = check_import('backend.routes.file_organizer_api', 'File organizer routes')
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"Total checks: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {total - passed}{Colors.END}")
    print(f"\nSuccess rate: {(passed/total*100):.1f}%\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL COMPONENTS VERIFIED!{Colors.END}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
        print("1. Start backend: python serve.py")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Open browser: http://localhost:5173")
        print("4. Click 'Memory Studio' → See all tabs!")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some components missing{Colors.END}")
        print("\nRe-run initialization:")
        print("  python scripts/init_book_tables_simple.py")

if __name__ == "__main__":
    main()
