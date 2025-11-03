"""Seed Grace knowledge base with foundational content"""

import asyncio
from backend.memory_service import memory_service

SEED_KNOWLEDGE = [
    {
        "path": "security/protocols.md",
        "content": """# Security Protocols

## Access Control
- All operations require authentication
- Governance policies enforce rules
- Hunter monitors for threats

## Audit Trail
- Immutable log with hash chain
- All actions timestamped
- Complete forensic history

## Incident Response
- Auto-detection via Hunter
- Self-healing attempts recovery
- Escalation to approvals
""",
        "domain": "security",
        "category": "protocols",
        "actor": "system"
    },
    {
        "path": "technical/architecture.md",
        "content": """# Grace Architecture

## Core Systems
1. Chat & Memory
2. Reflection Loop
3. Learning Engine
4. Causal Tracker
5. Governance Engine
6. Hunter Protocol
7. Self-Healing
8. Meta-Loops

## Data Flow
User Input → Governance Check → Execute → Log Immutably → Trigger Mesh → Subscribers React
""",
        "domain": "technical",
        "category": "documentation",
        "actor": "system"
    },
    {
        "path": "research/autonomous-ai.md",
        "content": """# Autonomous AI Capabilities

## Grace's Autonomous Features
- Self-observation (monitors conversations)
- Self-reflection (identifies patterns)
- Self-learning (creates tasks from patterns)
- Self-governance (enforces policies)
- Self-healing (repairs failures)
- Self-optimization (meta-loops)

## Safety Mechanisms
- Immutable audit trail
- Policy enforcement
- Approval workflows
- Threat detection
- Hash-chain verification
""",
        "domain": "research",
        "category": "ai",
        "actor": "system"
    },
    {
        "path": "examples/python-basics.py",
        "content": """# Grace Sandbox Example

print("Hello from Grace Sandbox!")

# Variables
name = "Grace"
version = "0.5"

# Functions
def greet(name):
    return f"Hello, {name}!"

# Execute
result = greet(name)
print(result)
print(f"Running Grace v{version}")
""",
        "domain": "examples",
        "category": "code",
        "actor": "system"
    },
    {
        "path": "policies/default-governance.json",
        "content": """{
  "policies": [
    {
      "name": "Block dangerous commands",
      "condition": {"keywords": ["rm -rf", "delete *", "DROP TABLE"]},
      "action": "block",
      "severity": "critical"
    },
    {
      "name": "Review system changes",
      "condition": {"action": "change_system_mode"},
      "action": "review",
      "severity": "high"
    }
  ]
}""",
        "domain": "governance",
        "category": "policies",
        "actor": "system"
    }
]

async def seed():
    print("🌱 Seeding Grace knowledge base...\n")
    
    for item in SEED_KNOWLEDGE:
        try:
            artifact_id = await memory_service.create_artifact(
                path=item["path"],
                content=item["content"],
                actor=item["actor"],
                domain=item["domain"],
                category=item["category"],
                reason="Initial knowledge base seeding"
            )
            print(f"✅ Created: {item['path']} (ID: {artifact_id})")
        except Exception as e:
            print(f"❌ Failed: {item['path']} - {e}")
    
    print("\n✅ Knowledge base seeded successfully!")
    print("View at: http://localhost:5173 → Memory Browser")

if __name__ == "__main__":
    asyncio.run(seed())
