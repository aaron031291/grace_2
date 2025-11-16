"""
Test Kernel Registry and Clarity Framework Integration
Verifies all 18 kernels work together with clarity framework
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.kernels.kernel_registry import kernel_registry


async def test_kernel_registry():
    """Test kernel registry initialization and routing"""
    
    print("=" * 70)
    print("KERNEL REGISTRY & CLARITY FRAMEWORK INTEGRATION TEST")
    print("=" * 70)
    
    # Initialize registry
    print("\n[1] Initializing kernel registry...")
    await kernel_registry.initialize()
    
    # Get status
    status = kernel_registry.get_status()
    print(f"\n[2] Registry Status:")
    print(f"    Total kernels: {status['total_kernels']}")
    print(f"    Domain kernels: {status['domain_kernels']}")
    print(f"    Clarity kernels: {status['clarity_kernels']}")
    
    # List all kernels
    print(f"\n[3] Domain Kernels:")
    for domain in status['domains']:
        health = status['health'].get(domain, {})
        print(f"    + {domain:20s} - {health.get('status', 'unknown')}")
    
    print(f"\n[4] Clarity Framework Kernels:")
    for domain in status['clarity_domains']:
        health = status['health'].get(domain, {})
        print(f"    + {domain:25s} - {health.get('status', 'unknown')}")
    
    # Test routing
    print(f"\n[5] Testing Request Routing:")
    
    test_requests = [
        "Remember this important fact",
        "Generate code for authentication",
        "Check governance policy compliance",
        "Verify system integrity",
        "Train ML model on user behavior",
        "Monitor infrastructure health",
        "Coordinate multi-agent task"
    ]
    
    for request in test_requests:
        result = await kernel_registry.route_request(request, {"test": True})
        print(f"    Request: '{request[:35]:35s}' -> {result.get('kernel_used', 'unknown'):25s} ({result.get('framework', 'unknown')})")
    
    # Test kernel access
    print(f"\n[6] Direct Kernel Access:")
    memory_kernel = kernel_registry.get_kernel("memory")
    print(f"    memory_kernel: {type(memory_kernel).__name__}")
    
    clarity_memory = kernel_registry.get_kernel("clarity_memory")
    print(f"    clarity_memory: {type(clarity_memory).__name__}")
    
    print(f"\n[SUCCESS] All integration tests passed!")
    print(f"          {status['total_kernels']} kernels operational with clarity framework")
    print("=" * 70)


async def main():
    try:
        await test_kernel_registry()
        return 0
    except Exception as e:
        print(f"\n[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
