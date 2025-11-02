"""Seed default governance policies for Grace"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from models import async_session
from governance_models import GovernancePolicy

async def seed_governance_policies():
    """Create 20+ default governance policies for production use"""
    
    policies = [
        # File System Policies
        {
            "name": "restrict_system_file_access",
            "severity": "critical",
            "condition": r"file_access AND path MATCHES ^/(etc|sys|proc|boot|dev|root)/.*",
            "action": "block",
            "description": "Block access to system directories without approval"
        },
        {
            "name": "restrict_home_directory_write",
            "severity": "high",
            "condition": r"file_write AND path MATCHES ^/home/[^/]+/\.(ssh|gnupg|config)/.*",
            "action": "block",
            "description": "Block writes to sensitive user config directories"
        },
        {
            "name": "allow_workspace_access",
            "severity": "low",
            "condition": r"file_access AND path MATCHES ^/(workspace|tmp|var/tmp)/.*",
            "action": "allow",
            "description": "Allow unrestricted access to workspace and temp"
        },
        {
            "name": "require_approval_for_deletion",
            "severity": "medium",
            "condition": r"file_delete AND path MATCHES .*",
            "action": "warn",
            "description": "Require approval for any file deletion"
        },
        
        # Code Execution Policies
        {
            "name": "block_shell_commands",
            "severity": "critical",
            "condition": r"execution AND command MATCHES .*(rm -rf|dd if=|mkfs|format|fdisk).*",
            "action": "block",
            "description": "Block destructive shell commands"
        },
        {
            "name": "sandbox_python_execution",
            "severity": "low",
            "condition": r"execution AND command MATCHES python.*",
            "action": "allow",
            "description": "Allow Python execution in sandbox"
        },
        {
            "name": "require_approval_for_downloads",
            "severity": "medium",
            "condition": r"execution AND command MATCHES .*(wget|curl|git clone).*",
            "action": "warn",
            "description": "Require approval for downloading external content"
        },
        {
            "name": "block_privilege_escalation",
            "severity": "critical",
            "condition": r"execution AND command MATCHES .*(sudo|su|pkexec).*",
            "action": "block",
            "description": "Block privilege escalation attempts"
        },
        
        # Network Policies
        {
            "name": "restrict_external_api_calls",
            "severity": "medium",
            "condition": r"network AND url MATCHES https?://(?!localhost|127\.0\.0\.1).*",
            "action": "warn",
            "description": "Require approval for external network calls"
        },
        {
            "name": "allow_localhost_connections",
            "severity": "low",
            "condition": r"network AND url MATCHES https?://(localhost|127\.0\.0\.1|0\.0\.0\.0):.*",
            "action": "allow",
            "description": "Allow localhost connections"
        },
        {
            "name": "block_sensitive_ports",
            "severity": "critical",
            "condition": r"network AND url MATCHES .*:(22|23|3389|5900).*",
            "action": "block",
            "description": "Block SSH, Telnet, RDP, VNC ports"
        },
        
        # Knowledge Ingestion Policies
        {
            "name": "require_high_trust_sources",
            "severity": "low",
            "condition": r"knowledge_ingestion AND trust_score < 70",
            "action": "warn",
            "description": "Warn on low-trust knowledge sources"
        },
        {
            "name": "block_untrusted_code_execution",
            "severity": "critical",
            "condition": r"knowledge_ingestion AND content MATCHES .*(eval|exec|__import__).*",
            "action": "block",
            "description": "Block ingestion of code with dangerous functions"
        },
        {
            "name": "allow_official_documentation",
            "severity": "low",
            "condition": r"knowledge_ingestion AND url MATCHES https://(docs\.python\.org|developer\.mozilla\.org|kubernetes\.io|reactjs\.org)/.*",
            "action": "allow",
            "description": "Auto-approve official documentation sources"
        },
        
        # Database Policies
        {
            "name": "block_drop_table",
            "severity": "critical",
            "condition": r"database AND query MATCHES .*(DROP TABLE|TRUNCATE|DELETE FROM users).*",
            "action": "block",
            "description": "Block destructive database operations"
        },
        {
            "name": "allow_read_queries",
            "severity": "low",
            "condition": r"database AND query MATCHES ^SELECT.*",
            "action": "allow",
            "description": "Allow SELECT queries"
        },
        {
            "name": "require_approval_for_schema_changes",
            "severity": "high",
            "condition": r"database AND query MATCHES .*(ALTER TABLE|CREATE TABLE|DROP COLUMN).*",
            "action": "warn",
            "description": "Require approval for schema modifications"
        },
        
        # ML/DL Policies
        {
            "name": "require_verification_for_model_deployment",
            "severity": "high",
            "condition": r"ml_deployment AND (accuracy < 0.85 OR test_samples < 100)",
            "action": "warn",
            "description": "Require verification before deploying ML models"
        },
        {
            "name": "block_untrusted_training_data",
            "severity": "medium",
            "condition": r"ml_training AND trust_score < 60",
            "action": "warn",
            "description": "Warn when training data has low trust scores"
        },
        
        # Self-Modification Policies
        {
            "name": "block_core_module_modification",
            "severity": "critical",
            "condition": r"self_modification AND path MATCHES .*(models\.py|auth\.py|verification\.py|governance\.py).*",
            "action": "block",
            "description": "Block modification of core Grace modules without approval"
        },
        {
            "name": "allow_plugin_modifications",
            "severity": "low",
            "condition": r"self_modification AND path MATCHES .*plugins/.*",
            "action": "allow",
            "description": "Allow plugin modifications"
        },
        
        # Meta-Loop Policies
        {
            "name": "require_approval_for_threshold_changes",
            "severity": "medium",
            "condition": r"meta_optimization AND change_requested = true",
            "action": "warn",
            "description": "Require approval before applying meta-loop recommendations"
        },
        {
            "name": "block_extreme_threshold_adjustments",
            "severity": "high",
            "condition": r"meta_optimization AND change_percent > 50",
            "action": "block",
            "description": "Block threshold changes > 50% from baseline"
        }
    ]
    
    async with async_session() as session:
        # Check which policies already exist
        existing = await session.execute(select(GovernancePolicy))
        existing_names = {p.name for p in existing.scalars().all()}
        
        new_count = 0
        for policy_data in policies:
            if policy_data["name"] not in existing_names:
                policy = GovernancePolicy(**policy_data)
                session.add(policy)
                new_count += 1
        
        await session.commit()
        print(f"✓ Seeded {new_count} governance policies ({len(existing_names)} already existed)")
        print(f"✓ Total policies: {len(policies)}")
        
        # Show summary by severity
        severity_counts = {}
        for p in policies:
            sev = p["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        print("\nPolicy breakdown by severity:")
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                print(f"  - {severity}: {count}")

if __name__ == "__main__":
    print("Seeding governance policies...")
    asyncio.run(seed_governance_policies())
    print("\n✅ Governance policies seeded successfully!")
