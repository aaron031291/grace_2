"""
Grace 3.0 - Vector Layer for Semantic Search
Lightweight implementation using TF-IDF (no external ML dependencies)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import sqlite3
import math
from collections import defaultdict, Counter
from datetime import datetime
import re

# Configuration
DB_FILE = 'grace_memory.db'
PORT = 5001  # Different port from main API

# Vector store (in-memory for now)
vector_store = {}  # {artifact_id: vector}
idf_scores = {}  # {term: idf_score}
document_count = 0


# ========== TF-IDF IMPLEMENTATION ==========

def tokenize(text):
    """Simple tokenization"""
    text = text.lower()
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    # Remove stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been', 'being'}
    return [t for t in tokens if t and t not in stop_words]


def compute_tf(tokens):
    """Compute term frequency"""
    tf = Counter(tokens)
    max_freq = max(tf.values()) if tf else 1
    return {term: freq / max_freq for term, freq in tf.items()}


def compute_idf(documents):
    """Compute inverse document frequency"""
    global idf_scores, document_count
    
    document_count = len(documents)
    term_doc_count = defaultdict(int)
    
    for doc_tokens in documents:
        unique_terms = set(doc_tokens)
        for term in unique_terms:
            term_doc_count[term] += 1
    
    idf_scores = {
        term: math.log(document_count / (1 + count))
        for term, count in term_doc_count.items()
    }


def compute_tfidf_vector(tokens):
    """Compute TF-IDF vector for a document"""
    tf = compute_tf(tokens)
    vector = {}
    
    for term, tf_score in tf.items():
        idf = idf_scores.get(term, 0)
        vector[term] = tf_score * idf
    
    return vector


def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors"""
    # Get all unique terms
    all_terms = set(vec1.keys()) | set(vec2.keys())
    
    # Compute dot product
    dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
    
    # Compute magnitudes
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return dot_product / (mag1 * mag2)


# ========== VECTOR STORE OPERATIONS ==========

def build_vector_index():
    """Build vector index from Fusion artifacts"""
    global vector_store
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all Fusion artifacts
        cursor.execute('''
            SELECT a.artifact_id, a.name, d.intent, d.origin, e.description
            FROM fusion_artifacts a
            JOIN memory_dna d ON a.artifact_id = d.artifact_id
            LEFT JOIN lifecycle_events e ON a.artifact_id = e.artifact_id
        ''')
        
        artifacts = cursor.fetchall()
        
        # Tokenize all documents
        documents = []
        artifact_tokens = {}
        
        for artifact in artifacts:
            # Combine all text fields
            text = f"{artifact['name']} {artifact['intent']} {artifact['origin']} {artifact['description'] or ''}"
            tokens = tokenize(text)
            documents.append(tokens)
            artifact_tokens[artifact['artifact_id']] = tokens
        
        # Compute IDF scores
        if documents:
            compute_idf(documents)
            
            # Compute TF-IDF vectors for each artifact
            for artifact_id, tokens in artifact_tokens.items():
                vector_store[artifact_id] = compute_tfidf_vector(tokens)
        
        conn.close()
        
        print(f"[Vector] 🧠 Indexed {len(vector_store)} artifacts")
        return len(vector_store)
    
    except Exception as e:
        print(f"[Vector] ❌ Index build failed: {e}")
        return 0


def semantic_search(query, top_k=5):
    """Perform semantic search"""
    # Tokenize query
    query_tokens = tokenize(query)
    query_vector = compute_tfidf_vector(query_tokens)
    
    # Compute similarities
    similarities = []
    for artifact_id, doc_vector in vector_store.items():
        similarity = cosine_similarity(query_vector, doc_vector)
        if similarity > 0:
            similarities.append({
                'artifactId': artifact_id,
                'similarity': similarity
            })
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    return similarities[:top_k]


# ========== HTTP REQUEST HANDLER ==========

class VectorHandler(BaseHTTPRequestHandler):
    
    def _send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
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
            if path == '/api/vector/health':
                self._send_json_response({
                    'status': 'healthy',
                    'indexed_count': len(vector_store),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            elif path == '/api/vector/stats':
                self._send_json_response({
                    'indexed_artifacts': len(vector_store),
                    'vocabulary_size': len(idf_scores),
                    'document_count': document_count
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
            
            if path == '/api/vector/index':
                # Rebuild index
                count = build_vector_index()
                self._send_json_response({
                    'success': True,
                    'indexed_count': count
                })
            
            elif path == '/api/vector/search':
                # Semantic search
                query = data.get('query', '')
                top_k = data.get('topK', 5)
                
                if not query:
                    self._send_json_response({'error': 'Query is required'}, 400)
                    return
                
                results = semantic_search(query, top_k)
                
                # Fetch full artifact details
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                detailed_results = []
                for result in results:
                    cursor.execute('''
                        SELECT a.artifact_id, a.name, a.type, d.intent, d.origin
                        FROM fusion_artifacts a
                        JOIN memory_dna d ON a.artifact_id = d.artifact_id
                        WHERE a.artifact_id = ?
                    ''', (result['artifactId'],))
                    
                    artifact = cursor.fetchone()
                    if artifact:
                        detailed_results.append({
                            'artifactId': artifact['artifact_id'],
                            'name': artifact['name'],
                            'type': artifact['type'],
                            'intent': artifact['intent'],
                            'origin': artifact['origin'],
                            'similarity': result['similarity']
                        })
                
                conn.close()
                
                print(f"[Vector] 🔍 Search: '{query}' → {len(detailed_results)} results")
                self._send_json_response(detailed_results)
            
            elif path == '/api/vector/embed':
                # Generate embedding for new artifact
                artifact_id = data.get('artifactId')
                content = data.get('content', '')
                
                if not artifact_id or not content:
                    self._send_json_response({'error': 'artifactId and content required'}, 400)
                    return
                
                tokens = tokenize(content)
                vector = compute_tfidf_vector(tokens)
                vector_store[artifact_id] = vector
                
                print(f"[Vector] ➕ Embedded: {artifact_id}")
                self._send_json_response({
                    'success': True,
                    'artifactId': artifact_id,
                    'vector_size': len(vector)
                })
            
            else:
                self._send_json_response({'error': 'Not found'}, 404)
        
        except Exception as e:
            print(f"Error in POST: {e}")
            self._send_json_response({'error': str(e)}, 500)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        pass


# ========== MAIN ==========

if __name__ == '__main__':
    print("=" * 50)
    print("🧠 Grace 3.0 Vector Layer (Semantic Search)")
    print("=" * 50)
    print(f"📊 Algorithm: TF-IDF")
    print(f"🌐 Server: http://localhost:{PORT}")
    print(f"🔗 Health: http://localhost:{PORT}/api/vector/health")
    print("=" * 50)
    print("")
    
    # Build initial index
    print("Building initial vector index...")
    count = build_vector_index()
    print(f"✅ Indexed {count} artifacts")
    print("")
    print("Press Ctrl+C to stop the server")
    print("")
    
    server = HTTPServer(('0.0.0.0', PORT), VectorHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        server.shutdown()
