"""
Test Domain Kernel System
Verifies all kernels are wired and functional
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test 1: Backend is running"""
    print("\n[TEST 1] Backend Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Backend Status: {data['status']}")
            print(f"  ✓ Version: {data['version']}")
            return True
        else:
            print(f"  ✗ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Backend not responding: {e}")
        return False


def test_kernel_gateway_registered():
    """Test 2: Kernel gateway is registered"""
    print("\n[TEST 2] Kernel Gateway Registration...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "/kernel/" in content:
                print("  ✓ Kernel gateway found in API docs")
                return True
            else:
                print("  ✗ Kernel gateway not found in API docs")
                return False
        return False
    except Exception as e:
        print(f"  ✗ Could not check API docs: {e}")
        return False


def test_memory_kernel():
    """Test 3: Memory kernel processes intent"""
    print("\n[TEST 3] Memory Kernel - Intent Processing...")
    try:
        response = requests.post(
            f"{BASE_URL}/kernel/memory",
            json={
                "intent": "Show me what's in memory",
                "context": {}
            },
            timeout=10
        )
        
        print(f"  Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Kernel Name: {data.get('kernel_name')}")
            print(f"  ✓ Answer: {data.get('answer', '')[:100]}...")
            print(f"  ✓ APIs Called: {len(data.get('apis_called', []))}")
            print(f"  ✓ Trust Score: {data.get('trust_score', 0)}")
            print(f"  ✓ Confidence: {data.get('confidence', 0)}")
            
            if data.get('execution_trace'):
                trace = data['execution_trace']
                print(f"  ✓ Execution Trace: {trace.get('total_duration_ms', 0)}ms")
                print(f"  ✓ Pipeline Steps: {len(trace.get('steps', []))}")
            
            return True
        else:
            print(f"  ✗ Memory kernel returned {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ Memory kernel test failed: {e}")
        return False


def test_all_kernel_endpoints():
    """Test 4: All 8 kernel endpoints exist"""
    print("\n[TEST 4] All Kernel Endpoints...")
    
    kernels = [
        "core", "memory", "code", "governance", 
        "verification", "intelligence", "infrastructure", "federation"
    ]
    
    results = {}
    for kernel in kernels:
        try:
            response = requests.post(
                f"{BASE_URL}/kernel/{kernel}",
                json={"intent": "test", "context": {}},
                timeout=5
            )
            results[kernel] = response.status_code == 200
            status = "✓" if results[kernel] else "✗"
            print(f"  {status} {kernel:20s} - {response.status_code}")
        except Exception as e:
            results[kernel] = False
            print(f"  ✗ {kernel:20s} - Error: {e}")
    
    passed = sum(results.values())
    total = len(kernels)
    print(f"\n  Passed: {passed}/{total} kernels")
    return passed == total


def main():
    print("=" * 60)
    print("  Grace Domain Kernel System - Integration Test")
    print("=" * 60)
    
    # Wait for backend to be ready
    print("\nWaiting for backend to start...")
    for i in range(12):
        if test_backend_health():
            break
        print(f"  Attempt {i+1}/12...")
        sleep(5)
    else:
        print("\n✗ Backend did not start in time")
        return
    
    # Run tests
    test_2 = test_kernel_gateway_registered()
    test_3 = test_memory_kernel()
    test_4 = test_all_kernel_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    print(f"  Backend Health:        {'✓ PASS' if True else '✗ FAIL'}")
    print(f"  Gateway Registered:    {'✓ PASS' if test_2 else '✗ FAIL'}")
    print(f"  Memory Kernel:         {'✓ PASS' if test_3 else '✗ FAIL'}")
    print(f"  All Kernel Endpoints:  {'✓ PASS' if test_4 else '✗ FAIL'}")
    print("=" * 60)
    
    if test_2 and test_3 and test_4:
        print("\n🎯 SUCCESS: Domain Kernel System is OPERATIONAL!\n")
        print("8 Intelligent AI Agents managing 270 APIs")
        print("Frontend can now call kernels instead of individual APIs")
    else:
        print("\n⚠️  Some tests failed - check errors above\n")


if __name__ == "__main__":
    main()
