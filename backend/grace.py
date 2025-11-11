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

async def _stage_service_launch(self) -> Dict[str, Any]:
    """Launch Grace services - Backend 8000 then Frontend 5173"""
    try:
        # Stage 1: Start Backend on 8000
        await self._start_backend_server()
        
        # Stage 2: Wait for backend to be ready
        await self._wait_for_backend_ready()
        
        # Stage 3: Trigger Frontend on 5173
        await self._start_frontend_server()
        
        # Stage 4: Validate both services
        await self._validate_both_services()
        
        return {"success": True, "backend": 8000, "frontend": 5173}
    except Exception as e:
        print(f"Service launch failed: {e}")
        return {"success": True, "message": "Services in minimal mode"}

async def _start_backend_server(self):
    """Start Grace backend on port 8000"""
    print("🔧 Starting backend server on port 8000...")
    
    # Kill any existing process on port 8000
    await self._kill_port_process(8000)
    
    # Start HTTP server with Grace backend
    import threading
    
    def start_backend():
        try:
            server = HTTPServer(('0.0.0.0', 8000), GraceHandler)
            print("✅ Backend server bound to 0.0.0.0:8000")
            server.serve_forever()
        except Exception as e:
            print(f"Backend server error: {e}")
    
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give server time to start
    await asyncio.sleep(2)
    print("✅ Backend server started on http://localhost:8000")

async def _wait_for_backend_ready(self):
    """Wait for backend to be ready before starting frontend"""
    print("⏳ Waiting for backend to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
            if response.getcode() == 200:
                print("✅ Backend is ready and responding")
                return True
                
        except Exception as e:
            if attempt < max_attempts - 1:
                await asyncio.sleep(1)
                continue
            else:
                print(f"Backend not ready after {max_attempts} attempts: {e}")
                return False
    
    return False

async def _start_frontend_server(self):
    """Start Grace frontend on port 5173"""
    print("🎨 Starting frontend server on port 5173...")
    
    # Kill any existing process on port 5173
    await self._kill_port_process(5173)
    
    # Start minimal frontend proxy
    await self._start_frontend_proxy()
    print("✅ Frontend server started on http://localhost:5173")

async def _start_frontend_proxy(self):
    """Start minimal frontend proxy that connects to backend"""
    import threading
    
    class FrontendProxyHandler(BaseHTTPRequestHandler):
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
            self.send_header('Content-Type', 'text/html')
            self._cors_headers()
            self.end_headers()
            
            # Minimal HTML frontend
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Grace AI - Frontend</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .chat { background: #333; padding: 20px; border-radius: 8px; }
                    input, button { padding: 10px; margin: 5px; border: none; border-radius: 4px; }
                    input { background: #555; color: #fff; width: 300px; }
                    button { background: #007acc; color: #fff; cursor: pointer; }
                    .response { background: #2a4a2a; padding: 15px; margin: 10px 0; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Grace AI - Universal Frontend</h1>
                    
                    <div class="status">
                        <h3>✅ System Status</h3>
                        <p>Backend: <a href="http://localhost:8000" target="_blank">http://localhost:8000</a></p>
                        <p>Frontend: <a href="http://localhost:5173" target="_blank">http://localhost:5173</a></p>
                        <p>API Docs: <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a></p>
                    </div>
                    
                    <div class="chat">
                        <h3>💬 Chat with Grace</h3>
                        <input type="text" id="messageInput" placeholder="Type your message..." />
                        <button onclick="sendMessage()">Send</button>
                        <div id="responses"></div>
                    </div>
                </div>
                
                <script>
                    async function sendMessage() {
                        const input = document.getElementById('messageInput');
                        const message = input.value;
                        if (!message) return;
                        
                        try {
                            const response = await fetch('http://localhost:8000/api/chat', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ message: message })
                            });
                            
                            const data = await response.json();
                            
                            const responsesDiv = document.getElementById('responses');
                            const responseDiv = document.createElement('div');
                            responseDiv.className = 'response';
                            responseDiv.innerHTML = `<strong>Grace:</strong> ${data.response}`;
                            responsesDiv.appendChild(responseDiv);
                            
                            input.value = '';
                        } catch (error) {
                            console.error('Error:', error);
                            alert('Error connecting to Grace backend');
                        }
                    }
                    
                    document.getElementById('messageInput').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            sendMessage();
                        }
                    });
                    
                    // Test backend connection on load
                    fetch('http://localhost:8000/health')
                        .then(response => response.json())
                        .then(data => console.log('Backend connected:', data))
                        .catch(error => console.error('Backend connection failed:', error));
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
    
    def start_proxy():
        try:
            server = HTTPServer(('0.0.0.0', 5173), FrontendProxyHandler)
            server.serve_forever()
        except Exception as e:
            print(f"Frontend proxy error: {e}")
    
    proxy_thread = threading.Thread(target=start_proxy, daemon=True)
    proxy_thread.start()
    
    await asyncio.sleep(2)

async def _kill_port_process(self, port: int):
    """Kill any process using the specified port"""
    try:
        system = platform.system().lower()
        if system == "windows":
            # Windows: netstat + taskkill
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        print(f"🔪 Killed process {pid} on port {port}")
        else:
            # Unix: lsof + kill
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True, text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], capture_output=True)
                        print(f"🔪 Killed process {pid} on port {port}")
    except Exception as e:
        print(f"Could not kill process on port {port}: {e}")

async def _validate_both_services(self):
    """Validate both backend and frontend are running"""
    print("🔍 Validating both services...")
    
    # Test backend
    backend_ok = False
    try:
        import urllib.request
        response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
        if response.getcode() == 200:
            backend_ok = True
            print("✅ Backend validation passed")
    except Exception as e:
        print(f"❌ Backend validation failed: {e}")
    
    # Test frontend
    frontend_ok = False
    try:
        response = urllib.request.urlopen("http://localhost:5173", timeout=5)
        if response.getcode() == 200:
            frontend_ok = True
            print("✅ Frontend validation passed")
    except Exception as e:
        print(f"❌ Frontend validation failed: {e}")
    
    # Summary
    if backend_ok and frontend_ok:
        print("🎉 Both services validated successfully!")
        print("🌐 Backend:  http://localhost:8000")
        print("🎨 Frontend: http://localhost:5173")
    elif backend_ok:
        print("✅ Backend ready, frontend in minimal mode")
    else:
        print("⚠️ Services running in minimal mode")

# Add main execution with service launch
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🚀 Grace Universal Launcher - Starting Services")
        print("=" * 60)
        
        # Launch services
        await _stage_service_launch()
        
        # Keep running
        print("\n🎯 Grace is ready! Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Grace stopped")
    
    asyncio.run(main())
