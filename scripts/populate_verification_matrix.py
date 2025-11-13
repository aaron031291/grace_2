#!/usr/bin/env python3
"""
Populate Verification Matrix with discovered ML/AI APIs
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from backend.models import async_session, init_db
from backend.memory_verification_matrix import MemoryVerificationMatrix
import asyncio


async def populate_matrix():
    """Populate verification matrix with discovered APIs"""
    
    print("=" * 70)
    print("POPULATING VERIFICATION MATRIX")
    print("=" * 70)
    
    # Initialize database
    await init_db()
    
    # Load discovered APIs
    api_file = Path(__file__).parent.parent / 'grace_training' / 'api_discovery' / 'ml_apis_discovered.json'
    
    with open(api_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    apis = data['ml_ai_apis']
    
    print(f"\n[LOADING] {len(apis)} ML/AI APIs discovered")
    
    # Create verification matrix
    async with async_session() as session:
        matrix = MemoryVerificationMatrix(session)
        
        added = 0
        for api in apis:
            print(f"\n[ADDING] {api['name']}")
            
            result = matrix.add_api_integration(
                name=api['name'],
                url=api['url'],
                auth_type=api['auth'],
                category='ML/AI API',
                capabilities=[api.get('useful_for', 'ML capabilities')],
                use_cases=['machine_learning', 'code_understanding', 'training']
            )
            
            print(f"  Status: {result['status']}")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Risk Score: {result['risk_score']:.2f}")
            print(f"  Approval Required: {result['approval_required']}")
            
            added += 1
    
    print(f"\n[COMPLETE] Added {added} APIs to verification matrix")
    print("\nNext steps:")
    print("  1. Run Hunter Bridge scans: python scripts/hunter_scan_apis.py")
    print("  2. Review pending approvals: python scripts/review_pending_apis.py")
    print("  3. Sandbox test: python scripts/sandbox_execute.py --integration <name>")


if __name__ == '__main__':
    asyncio.run(populate_matrix())
