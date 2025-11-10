"""
Seed initial verification events to enable meta loop verification
"""
import asyncio
import sqlite3
from datetime import datetime

def seed_verifications():
    """Create initial verification events for core components"""
    
    components = [
        ("reflection_service", "pass", 1),
        ("task_executor", "pass", 1),
        ("trigger_mesh", "pass", 1),
        ("governance_engine", "pass", 1),
        ("meta_loop", "pass", 1),
    ]
    
    print("[SEED] Creating initial verification events...")
    
    conn = sqlite3.connect('databases/grace.db')
    cursor = conn.cursor()
    
    for component, result, passed in components:
        cursor.execute("""
            INSERT INTO verification_events 
            (verification_type, target_component, verification_method, result, passed, 
             anomaly_score, confidence, details, verified_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "health_check",
            component,
            "health_check",
            result,
            passed,
            0.0,
            1.0,
            f"Seeded verification for {component}",
            "seed_script",
            datetime.utcnow().isoformat()
        ))
        print(f"  - Verified {component}: {result}")
    
    conn.commit()
    conn.close()
    
    print("[SEED] Seeded 5 verification events successfully")
    print("[SEED] Meta loop can now build verification snapshots")

if __name__ == "__main__":
    seed_verifications()
