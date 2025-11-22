"""
Grace 3.0 - Librarian API Server (SQLite Version)
Simplified backend for immediate deployment
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from collections import OrderedDict
import json
import sqlite3
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database file
DB_FILE = 'grace_memory.db'
LIGHTNING_TTL = 300  # 5 minutes

# In-memory Lightning store
lightning_store = OrderedDict()


# ========== DATABASE SETUP ==========

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
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


def cleanup_expired_lightning():
    """Remove expired Lightning items"""
    now = datetime.utcnow()
    expired = [k for k, v in lightning_store.items() if v['expires_at'] < now]
    for key in expired:
        del lightning_store[key]


# ========== HEALTH CHECK ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'SQLite',
        'cache': 'In-Memory',
        'timestamp': datetime.utcnow().isoformat()
    })


# ========== LIGHTNING LAYER ==========

@app.route('/api/librarian/lightning', methods=['POST'])
def add_to_lightning():
    try:
        cleanup_expired_lightning()
        data = request.json
        artifact_id = data['id']
        
        lightning_store[artifact_id] = {
            'data': data,
            'expires_at': datetime.utcnow() + timedelta(seconds=LIGHTNING_TTL)
        }
        
        return jsonify({'success': True, 'artifactId': artifact_id, 'ttl': LIGHTNING_TTL}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/librarian/lightning', methods=['GET'])
def get_lightning_items():
    try:
        cleanup_expired_lightning()
        items = []
        
        for artifact_id, entry in lightning_store.items():
            item = entry['data'].copy()
            ttl_remaining = int((entry['expires_at'] - datetime.utcnow()).total_seconds())
            item['ttl'] = max(0, ttl_remaining)
            items.append(item)
        
        return jsonify(items), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/librarian/lightning/<artifact_id>', methods=['DELETE'])
def delete_lightning_item(artifact_id):
    try:
        if artifact_id in lightning_store:
            del lightning_store[artifact_id]
            return jsonify({'success': True, 'artifactId': artifact_id}), 200
        return jsonify({'error': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== FUSION LAYER ==========

@app.route('/api/librarian/fusion', methods=['POST'])
def add_to_fusion():
    try:
        data = request.json
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Insert or update artifact
        now = datetime.utcnow().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO fusion_artifacts (artifact_id, name, type, layer, created_at, updated_at)
            VALUES (?, ?, ?, 'fusion', ?, ?)
        ''', (data['id'], data['name'], data['type'], now, now))
        
        # Insert DNA
        dna = data['dna']
        cursor.execute('''
            INSERT INTO memory_dna (artifact_id, version_id, origin, timestamp, intent, checksum, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['id'], dna['versionId'], dna['origin'], dna['timestamp'], dna['intent'], dna['checksum'], now))
        
        # Insert lifecycle events
        for event in dna['lifecycle']:
            cursor.execute('''
                INSERT INTO lifecycle_events (artifact_id, timestamp, action, actor, description, previous_version_id, snapshot, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['id'], event['timestamp'], event['action'], event['actor'], event['description'], 
                  event.get('previousVersionId'), json.dumps(event.get('snapshot')), now))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'artifactId': data['id']}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/librarian/fusion', methods=['GET'])
def get_fusion_items():
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
        return jsonify(items), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== PROMOTION ==========

@app.route('/api/librarian/promote', methods=['POST'])
def promote_to_fusion():
    try:
        cleanup_expired_lightning()
        data = request.json
        artifact_id = data['artifactId']
        
        if artifact_id not in lightning_store:
            return jsonify({'success': False, 'error': 'Item not found in Lightning'}), 404
        
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
        
        return jsonify({'success': True, 'artifactId': artifact_id}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== STATS ==========

@app.route('/api/librarian/stats', methods=['GET'])
def get_stats():
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
        
        return jsonify({
            'lightning': {'count': len(lightning_store), 'ttl': LIGHTNING_TTL},
            'fusion': {'count': fusion_count},
            'recentActivity': [{
                'timestamp': e['timestamp'],
                'action': e['action'],
                'actor': e['actor'],
                'description': e['description']
            } for e in recent_events]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    print("🚀 Grace 3.0 Librarian API (SQLite) starting...")
    print("📊 Database: SQLite (grace_memory.db)")
    print("⚡ Cache: In-Memory")
    print("🌐 Server: http://localhost:5000")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=True)
