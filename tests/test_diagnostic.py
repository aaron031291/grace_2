"""Diagnostic test to find where it hangs"""
import asyncio
import sys

async def test_step_by_step():
    print("Step 1: Import models...")
    sys.stdout.flush()
    from backend.models import async_session
    print("  OK")
    
    print("Step 2: Test DB connection...")
    sys.stdout.flush()
    from sqlalchemy import text
    async with async_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    print("  OK")
    
    print("Step 3: Import trigger_mesh...")
    sys.stdout.flush()
    from backend.trigger_mesh import trigger_mesh, TriggerEvent
    print("  OK")
    
    print("Step 4: Create test event...")
    sys.stdout.flush()
    from datetime import datetime, timezone
    test_event = TriggerEvent(
        event_type="test.diagnostic",
        source="test",
        actor="test",
        resource="test",
        payload={"test": True},
        timestamp=datetime.now(timezone.utc)
    )
    print("  OK")
    
    print("Step 5: Publish event...")
    sys.stdout.flush()
    await trigger_mesh.publish(test_event)
    print("  OK")
    
    print("\nAll steps passed!")

if __name__ == "__main__":
    asyncio.run(test_step_by_step())
