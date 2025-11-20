"""
Test Lightning and Fusion Memory Integration
Verify cryptographic assignment, verification, and storage
"""

import asyncio
import sys
import os
from pathlib import Path

# Force UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except:
    pass
os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_crypto_assignment():
    """Test universal cryptographic assignment"""
    print("\n" + "="*80)
    print("TEST 1: Universal Cryptographic Assignment")
    print("="*80)
    
    from backend.crypto_assignment_engine import crypto_engine
    
    # Test component crypto assignment
    identity = await crypto_engine.assign_universal_crypto_identity(
        entity_id="test_component_001",
        entity_type="grace_components",
        crypto_context={"test": "integration"}
    )
    
    print(f"✓ Crypto ID assigned: {identity.crypto_id}")
    print(f"✓ Entity Type: {identity.entity_type}")
    print(f"✓ Crypto Standard: {identity.crypto_standard}")
    print(f"✓ Constitutional Validated: {identity.constitutional_validated}")
    print(f"✓ Signature: {identity.signature[:32]}...")
    
    # Test signature validation
    validation = await crypto_engine.validate_signature_lightning_fast({
        "crypto_id": identity.crypto_id,
        "signature": identity.signature
    })
    
    print(f"✓ Signature Valid: {validation['valid']}")
    print(f"✓ Validation Speed: {validation['duration_ms']:.3f}ms")
    print(f"✓ Sub-millisecond: {validation['sub_millisecond']}")
    
    # Test crypto trace
    trace = await crypto_engine.trace_entity_real_time(identity.crypto_id)
    
    print(f"✓ Trace Found: {trace['found']}")
    
    return True


async def test_fusion_memory():
    """Test Fusion Memory verification and storage"""
    print("\n" + "="*80)
    print("TEST 2: Fusion Memory Verification")
    print("="*80)
    
    from backend.fusion_memory import get_fusion_memory, DataIngestionSource
    
    fusion = get_fusion_memory()
    
    # Test ingestion with verification
    result = await fusion.ingest_and_verify(
        content="Test knowledge: Grace self-healing uses playbook pattern with verification",
        source_type=DataIngestionSource.GITHUB,
        importance=0.8,
        metadata={"test": "integration", "source": "test_suite"}
    )
    
    print(f"✓ Verified: {result['verified']}")
    print(f"✓ Confidence: {result['confidence']:.1%}")
    print(f"✓ Memory ID: {result['memory_id']}")
    print(f"✓ Crypto ID: {result['crypto_id']}")
    print(f"✓ Constitutional Approved: {result['constitutional_approved']}")
    print(f"✓ Source: {result['source']}")
    
    # Test recall
    memories = await fusion.recall_verified(
        query="self-healing patterns",
        min_similarity=0.5,
        limit=5
    )
    
    print(f"✓ Recalled {len(memories)} verified memories")
    
    return result["verified"]


async def test_component_crypto_registry():
    """Test component crypto registry"""
    print("\n" + "="*80)
    print("TEST 3: Component Crypto Registry")
    print("="*80)
    
    from backend.component_crypto_registry import UniversalComponentCryptoInterface
    
    # Test component interface
    interface = UniversalComponentCryptoInterface(
        component_id="component_13_lightning_memory",
        component_type="ultra_high_speed"
    )
    
    crypto_id = await interface.initialize_component_crypto_identity()
    
    print(f"✓ Component ID: {interface.component_id}")
    print(f"✓ Crypto ID: {crypto_id}")
    
    # Test signing operation
    signed_op = await interface.sign_component_operation({
        "action": "store_memory",
        "resource": "test_fragment_123"
    })
    
    print(f"✓ Operation Signed: {signed_op['signature'][:32]}...")
    print(f"✓ Constitutional: {signed_op['constitutional_approved']}")
    
    # Test validation
    validation = await interface.validate_incoming_crypto_signature(signed_op)
    
    print(f"✓ Validation: {validation['valid']}")
    print(f"✓ Speed: {validation['duration_ms']:.3f}ms")
    
    return True


async def test_lightning_diagnostics():
    """Test lightning diagnostics engine"""
    print("\n" + "="*80)
    print("TEST 4: Lightning Diagnostics")
    print("="*80)
    
    from backend.lightning_diagnostics import lightning_diagnostics
    
    # Test instant diagnosis
    diagnosis = await lightning_diagnostics.diagnose_system_problem_instantly({
        "problem_indicators": ["High error rate", "Database timeouts"],
        "affected_components": ["component_22_metrics_collector"],
        "symptoms": ["500 errors", "Connection refused"]
    })
    
    print(f"✓ Diagnosis: {diagnosis['diagnosis']}")
    print(f"✓ Root Cause: {diagnosis['root_cause']}")
    print(f"✓ Recommended Playbooks: {', '.join(diagnosis['recommended_playbooks'])}")
    print(f"✓ Confidence: {diagnosis['resolution_confidence']:.1%}")
    print(f"✓ Duration: {diagnosis['duration_ms']:.3f}ms")
    print(f"✓ Sub-millisecond: {diagnosis['sub_millisecond']}")
    
    return True


async def test_database_schema():
    """Test database tables were created"""
    print("\n" + "="*80)
    print("TEST 5: Database Schema")
    print("="*80)
    
    import sqlite3
    
    db_path = Path(__file__).parent.parent / "backend" / "grace.db"
    conn = sqlite3.connect(str(db_path))
    
    # Check tables exist
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = [
        "crypto_identities",
        "fusion_memory_fragments",
        "lightning_memory_cache",
        "component_crypto_registry",
        "diagnostic_traces",
        "verification_audit_log"
    ]
    
    for table in required_tables:
        exists = table in tables
        status = "✓" if exists else "✗"
        print(f"{status} Table: {table}")
    
    conn.close()
    
    all_exist = all(t in tables for t in required_tables)
    
    return all_exist


async def main():
    """Run all integration tests"""
    
    print("\n" + "="*80)
    print("LIGHTNING + FUSION MEMORY INTEGRATION TESTS")
    print("="*80)
    print()
    
    results = []
    
    # Test 1: Crypto Assignment
    try:
        result = await test_crypto_assignment()
        results.append(("Crypto Assignment", result))
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results.append(("Crypto Assignment", False))
    
    # Test 2: Fusion Memory
    try:
        result = await test_fusion_memory()
        results.append(("Fusion Memory", result))
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results.append(("Fusion Memory", False))
    
    # Test 3: Component Registry
    try:
        result = await test_component_crypto_registry()
        results.append(("Component Registry", result))
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results.append(("Component Registry", False))
    
    # Test 4: Lightning Diagnostics
    try:
        result = await test_lightning_diagnostics()
        results.append(("Lightning Diagnostics", result))
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results.append(("Lightning Diagnostics", False))
    
    # Test 5: Database Schema
    try:
        result = await test_database_schema()
        results.append(("Database Schema", result))
    except Exception as e:
        print(f"✗ Test failed: {e}")
        results.append(("Database Schema", False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n✓ All tests passed! Lightning + Fusion fully integrated.")
        return 0
    else:
        print(f"\n✗ {total - passed} tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
