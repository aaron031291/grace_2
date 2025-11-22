"""
Grace 3.0 - Librarian API Routes
FastAPI endpoints for Cryptographic Provenance system
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sqlite3
import json
from collections import OrderedDict

router = APIRouter(prefix="/api/librarian", tags=["librarian"])

# Configuration
DB_FILE = 'backend/grace_memory.db'
LIGHTNING_TTL = 300  # 5 minutes

# In-memory Lightning store
lightning_store = OrderedDict()  # {artifact_id: {data, expires_at}}


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


# ========== HELPER FUNCTIONS ==========

def cleanup_expired_lightning():
    """Remove expired Lightning items"""
    now = datetime.utcnow()
    expired = [k for k, v in lightning_store.items() if v['expires_at'] < now]
    for key in expired:
        del lightning_store[key]
        print(f"[Lightning] ⚡💨 Expired: {key}")


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


# Initialize database on module load
try:
    init_db()
    print("[Librarian] ✅ Database initialized")
except Exception as e:
    print(f"[Librarian] ⚠️ Database init warning: {e}")


# ========== ENDPOINTS ==========

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "SQLite",
        "cache": "In-Memory",
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
        
        return {
            "success": True,
            "artifactId": artifact_id,
            "ttl": LIGHTNING_TTL
        }
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


@router.post("/fusion")
async def add_to_fusion(item: LibrarianItem):
    """Add item to Fusion (durable) store"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        # Insert or update artifact
        cursor.execute('''
            INSERT OR REPLACE INTO fusion_artifacts (artifact_id, name, type, layer, created_at, updated_at)
            VALUES (?, ?, ?, 'fusion', ?, ?)
        ''', (item.id, item.name, item.type, now, now))
        
        # Insert DNA
        cursor.execute('''
            INSERT INTO memory_dna (artifact_id, version_id, origin, timestamp, intent, checksum, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item.id, item.dna.versionId, item.dna.origin, item.dna.timestamp, 
              item.dna.intent, item.dna.checksum, now))
        
        # Insert lifecycle events
        for event in item.dna.lifecycle:
            cursor.execute('''
                INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description, previous_version_id, snapshot, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item.id, event.timestamp, event.action, event.actor, event.description,
                  event.previousVersionId, json.dumps(event.snapshot) if event.snapshot else None, now))
        
        conn.commit()
        conn.close()
        
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
            # Get DNA
            cursor.execute('SELECT * FROM memory_dna WHERE artifact_id = ? ORDER BY created_at DESC LIMIT 1', 
                          (artifact['artifact_id'],))
            dna = cursor.fetchone()
            
            # Get lifecycle events
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
        
        # Add to Fusion
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
        
        # Remove from Lightning
        del lightning_store[artifact_id]
        
        return {"success": True, "artifactId": artifact_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rename")
async def rename_artifact(request: RenameRequest):
    """Rename artifact (preserves ArtifactID)"""
    try:
        artifact_id = request.artifactId
        new_name = request.newName
        
        # Try Fusion first
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM fusion_artifacts WHERE artifact_id = ?', (artifact_id,))
        result = cursor.fetchone()
        
        if result:
            old_name = result[0]
            cursor.execute('UPDATE fusion_artifacts SET name = ?, updated_at = ? WHERE artifact_id = ?',
                          (new_name, datetime.utcnow().isoformat(), artifact_id))
            
            # Add lifecycle event
            cursor.execute('''
                INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description, created_at)
                VALUES (?, ?, 'Renamed', 'User', ?, ?)
            ''', (artifact_id, datetime.utcnow().isoformat(), 
                  f'Renamed from "{old_name}" to "{new_name}"', datetime.utcnow().isoformat()))
            
            conn.commit()
            conn.close()
            return {"success": True, "artifactId": artifact_id}
        
        conn.close()
        
        # Try Lightning
        if artifact_id in lightning_store:
            item = lightning_store[artifact_id]['data']
            old_name = item['name']
            item['name'] = new_name
            
            # Add lifecycle event
            item['dna']['lifecycle'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'Renamed',
                'actor': 'User',
                'description': f'Renamed from "{old_name}" to "{new_name}"'
            })
            
            return {"success": True, "artifactId": artifact_id}
        
        raise HTTPException(status_code=404, detail="Item not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            "recentActivity": [{
                "timestamp": e['timestamp'],
                "action": e['action'],
                "actor": e['actor'],
                "description": e['description']
            } for e in recent_events]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
