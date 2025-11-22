"""
Librarian API - Cryptographic Provenance System
Knowledge management with Memory DNA tracking
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sqlite3
import json
from collections import OrderedDict
import asyncio
import math
import re
from collections import defaultdict, Counter

router = APIRouter(prefix="/librarian", tags=["Librarian"])

# Configuration
DB_FILE = 'backend/grace_memory.db'
LIGHTNING_TTL = 300  # 5 minutes

# In-memory stores
lightning_store = OrderedDict()  # {artifact_id: {data, expires_at}}
vector_store = {}  # {artifact_id: vector}
idf_scores = {}  # {term: idf_score}
document_count = 0


# ========== MODELS ==========

class LifecycleEvent(BaseModel):
    timestamp: str
    action: str
    actor: str
    description: str
    previousVersionId: Optional[str] = None
    snapshot: Optional[Dict[str, Any]] = None


class MemoryDNA(BaseModel):
    artifactId: str
    versionId: str
    origin: str
    timestamp: str
    intent: str
    checksum: str
    lifecycle: List[LifecycleEvent]


class LibrarianItem(BaseModel):
    id: str
    name: str
    type: str
    dna: MemoryDNA
    layer: str
    ttl: Optional[int] = None


class PromoteRequest(BaseModel):
    artifactId: str


class RenameRequest(BaseModel):
    artifactId: str
    newName: str


class SearchRequest(BaseModel):
    query: str
    topK: int = 5


class EmbedRequest(BaseModel):
    artifactId: str
    content: str


# ========== HELPER FUNCTIONS ==========

def cleanup_expired_lightning():
    """Remove expired Lightning items"""
    now = datetime.utcnow()
    expired = [k for k, v in lightning_store.items() if v['expires_at'] < now]
    for key in expired:
        del lightning_store[key]


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


# ========== TF-IDF FUNCTIONS ==========

def tokenize(text):
    """Simple tokenization"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
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
    all_terms = set(vec1.keys()) | set(vec2.keys())
    dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return dot_product / (mag1 * mag2)


def build_vector_index():
    """Build vector index from Fusion artifacts"""
    global vector_store
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.artifact_id, a.name, d.intent, d.origin, e.description
            FROM fusion_artifacts a
            JOIN memory_dna d ON a.artifact_id = d.artifact_id
            LEFT JOIN lifecycle_events e ON a.artifact_id = e.artifact_id
        ''')
        
        artifacts = cursor.fetchall()
        documents = []
        artifact_tokens = {}
        
        for artifact in artifacts:
            text = f"{artifact['name']} {artifact['intent']} {artifact['origin']} {artifact['description'] or ''}"
            tokens = tokenize(text)
            documents.append(tokens)
            artifact_tokens[artifact['artifact_id']] = tokens
        
        if documents:
            compute_idf(documents)
            for artifact_id, tokens in artifact_tokens.items():
                vector_store[artifact_id] = compute_tfidf_vector(tokens)
        
        conn.close()
        return len(vector_store)
    except Exception as e:
        print(f"[Vector] ❌ Index build failed: {e}")
        return 0


# Initialize database on module load
try:
    init_db()
    print("[Librarian] ✅ Database initialized")
except Exception as e:
    print(f"[Librarian] ⚠️ Database init warning: {e}")


# ========== LIGHTNING ENDPOINTS ==========

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "SQLite",
        "cache": "In-Memory",
        "vector_index": len(vector_store),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/lightning")
async def add_to_lightning(item: LibrarianItem):
    """Add item to Lightning (volatile) store"""
    try:
        cleanup_expired_lightning()
        artifact_id = item.id
        
        lightning_store[artifact_id] = {
            'data': item.dict(),
            'expires_at': datetime.utcnow() + timedelta(seconds=LIGHTNING_TTL)
        }
        
        return {"success": True, "artifactId": artifact_id, "ttl": LIGHTNING_TTL}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lightning")
async def get_lightning_items():
    """Get all Lightning items"""
    try:
        cleanup_expired_lightning()
        items = []
        
        for artifact_id, entry in lightning_store.items():
            item = entry['data'].copy()
            ttl_remaining = int((entry['expires_at'] - datetime.utcnow()).total_seconds())
            item['ttl'] = max(0, ttl_remaining)
            items.append(item)
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/lightning/{artifact_id}")
async def delete_lightning_item(artifact_id: str):
    """Delete Lightning item"""
    try:
        if artifact_id in lightning_store:
            del lightning_store[artifact_id]
            return {"success": True, "artifactId": artifact_id}
        raise HTTPException(status_code=404, detail="Item not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== FUSION ENDPOINTS ==========

@router.post("/fusion")
async def add_to_fusion(item: LibrarianItem):
    """Add item to Fusion (durable) store"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO fusion_artifacts (artifact_id, name, type, layer, created_at, updated_at)
            VALUES (?, ?, ?, 'fusion', ?, ?)
        ''', (item.id, item.name, item.type, now, now))
        
        cursor.execute('''
            INSERT INTO memory_dna (artifact_id, version_id, origin, timestamp, intent, checksum, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item.id, item.dna.versionId, item.dna.origin, item.dna.timestamp, 
              item.dna.intent, item.dna.checksum, now))
        
        for event in item.dna.lifecycle:
            cursor.execute('''
                INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description, previous_version_id, snapshot, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item.id, event.timestamp, event.action, event.actor, event.description,
                  event.previousVersionId, json.dumps(event.snapshot) if event.snapshot else None, now))
        
        conn.commit()
        conn.close()
        
        # Auto-index in vector store
        content = f"{item.name} {item.dna.intent} {item.dna.origin}"
        tokens = tokenize(content)
        if tokens:
            vector_store[item.id] = compute_tfidf_vector(tokens)
        
        return {"success": True, "artifactId": item.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fusion")
async def get_fusion_items():
    """Get all Fusion items"""
    try:
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
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/promote")
async def promote_to_fusion(request: PromoteRequest):
    """Promote item from Lightning to Fusion"""
    try:
        cleanup_expired_lightning()
        artifact_id = request.artifactId
        
        if artifact_id not in lightning_store:
            raise HTTPException(status_code=404, detail="Item not found in Lightning")
        
        item_data = lightning_store[artifact_id]['data']
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO fusion_artifacts (artifact_id, name, type, layer, created_at, updated_at)
            VALUES (?, ?, ?, 'fusion', ?, ?)
        ''', (item_data['id'], item_data['name'], item_data['type'], now, now))
        
        dna = item_data['dna']
        cursor.execute('''
            INSERT INTO memory_dna (artifact_id, version_id, origin, timestamp, intent, checksum, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_data['id'], dna['versionId'], dna['origin'], dna['timestamp'], 
              dna['intent'], dna['checksum'], now))
        
        for event in dna['lifecycle']:
            cursor.execute('''
                INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description, previous_version_id, snapshot, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_data['id'], event['timestamp'], event['action'], event['actor'], event['description'],
                  event.get('previousVersionId'), json.dumps(event.get('snapshot')), now))
        
        conn.commit()
        conn.close()
        
        del lightning_store[artifact_id]
        
        return {"success": True, "artifactId": artifact_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== VECTOR ENDPOINTS ==========

@router.post("/vector/index")
async def rebuild_vector_index():
    """Rebuild vector index"""
    count = build_vector_index()
    return {"success": True, "indexed_count": count}


@router.post("/vector/search")
async def semantic_search(request: SearchRequest):
    """Perform semantic search"""
    try:
        query_tokens = tokenize(request.query)
        query_vector = compute_tfidf_vector(query_tokens)
        
        similarities = []
        for artifact_id, doc_vector in vector_store.items():
            similarity = cosine_similarity(query_vector, doc_vector)
            if similarity > 0:
                similarities.append({"artifactId": artifact_id, "similarity": similarity})
        
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        results = similarities[:request.topK]
        
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
        return detailed_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vector/embed")
async def embed_artifact(request: EmbedRequest):
    """Generate embedding for artifact"""
    try:
        tokens = tokenize(request.content)
        vector = compute_tfidf_vector(tokens)
        vector_store[request.artifactId] = vector
        
        return {"success": True, "artifactId": request.artifactId, "vector_size": len(vector)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== STATS ==========

@router.get("/stats")
async def get_stats():
    """Get Librarian statistics"""
    try:
        cleanup_expired_lightning()
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM fusion_artifacts')
        fusion_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT * FROM lifecycle_events ORDER BY created_at DESC LIMIT 10')
        recent_events = cursor.fetchall()
        
        conn.close()
        
        return {
            "lightning": {"count": len(lightning_store), "ttl": LIGHTNING_TTL},
            "fusion": {"count": fusion_count},
            "vector": {"indexed": len(vector_store)},
            "recentActivity": [{
                "timestamp": e['timestamp'],
                "action": e['action'],
                "actor": e['actor'],
                "description": e['description']
            } for e in recent_events]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
