import sqlite3
import sys
import os

def check_db():
    print("="*30)
    print("DATABASE CHECK")
    print("="*30)
    db_path = "databases/grace.db"
    if not os.path.exists(db_path):
        # Fallback if running from scripts dir
        if os.path.exists("../databases/grace.db"):
            db_path = "../databases/grace.db"
            
    if not os.path.exists(db_path):
        print(f"[FAIL] Database file '{db_path}' not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Found {len(tables)} tables.")
        if "vector_embeddings" in tables:
            print("[OK] Table 'vector_embeddings' exists.")
        else:
            print("[FAIL] Table 'vector_embeddings' MISSING.")
            print("Existing tables:", ", ".join(sorted(tables)))
            
    except Exception as e:
        print(f"[ERROR] checking database: {e}")

def check_imports():
    print("\n" + "="*30)
    print("IMPORT CHECK")
    print("="*30)
    
    # Add root to path
    from pathlib import Path
    root_dir = Path(__file__).parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
    modules_to_check = [
        "backend.anomaly_watchdog",
        "backend.immutable_log"
    ]
    
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"[OK] Successfully imported {module}")
        except ImportError as e:
            print(f"[FAIL] Failed to import {module}: {e}")
        except Exception as e:
            print(f"[FAIL] Error importing {module}: {e}")

if __name__ == "__main__":
    check_db()
    check_imports()
