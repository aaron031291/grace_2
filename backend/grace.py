#!/usr/bin/env python3
"""
Grace Universal Service Launcher
Single command to start both backend (8000) and frontend (5173)
"""

import asyncio
import subprocess
import platform
import threading
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

class GraceServiceLauncher:
    """Grace Universal Service Launcher"""
    
    def __init__(self):
        self.backend_port = 8000
        self.frontend_port = 5173
        self.services_running = False
    
    async def _stage_service_launch(self) -> Dict[str, Any]:
        """Launch Grace services - Backend 8000 then Frontend 5173"""
        try:
            print("🔧 Starting backend server on port 8000...")
            await self._start_backend_server()
            
            print("⏳ Waiting for backend to be ready...")
            await self._wait_for_backend_ready()
            
            print("🎨 Starting frontend server on port 5173...")
            await self._start_frontend_server()
            
            print("🔍 Validating both services...")
            await self._validate_both_services()
            
            self.services_running = True
            return {"success": True, "backend": 8000, "frontend": 5173}
            
        except Exception as e:
            print(f"❌ Service launch failed: {e}")
            return {"success": False, "message": "Services in minimal mode", "error": str(e)}

    async def _start_backend_server(self):
        """Start Grace backend on port 8000"""
        # Kill any existing process on port 8000
        await self._kill_port_process(8000)
        
        # Start uvicorn server in background thread
        def start_uvicorn():
            try:
                import uvicorn
                uvicorn.run(
                    "main:app",
                    host="0.0.0.0",
                    port=8000,
                    reload=False,
                    log_level="warning"
                )
            except ImportError:
                print("⚠️ uvicorn not found, using basic HTTP server")
                self._start_basic_backend()
            except Exception as e:
                print(f"Backend server error: {e}")
        
        backend_thread = threading.Thread(target=start_uvicorn, daemon=True)
        backend_thread.start()
        
        # Give server time to start
        await asyncio.sleep(3)
        print("✅ Backend server started on http://localhost:8000")

    def _start_basic_backend(self):
        """Fallback basic HTTP server"""
        class BasicBackendHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "ok", "service": "grace_backend"}')
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>Grace Backend - Basic Mode</h1>')
        
        server = HTTPServer(('0.0.0.0', 8000), BasicBackendHandler)
        server.serve_forever()

    async def _wait_for_backend_ready(self):
        """Wait for backend to be ready"""
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                import urllib.request
                response = urllib.request.urlopen("http://localhost:8000/health", timeout=3)
                if response.getcode() == 200:
                    print("✅ Backend is ready and responding")
                    return True
            except Exception:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)
                    print(f"⏳ Waiting... ({attempt + 1}/{max_attempts})")
                    continue
                else:
                    print("⚠️ Backend not responding, continuing anyway")
                    return False
        return False

    async def _start_frontend_server(self):
        """Start Grace frontend on port 5173"""
        await self._kill_port_process(5173)
        await self._start_frontend_proxy()
        print("✅ Frontend server started on http://localhost:5173")

    async def _start_frontend_proxy(self):
        """Start frontend proxy server"""
        class FrontendHandler(BaseHTTPRequestHandler):
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
                
                html = """<!DOCTYPE html>
<html><head><title>Grace AI</title>
<style>
body{font-family:Arial;margin:40px;background:#1a1a1a;color:#fff}
.container{max-width:800px;margin:0 auto}
.status{background:#2a2a2a;padding:20px;border-radius:8px;margin:20px 0}
.chat{background:#333;padding:20px;border-radius:8px}
input,button{padding:10px;margin:5px;border:none;border-radius:4px}
input{background:#555;color:#fff;width:300px}
button{background:#007acc;color:#fff;cursor:pointer}
.response{background:#2a4a2a;padding:15px;margin:10px 0;border-radius:4px}
</style></head><body>
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
</div></div>
<script>
async function sendMessage(){
const input=document.getElementById('messageInput');
const message=input.value;if(!message)return;
try{
const response=await fetch('http://localhost:8000/api/chat',{
method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({message:message})});
const data=await response.json();
const responsesDiv=document.getElementById('responses');
const responseDiv=document.createElement('div');
responseDiv.className='response';
responseDiv.innerHTML=`<strong>Grace:</strong> ${data.response}`;
responsesDiv.appendChild(responseDiv);input.value='';
}catch(error){console.error('Error:',error);alert('Error connecting to Grace backend');}}
document.getElementById('messageInput').addEventListener('keypress',function(e){
if(e.key==='Enter'){sendMessage();}});
</script></body></html>"""
                
                self.wfile.write(html.encode())
        
        def start_frontend():
            try:
                server = HTTPServer(('0.0.0.0', 5173), FrontendHandler)
                server.serve_forever()
            except Exception as e:
                print(f"Frontend server error: {e}")
        
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        frontend_thread.start()
        await asyncio.sleep(1)

    async def _kill_port_process(self, port: int):
        """Kill process using specified port"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
            else:
                result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
                if result.stdout:
                    for pid in result.stdout.strip().split('\n'):
                        if pid:
                            subprocess.run(['kill', '-9', pid], capture_output=True)
        except Exception:
            pass  # Ignore errors

    async def _validate_both_services(self):
        """Validate both services are running"""
        backend_ok = frontend_ok = False
        
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:8000/health", timeout=3)
            if response.getcode() == 200:
                backend_ok = True
                print("✅ Backend validation passed")
        except Exception:
            print("⚠️ Backend validation failed")
        
        try:
            response = urllib.request.urlopen("http://localhost:5173", timeout=3)
            if response.getcode() == 200:
                frontend_ok = True
                print("✅ Frontend validation passed")
        except Exception:
            print("⚠️ Frontend validation failed")
        
        if backend_ok and frontend_ok:
            print("🎉 Both services validated successfully!")
            print("🌐 Backend:  http://localhost:8000")
            print("🎨 Frontend: http://localhost:5173")
        else:
            print("⚠️ Services running in minimal mode")

    async def launch(self):
        """Main launch method"""
        print("🚀 Grace Universal Launcher - Starting Services")
        print("=" * 60)
        
        result = await self._stage_service_launch()
        
        if result["success"]:
            print("\n🎯 Grace is ready! Press Ctrl+C to stop")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Grace stopped")
        else:
            print(f"\n❌ Launch failed: {result.get('error', 'Unknown error')}")

def main():
    """Entry point"""
    launcher = GraceServiceLauncher()
    asyncio.run(launcher.launch())

if __name__ == "__main__":
    main()
