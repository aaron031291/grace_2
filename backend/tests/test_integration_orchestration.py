"""
Integration Orchestration Tests
End-to-end tests for system integration, crypto signing, and data flow

Tests:
- Crypto key generation
- Message signing and verification
- System-to-system communication
- Data flow tracking
- Integration health monitoring
- Full stack integration
"""

import pytest
import asyncio
from datetime import datetime, timezone

from backend.crypto_key_manager import crypto_key_manager
from backend.integration_orchestrator import integration_orchestrator


@pytest.mark.asyncio
async def test_crypto_key_generation():
    """Test crypto key generation for components"""
    
    # Start crypto key manager
    await crypto_key_manager.start()
    
    # Generate key for test component
    component_id = "test_component_1"
    crypto_key = await crypto_key_manager.generate_key_for_component(component_id)
    
    assert crypto_key is not None
    assert crypto_key.component_id == component_id
    assert crypto_key.key_id.startswith("key_")
    assert crypto_key.private_key is not None
    assert crypto_key.public_key is not None
    assert not crypto_key.rotated
    
    # Verify key is stored
    assert component_id in crypto_key_manager.component_keys
    assert crypto_key.key_id in crypto_key_manager.keys
    
    print(f"✓ Generated key for {component_id}: {crypto_key.key_id}")


@pytest.mark.asyncio
async def test_message_signing():
    """Test message signing with Ed25519"""
    
    await crypto_key_manager.start()
    
    component_id = "test_component_2"
    message = {
        "type": "test_message",
        "data": "Hello, World!",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Sign message
    signed_message = await crypto_key_manager.sign_message(component_id, message)
    
    assert signed_message is not None
    assert signed_message.component_id == component_id
    assert signed_message.signature is not None
    assert signed_message.message == message
    assert not signed_message.verified
    
    print(f"✓ Signed message from {component_id}")
    print(f"  Signature: {signed_message.signature[:32]}...")


@pytest.mark.asyncio
async def test_message_verification():
    """Test message verification"""
    
    await crypto_key_manager.start()
    
    component_id = "test_component_3"
    message = {
        "type": "test_message",
        "data": "Verify me!",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Sign message
    signed_message = await crypto_key_manager.sign_message(component_id, message)
    
    # Verify message
    is_valid = await crypto_key_manager.verify_message(signed_message)
    
    assert is_valid
    assert signed_message.verified
    
    print(f"✓ Verified message from {component_id}")


@pytest.mark.asyncio
async def test_invalid_signature():
    """Test detection of invalid signatures"""
    
    await crypto_key_manager.start()
    
    component_id = "test_component_4"
    message = {
        "type": "test_message",
        "data": "Original message"
    }
    
    # Sign message
    signed_message = await crypto_key_manager.sign_message(component_id, message)
    
    # Tamper with message
    signed_message.message["data"] = "Tampered message"
    
    # Verify should fail
    is_valid = await crypto_key_manager.verify_message(signed_message)
    
    assert not is_valid
    
    print(f"✓ Detected tampered message from {component_id}")


@pytest.mark.asyncio
async def test_key_rotation():
    """Test key rotation"""
    
    await crypto_key_manager.start()
    
    component_id = "test_component_5"
    
    # Generate initial key
    old_key = await crypto_key_manager.generate_key_for_component(component_id)
    old_key_id = old_key.key_id
    
    # Rotate key
    new_key = await crypto_key_manager.rotate_key(component_id)
    
    assert new_key.key_id != old_key_id
    assert old_key.rotated
    assert not new_key.rotated
    assert crypto_key_manager.component_keys[component_id] == new_key.key_id
    
    print(f"✓ Rotated key for {component_id}")
    print(f"  Old key: {old_key_id}")
    print(f"  New key: {new_key.key_id}")


@pytest.mark.asyncio
async def test_integration_orchestrator_startup():
    """Test integration orchestrator startup"""
    
    await crypto_key_manager.start()
    await integration_orchestrator.start()
    
    assert integration_orchestrator.running
    assert len(integration_orchestrator.CORE_SYSTEMS) > 0
    assert len(integration_orchestrator.integrations) > 0
    
    # Verify crypto keys were generated for all systems
    for system in integration_orchestrator.CORE_SYSTEMS:
        assert system in crypto_key_manager.component_keys
    
    print(f"✓ Integration orchestrator started")
    print(f"  Systems: {len(integration_orchestrator.CORE_SYSTEMS)}")
    print(f"  Integrations: {len(integration_orchestrator.integrations)}")


@pytest.mark.asyncio
async def test_system_to_system_communication():
    """Test signed communication between systems"""
    
    await crypto_key_manager.start()
    await integration_orchestrator.start()
    
    source = "mission_control_hub"
    target = "elite_self_healing"
    message = {
        "type": "test_communication",
        "data": "Hello from Mission Control!",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Send signed message
    signed_message = await integration_orchestrator.send_signed_message(
        source_system=source,
        target_system=target,
        message=message
    )
    
    assert signed_message is not None
    assert signed_message.component_id == source
    
    # Verify message
    is_valid = await integration_orchestrator.verify_and_receive_message(signed_message)
    
    assert is_valid
    
    # Check integration tracking
    integration_key = f"{source}→{target}"
    assert integration_key in integration_orchestrator.integrations
    integration = integration_orchestrator.integrations[integration_key]
    assert integration.message_count > 0
    
    print(f"✓ System-to-system communication: {source} → {target}")


@pytest.mark.asyncio
async def test_data_flow_tracking():
    """Test data flow tracking"""
    
    await integration_orchestrator.start()
    
    source = "autonomous_coding_pipeline"
    destination = "immutable_log"
    data_type = "mission_result"
    
    # Track data flow
    await integration_orchestrator.track_data_flow(
        source=source,
        destination=destination,
        data_type=data_type,
        signed=True
    )
    
    # Verify data flow was tracked
    assert len(integration_orchestrator.data_flows) > 0
    
    latest_flow = integration_orchestrator.data_flows[-1]
    assert latest_flow.source == source
    assert latest_flow.destination == destination
    assert latest_flow.data_type == data_type
    assert latest_flow.signed
    
    print(f"✓ Data flow tracked: {source} → {destination} ({data_type})")


@pytest.mark.asyncio
async def test_integration_statistics():
    """Test integration statistics"""
    
    await crypto_key_manager.start()
    await integration_orchestrator.start()
    
    # Generate some activity
    for i in range(5):
        message = {"test": f"message_{i}"}
        await integration_orchestrator.send_signed_message(
            source_system="test_source",
            target_system="test_target",
            message=message
        )
    
    # Get statistics
    stats = integration_orchestrator.get_statistics()
    
    assert stats["total_systems"] > 0
    assert stats["total_integrations"] > 0
    assert stats["total_messages"] >= 5
    assert stats["signed_messages"] >= 5
    
    print(f"✓ Integration statistics:")
    print(f"  Total systems: {stats['total_systems']}")
    print(f"  Total integrations: {stats['total_integrations']}")
    print(f"  Total messages: {stats['total_messages']}")
    print(f"  Signed messages: {stats['signed_messages']}")


@pytest.mark.asyncio
async def test_crypto_statistics():
    """Test crypto key manager statistics"""
    
    await crypto_key_manager.start()
    
    # Generate some keys
    for i in range(3):
        await crypto_key_manager.generate_key_for_component(f"test_component_{i}")
    
    # Sign some messages
    for i in range(5):
        message = {"test": f"message_{i}"}
        await crypto_key_manager.sign_message("test_component_0", message)
    
    # Get statistics
    stats = crypto_key_manager.get_statistics()
    
    assert stats["total_keys"] >= 3
    assert stats["signatures_generated"] >= 5
    
    print(f"✓ Crypto statistics:")
    print(f"  Total keys: {stats['total_keys']}")
    print(f"  Signatures generated: {stats['signatures_generated']}")


@pytest.mark.asyncio
async def test_integration_map():
    """Test integration map generation"""
    
    await integration_orchestrator.start()
    
    integration_map = integration_orchestrator.get_integration_map()
    
    assert "systems" in integration_map
    assert "integrations" in integration_map
    assert "communication_matrix" in integration_map
    
    assert len(integration_map["systems"]) > 0
    assert len(integration_map["integrations"]) > 0
    
    print(f"✓ Integration map generated:")
    print(f"  Systems: {len(integration_map['systems'])}")
    print(f"  Integrations: {len(integration_map['integrations'])}")
    print(f"  Communication paths: {sum(len(targets) for targets in integration_map['communication_matrix'].values())}")


@pytest.mark.asyncio
async def test_full_stack_integration():
    """Test full stack integration"""
    
    await crypto_key_manager.start()
    await integration_orchestrator.start()
    
    # Test critical integration paths
    test_paths = [
        ("mission_control_hub", "autonomous_coding_pipeline"),
        ("mission_control_hub", "self_healing_workflow"),
        ("elite_self_healing", "shared_orchestrator"),
        ("elite_coding_agent", "shared_orchestrator"),
        ("autonomous_coding_pipeline", "governance_engine"),
        ("autonomous_coding_pipeline", "hunter_engine"),
    ]
    
    results = []
    
    for source, target in test_paths:
        message = {
            "type": "integration_test",
            "test": f"{source}_to_{target}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send signed message
        signed = await integration_orchestrator.send_signed_message(
            source_system=source,
            target_system=target,
            message=message
        )
        
        # Verify message
        verified = await integration_orchestrator.verify_and_receive_message(signed)
        
        results.append({
            "source": source,
            "target": target,
            "verified": verified
        })
    
    # All integrations should be verified
    assert all(r["verified"] for r in results)
    
    print(f"✓ Full stack integration test passed")
    print(f"  Tested {len(results)} integration paths")
    print(f"  All paths verified: {all(r['verified'] for r in results)}")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_crypto_key_generation())
    asyncio.run(test_message_signing())
    asyncio.run(test_message_verification())
    asyncio.run(test_invalid_signature())
    asyncio.run(test_key_rotation())
    asyncio.run(test_integration_orchestrator_startup())
    asyncio.run(test_system_to_system_communication())
    asyncio.run(test_data_flow_tracking())
    asyncio.run(test_integration_statistics())
    asyncio.run(test_crypto_statistics())
    asyncio.run(test_integration_map())
    asyncio.run(test_full_stack_integration())
    
    print("\n" + "=" * 80)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("=" * 80)

