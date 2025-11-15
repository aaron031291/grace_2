"""
Kill all Grace processes
Clean shutdown of all instances
"""

import psutil
import os
import signal

print("\n" + "="*70)
print("KILLING ALL GRACE PROCESSES")
print("="*70)

killed = []
errors = []

# Find all Python processes
print("\n[1/2] Finding Grace processes...")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        # Check if it's a Python process running Grace
        if proc.info['name'] and 'python' in proc.info['name'].lower():
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('serve' in str(arg).lower() or 'grace' in str(arg).lower() for arg in cmdline):
                pid = proc.info['pid']
                print(f"  Found Grace process: PID {pid}")
                print(f"    Command: {' '.join(cmdline[:3])}")
                
                try:
                    proc.kill()
                    killed.append(pid)
                    print(f"    ✓ Killed PID {pid}")
                except Exception as e:
                    errors.append((pid, str(e)))
                    print(f"    ✗ Failed to kill PID {pid}: {e}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Find processes using ports 8000-8100
print("\n[2/2] Finding processes on ports 8000-8100...")
for conn in psutil.net_connections():
    if conn.laddr and 8000 <= conn.laddr.port <= 8100:
        try:
            proc = psutil.Process(conn.pid)
            pid = conn.pid
            port = conn.laddr.port
            
            if pid not in killed:
                print(f"  Found process using port {port}: PID {pid} ({proc.name()})")
                try:
                    proc.kill()
                    killed.append(pid)
                    print(f"    ✓ Killed PID {pid}")
                except Exception as e:
                    errors.append((pid, str(e)))
                    print(f"    ✗ Failed to kill PID {pid}: {e}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

print("\n" + "="*70)
print("CLEANUP SUMMARY")
print("="*70)
print(f"\nKilled: {len(killed)} processes")
if killed:
    print(f"  PIDs: {', '.join(str(p) for p in killed)}")

if errors:
    print(f"\nErrors: {len(errors)}")
    for pid, error in errors:
        print(f"  PID {pid}: {error}")

print("\n✅ All Grace processes stopped")
print("✅ Ports 8000-8100 should now be free")
print("\nStart Grace again:")
print("  python serve.py")
print("\n" + "="*70)
