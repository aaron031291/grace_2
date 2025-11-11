#!/usr/bin/env python3
"""
Universal Grace Launcher - Multi-OS Integration
Works on Windows, Mac, Linux, Docker, WSL
"""
import os
import sys
import subprocess
import time
import json
import platform
import signal
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

class GraceHandler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._cors_headers()
        self.end_headers()
        
        if self.path == '/health':
            response = {
                "status": "healthy", 
                "message": "Grace is running!",
                "os": get_os_info(),
                "python": sys.version,
                "platform": platform.platform()
            }
        elif self.path == '/api/chat':
            response = {"message": "Use POST for chat", "status": "ok"}
        elif self.path == '/api/system':
            response = get_system_info()
        else:
            response = {"message": "Grace Backend Online", "status": "ok"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._cors_headers()
        self.end_headers()
        
        user_message = data.get('message', 'Hello')
        os_info = get_os_info()
        
        response = {
            "response": f"Grace ({os_info['name']}): I received '{user_message}'. All systems operational!",
            "status": "success",
            "os": os_info,
            "capabilities": get_os_capabilities()
        }
        
        self.wfile.write(json.dumps(response).encode())

def get_os_info():
    """Get detailed OS information"""
    system = platform.system().lower()
    
    if system == 'windows':
        return {
            "name": "Windows",
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "is_wsl": 'microsoft' in platform.uname().release.lower()
        }
    elif system == 'darwin':
        return {
            "name": "macOS",
            "version": platform.mac_ver()[0],
            "architecture": platform.architecture()[0]
        }
    elif system == 'linux':
        return {
            "name": "Linux",
            "distribution": get_linux_distro(),
            "architecture": platform.architecture()[0],
            "is_docker": os.path.exists('/.dockerenv')
        }
    else:
        return {
            "name": system,
            "version": platform.version(),
            "architecture": platform.architecture()[0]
        }

def get_linux_distro():
    """Get Linux distribution info"""
    try:
        with open('/etc/os-release', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('PRETTY_NAME='):
                    return line.split('=')[1].strip().strip('"')
    except:
        pass
    return "Unknown Linux"

def get_os_capabilities():
    """Get OS-specific capabilities"""
    system = platform.system().lower()
    
    capabilities = {
        "shell": get_default_shell(),
        "package_manager": get_package_manager(),
        "process_management": True,
        "file_system": get_file_system_info(),
        "networking": True
    }
    
    return capabilities

def get_default_shell():
    """Get default shell for the OS"""
    system = platform.system().lower()
    
    if system == 'windows':
        return "cmd.exe" if not os.getenv('PSModulePath') else "powershell.exe"
    else:
        return os.getenv('SHELL', '/bin/bash')

def get_package_manager():
    """Detect available package managers"""
    managers = []
    
    # Python package managers
    if subprocess.run(['pip', '--version'], capture_output=True).returncode == 0:
        managers.append('pip')
    
    # System package managers
    system = platform.system().lower()
    if system == 'windows':
        if subprocess.run(['choco', '--version'], capture_output=True).returncode == 0:
            managers.append('chocolatey')
        if subprocess.run(['winget', '--version'], capture_output=True).returncode == 0:
            managers.append('winget')
    elif system == 'darwin':
        if subprocess.run(['brew', '--version'], capture_output=True).returncode == 0:
            managers.append('homebrew')
    elif system == 'linux':
        for pm in ['apt', 'yum', 'dnf', 'pacman', 'zypper']:
            if subprocess.run(['which', pm], capture_output=True).returncode == 0:
                managers.append(pm)
    
    return managers

def get_file_system_info():
    """Get file system information"""
    return {
        "separator": os.sep,
        "path_separator": os.pathsep,
        "current_dir": str(Path.cwd()),
        "home_dir": str(Path.home()),
        "temp_dir": str(Path.cwd() / 'temp') if (Path.cwd() / 'temp').exists() else None
    }

def get_system_info():
    """Get comprehensive system information"""
    return {
        "os": get_os_info(),
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "platform": sys.platform
        },
        "hardware": {
            "processor": platform.processor(),
            "machine": platform.machine(),
            "node": platform.node()
        },
        "capabilities": get_os_capabilities(),
        "environment": {
            "path": os.getenv('PATH', '').split(os.pathsep)[:5],  # First 5 PATH entries
            "user": os.getenv('USER') or os.getenv('USERNAME'),
            "home": str(Path.home())
        }
    }

def setup_signal_handlers():
    """Setup OS-appropriate signal handlers"""
    def signal_handler(signum, frame):
        print(f"\n� Grace stopped (signal {signum})")
        sys.exit(0)
    
    # Cross-platform signal handling
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    
    if platform.system() != 'Windows':
        signal.signal(signal.SIGTERM, signal_handler)  # Termination

def kill_existing_processes():
    """Kill existing Grace processes (OS-specific)"""
    system = platform.system().lower()
    
    try:
        if system == 'windows':
            # Windows: Kill python processes on port 8000
            subprocess.run(['netstat', '-ano'], capture_output=True, check=False)
        else:
            # Unix-like: Kill processes using port 8000
            subprocess.run(['pkill', '-f', 'grace.py'], capture_output=True, check=False)
            subprocess.run(['lsof', '-ti:8000'], capture_output=True, check=False)
    except:
        pass  # Ignore errors in cleanup

def main():
    # Setup signal handlers
    setup_signal_handlers()
    
    # Clean up existing processes
    kill_existing_processes()
    
    # Display startup info
    os_info = get_os_info()
    print("�🚀 GRACE - Universal Multi-OS Launcher")
    print("=" * 50)
    print(f"🖥️  OS: {os_info['name']} {os_info.get('version', '')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📍 Backend: http://localhost:8000")
    print(f"🔍 Health:  http://localhost:8000/health")
    print(f"💬 Chat:    http://localhost:8000/api/chat")
    print(f"⚙️  System:  http://localhost:8000/api/system")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        server = HTTPServer(('localhost', 8000), GraceHandler)
        print(f"✅ Grace started successfully on {os_info['name']}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Grace stopped gracefully")
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 8000 is busy. Kill existing processes and try again.")
        else:
            print(f"❌ OS Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
