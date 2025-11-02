"""Seed default governance policies for Grace"""

import asyncio
from sqlalchemy import select
from models import async_session
from governance_models import GovernancePolicy

async def seed_governance_policies():
    """Create 20+ default governance policies for production use"""
    
    policies = [
        # File System Policies
        {
            "policy_name": "restrict_system_file_access",
            "policy_type": "file_access",
            "resource_pattern": r"^/(etc|sys|proc|boot|dev|root)/.*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "critical",
            "description": "Block access to system directories without approval"
        },
        {
            "policy_name": "restrict_home_directory_write",
            "policy_type": "file_write",
            "resource_pattern": r"^/home/[^/]+/\.(ssh|gnupg|config)/.*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "high",
            "description": "Block writes to sensitive user config directories"
        },
        {
            "policy_name": "allow_workspace_access",
            "policy_type": "file_access",
            "resource_pattern": r"^/(workspace|tmp|var/tmp)/.*",
            "action": "allow",
            "requires_approval": False,
            "risk_level": "low",
            "description": "Allow unrestricted access to workspace and temp"
        },
        {
            "policy_name": "require_approval_for_deletion",
            "policy_type": "file_delete",
            "resource_pattern": r".*",
            "action": "warn",
            "requires_approval": True,
            "risk_level": "medium",
            "description": "Require approval for any file deletion"
        },
        
        # Code Execution Policies
        {
            "policy_name": "block_shell_commands",
            "policy_type": "execution",
            "resource_pattern": r".*(rm -rf|dd if=|mkfs|format|fdisk).*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "critical",
            "description": "Block destructive shell commands"
        },
        {
            "policy_name": "sandbox_python_execution",
            "policy_type": "execution",
            "resource_pattern": r"python.*",
            "action": "allow",
            "requires_approval": False,
            "risk_level": "low",
            "description": "Allow Python execution in sandbox"
        },
        {
            "policy_name": "require_approval_for_downloads",
            "policy_type": "execution",
            "resource_pattern": r".*(wget|curl|git clone).*",
            "action": "warn",
            "requires_approval": True,
            "risk_level": "medium",
            "description": "Require approval for downloading external content"
        },
        {
            "policy_name": "block_privilege_escalation",
            "policy_type": "execution",
            "resource_pattern": r".*(sudo|su|pkexec).*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "critical",
            "description": "Block privilege escalation attempts"
        },
        
        # Network Policies
        {
            "policy_name": "restrict_external_api_calls",
            "policy_type": "network",
            "resource_pattern": r"https?://(?!localhost|127\.0\.0\.1).*",
            "action": "warn",
            "requires_approval": True,
            "risk_level": "medium",
            "description": "Require approval for external network calls"
        },
        {
            "policy_name": "allow_localhost_connections",
            "policy_type": "network",
            "resource_pattern": r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0):.*",
            "action": "allow",
            "requires_approval": False,
            "risk_level": "low",
            "description": "Allow localhost connections"
        },
        {
            "policy_name": "block_sensitive_ports",
            "policy_type": "network",
            "resource_pattern": r".*:(22|23|3389|5900).*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "critical",
            "description": "Block SSH, Telnet, RDP, VNC ports"
        },
        
        # Knowledge Ingestion Policies
        {
            "policy_name": "require_high_trust_sources",
            "policy_type": "knowledge_ingestion",
            "resource_pattern": r".*",
            "action": "warn",
            "requires_approval": False,
            "risk_level": "low",
            "description": "Warn on low-trust knowledge sources",
            "metadata": {"min_trust_score": 70.0}
        },
        {
            "policy_name": "block_untrusted_code_execution",
            "policy_type": "knowledge_ingestion",
            "resource_pattern": r".*(eval|exec|__import__).*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "critical",
            "description": "Block ingestion of code with dangerous functions"
        },
        {
            "policy_name": "allow_official_documentation",
            "policy_type": "knowledge_ingestion",
            "resource_pattern": r"https://(docs\.python\.org|developer\.mozilla\.org|kubernetes\.io|reactjs\.org)/.*",
            "action": "allow",
            "requires_approval": False,
            "risk_level": "low",
            "description": "Auto-approve official documentation sources"
        },
        
        # Database Policies
        {
            "policy_name": "block_drop_table",
            "policy_type": "database",
            "resource_pattern": r".*(DROP TABLE|TRUNCATE|DELETE FROM users).*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "critical",
            "description": "Block destructive database operations"
        },
        {
            "policy_name": "allow_read_queries",
            "policy_type": "database",
            "resource_pattern": r"^SELECT.*",
            "action": "allow",
            "requires_approval": False,
            "risk_level": "low",
            "description": "Allow SELECT queries"
        },
        {
            "policy_name": "require_approval_for_schema_changes",
            "policy_type": "database",
            "resource_pattern": r".*(ALTER TABLE|CREATE TABLE|DROP COLUMN).*",
            "action": "warn",
            "requires_approval": True,
            "risk_level": "high",
            "description": "Require approval for schema modifications"
        },
        
        # ML/DL Policies
        {
            "policy_name": "require_verification_for_model_deployment",
            "policy_type": "ml_deployment",
            "resource_pattern": r".*",
            "action": "warn",
            "requires_approval": True,
            "risk_level": "high",
            "description": "Require verification before deploying ML models",
            "metadata": {"min_accuracy": 0.85, "min_test_samples": 100}
        },
        {
            "policy_name": "block_untrusted_training_data",
            "policy_type": "ml_training",
            "resource_pattern": r".*",
            "action": "warn",
            "requires_approval": False,
            "risk_level": "medium",
            "description": "Warn when training data has low trust scores",
            "metadata": {"min_trust_score": 60.0}
        },
        
        # Self-Modification Policies
        {
            "policy_name": "block_core_module_modification",
            "policy_type": "self_modification",
            "resource_pattern": r".*(models\.py|auth\.py|verification\.py|governance\.py).*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "critical",
            "description": "Block modification of core Grace modules without approval"
        },
        {
            "policy_name": "allow_plugin_modifications",
            "policy_type": "self_modification",
            "resource_pattern": r".*plugins/.*",
            "action": "allow",
            "requires_approval": False,
            "risk_level": "low",
            "description": "Allow plugin modifications"
        },
        
        # Meta-Loop Policies
        {
            "policy_name": "require_approval_for_threshold_changes",
            "policy_type": "meta_optimization",
            "resource_pattern": r".*",
            "action": "warn",
            "requires_approval": True,
            "risk_level": "medium",
            "description": "Require approval before applying meta-loop recommendations"
        },
        {
            "policy_name": "block_extreme_threshold_adjustments",
            "policy_type": "meta_optimization",
            "resource_pattern": r".*",
            "action": "block",
            "requires_approval": True,
            "risk_level": "high",
            "description": "Block threshold changes > 50% from baseline",
            "metadata": {"max_change_percent": 50.0}
        }
    ]
    
    async with async_session() as session:
        # Check which policies already exist
        existing = await session.execute(select(GovernancePolicy))
        existing_names = {p.policy_name for p in existing.scalars().all()}
        
        new_count = 0
        for policy_data in policies:
            if policy_data["policy_name"] not in existing_names:
                policy = GovernancePolicy(**policy_data)
                session.add(policy)
                new_count += 1
        
        await session.commit()
        print(f"✓ Seeded {new_count} governance policies ({len(existing_names)} already existed)")
        print(f"✓ Total policies: {len(policies)}")
        
        # Show summary by type
        policy_types = {}
        for p in policies:
            pt = p["policy_type"]
            policy_types[pt] = policy_types.get(pt, 0) + 1
        
        print("\nPolicy breakdown:")
        for ptype, count in sorted(policy_types.items()):
            print(f"  - {ptype}: {count}")

if __name__ == "__main__":
    print("Seeding governance policies...")
    asyncio.run(seed_governance_policies())
    print("\n✅ Governance policies seeded successfully!")
