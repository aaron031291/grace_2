import socket
import psutil
import sys

def check_port(port):
    try:
        # Check if port is in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            # Find the process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr.port == port:
                            print(f"X Port {port} is IN USE by PID {proc.info['pid']} ({proc.info['name']})")
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            print(f"X Port {port} is IN USE (process not identified)")
            return True
        else:
            print(f"OK Port {port} is FREE")
            return False
    except Exception as e:
        print(f"Error checking port {port}: {e}")
        return False

def kill_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"Killing PID {proc.info['pid']}...")
                    proc.terminate()
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

if __name__ == "__main__":
    print("Checking Grace ports...")
    ports = [8000, 8017, 5173]
    issues = False
    for p in ports:
        if check_port(p):
            issues = True
            # Uncomment to auto-kill:
            # kill_process_on_port(p)
    
    if issues:
        print("\n! Some ports are blocked. Run 'taskkill /F /IM python.exe /T' to clear them.")
        sys.exit(1)
    else:
        print("\n* All ports clear. Ready to start Grace.")
        sys.exit(0)
