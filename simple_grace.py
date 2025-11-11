import http.server
import socketserver
import json

class GraceHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"message": "Grace is running!", "status": "ok"}
        self.wfile.write(json.dumps(response).encode())

PORT = 8000
print(f"Grace running on http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), GraceHandler) as httpd:
    httpd.serve_forever()
