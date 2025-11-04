"""Seed baseline data required for a functional Grace environment."""

import asyncio
from typing import Iterable

from sqlalchemy import select

from backend.models import async_session
from backend.governance_models import GovernancePolicy, SecurityRule
from backend.trusted_sources import trust_manager


GOVERNANCE_POLICIES = [
    {
        "name": "restrict_system_file_access",
        "severity": "critical",
        "condition": r"file_access AND path MATCHES ^/(etc|sys|proc|boot|dev|root)/.*",
        "action": "block",
        "description": "Block access to system directories without approval",
    },
    {
        "name": "restrict_home_directory_write",
        "severity": "high",
        "condition": r"file_write AND path MATCHES ^/home/[^/]+/\.(ssh|gnupg|config)/.*",
        "action": "block",
        "description": "Block writes to sensitive user config directories",
    },
    {
        "name": "allow_workspace_access",
        "severity": "low",
        "condition": r"file_access AND path MATCHES ^/(workspace|tmp|var/tmp)/.*",
        "action": "allow",
        "description": "Allow unrestricted access to workspace and temp",
    },
    {
        "name": "require_approval_for_deletion",
        "severity": "medium",
        "condition": r"file_delete AND path MATCHES .*",
        "action": "warn",
        "description": "Require approval for any file deletion",
    },
    {
        "name": "block_shell_commands",
        "severity": "critical",
        "condition": r"execution AND command MATCHES .*(rm -rf|dd if=|mkfs|format|fdisk).*",
        "action": "block",
        "description": "Block destructive shell commands",
    },
    {
        "name": "sandbox_python_execution",
        "severity": "low",
        "condition": r"execution AND command MATCHES python.*",
        "action": "allow",
        "description": "Allow Python execution in sandbox",
    },
    {
        "name": "require_approval_for_downloads",
        "severity": "medium",
        "condition": r"execution AND command MATCHES .*(wget|curl|git clone).*",
        "action": "warn",
        "description": "Require approval for downloading external content",
    },
    {
        "name": "block_privilege_escalation",
        "severity": "critical",
        "condition": r"execution AND command MATCHES .*(sudo|su|pkexec).*",
        "action": "block",
        "description": "Block privilege escalation attempts",
    },
    {
        "name": "restrict_external_api_calls",
        "severity": "medium",
        "condition": r"network AND url MATCHES https?://(?!localhost|127\.0\.0\.1).*",
        "action": "warn",
        "description": "Require approval for external network calls",
    },
    {
        "name": "allow_localhost_connections",
        "severity": "low",
        "condition": r"network AND url MATCHES https?://(localhost|127\.0\.0\.1|0\.0\.0\.0):.*",
        "action": "allow",
        "description": "Allow localhost connections",
    },
    {
        "name": "block_sensitive_ports",
        "severity": "critical",
        "condition": r"network AND url MATCHES .*:(22|23|3389|5900).*",
        "action": "block",
        "description": "Block SSH, Telnet, RDP, VNC ports",
    },
    {
        "name": "require_high_trust_sources",
        "severity": "low",
        "condition": r"knowledge_ingestion AND trust_score < 70",
        "action": "warn",
        "description": "Warn on low-trust knowledge sources",
    },
    {
        "name": "block_untrusted_code_execution",
        "severity": "critical",
        "condition": r"knowledge_ingestion AND content MATCHES .*(eval|exec|__import__).*",
        "action": "block",
        "description": "Block ingestion of code with dangerous functions",
    },
    {
        "name": "allow_official_documentation",
        "severity": "low",
        "condition": r"knowledge_ingestion AND url MATCHES https://(docs\.python\.org|developer\.mozilla\.org|kubernetes\.io|reactjs\.org)/.*",
        "action": "allow",
        "description": "Auto-approve official documentation sources",
    },
    {
        "name": "block_drop_table",
        "severity": "critical",
        "condition": r"database AND query MATCHES .*(DROP TABLE|TRUNCATE|DELETE FROM users).*",
        "action": "block",
        "description": "Block destructive database operations",
    },
    {
        "name": "allow_read_queries",
        "severity": "low",
        "condition": r"database AND query MATCHES ^SELECT.*",
        "action": "allow",
        "description": "Allow SELECT queries",
    },
    {
        "name": "require_approval_for_schema_changes",
        "severity": "high",
        "condition": r"database AND query MATCHES .*(ALTER TABLE|CREATE TABLE|DROP COLUMN).*",
        "action": "warn",
        "description": "Require approval for schema modifications",
    },
    {
        "name": "require_verification_for_model_deployment",
        "severity": "high",
        "condition": r"ml_deployment AND (accuracy < 0.85 OR test_samples < 100)",
        "action": "warn",
        "description": "Require verification before deploying ML models",
    },
    {
        "name": "block_untrusted_training_data",
        "severity": "medium",
        "condition": r"ml_training AND trust_score < 60",
        "action": "warn",
        "description": "Warn when training data has low trust scores",
    },
    {
        "name": "block_core_module_modification",
        "severity": "critical",
        "condition": r"self_modification AND path MATCHES .*(models\.py|auth\.py|verification\.py|governance\.py).*",
        "action": "block",
        "description": "Block modification of core Grace modules without approval",
    },
    {
        "name": "allow_plugin_modifications",
        "severity": "low",
        "condition": r"self_modification AND path MATCHES .*plugins/.*",
        "action": "allow",
        "description": "Allow plugin modifications",
    },
]


SECURITY_RULES = [
    {
        "name": "sql_injection_detection",
        "condition": r"pattern_match: .*(UNION SELECT|OR 1=1|DROP TABLE|--\s|;--|\bEXEC\b|\bUNION\b.*\bSELECT\b).*",
        "severity": "critical",
        "action": "alert_and_block",
        "description": "Detect SQL injection attempts in inputs",
    },
    {
        "name": "xss_detection",
        "condition": r"pattern_match: .*(<script|javascript:|onerror=|onload=|<iframe|eval\(|document\.cookie).*",
        "severity": "high",
        "action": "alert_and_block",
        "description": "Detect cross-site scripting (XSS) attempts",
    },
    {
        "name": "command_injection_detection",
        "condition": r"pattern_match: .*(;|\||&&|\$\(|`).*(\brm\b|\bcat\b|\bwget\b|\bcurl\b|\bash\b).*",
        "severity": "critical",
        "action": "alert_and_block",
        "description": "Detect OS command injection attempts",
    },
    {
        "name": "path_traversal_detection",
        "condition": r"pattern_match: .*(\.\./|\.\.\\|%2e%2e|\.\.%2f|\.\.%5c).*",
        "severity": "high",
        "action": "alert_and_block",
        "description": "Detect path traversal attempts",
    },
    {
        "name": "api_key_exposure",
        "condition": r"pattern_match: .*(api[_-]?key|apikey|access[_-]?token|secret[_-]?key).*[:=]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?.*",
        "severity": "critical",
        "action": "alert_and_redact",
        "description": "Detect API keys or secrets in code/messages",
    },
    {
        "name": "aws_credentials_exposure",
        "condition": r"pattern_match: .*(AKIA[0-9A-Z]{16}|aws_access_key_id|aws_secret_access_key).*",
        "severity": "critical",
        "action": "alert_and_redact",
        "description": "Detect AWS credentials exposure",
    },
    {
        "name": "private_key_exposure",
        "condition": r"pattern_match: .*(-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----|BEGIN PRIVATE KEY).*",
        "severity": "critical",
        "action": "alert_and_redact",
        "description": "Detect private key exposure",
    },
    {
        "name": "excessive_api_calls",
        "condition": r"rate_limit: api_calls > 100 per 60 seconds",
        "severity": "medium",
        "action": "alert",
        "description": "Alert on >100 API calls per minute from single user",
    },
    {
        "name": "repeated_authentication_failures",
        "condition": r"rate_limit: auth_failures > 5 per 300 seconds at /auth/login",
        "severity": "high",
        "action": "alert_and_block",
        "description": "Block after 5 failed login attempts in 5 minutes",
    },
    {
        "name": "unusual_file_access_volume",
        "condition": r"anomaly: file_access > 50 per 60 seconds",
        "severity": "medium",
        "action": "alert",
        "description": "Alert on >50 file access operations per minute",
    },
    {
        "name": "dangerous_python_functions",
        "condition": r"pattern_match: .*(eval\(|exec\(|compile\(|__import__\(|open\(.*['\"]w['\"]).*",
        "severity": "high",
        "action": "alert",
        "description": "Warn on dangerous Python functions in code",
    },
    {
        "name": "crypto_mining_indicators",
        "condition": r"pattern_match: .*(xmrig|ethminer|stratum\+tcp|mining\.pool|cryptonight).*",
        "severity": "critical",
        "action": "alert_and_block",
        "description": "Detect cryptocurrency mining attempts",
    },
    {
        "name": "reverse_shell_detection",
        "condition": r"pattern_match: .*(nc -e|/bin/sh|bash -i|socat.*exec|python.*socket\.connect).*",
        "severity": "critical",
        "action": "alert_and_block",
        "description": "Detect reverse shell attempts",
    },
    {
        "name": "large_data_transfer",
        "condition": r"anomaly: data_transfer > 104857600 bytes",
        "severity": "high",
        "action": "alert",
        "description": "Alert on data transfers >100MB in single request",
    },
    {
        "name": "sensitive_data_regex",
        "condition": r"pattern_match: .*(ssn|social.security|\b\d{3}-\d{2}-\d{4}\b|credit.card|\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b).*",
        "severity": "critical",
        "action": "alert_and_redact",
        "description": "Detect and redact SSN/credit card numbers",
    },
    {
        "name": "privilege_escalation_attempts",
        "condition": r"pattern_match: .*(sudo|su -|pkexec|chmod 777|chown root).*",
        "severity": "critical",
        "action": "alert_and_block",
        "description": "Detect privilege escalation attempts",
    },
    {
        "name": "unauthorized_admin_access",
        "condition": r"access_control: non_admin accessing /admin/.*",
        "severity": "high",
        "action": "alert",
        "description": "Alert on non-admin users accessing admin endpoints",
    },
]


async def _seed_collection(session, model, records: Iterable[dict]) -> int:
    result = await session.execute(select(model.name))
    existing = set(result.scalars())

    created = 0
    for record in records:
        if record["name"] in existing:
            continue
        session.add(model(**record))
        created += 1

    if created:
        await session.commit()
    return created


async def seed_baseline() -> None:
    async with async_session() as session:
        policies_added = await _seed_collection(session, GovernancePolicy, GOVERNANCE_POLICIES)
        rules_added = await _seed_collection(session, SecurityRule, SECURITY_RULES)

    await trust_manager.initialize_defaults()

    print("Baseline seed complete:")
    print(f"  Governance policies inserted: {policies_added}")
    print(f"  Security rules inserted:   {rules_added}")
    print("  Trusted sources ensured via trust_manager.initialize_defaults()")


if __name__ == "__main__":
    asyncio.run(seed_baseline())
