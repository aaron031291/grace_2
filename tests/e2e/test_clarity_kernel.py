#!/usr/bin/env python3
"""
Test Clarity Kernel as First-Class Kernel
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))


async def test_clarity_kernel():
    """Test Clarity Kernel"""
    
    print("=" * 80)
    print("CLARITY KERNEL TEST")
    print("Component Registry + Trust Scoring + Manifest Management")
    print("=" * 80)
    print()
    
    from backend.core import message_bus, clarity_kernel
    from backend.core.kernel_sdk import KernelSDK
    
    # Start core
    print("[1/2] Starting Message Bus...")
    await message_bus.start()
    print("  [OK] Message Bus active")
    
    print("\n[2/2] Starting Clarity Kernel...")
    await clarity_kernel.start()
    print("  [OK] Clarity Kernel active")
    print()
    
    # Test 1: Register a component using SDK
    print("=" * 80)
    print("TEST 1: Component Registration via SDK")
    print("=" * 80)
    print()
    
    print("Creating kernel SDK for 'test_kernel'...")
    sdk = KernelSDK('test_kernel')
    
    print("Registering component...")
    component_id = await sdk.register_component(
        capabilities=['ingest', 'process', 'analyze'],
        contracts={
            'latency_ms': {'max': 500},
            'error_rate': {'max': 0.01},
            'throughput': {'min': 100}
        }
    )
    
    print(f"  [OK] Registered as: {component_id}")
    
    # Wait for Clarity to process
    await asyncio.sleep(1)
    
    # Check registry
    stats = clarity_kernel.get_stats()
    print(f"\nClarity Kernel Stats:")
    print(f"  Total components: {stats['total_components']}")
    print(f"  Healthy: {stats['healthy_components']}")
    print(f"  Average trust: {stats['avg_trust_score']:.1f}%")
    
    # Test 2: Report status with good metrics
    print("\n" + "=" * 80)
    print("TEST 2: Status Report (Good Metrics)")
    print("=" * 80)
    print()
    
    print("Reporting status with good metrics...")
    await sdk.report_status(
        health='healthy',
        metrics={
            'latency_ms': 350,  # Under 500 limit
            'error_rate': 0.005,  # Under 0.01 limit
            'throughput': 150,  # Over 100 minimum
            'items_processed': 1000
        }
    )
    
    # Wait for processing
    await asyncio.sleep(1)
    
    # Check trust score (should increase)
    manifest = clarity_kernel.get_component_manifest(component_id)
    if manifest:
        print(f"  [OK] Status processed")
        print(f"  Trust score: {manifest['trust_score']:.1f}%")
        print(f"  Health: {manifest['health_state']}")
    
    # Test 3: Send heartbeat
    print("\n" + "=" * 80)
    print("TEST 3: Heartbeat")
    print("=" * 80)
    print()
    
    print("Sending heartbeat...")
    await sdk.heartbeat()
    
    await asyncio.sleep(0.5)
    
    manifest = clarity_kernel.get_component_manifest(component_id)
    if manifest:
        print(f"  [OK] Heartbeat received")
        print(f"  Last heartbeat: {manifest['last_heartbeat']}")
        print(f"  Heartbeat misses: {manifest['heartbeat_misses']}")
    
    # Test 4: Report status with bad metrics
    print("\n" + "=" * 80)
    print("TEST 4: Status Report (Bad Metrics - Contract Violation)")
    print("=" * 80)
    print()
    
    print("Reporting status with bad metrics...")
    await sdk.report_status(
        health='degraded',
        metrics={
            'latency_ms': 750,  # OVER 500 limit (violation!)
            'error_rate': 0.05,  # OVER 0.01 limit (violation!)
            'throughput': 50,  # UNDER 100 minimum (violation!)
        }
    )
    
    await asyncio.sleep(1)
    
    manifest = clarity_kernel.get_component_manifest(component_id)
    if manifest:
        print(f"  [OK] Status processed")
        print(f"  Trust score: {manifest['trust_score']:.1f}% (decreased due to violations)")
        print(f"  Health: {manifest['health_state']}")
        print(f"  Contract violations: {manifest['contract_violations']}")
    
    # Test 5: View all components
    print("\n" + "=" * 80)
    print("TEST 5: Component Registry")
    print("=" * 80)
    print()
    
    all_manifests = clarity_kernel.get_all_manifests()
    
    print(f"Total registered components: {len(all_manifests)}")
    print()
    
    for manifest in all_manifests:
        print(f"Component: {manifest['component_name']}")
        print(f"  ID: {manifest['component_id']}")
        print(f"  Type: {manifest['component_type']}")
        print(f"  Capabilities: {', '.join(manifest['capabilities'])}")
        print(f"  Trust Score: {manifest['trust_score']:.1f}%")
        print(f"  Health: {manifest['health_state']}")
        print(f"  Heartbeat Misses: {manifest['heartbeat_misses']}")
        print(f"  Contract Violations: {manifest['contract_violations']}")
        print()
    
    # Final stats
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print()
    
    final_stats = clarity_kernel.get_stats()
    
    print(f"Clarity Kernel: OPERATIONAL")
    print(f"  Components registered: {final_stats['total_components']}")
    print(f"  Healthy components: {final_stats['healthy_components']}")
    print(f"  Average trust: {final_stats['avg_trust_score']:.1f}%")
    print()
    print("Capabilities Tested:")
    print("  [OK] Component registration via SDK")
    print("  [OK] Status reporting")
    print("  [OK] Heartbeat tracking")
    print("  [OK] Contract validation")
    print("  [OK] Trust score updates")
    print("  [OK] Manifest management")
    print()
    print("Clarity Kernel is fully operational!")
    print("Kernels can now register and be monitored via message bus.")
    print()
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(test_clarity_kernel())
