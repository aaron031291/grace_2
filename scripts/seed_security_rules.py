"""Seed Hunter with default security rules"""

import asyncio
import json
from backend.governance_models import SecurityRule
from backend.models import async_session

DEFAULT_RULES = [
    {
        "name": "Dangerous Commands",
        "description": "Detect dangerous system commands",
        "condition": json.dumps({
            "keywords": ["rm -rf", "delete *", "DROP TABLE", "DROP DATABASE"],
            "action": "sandbox_run"
        }),
        "severity": "critical",
        "action": "block"
    },
    {
        "name": "Secret Exposure",
        "description": "Detect hardcoded secrets in code",
        "condition": json.dumps({
            "keywords": ["password=", "api_key=", "secret=", "token="],
            "forbidden_paths": []
        }),
        "severity": "high",
        "action": "log"
    },
    {
        "name": "Suspicious File Access",
        "description": "Detect access to sensitive system paths",
        "condition": json.dumps({
            "forbidden_paths": ["/etc/", "/sys/", "C:\\Windows\\System32"],
            "action": "file_write"
        }),
        "severity": "high",
        "action": "block"
    },
    {
        "name": "Rapid Execution",
        "description": "Detect potential automated attacks",
        "condition": json.dumps({
            "action": "sandbox_run",
            "keywords": []
        }),
        "severity": "medium",
        "action": "log"
    }
]

async def seed_rules():
    print("Seeding Hunter security rules...\n")
    
    async with async_session() as session:
        for rule_data in DEFAULT_RULES:
            rule = SecurityRule(
                name=rule_data["name"],
                description=rule_data["description"],
                condition=rule_data["condition"],
                severity=rule_data["severity"],
                action=rule_data["action"]
            )
            session.add(rule)
            print(f"[+] Added rule: {rule_data['name']} ({rule_data['severity']})")
        
        await session.commit()
    
    print("\n[SUCCESS] Hunter security rules seeded!")
    print("View at: http://localhost:8000/api/hunter/rules")

if __name__ == "__main__":
    asyncio.run(seed_rules())
