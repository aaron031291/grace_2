#!/usr/bin/env python3
"""
Seed Minimal World Model Fixture - Phase 0
Creates minimal world model data for consistent testing
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

async def seed_minimal_world_model():
    """Seed minimal world model fixture for testing"""
    print("🌱 Seeding minimal world model fixture...")
    
    # Create minimal world model data
    world_model_fixture = {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "entities": [
            {
                "id": "grace_system",
                "type": "system",
                "name": "Grace AI System",
                "status": "active",
                "components": ["guardian", "self_heal", "governance"]
            },
            {
                "id": "test_service",
                "type": "service", 
                "name": "Test Service",
                "status": "healthy",
                "port": 8001
            }
        ],
        "relationships": [
            {
                "from": "grace_system",
                "to": "test_service",
                "type": "manages",
                "strength": 1.0
            }
        ],
        "metrics": {
            "total_entities": 2,
            "total_relationships": 1,
            "health_score": 1.0,
            "last_updated": datetime.now().isoformat()
        }
    }
    
    # Save fixture
    fixture_path = Path("tests/fixtures/minimal_world_model.json")
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(fixture_path, 'w') as f:
        json.dump(world_model_fixture, f, indent=2)
    
    print(f"✅ Minimal world model seeded: {fixture_path}")
    print(f"   Entities: {len(world_model_fixture['entities'])}")
    print(f"   Relationships: {len(world_model_fixture['relationships'])}")
    
    return True

if __name__ == "__main__":
    asyncio.run(seed_minimal_world_model())