import sqlite3
import os
import sys
import importlib
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def check_database(db_path):
    print_header(f"Checking Database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at: {db_path}")
        return False
    
    print(f"✅ Database file exists at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("⚠️  No tables found in database!")
        else:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")
        return False

def check_imports():
    print_header("Checking Service Imports")
    
    services = [
        ("backend.misc.anomaly_watchdog", "Anomaly Watchdog"),
        ("backend.core.immutable_log", "Immutable Log (Core)"),
        ("backend.logging.immutable_log", "Immutable Log (Logging)"),
        ("backend.immutable_log", "Immutable Log (Direct Import - Expected to Fail?)")
    ]
    
    # Add root to sys.path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, root_dir)
    
    for module_path, name in services:
        print(f"\nTesting import: {name} ({module_path})")
        try:
            importlib.import_module(module_path)
            print(f"✅ Successfully imported {module_path}")
        except ImportError as e:
            print(f"❌ Failed to import {module_path}")
            print(f"   Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error importing {module_path}")
            print(f"   Error: {e}")

def main():
    print_header("Grace System Verification")
    print(f"Root: {os.getcwd()}")
    
    # Check Root DB
    check_database("grace.db")
    
    # Check Databases DB
    check_database("databases/grace.db")
    
    # Check Imports
    check_imports()

if __name__ == "__main__":
    main()
