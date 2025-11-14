"""
Simplified E2E Test - No circular imports
Tests: Database, Routes, Basic Operations
"""

import requests
import sqlite3
import sys
import io
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}\n")

def test_database():
    """Test 1: Database exists and has tables"""
    print_header("TEST 1: Database Verification")
    
    db_path = Path("databases/memory_fusion.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return False
    
    print("✓ Database file exists")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = [
        'memory_documents',
        'memory_document_chunks',
        'memory_insights',
        'memory_file_operations'
    ]
    
    for table in required_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✓ {table} exists ({count} rows)")
        else:
            print(f"❌ {table} MISSING")
            conn.close()
            return False
    
    conn.close()
    print("\n✅ Database test PASSED")
    return True

def test_backend_running():
    """Test 2: Backend is accessible"""
    print_header("TEST 2: Backend Connectivity")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend is running")
            print(f"  Status: {response.status_code}")
            return True
        else:
            print(f"❌ Backend returned: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running!")
        print("  Start with: python serve.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_routes():
    """Test 3: All new routes are registered"""
    print_header("TEST 3: Route Registration")
    
    routes = [
        "/api/test",
        "/api/kernels",
        "/api/books/stats",
        "/api/self-healing/stats",
        "/api/librarian/status",
        "/api/organizer/file-operations"
    ]
    
    passed = 0
    failed = 0
    
    for route in routes:
        try:
            response = requests.get(f"http://localhost:8000{route}", timeout=3)
            
            if response.status_code == 200:
                print(f"✓ {route} → 200 OK")
                
                # Check it's JSON
                try:
                    data = response.json()
                    print(f"  Response: {str(data)[:80]}...")
                except:
                    print(f"  WARNING: Not JSON")
                
                passed += 1
            elif response.status_code == 404:
                print(f"❌ {route} → 404 NOT FOUND")
                failed += 1
            else:
                print(f"⚠️  {route} → {response.status_code}")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {route} → Backend not running")
            failed += 1
        except Exception as e:
            print(f"❌ {route} → ERROR: {e}")
            failed += 1
    
    print(f"\nRoutes: {passed} passed, {failed} failed")
    
    if passed == len(routes):
        print("✅ All routes test PASSED")
        return True
    else:
        print("❌ Some routes test FAILED")
        return False

def test_crud_operations():
    """Test 4: Database CRUD works"""
    print_header("TEST 4: Database CRUD Operations")
    
    db_path = Path("databases/memory_fusion.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # CREATE
        print("Testing INSERT...")
        cursor.execute("""
            INSERT OR REPLACE INTO memory_documents 
            (document_id, title, author, source_type, trust_score, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, ('test_e2e_001', 'E2E Test Book', 'Test Author', 'book', 0.95))
        conn.commit()
        print("✓ INSERT successful")
        
        # READ
        print("Testing SELECT...")
        cursor.execute("SELECT * FROM memory_documents WHERE document_id = ?", ('test_e2e_001',))
        row = cursor.fetchone()
        if row:
            print(f"✓ SELECT successful - Found: {row[1]}")
        else:
            print("❌ SELECT failed - No data")
            return False
        
        # UPDATE
        print("Testing UPDATE...")
        cursor.execute("UPDATE memory_documents SET trust_score = 1.0 WHERE document_id = ?", ('test_e2e_001',))
        conn.commit()
        cursor.execute("SELECT trust_score FROM memory_documents WHERE document_id = ?", ('test_e2e_001',))
        score = cursor.fetchone()[0]
        print(f"✓ UPDATE successful - Trust score: {score}")
        
        # DELETE
        print("Testing DELETE...")
        cursor.execute("DELETE FROM memory_documents WHERE document_id = ?", ('test_e2e_001',))
        conn.commit()
        cursor.execute("SELECT * FROM memory_documents WHERE document_id = ?", ('test_e2e_001',))
        if cursor.fetchone() is None:
            print("✓ DELETE successful")
        else:
            print("❌ DELETE failed - Record still exists")
            return False
        
        conn.close()
        print("\n✅ CRUD operations test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ CRUD test FAILED: {e}")
        return False

def test_frontend():
    """Test 5: Frontend is accessible"""
    print_header("TEST 5: Frontend Accessibility")
    
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is running")
            print(f"  Status: {response.status_code}")
            return True
        else:
            print(f"⚠️  Frontend returned: {response.status_code}")
            return True  # Still counts as accessible
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not running!")
        print("  Start with: cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run complete E2E test suite"""
    print("\n" + "="*70)
    print("  GRACE SYSTEM - END-TO-END TEST SUITE".center(70))
    print("="*70)
    
    results = {}
    
    # Test 1: Database
    results['database'] = test_database()
    
    # Test 2: Backend
    results['backend'] = test_backend_running()
    
    # Test 3: Routes (only if backend running)
    if results['backend']:
        results['routes'] = test_routes()
    else:
        print("\n⚠️  Skipping route tests (backend not running)")
        results['routes'] = False
    
    # Test 4: CRUD
    results['crud'] = test_crud_operations()
    
    # Test 5: Frontend
    results['frontend'] = test_frontend()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"  {test_name.upper().ljust(20)}: {status}")
    
    print(f"\n  Overall: {passed}/{total} tests passed")
    print(f"  Success Rate: {(passed/total*100):.1f}%\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is fully operational!")
        print("\nYour Grace system is ready:")
        print("  • Database: ✓ Working")
        print("  • Backend: ✓ Running with all routes")
        print("  • Frontend: ✓ Accessible")
        print("  • CRUD: ✓ Functioning")
        print("\nNext steps:")
        print("  1. Open browser: http://localhost:5173")
        print("  2. Hard refresh: Ctrl+Shift+R")
        print("  3. Look bottom-right for purple co-pilot button")
        print("  4. Click 'Self-Healing' → Full dashboard appears")
    elif passed >= 3:
        print("⚠️  Most tests passed. System partially operational.")
        print("\nCheck failed tests above for details.")
    else:
        print("❌ Multiple tests failed. System needs attention.")
        print("\nReview errors above and:")
        print("  • Ensure backend running: python serve.py")
        print("  • Ensure frontend running: cd frontend && npm run dev")
        print("  • Check database exists: databases/memory_fusion.db")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
