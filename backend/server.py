"""
Grace 3.0 - Librarian API Server
Production backend for Cryptographic Provenance system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import redis
import json
import os
from dotenv import load_dotenv

from models import Base, FusionArtifact, MemoryDNA, LifecycleEvent

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Database configuration
DATABASE_URL = f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis configuration (Lightning layer)
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    password=os.getenv('REDIS_PASSWORD', None),
    decode_responses=True
)

# Constants
LIGHTNING_TTL = int(os.getenv('LIGHTNING_TTL', 300))  # 5 minutes


# ========== HEALTH CHECK ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check PostgreSQL
        db = SessionLocal()
        db.execute('SELECT 1')
        db.close()
        pg_status = 'healthy'
    except Exception as e:
        pg_status = f'unhealthy: {str(e)}'
    
    try:
        # Check Redis
        redis_client.ping()
        redis_status = 'healthy'
    except Exception as e:
        redis_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy' if pg_status == 'healthy' and redis_status == 'healthy' else 'degraded',
        'postgresql': pg_status,
        'redis': redis_status,
        'timestamp': datetime.utcnow().isoformat()
    })


# ========== LIGHTNING LAYER (Redis) ==========

@app.route('/api/librarian/lightning', methods=['POST'])
def add_to_lightning():
    """Add item to Lightning (volatile) store"""
    try:
        data = request.json
        artifact_id = data['id']
        
        # Store in Redis with TTL
        redis_client.setex(
            f"lightning:{artifact_id}",
            LIGHTNING_TTL,
            json.dumps(data)
        )
        
        return jsonify({
            'success': True,
            'artifactId': artifact_id,
            'ttl': LIGHTNING_TTL
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/librarian/lightning', methods=['GET'])
def get_lightning_items():
    """Get all Lightning items"""
    try:
        keys = redis_client.keys('lightning:*')
        items = []
        
        for key in keys:
            item_json = redis_client.get(key)
            if item_json:
                item = json.loads(item_json)
                # Add TTL info
                ttl = redis_client.ttl(key)
                item['ttl'] = ttl if ttl > 0 else None
                items.append(item)
        
        return jsonify(items), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/librarian/lightning/<artifact_id>', methods=['GET'])
def get_lightning_item(artifact_id):
    """Get specific Lightning item"""
    try:
        item_json = redis_client.get(f"lightning:{artifact_id}")
        
        if not item_json:
            return jsonify({'error': 'Item not found'}), 404
        
        item = json.loads(item_json)
        ttl = redis_client.ttl(f"lightning:{artifact_id}")
        item['ttl'] = ttl if ttl > 0 else None
        
        return jsonify(item), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/librarian/lightning/<artifact_id>', methods=['DELETE'])
def delete_lightning_item(artifact_id):
    """Delete Lightning item (expire it)"""
    try:
        result = redis_client.delete(f"lightning:{artifact_id}")
        
        if result == 0:
            return jsonify({'error': 'Item not found'}), 404
        
        return jsonify({'success': True, 'artifactId': artifact_id}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== FUSION LAYER (PostgreSQL) ==========

@app.route('/api/librarian/fusion', methods=['POST'])
def add_to_fusion():
    """Add item to Fusion (durable) store"""
    db = SessionLocal()
    try:
        data = request.json
        
        # Create or update artifact
        artifact = db.query(FusionArtifact).filter_by(artifact_id=data['id']).first()
        
        if artifact:
            # Update existing
            artifact.name = data['name']
            artifact.type = data['type']
            artifact.layer = data['layer']
            artifact.updated_at = datetime.utcnow()
        else:
            # Create new
            artifact = FusionArtifact(
                artifact_id=data['id'],
                name=data['name'],
                type=data['type'],
                layer=data['layer']
            )
            db.add(artifact)
        
        # Add DNA
        dna_data = data['dna']
        dna = MemoryDNA(
            artifact_id=data['id'],
            version_id=dna_data['versionId'],
            origin=dna_data['origin'],
            timestamp=datetime.fromisoformat(dna_data['timestamp'].replace('Z', '+00:00')) if isinstance(dna_data['timestamp'], str) else dna_data['timestamp'],
            intent=dna_data['intent'],
            checksum=dna_data['checksum']
        )
        db.add(dna)
        
        # Add lifecycle events
        for event_data in dna_data['lifecycle']:
            event = LifecycleEvent(
                artifact_id=data['id'],
                timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')) if isinstance(event_data['timestamp'], str) else datetime.utcnow(),
                action=event_data['action'],
                actor=event_data['actor'],
                description=event_data['description'],
                previous_version_id=event_data.get('previousVersionId'),
                snapshot=event_data.get('snapshot')
            )
            db.add(event)
        
        db.commit()
        
        return jsonify({'success': True, 'artifactId': data['id']}), 201
    
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        db.close()


@app.route('/api/librarian/fusion', methods=['GET'])
def get_fusion_items():
    """Get all Fusion items"""
    db = SessionLocal()
    try:
        artifacts = db.query(FusionArtifact).order_by(FusionArtifact.created_at.desc()).all()
        items = []
        
        for artifact in artifacts:
            # Get latest DNA
            dna = db.query(MemoryDNA).filter_by(artifact_id=artifact.artifact_id).order_by(MemoryDNA.created_at.desc()).first()
            
            # Get lifecycle events
            events = db.query(LifecycleEvent).filter_by(artifact_id=artifact.artifact_id).order_by(LifecycleEvent.created_at.asc()).all()
            
            if dna:
                item = artifact.to_dict()
                item['dna'] = dna.to_dict()
                item['dna']['lifecycle'] = [event.to_dict() for event in events]
                items.append(item)
        
        return jsonify(items), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


@app.route('/api/librarian/fusion/<artifact_id>', methods=['GET'])
def get_fusion_item(artifact_id):
    """Get specific Fusion item"""
    db = SessionLocal()
    try:
        artifact = db.query(FusionArtifact).filter_by(artifact_id=artifact_id).first()
        
        if not artifact:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get latest DNA
        dna = db.query(MemoryDNA).filter_by(artifact_id=artifact_id).order_by(MemoryDNA.created_at.desc()).first()
        
        # Get lifecycle events
        events = db.query(LifecycleEvent).filter_by(artifact_id=artifact_id).order_by(LifecycleEvent.created_at.asc()).all()
        
        item = artifact.to_dict()
        if dna:
            item['dna'] = dna.to_dict()
            item['dna']['lifecycle'] = [event.to_dict() for event in events]
        
        return jsonify(item), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


# ========== PROMOTION ENDPOINT ==========

@app.route('/api/librarian/promote', methods=['POST'])
def promote_to_fusion():
    """Promote item from Lightning to Fusion"""
    db = SessionLocal()
    try:
        data = request.json
        artifact_id = data['artifactId']
        
        # Get from Redis
        item_json = redis_client.get(f"lightning:{artifact_id}")
        if not item_json:
            return jsonify({'success': False, 'error': 'Item not found in Lightning'}), 404
        
        item = json.loads(item_json)
        
        # Add to Fusion (PostgreSQL)
        artifact = FusionArtifact(
            artifact_id=item['id'],
            name=item['name'],
            type=item['type'],
            layer='fusion'
        )
        db.add(artifact)
        
        # Add DNA
        dna_data = item['dna']
        dna = MemoryDNA(
            artifact_id=item['id'],
            version_id=dna_data['versionId'],
            origin=dna_data['origin'],
            timestamp=datetime.fromisoformat(dna_data['timestamp'].replace('Z', '+00:00')) if isinstance(dna_data['timestamp'], str) else datetime.utcnow(),
            intent=dna_data['intent'],
            checksum=dna_data['checksum']
        )
        db.add(dna)
        
        # Add lifecycle events
        for event_data in dna_data['lifecycle']:
            event = LifecycleEvent(
                artifact_id=item['id'],
                timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')) if isinstance(event_data['timestamp'], str) else datetime.utcnow(),
                action=event_data['action'],
                actor=event_data['actor'],
                description=event_data['description'],
                previous_version_id=event_data.get('previousVersionId'),
                snapshot=event_data.get('snapshot')
            )
            db.add(event)
        
        db.commit()
        
        # Remove from Lightning (Redis)
        redis_client.delete(f"lightning:{artifact_id}")
        
        return jsonify({'success': True, 'artifactId': artifact_id}), 200
    
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        db.close()


# ========== RENAME/MOVE OPERATIONS ==========

@app.route('/api/librarian/rename', methods=['POST'])
def rename_artifact():
    """Rename artifact (preserves ArtifactID)"""
    db = SessionLocal()
    try:
        data = request.json
        artifact_id = data['artifactId']
        new_name = data['newName']
        
        # Try Fusion first
        artifact = db.query(FusionArtifact).filter_by(artifact_id=artifact_id).first()
        
        if artifact:
            old_name = artifact.name
            artifact.name = new_name
            artifact.updated_at = datetime.utcnow()
            
            # Add lifecycle event
            event = LifecycleEvent(
                artifact_id=artifact_id,
                timestamp=datetime.utcnow(),
                action='Renamed',
                actor='User',
                description=f'Renamed from "{old_name}" to "{new_name}"'
            )
            db.add(event)
            db.commit()
            
            return jsonify({'success': True, 'artifactId': artifact_id}), 200
        
        # Try Lightning
        item_json = redis_client.get(f"lightning:{artifact_id}")
        if item_json:
            item = json.loads(item_json)
            old_name = item['name']
            item['name'] = new_name
            
            # Add lifecycle event
            item['dna']['lifecycle'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'Renamed',
                'actor': 'User',
                'description': f'Renamed from "{old_name}" to "{new_name}"'
            })
            
            # Update in Redis
            ttl = redis_client.ttl(f"lightning:{artifact_id}")
            redis_client.setex(f"lightning:{artifact_id}", ttl if ttl > 0 else LIGHTNING_TTL, json.dumps(item))
            
            return jsonify({'success': True, 'artifactId': artifact_id}), 200
        
        return jsonify({'success': False, 'error': 'Item not found'}), 404
    
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        db.close()


# ========== STATS ENDPOINT ==========

@app.route('/api/librarian/stats', methods=['GET'])
def get_stats():
    """Get Librarian statistics"""
    db = SessionLocal()
    try:
        # Lightning stats
        lightning_keys = redis_client.keys('lightning:*')
        lightning_count = len(lightning_keys)
        
        # Fusion stats
        fusion_count = db.query(FusionArtifact).count()
        
        # Recent activity
        recent_events = db.query(LifecycleEvent).order_by(LifecycleEvent.created_at.desc()).limit(10).all()
        
        return jsonify({
            'lightning': {
                'count': lightning_count,
                'ttl': LIGHTNING_TTL
            },
            'fusion': {
                'count': fusion_count
            },
            'recentActivity': [event.to_dict() for event in recent_events]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.close()


if __name__ == '__main__':
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Run server
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"🚀 Grace 3.0 Librarian API starting on port {port}...")
    print(f"📊 PostgreSQL: {os.getenv('DATABASE_NAME')}@{os.getenv('DATABASE_HOST')}")
    print(f"⚡ Redis: {os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
