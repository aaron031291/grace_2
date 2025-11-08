"""Seed Parliament System

Create default committees and Grace agent members.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.parliament_engine import parliament_engine
from backend.models import engine, Base

async def seed_parliament():
    """Seed parliament with default committees and members"""
    
    print("🏛️ Seeding Parliament System...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 1. Create Committees
    print("\n📋 Creating Committees...")
    
    committees = [
        {
            "committee_name": "security",
            "display_name": "Security Committee",
            "description": "Oversees security-related governance decisions",
            "responsibilities": ["security", "access_control", "authentication", "authorization"],
            "min_members": 3,
            "max_members": 10,
            "default_quorum": 3,
            "default_threshold": 0.6,
            "auto_assign_categories": ["security"],
            "auto_assign_risk_levels": ["high", "critical"]
        },
        {
            "committee_name": "execution",
            "display_name": "Execution Committee",
            "description": "Reviews code execution and system operations",
            "responsibilities": ["execute", "run", "deploy", "operate"],
            "min_members": 3,
            "max_members": 8,
            "default_quorum": 3,
            "default_threshold": 0.5,
            "auto_assign_categories": ["execution"],
            "auto_assign_risk_levels": []
        },
        {
            "committee_name": "knowledge",
            "display_name": "Knowledge Committee",
            "description": "Manages knowledge ingestion and learning",
            "responsibilities": ["learn", "ingest", "knowledge", "training"],
            "min_members": 3,
            "max_members": 8,
            "default_quorum": 2,
            "default_threshold": 0.5,
            "auto_assign_categories": ["knowledge"],
            "auto_assign_risk_levels": []
        },
        {
            "committee_name": "meta",
            "display_name": "Meta Committee",
            "description": "Handles meta-level decisions and system optimization",
            "responsibilities": ["meta", "optimize", "configure", "tune"],
            "min_members": 3,
            "max_members": 6,
            "default_quorum": 3,
            "default_threshold": 0.66,
            "auto_assign_categories": ["meta"],
            "auto_assign_risk_levels": []
        },
        {
            "committee_name": "general",
            "display_name": "General Committee",
            "description": "Default committee for uncategorized decisions",
            "responsibilities": ["*"],
            "min_members": 3,
            "max_members": 10,
            "default_quorum": 3,
            "default_threshold": 0.5,
            "auto_assign_categories": [],
            "auto_assign_risk_levels": []
        }
    ]
    
    for committee in committees:
        try:
            await parliament_engine.create_committee(**committee)
            print(f"  [OK] Created committee: {committee['display_name']}")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"  -> Committee already exists: {committee['display_name']}")
            else:
                print(f"  [FAIL] Error creating {committee['display_name']}: {e}")
    
    # 2. Create Grace Agent Members
    print("\n[AI] Creating Grace Agent Members...")
    
    grace_members = [
        {
            "member_id": "grace_reflection",
            "member_type": "grace_reflection",
            "display_name": "GRACE Reflection Engine",
            "role": "member",
            "committees": ["execution", "knowledge", "meta"],
            "vote_weight": 1.0
        },
        {
            "member_id": "grace_hunter",
            "member_type": "grace_hunter",
            "display_name": "GRACE Hunter (Security)",
            "role": "member",
            "committees": ["security"],
            "vote_weight": 1.5  # Higher weight for security expertise
        },
        {
            "member_id": "grace_meta",
            "member_type": "grace_meta",
            "display_name": "GRACE Meta-Loop Engine",
            "role": "member",
            "committees": ["meta", "execution"],
            "vote_weight": 1.0
        },
        {
            "member_id": "grace_causal",
            "member_type": "grace_causal",
            "display_name": "GRACE Causal Reasoning",
            "role": "member",
            "committees": ["execution", "knowledge", "meta"],
            "vote_weight": 1.0
        },
        {
            "member_id": "grace_parliament",
            "member_type": "grace_agent",
            "display_name": "GRACE Parliament Agent",
            "role": "member",
            "committees": ["security", "execution", "knowledge", "meta"],
            "vote_weight": 1.0
        }
    ]
    
    for member in grace_members:
        try:
            await parliament_engine.create_member(**member)
            print(f"  [OK] Created member: {member['display_name']}")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"  -> Member already exists: {member['display_name']}")
            else:
                print(f"  [FAIL] Error creating {member['display_name']}: {e}")
    
    # 3. Create Admin User Member
    print("\n👤 Creating Human Members...")
    
    human_members = [
        {
            "member_id": "admin",
            "member_type": "human",
            "display_name": "Administrator",
            "role": "admin",
            "committees": ["security", "execution", "knowledge", "meta", "general"],
            "vote_weight": 1.0
        }
    ]
    
    for member in human_members:
        try:
            await parliament_engine.create_member(**member)
            print(f"  [OK] Created member: {member['display_name']}")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"  -> Member already exists: {member['display_name']}")
            else:
                print(f"  [FAIL] Error creating {member['display_name']}: {e}")
    
    # 4. Summary
    print("\n📊 Parliament Summary:")
    stats = await parliament_engine.get_statistics()
    print(f"  Total Members: {stats['total_members']}")
    print(f"  Active Members: {stats['active_members']}")
    
    committees_list = await parliament_engine.list_committees()
    print(f"  Total Committees: {len(committees_list)}")
    
    print("\n✅ Parliament seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_parliament())
