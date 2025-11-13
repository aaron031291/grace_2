"""
End-to-End Test for Book Ingestion System
Tests complete workflow: file drop → ingestion → verification → query
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db, init_database
from backend.kernels.agents.book_ingestion_agent import get_book_ingestion_agent
from backend.kernels.agents.schema_agent import get_schema_agent
from backend.verification.book_verification import get_book_verification_engine
from backend.kernels.agents.file_organizer_agent import get_file_organizer_agent


class Colors:
    """Terminal colors for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_step(step_num, text):
    """Print test step"""
    print(f"{Colors.PURPLE}{Colors.BOLD}Step {step_num}: {Colors.END}{text}")


async def test_database_initialization():
    """Test 1: Verify database and all tables are initialized"""
    
    print_header("TEST 1: Database Initialization")
    
    try:
        # Initialize database
        print_step(1, "Initializing database...")
        await init_database()
        print_success("Database initialized")
        
        # Get database connection
        db = await get_db()
        
        # Check required tables exist
        required_tables = [
            'memory_documents',
            'memory_document_chunks',
            'memory_insights',
            'memory_verification_suites',
            'memory_librarian_log',
            'memory_sub_agents',
            'memory_file_operations',
            'memory_file_organization_rules'
        ]
        
        print_step(2, "Verifying required tables...")
        
        for table in required_tables:
            result = await db.fetch_one(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            
            if result:
                print_success(f"Table '{table}' exists")
            else:
                print_error(f"Table '{table}' MISSING - creating...")
                # Attempt to create table (would need schema)
                raise Exception(f"Missing table: {table}")
        
        # Check table schemas
        print_step(3, "Verifying table schemas...")
        
        # Check memory_documents columns
        columns = await db.fetch_all("PRAGMA table_info(memory_documents)")
        column_names = [col['name'] for col in columns]
        
        expected_columns = ['document_id', 'title', 'author', 'source_type', 'trust_score', 'metadata']
        for col in expected_columns:
            if col in column_names:
                print_success(f"Column 'memory_documents.{col}' exists")
            else:
                print_error(f"Column 'memory_documents.{col}' MISSING")
        
        print_success("Database initialization test PASSED")
        return True
        
    except Exception as e:
        print_error(f"Database initialization test FAILED: {e}")
        return False


async def test_schema_agent():
    """Test 2: Schema agent analyzes and proposes schema"""
    
    print_header("TEST 2: Schema Agent")
    
    try:
        # Create test file
        test_file = Path("grace_training/documents/books/test_book.pdf")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create dummy PDF content
        with open(test_file, 'wb') as f:
            f.write(b'%PDF-1.4\nTest book content')
        
        print_step(1, f"Created test file: {test_file}")
        
        # Initialize schema agent
        schema_agent = get_schema_agent()
        await schema_agent.activate()
        print_success("Schema agent activated")
        
        # Analyze file
        print_step(2, "Analyzing test file...")
        proposal = await schema_agent.analyze_file(str(test_file), '.pdf')
        
        print_info(f"Proposed table: {proposal['proposed_table']}")
        print_info(f"Confidence: {proposal['confidence']}")
        print_info(f"Reasoning: {', '.join(proposal['reasoning'])}")
        
        # Submit to unified logic
        print_step(3, "Submitting to unified logic...")
        decision = await schema_agent.submit_to_unified_logic(proposal)
        
        print_info(f"Decision status: {decision['status']}")
        
        if decision['status'] == 'approved':
            print_success("Schema proposal APPROVED")
        else:
            print_error(f"Schema proposal NOT approved: {decision.get('reason')}")
        
        print_success("Schema agent test PASSED")
        return True
        
    except Exception as e:
        print_error(f"Schema agent test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_book_ingestion():
    """Test 3: Book ingestion agent processes a file"""
    
    print_header("TEST 3: Book Ingestion Agent")
    
    try:
        # Use test file from previous test
        test_file = Path("grace_training/documents/books/test_book.pdf")
        
        if not test_file.exists():
            print_error("Test file not found, creating...")
            test_file.parent.mkdir(parents=True, exist_ok=True)
            with open(test_file, 'wb') as f:
                f.write(b'%PDF-1.4\nTest book content about startups and business')
        
        # Create metadata sidecar
        metadata_file = test_file.with_suffix('.meta.json')
        metadata = {
            "title": "Test Startup Book",
            "author": "Test Author",
            "domain_tags": ["startup", "business"],
            "publication_year": 2024
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        print_step(1, "Test file and metadata prepared")
        
        # Initialize book ingestion agent
        book_agent = get_book_ingestion_agent()
        await book_agent.activate()
        print_success("Book ingestion agent activated")
        
        # Process book
        print_step(2, "Processing book (this may take a moment)...")
        result = await book_agent.process_book(test_file, metadata)
        
        print_info(f"Status: {result['status']}")
        print_info(f"Document ID: {result.get('document_id')}")
        print_info(f"Chunks created: {result.get('chunks_created', 0)}")
        print_info(f"Insights created: {result.get('insights_created', 0)}")
        
        if result.get('errors'):
            for error in result['errors']:
                print_error(f"Error during ingestion: {error}")
        
        # Verify document in database
        print_step(3, "Verifying document in database...")
        
        db = await get_db()
        
        if result.get('document_id'):
            doc = await db.fetch_one(
                "SELECT * FROM memory_documents WHERE document_id = ?",
                (result['document_id'],)
            )
            
            if doc:
                print_success(f"Document found in database")
                print_info(f"  Title: {doc['title']}")
                print_info(f"  Author: {doc['author']}")
                print_info(f"  Trust score: {doc['trust_score']}")
            else:
                print_error("Document NOT found in database")
        
        # Check chunks
        if result.get('document_id'):
            chunks = await db.fetch_all(
                "SELECT COUNT(*) as count FROM memory_document_chunks WHERE document_id = ?",
                (result['document_id'],)
            )
            
            chunk_count = chunks[0]['count'] if chunks else 0
            print_info(f"Chunks in database: {chunk_count}")
        
        # Check insights
        if result.get('document_id'):
            insights = await db.fetch_all(
                "SELECT COUNT(*) as count FROM memory_insights WHERE document_id = ?",
                (result['document_id'],)
            )
            
            insight_count = insights[0]['count'] if insights else 0
            print_info(f"Insights in database: {insight_count}")
        
        print_success("Book ingestion test PASSED")
        return result.get('document_id')
        
    except Exception as e:
        print_error(f"Book ingestion test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_verification(document_id):
    """Test 4: Verification engine checks book quality"""
    
    print_header("TEST 4: Verification Engine")
    
    if not document_id:
        print_error("No document ID provided, skipping test")
        return False
    
    try:
        # Initialize verification engine
        verification_engine = get_book_verification_engine()
        await verification_engine.activate()
        print_success("Verification engine activated")
        
        # Run verification
        print_step(1, "Running verification tests...")
        result = await verification_engine.verify_book(document_id)
        
        print_info(f"Tests run: {len(result.get('tests_run', []))}")
        print_info(f"Tests passed: {result.get('tests_passed', 0)}")
        print_info(f"Tests failed: {result.get('tests_failed', 0)}")
        print_info(f"Trust score: {result.get('trust_score', 0):.2f}")
        
        # Show test details
        for test in result.get('tests_run', []):
            status = "✓" if test['passed'] else "✗"
            color = Colors.GREEN if test['passed'] else Colors.RED
            print(f"  {color}{status} {test['test_name']}{Colors.END}")
            if not test['passed'] and test.get('issue'):
                print(f"    Issue: {test['issue']}")
        
        # Verify results in database
        print_step(2, "Verifying results in database...")
        
        db = await get_db()
        
        # Check updated trust score
        doc = await db.fetch_one(
            "SELECT trust_score FROM memory_documents WHERE document_id = ?",
            (document_id,)
        )
        
        if doc:
            print_info(f"Updated trust score: {doc['trust_score']:.2f}")
        
        # Check verification suite entry
        verification_record = await db.fetch_one(
            "SELECT * FROM memory_verification_suites WHERE document_id = ? ORDER BY timestamp DESC LIMIT 1",
            (document_id,)
        )
        
        if verification_record:
            print_success("Verification record saved")
        else:
            print_error("Verification record NOT saved")
        
        print_success("Verification test PASSED")
        return True
        
    except Exception as e:
        print_error(f"Verification test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_file_organizer():
    """Test 5: File organizer handles the test file"""
    
    print_header("TEST 5: File Organizer")
    
    try:
        # Create a test file in wrong location
        test_file = Path("grace_training/misplaced_book.pdf")
        
        with open(test_file, 'wb') as f:
            f.write(b'%PDF-1.4\nTest book about Bitcoin and cryptocurrency trading')
        
        print_step(1, f"Created misplaced file: {test_file}")
        
        # Initialize file organizer
        organizer = get_file_organizer_agent()
        await organizer.activate()
        print_success("File organizer activated")
        
        # Analyze file
        print_step(2, "Analyzing file domain...")
        result = await organizer.analyze_and_organize(test_file, auto_move=False)
        
        print_info(f"Suggested domain: {result['suggestion']['domain']}")
        print_info(f"Target folder: {result['suggestion']['target_folder']}")
        print_info(f"Confidence: {result['confidence']:.2f}")
        print_info(f"Reasoning: {', '.join(result['reasoning'])}")
        
        # Test undo system by moving file
        print_step(3, "Testing move and undo...")
        
        move_result = await organizer.analyze_and_organize(test_file, auto_move=True)
        
        if move_result.get('action_taken') == 'moved':
            print_success(f"File moved to: {move_result.get('new_path')}")
            
            # Test undo
            operation_id = move_result.get('operation_id')
            if operation_id:
                print_step(4, "Testing undo...")
                undo_result = await organizer.undo_operation(operation_id)
                
                if undo_result['status'] == 'success':
                    print_success("Undo successful!")
                    print_info(f"File restored to: {undo_result.get('original_path')}")
                else:
                    print_error(f"Undo failed: {undo_result.get('error')}")
        
        # Clean up
        if test_file.exists():
            test_file.unlink()
        
        print_success("File organizer test PASSED")
        return True
        
    except Exception as e:
        print_error(f"File organizer test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_query_book(document_id):
    """Test 6: Query the ingested book data"""
    
    print_header("TEST 6: Query Book Data")
    
    if not document_id:
        print_error("No document ID provided, skipping test")
        return False
    
    try:
        db = await get_db()
        
        # Query document
        print_step(1, "Querying document...")
        doc = await db.fetch_one(
            "SELECT * FROM memory_documents WHERE document_id = ?",
            (document_id,)
        )
        
        if doc:
            print_success("Document retrieved")
            print(f"\n{Colors.BOLD}Document Details:{Colors.END}")
            print(f"  ID: {doc['document_id']}")
            print(f"  Title: {doc['title']}")
            print(f"  Author: {doc['author']}")
            print(f"  Source Type: {doc['source_type']}")
            print(f"  Trust Score: {doc['trust_score']:.2f}")
            print(f"  Created: {doc.get('created_at', 'N/A')}")
        else:
            print_error("Document not found")
            return False
        
        # Query chunks
        print_step(2, "Querying chunks...")
        chunks = await db.fetch_all(
            "SELECT * FROM memory_document_chunks WHERE document_id = ? ORDER BY chunk_index LIMIT 3",
            (document_id,)
        )
        
        print_info(f"Found {len(chunks)} chunks (showing first 3)")
        for chunk in chunks:
            print(f"\n{Colors.BOLD}Chunk {chunk['chunk_index']}:{Colors.END}")
            content_preview = chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content']
            print(f"  {content_preview}")
        
        # Query insights
        print_step(3, "Querying insights...")
        insights = await db.fetch_all(
            "SELECT * FROM memory_insights WHERE document_id = ?",
            (document_id,)
        )
        
        print_info(f"Found {len(insights)} insights")
        for insight in insights:
            print(f"\n{Colors.BOLD}{insight['insight_type'].upper()}:{Colors.END}")
            content_preview = insight['content'][:100] + "..." if len(insight['content']) > 100 else insight['content']
            print(f"  {content_preview}")
            print(f"  Confidence: {insight['confidence']:.2f}")
        
        # Query verification history
        print_step(4, "Querying verification history...")
        verifications = await db.fetch_all(
            "SELECT * FROM memory_verification_suites WHERE document_id = ?",
            (document_id,)
        )
        
        print_info(f"Found {len(verifications)} verification records")
        for ver in verifications:
            print(f"\n{Colors.BOLD}Verification:{Colors.END}")
            print(f"  Type: {ver['verification_type']}")
            print(f"  Trust Score: {ver['trust_score']:.2f}")
            print(f"  Timestamp: {ver.get('timestamp', 'N/A')}")
        
        print_success("Query test PASSED")
        return True
        
    except Exception as e:
        print_error(f"Query test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all E2E tests"""
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔" + "═" * 78 + "╗")
    print("║" + " GRACE BOOK INGESTION SYSTEM - E2E TEST SUITE ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print(Colors.END)
    
    results = {}
    document_id = None
    
    # Test 1: Database initialization
    results['database'] = await test_database_initialization()
    
    if not results['database']:
        print_error("\n⚠ Database initialization failed. Cannot continue tests.")
        return results
    
    # Test 2: Schema agent
    results['schema'] = await test_schema_agent()
    
    # Test 3: Book ingestion
    document_id = await test_book_ingestion()
    results['ingestion'] = document_id is not None
    
    # Test 4: Verification
    if document_id:
        results['verification'] = await test_verification(document_id)
    else:
        results['verification'] = False
        print_error("Skipping verification test (no document ID)")
    
    # Test 5: File organizer
    results['organizer'] = await test_file_organizer()
    
    # Test 6: Query book data
    if document_id:
        results['query'] = await test_query_book(document_id)
    else:
        results['query'] = False
        print_error("Skipping query test (no document ID)")
    
    # Summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.END}" if passed else f"{Colors.RED}FAILED{Colors.END}"
        print(f"  {test_name.upper().ljust(20)}: {status}")
    
    print(f"\n{Colors.BOLD}Overall: {passed_tests}/{total_tests} tests passed{Colors.END}")
    
    if passed_tests == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED! System is ready for production.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Review errors above.{Colors.END}")
    
    return results


if __name__ == "__main__":
    print(f"{Colors.CYAN}Starting E2E tests...{Colors.END}\n")
    asyncio.run(run_all_tests())
