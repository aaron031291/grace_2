"""
Seed Governance Policies for Meta-Loop Recommendations
Ensures risky meta-loop changes require approval
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from governance_models import GovernancePolicy
from models import async_session, init_db
from sqlalchemy import select

async def seed_meta_governance():
    """Create governance policies for meta-loop changes"""
    
    await init_db()
    
    policies = [
        {
            "name": "meta_loop_high_risk_review",
            "description": "Require approval for high-risk meta-loop changes",
            "action": "review",
            "condition": {
                "action": "meta.recommendation_applied",
                "keywords": ["high"]
            }
        },
        {
            "name": "meta_loop_threshold_changes",
            "description": "Log all threshold changes",
            "action": "log",
            "condition": {
                "action": "meta.recommendation_applied",
                "resource": "threshold"
            }
        },
        {
            "name": "meta_loop_interval_critical",
            "description": "Block very short intervals (< 30s)",
            "action": "deny",
            "condition": {
                "action": "meta.recommendation_applied",
                "resource": "interval",
                "keywords": ["interval", "30"]
            }
        },
        {
            "name": "meta_loop_rollback_alert",
            "description": "Alert on recommendation rollbacks",
            "action": "review",
            "condition": {
                "action": "meta.recommendation_rollback",
                "keywords": ["rollback"]
            }
        }
    ]
    
    async with async_session() as session:
        for policy_data in policies:
            # Check if exists
            result = await session.execute(
                select(GovernancePolicy).where(
                    GovernancePolicy.name == policy_data["name"]
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                import json
                policy = GovernancePolicy(
                    name=policy_data["name"],
                    description=policy_data["description"],
                    action=policy_data["action"],
                    condition=json.dumps(policy_data["condition"]),
                    enabled=True
                )
                session.add(policy)
                print(f"✓ Created policy: {policy_data['name']}")
            else:
                print(f"⊙ Policy already exists: {policy_data['name']}")
        
        await session.commit()
    
    print(f"\n✓ Meta-loop governance policies seeded")

if __name__ == "__main__":
    asyncio.run(seed_meta_governance())
