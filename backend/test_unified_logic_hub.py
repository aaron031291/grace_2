"""
Test Unified Logic Hub End-to-End Flow

Demonstrates the complete pipeline for schema, code, and playbook updates
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_schema_update():
    """Test schema update flow"""
    print("\n" + "="*60)
    print("TEST: Schema Update Flow")
    print("="*60)
    
    from unified_logic_hub import submit_schema_update
    
    # Submit schema update
    update_id = await submit_schema_update(
        endpoint="/api/memory/store",
        current_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "domain": {"type": "string"}
            },
            "required": ["content"]
        },
        proposed_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "domain": {"type": "string"},
                "metadata": {"type": "object"},  # New field
                "tags": {"type": "array"}  # New field
            },
            "required": ["content"]
        },
        created_by="test_user",
        risk_level="low"
    )
    
    print(f"\n✓ Schema update submitted: {update_id}")
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Check status
    from unified_logic_hub import unified_logic_hub
    status = await unified_logic_hub.get_update_status(update_id)
    
    if status:
        print(f"✓ Status: {status['status']}")
        print(f"✓ Validation: {status['validation_results']}")
        print(f"✓ Crypto ID: {status.get('crypto_id', 'N/A')[:20]}...")
    else:
        print("✗ Update not found")
    
    return update_id


async def test_code_module_update():
    """Test code module update flow"""
    print("\n" + "="*60)
    print("TEST: Code Module Update Flow")
    print("="*60)
    
    from unified_logic_hub import submit_code_module_update
    
    # Submit code module update
    update_id = await submit_code_module_update(
        modules={
            "test_module.py": """
# Test module for unified logic hub
def hello_grace():
    return "Hello from updated code!"

def calculate(x, y):
    return x + y
"""
        },
        component_targets=["agentic_spine", "ml_pipeline"],
        created_by="test_developer",
        risk_level="medium"
    )
    
    print(f"\n✓ Code module update submitted: {update_id}")
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Check status
    from unified_logic_hub import unified_logic_hub
    status = await unified_logic_hub.get_update_status(update_id)
    
    if status:
        print(f"✓ Status: {status['status']}")
        print(f"✓ Components: {', '.join(status['component_targets'])}")
        print(f"✓ Checksum: {status.get('checksum', 'N/A')[:16]}...")
    else:
        print("✗ Update not found")
    
    return update_id


async def test_playbook_update():
    """Test playbook update flow"""
    print("\n" + "="*60)
    print("TEST: Playbook Update Flow")
    print("="*60)
    
    from unified_logic_hub import submit_playbook_update
    
    # Submit playbook update
    update_id = await submit_playbook_update(
        playbook_name="test_healing_playbook",
        playbook_content={
            "description": "Test healing playbook for database connection issues",
            "triggers": [
                {"type": "error_pattern", "pattern": "database connection failed"}
            ],
            "steps": [
                {"action": "restart_connection_pool", "timeout": 30},
                {"action": "verify_connectivity", "retries": 3}
            ],
            "rollback_steps": [
                {"action": "restore_previous_pool"}
            ],
            "success_criteria": {
                "metric": "db_connection_success_rate",
                "threshold": 0.95
            }
        },
        component_targets=["self_heal_scheduler", "playbook_executor"],
        created_by="test_healer",
        risk_level="medium"
    )
    
    print(f"\n✓ Playbook update submitted: {update_id}")
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Check status
    from unified_logic_hub import unified_logic_hub
    status = await unified_logic_hub.get_update_status(update_id)
    
    if status:
        print(f"✓ Status: {status['status']}")
        print(f"✓ History: {len(status['status_history'])} stages")
        if status.get('diagnostics'):
            print(f"⚠ Diagnostics: {status['diagnostics']}")
    else:
        print("✗ Update not found")
    
    return update_id


async def test_hub_stats():
    """Test hub statistics"""
    print("\n" + "="*60)
    print("TEST: Hub Statistics")
    print("="*60)
    
    from unified_logic_hub import unified_logic_hub
    
    stats = unified_logic_hub.get_stats()
    
    print(f"\n✓ Total Updates: {stats['total_updates']}")
    print(f"✓ Successful: {stats['successful_updates']}")
    print(f"✓ Failed: {stats['failed_updates']}")
    print(f"✓ Rollbacks: {stats['rollbacks']}")
    print(f"✓ Active: {stats['active_updates']}")
    print(f"✓ Success Rate: {stats['success_rate']:.1%}")


async def test_list_updates():
    """Test listing recent updates"""
    print("\n" + "="*60)
    print("TEST: List Recent Updates")
    print("="*60)
    
    from unified_logic_hub import unified_logic_hub
    
    updates = await unified_logic_hub.list_recent_updates(limit=5)
    
    print(f"\n✓ Recent updates ({len(updates)}):")
    for update in updates:
        print(f"  - {update['update_id']}: {update['update_type']} ({update['status']})")


async def test_immutable_log_integration():
    """Test immutable log integration"""
    print("\n" + "="*60)
    print("TEST: Immutable Log Integration")
    print("="*60)
    
    try:
        from immutable_log import immutable_log
        
        # Get recent logic hub entries
        entries = await immutable_log.get_entries(
            subsystem="unified_logic_hub",
            limit=5
        )
        
        print(f"\n✓ Immutable log entries: {len(entries)}")
        for entry in entries:
            print(f"  - Seq {entry['sequence']}: {entry['action']} ({entry['result']})")
        
    except ImportError:
        print("⚠ Immutable log not available")


async def test_trigger_mesh_subscription():
    """Test trigger mesh subscription"""
    print("\n" + "="*60)
    print("TEST: Trigger Mesh Subscription")
    print("="*60)
    
    try:
        from trigger_mesh import trigger_mesh
        
        received_events = []
        
        async def on_logic_update(event):
            received_events.append(event)
            print(f"  ↳ Received: {event.event_type} for {event.payload.get('update_id')}")
        
        # Subscribe
        trigger_mesh.subscribe("unified_logic.*", on_logic_update)
        print("\n✓ Subscribed to unified_logic.* events")
        
        # Submit a test update
        from unified_logic_hub import unified_logic_hub
        
        update_id = await unified_logic_hub.submit_update(
            update_type="config",
            component_targets=["test_component"],
            content={"config_changes": {"test": "value"}},
            created_by="test_subscription",
            risk_level="low"
        )
        
        # Wait for event
        await asyncio.sleep(3)
        
        if received_events:
            print(f"✓ Received {len(received_events)} events via trigger mesh")
        else:
            print("⚠ No events received (trigger mesh may not be started)")
        
    except ImportError:
        print("⚠ Trigger mesh not available")


async def main():
    """Run all tests"""
    
    print("\n" + "="*60)
    print("UNIFIED LOGIC HUB - END-TO-END TEST SUITE")
    print("="*60)
    
    try:
        # Test core update types
        await test_schema_update()
        await test_code_module_update()
        await test_playbook_update()
        
        # Test observability
        await test_hub_stats()
        await test_list_updates()
        
        # Test integrations
        await test_immutable_log_integration()
        await test_trigger_mesh_subscription()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
