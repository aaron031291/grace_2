"""Verify all Grace systems start correctly"""

import asyncio
import time

async def verify():
    print("\n" + "="*60)
    print("GRACE STARTUP VERIFICATION")
    print("="*60 + "\n")
    
    print("Checking imports...")
    try:
        from backend.main import app
        print("[OK] Main app imports")
        
        from backend.reflection import reflection_service
        print("[OK] Reflection service")
        
        from backend.trigger_mesh import trigger_mesh
        print("[OK] Trigger mesh")
        
        from backend.task_executor import task_executor
        print("[OK] Task executor")
        
        from backend.self_healing import health_monitor
        print("[OK] Health monitor")
        
        from backend.meta_loop import meta_loop_engine
        print("[OK] Meta-loop engine")
        
        from backend.trusted_sources import trust_manager
        print("[OK] Trust manager")
        
        from backend.training_pipeline import training_pipeline
        print("[OK] Training pipeline")
        
        from backend.verification import verification_engine
        print("[OK] Verification engine")
        
        print("\n[SUCCESS] All modules import without errors!\n")
        
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}\n")
        return False
    
    print("Checking database models...")
    try:
        from backend.models import Base, engine
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print(f"[OK] {len(Base.metadata.tables)} tables created")
        
        table_list = list(Base.metadata.tables.keys())
        print(f"\nTables: {', '.join(table_list[:10])}...")
        print(f"        ...and {len(table_list) - 10} more\n")
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}\n")
        return False
    
    print("System verification complete!")
    print("\n" + "="*60)
    print("READY TO START")
    print("="*60)
    print("\nRun: python grace_cli.py start")
    print("Or:  uvicorn backend.main:app --reload\n")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(verify())
    exit(0 if result else 1)
