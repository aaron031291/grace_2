"""
Test Metrics API
Quick test to verify metrics server is responding
"""

import asyncio
import httpx

async def test_api():
    print("Testing Metrics API at http://localhost:8001...")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Test health
            print("\n[1/4] GET /health")
            r = await client.get("http://localhost:8001/health")
            print(f"  Status: {r.status_code}")
            print(f"  Response: {r.json()}")
            
            # Test cognition status
            print("\n[2/4] GET /api/cognition/status")
            r = await client.get("http://localhost:8001/api/cognition/status")
            print(f"  Status: {r.status_code}")
            data = r.json()
            print(f"  Overall Health: {data.get('overall_health', 0):.1%}")
            print(f"  Domains: {len(data.get('domains', {}))}")
            
            # Test readiness
            print("\n[3/4] GET /api/cognition/readiness")
            r = await client.get("http://localhost:8001/api/cognition/readiness")
            print(f"  Status: {r.status_code}")
            data = r.json()
            print(f"  Ready: {data.get('ready', False)}")
            print(f"  Benchmarks: {len(data.get('benchmarks', {}))}")
            
            # Test root
            print("\n[4/4] GET /")
            r = await client.get("http://localhost:8001/")
            print(f"  Status: {r.status_code}")
            print(f"  Service: {r.json().get('service')}")
            
            print("\n" + "=" * 60)
            print("SUCCESS: All API endpoints responding!")
            print("=" * 60)
            return True
            
    except httpx.ConnectError:
        print("\nERROR: Cannot connect to metrics server")
        print("Start it with: start_metrics_server.bat")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_api())
    exit(0 if result else 1)
