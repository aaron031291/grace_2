"""
Grace 3.0 - Librarian API Server (Pure Python)
Using only Python standard library - no external dependencies
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sqlite3
from datetime import datetime, timedelta
from collections import OrderedDict
import os

# Configuration
DB_FILE = 'grace_memory.db'
LIGHTNING_TTL = 300  # 5 minutes
PORT = 5000

# In-memory Lightning store
lightning_store = OrderedDict()


# ========== DATABASE SETUP ==========

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fusion_artifacts (
            artifact_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            layer TEXT DEFAULT 'fusion',
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_dna (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artifact_id TEXT NOT NULL,
            version_id TEXT UNIQUE NOT NULL,
            origin TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            intent TEXT NOT NULL,
            checksum TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lifecycle_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artifact_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            description TEXT,
            previous_version_id TEXT,
            snapshot TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")


def cleanup_expired_lightning():
    """Remove expired Lightning items"""
    now = datetime.utcnow()
    expired = [k for k, v in lightning_store.items() if v['expires_at'] < now]
    for key in expired:
        del lightning_store[key]
        print(f"[Lightning] ⚡💨 Expired: {key}")


# ========== REQUEST HANDLER ==========

class LibrarianHandler(BaseHTTPRequestHandler):
    
    def _send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS for CORS preflight"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            if path == '/api/health':
                self._send_json_response({
                    'status': 'healthy',
                    'database': 'SQLite',
                    'cache': 'In-Memory',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            elif path == '/api/librarian/lightning':
                cleanup_expired_lightning()
                items = []
                for artifact_id, entry in lightning_store.items():
                    item = entry['data'].copy()
                    ttl_remaining = int((entry['expires_at'] - datetime.utcnow()).total_seconds())
                    item['ttl'] = max(0, ttl_remaining)
                    items.append(item)
                self._send_json_response(items)
            
            elif path == '/api/librarian/fusion':
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM fusion_artifacts ORDER BY created_at DESC')
                artifacts = cursor.fetchall()
                
                items = []
                for artifact in artifacts:
                    cursor.execute('SELECT * FROM memory_dna WHERE artifact_id = ? ORDER BY created_at DESC LIMIT 1', 
                                  (artifact['artifact_id'],))
                    dna = cursor.fetchone()
                    
                    cursor.execute('SELECT * FROM lifecycle_events WHERE artifact_id = ? ORDER BY created_at ASC', 
                                  (artifact['artifact_id'],))
                    events = cursor.fetchall()
                    
                    if dna:
                        item = {
                            'id': artifact['artifact_id'],
                            'name': artifact['name'],
                            'type': artifact['type'],
                            'layer': artifact['layer'],
                            'dna': {
                                'artifactId': dna['artifact_id'],
                                'versionId': dna['version_id'],
                                'origin': dna['origin'],
                                'timestamp': dna['timestamp'],
                                'intent': dna['intent'],
                                'checksum': dna['checksum'],
                                'lifecycle': [{
                                    'timestamp': e['timestamp'],
                                    'action': e['action'],
                                    'actor': e['actor'],
                                    'description': e['description'],
                                    'previousVersionId': e['previous_version_id'],
                                    'snapshot': json.loads(e['snapshot']) if e['snapshot'] else None
                                } for e in events]
                            }
                        }
                        items.append(item)
                
                conn.close()
                self._send_json_response(items)
            
            elif path == '/api/librarian/stats':
                cleanup_expired_lightning()
                
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) as count FROM fusion_artifacts')
                fusion_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT * FROM lifecycle_events ORDER BY created_at DESC LIMIT 10')
                recent_events = cursor.fetchall()
                
                conn.close()
                
                self._send_json_response({
                    'lightning': {'count': len(lightning_store), 'ttl': LIGHTNING_TTL},
                    'fusion': {'count': fusion_count},
                    'recentActivity': [{
                        'timestamp': e['timestamp'],
                        'action': e['action'],
                        'actor': e['actor'],
                        'description': e['description']
                    } for e in recent_events]
                })
            
            else:
                self._send_json_response({'error': 'Not found'}, 404)
        
        except Exception as e:
            print(f"Error in GET: {e}")
            self._send_json_response({'error': str(e)}, 500)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            if path == '/api/librarian/lightning':
                cleanup_expired_lightning()
                artifact_id = data['id']
                
                lightning_store[artifact_id] = {
                    'data': data,
                    'expires_at': datetime.utcnow() + timedelta(seconds=LIGHTNING_TTL)
                }
                
                print(f"[Lightning] ⚡ Added: {artifact_id}")
                self._send_json_response({'success': True, 'artifactId': artifact_id, 'ttl': LIGHTNING_TTL}, 201)
            
            elif path == '/api/librarian/fusion':
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                now = datetime.utcnow().isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO fusion_artifacts (artifact_id, name, type, layer, created_at, updated_at)
                    VALUES (?, ?, ?, 'fusion', ?, ?)
                ''', (data['id'], data['name'], data['type'], now, now))
                
                dna = data['dna']
                cursor.execute('''
                    INSERT INTO memory_dna (artifact_id, version_id, origin, timestamp, intent, checksum, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['id'], dna['versionId'], dna['origin'], dna['timestamp'], dna['intent'], dna['checksum'], now))
                
                for event in dna['lifecycle']:
                    cursor.execute('''
                        INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description, previous_version_id, snapshot, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (data['id'], event['timestamp'], event['action'], event['actor'], event['description'],
                          event.get('previousVersionId'), json.dumps(event.get('snapshot')), now))
                
                conn.commit()
                conn.close()
                
                print(f"[Fusion] 🧱 Added: {data['id']}")
                self._send_json_response({'success': True, 'artifactId': data['id']}, 201)
            
            elif path == '/api/librarian/promote':
                cleanup_expired_lightning()
                artifact_id = data['artifactId']
                
                if artifact_id not in lightning_store:
                    self._send_json_response({'success': False, 'error': 'Item not found in Lightning'}, 404)
                    return
                
                item = lightning_store[artifact_id]['data']
                
                # Add to Fusion
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                now = datetime.utcnow().isoformat()
                
                cursor.execute('''
                    INSERT INTO fusion_artifacts (artifact_id, name, type, layer, created_at, updated_at)
                    VALUES (?, ?, ?, 'fusion', ?, ?)
                ''', (item['id'], item['name'], item['type'], now, now))
                
                dna = item['dna']
                cursor.execute('''
                    INSERT INTO memory_dna (artifact_id, version_id, origin, timestamp, intent, checksum, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (item['id'], dna['versionId'], dna['origin'], dna['timestamp'], dna['intent'], dna['checksum'], now))
                
                for event in dna['lifecycle']:
                    cursor.execute('''
                        INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description, previous_version_id, snapshot, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (item['id'], event['timestamp'], event['action'], event['actor'], event['description'],
                          event.get('previousVersionId'), json.dumps(event.get('snapshot')), now))
                
                conn.commit()
                conn.close()
                
                # Remove from Lightning
                del lightning_store[artifact_id]
                
                print(f"[Promotion] 🧱 Promoted: {artifact_id}")
                self._send_json_response({'success': True, 'artifactId': artifact_id})
            
            else:
                self._send_json_response({'error': 'Not found'}, 404)
        
        except Exception as e:
            print(f"Error in POST: {e}")
            self._send_json_response({'error': str(e)}, 500)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')
        
        try:
            if len(path_parts) >= 5 and path_parts[3] == 'lightning':
                artifact_id = path_parts[4]
                
                if artifact_id in lightning_store:
                    del lightning_store[artifact_id]
                    print(f"[Lightning] 🗑️ Deleted: {artifact_id}")
                    self._send_json_response({'success': True, 'artifactId': artifact_id})
                else:
                    self._send_json_response({'error': 'Item not found'}, 404)
            else:
                self._send_json_response({'error': 'Not found'}, 404)
        
        except Exception as e:
            print(f"Error in DELETE: {e}")
            self._send_json_response({'error': str(e)}, 500)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        pass  # Suppress default logging


# ========== MAIN ==========

if __name__ == '__main__':
    init_db()
    
    print("=" * 50)
    print("🚀 Grace 3.0 Librarian API Server")
    print("=" * 50)
    print(f"📊 Database: SQLite ({DB_FILE})")
    print(f"⚡ Cache: In-Memory")
    print(f"🌐 Server: http://localhost:{PORT}")
    print(f"🔗 Health: http://localhost:{PORT}/api/health")
    print("=" * 50)
    print("")
    print("Press Ctrl+C to stop the server")
    print("")
    
    server = HTTPServer(('0.0.0.0', PORT), LibrarianHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        server.shutdown()
