#!/usr/bin/env python3
"""
Ultra-simple Grace backend that always works
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class SimpleGraceHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        path = self.path
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        if path == '/health':
            response = {"status": "healthy", "message": "Grace is running!"}
        elif path == '/':
            response = {"message": "Grace Backend Online", "status": "ok"}
        else:
            response = {"message": f"Grace received GET request to {path}", "status": "ok"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                data = {}
        else:
            data = {}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        user_message = data.get('message', 'Hello')
        response = {
            "response": f"Grace: I received your message '{user_message}'. The full system is being integrated!",
            "status": "success",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        self.wfile.write(json.dumps(response).encode())

def main():
    PORT = 8000
    print("=" * 50)
    print("🚀 GRACE BACKEND STARTING")
    print("=" * 50)
    print(f"📍 Server: http://localhost:{PORT}")
    print(f"🔍 Health: http://localhost:{PORT}/health")
    print(f"💬 Ready for frontend connections!")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        server = HTTPServer(('localhost', PORT), SimpleGraceHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Grace Backend stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try a different port or check if something else is using port 8000")

if __name__ == '__main__':
    main()