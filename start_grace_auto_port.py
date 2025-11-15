"""
Start Grace on first available port
"""

import socket
import uvicorn
import sys

def find_free_port(start_port=8000, max_tries=10):
    """Find first available port"""
    for port in range(start_port, start_port + max_tries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

print("\n" + "="*70)
print("GRACE - AUTO PORT SELECTION")
print("="*70)

# Find free port
port = find_free_port()

if not port:
    print("\n❌ No available ports found (tried 8000-8009)")
    print("\nKill existing processes:")
    print("  netstat -ano | findstr :800")
    print("  taskkill /PID <pid> /F")
    sys.exit(1)

print(f"\n✅ Found available port: {port}")

# Test imports
print("\n[1/2] Loading Grace...")
try:
    from backend.main import app
    print("✅ Grace loaded successfully")
except Exception as e:
    print(f"❌ Failed to load: {e}")
    sys.exit(1)

# Start server
print(f"\n[2/2] Starting server on port {port}...")
print("\n" + "="*70)
print(f"Grace will be available at:")
print(f"  📡 API: http://localhost:{port}")
print(f"  📖 Docs: http://localhost:{port}/docs")
print(f"  ❤️ Health: http://localhost:{port}/health")
print("\n💡 Next steps:")
print(f"  1. Run: python auto_configure.py  # Updates clients to port {port}")
print(f"  2. Use: python remote_access_client.py setup")
print(f"  3. Use: python start_grace_now.py")
print("\nPress Ctrl+C to stop")
print("="*70)
print()

try:
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n\n✋ Shutting down...")
