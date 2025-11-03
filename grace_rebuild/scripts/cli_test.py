"""
CLI Test - Simple command line interface for Grace
Works with minimal_backend.py running on port 8000
"""

import sys
sys.path.insert(0, '.')

def show_status():
    """Display cognition status"""
    try:
        import httpx
        
        print("\n" + "=" * 60)
        print("GRACE COGNITION STATUS")
        print("=" * 60)
        
        response = httpx.get('http://localhost:8000/api/status', timeout=3)
        data = response.json()
        
        print(f"\nOverall Metrics:")
        print(f"  Health:     {data['overall_health']:.1%}")
        print(f"  Trust:      {data['overall_trust']:.1%}")
        print(f"  Confidence: {data['overall_confidence']:.1%}")
        print(f"  SaaS Ready: {'YES' if data['saas_ready'] else 'NO'}")
        
        print(f"\nDomain Status ({len(data['domains'])} domains):")
        for name, domain in list(data['domains'].items())[:8]:
            print(f"  {name:15} {domain['health']:.1%}")
        
        print("\n" + "=" * 60)
        
    except httpx.ConnectError:
        print("\nERROR: Backend not running")
        print("Start with: py minimal_backend.py")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_status()
    else:
        print("Grace CLI")
        print("\nUsage:")
        print("  py cli_test.py status    - Show cognition status")
        print("\nMake sure backend is running:")
        print("  py minimal_backend.py")
