"""Find what's using port 8000"""
import psutil

print("Checking port 8000...")

for conn in psutil.net_connections():
    if conn.laddr and conn.laddr.port == 8000:
        try:
            proc = psutil.Process(conn.pid)
            print(f"\nPort 8000 in use by:")
            print(f"  PID: {conn.pid}")
            print(f"  Name: {proc.name()}")
            print(f"  Status: {conn.status}")
            print(f"  Command: {' '.join(proc.cmdline()[:5])}")
            print(f"\nTo kill:")
            print(f"  taskkill /PID {conn.pid} /F")
        except:
            print(f"Port 8000 in use by PID {conn.pid} (access denied)")
            print(f"\nTo kill:")
            print(f"  taskkill /PID {conn.pid} /F")

print("\nOr just run: KILL_AND_RESTART.cmd")
