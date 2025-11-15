"""
Grace Server - Fixed Version
Minimal boot, maximum reliability
"""

import uvicorn
import sys
import asyncio

print("\n" + "="*70)
print("GRACE - STARTING")
print("="*70)

# Test imports first
print("\n[1/3] Testing imports...")
try:
    from backend.main import app
    print("✅ Backend loaded successfully")
except Exception as e:
    print(f"❌ Failed to load backend: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)

print("\n[2/3] Checking routes...")
try:
    route_count = len(app.routes)
    print(f"✅ {route_count} API routes registered")
    
    # Show what's available
    print("\nAvailable APIs:")
    print("  • Remote Access: /api/remote/*")
    print("  • Learning: /api/learning/*")
    print("  • Health: /health")
    print("  • Docs: /docs")
except Exception as e:
    print(f"⚠️ Warning: {e}")

print("\n[3/3] Starting server...")
print("\nGrace will be available at:")
print("  📡 API: http://localhost:8000")
print("  📖 Docs: http://localhost:8000/docs")
print("  ❤️ Health: http://localhost:8000/health")
print("\n💡 To use Grace:")
print("  • Terminal 2: python start_grace_now.py (learning)")
print("  • Terminal 2: python remote_access_client.py setup (remote access)")
print("\nPress Ctrl+C to stop")
print("="*70)
print()

if __name__ == "__main__":
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n✋ Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
