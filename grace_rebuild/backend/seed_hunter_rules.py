"""Seed default Hunter security rules"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.models import async_session
from backend.governance_models import SecurityRule

async def seed_hunter_rules():
    """Create 15+ default Hunter security rules"""
    
    rules = [
        # Injection Attack Detection
        {
            "rule_name": "sql_injection_detection",
            "rule_type": "pattern_match",
            "pattern": r".*(UNION SELECT|OR 1=1|DROP TABLE|--\s|;--|\bEXEC\b|\bUNION\b.*\bSELECT\b).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect SQL injection attempts in inputs",
            "auto_remediate": True
        },
        {
            "rule_name": "xss_detection",
            "rule_type": "pattern_match",
            "pattern": r".*(<script|javascript:|onerror=|onload=|<iframe|eval\(|document\.cookie).*",
            "severity": "high",
            "action": "alert_and_block",
            "description": "Detect cross-site scripting (XSS) attempts",
            "auto_remediate": True
        },
        {
            "rule_name": "command_injection_detection",
            "rule_type": "pattern_match",
            "pattern": r".*(;|\||&&|\$\(|\`).*(\brm\b|\bcat\b|\bwget\b|\bcurl\b|\bash\b).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect OS command injection attempts",
            "auto_remediate": True
        },
        {
            "rule_name": "path_traversal_detection",
            "rule_type": "pattern_match",
            "pattern": r".*(\.\.\/|\.\.\\|%2e%2e|\.\.%2f|\.\.%5c).*",
            "severity": "high",
            "action": "alert_and_block",
            "description": "Detect path traversal attempts",
            "auto_remediate": True
        },
        
        # Secret Exposure Detection
        {
            "rule_name": "api_key_exposure",
            "rule_type": "pattern_match",
            "pattern": r".*(api[_-]?key|apikey|access[_-]?token|secret[_-]?key).*[:=]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?.*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect API keys or secrets in code/messages",
            "auto_remediate": True
        },
        {
            "rule_name": "aws_credentials_exposure",
            "rule_type": "pattern_match",
            "pattern": r".*(AKIA[0-9A-Z]{16}|aws_access_key_id|aws_secret_access_key).*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect AWS credentials exposure",
            "auto_remediate": True
        },
        {
            "rule_name": "private_key_exposure",
            "rule_type": "pattern_match",
            "pattern": r".*(-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----|BEGIN PRIVATE KEY).*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect private key exposure",
            "auto_remediate": True
        },
        
        # Anomalous Behavior Detection
        {
            "rule_name": "excessive_api_calls",
            "rule_type": "rate_limit",
            "pattern": r".*",
            "severity": "medium",
            "action": "alert",
            "description": "Alert on >100 API calls per minute from single user",
            "auto_remediate": False,
            "metadata": {"threshold": 100, "window_seconds": 60}
        },
        {
            "rule_name": "repeated_authentication_failures",
            "rule_type": "rate_limit",
            "pattern": r".*/auth/login.*",
            "severity": "high",
            "action": "alert_and_block",
            "description": "Block after 5 failed login attempts in 5 minutes",
            "auto_remediate": True,
            "metadata": {"threshold": 5, "window_seconds": 300}
        },
        {
            "rule_name": "unusual_file_access_volume",
            "rule_type": "anomaly",
            "pattern": r".*",
            "severity": "medium",
            "action": "alert",
            "description": "Alert on >50 file access operations per minute",
            "auto_remediate": False,
            "metadata": {"threshold": 50, "window_seconds": 60}
        },
        
        # Malicious Content Detection
        {
            "rule_name": "dangerous_python_functions",
            "rule_type": "pattern_match",
            "pattern": r".*(eval\(|exec\(|compile\(|__import__\(|open\(.*['\"]w['\"]).*",
            "severity": "high",
            "action": "alert",
            "description": "Warn on dangerous Python functions in code",
            "auto_remediate": False
        },
        {
            "rule_name": "crypto_mining_indicators",
            "rule_type": "pattern_match",
            "pattern": r".*(xmrig|ethminer|stratum\+tcp|mining\.pool|cryptonight).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect cryptocurrency mining attempts",
            "auto_remediate": True
        },
        {
            "rule_name": "reverse_shell_detection",
            "rule_type": "pattern_match",
            "pattern": r".*(nc -e|/bin/sh|bash -i|socat.*exec|python.*socket\.connect).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect reverse shell attempts",
            "auto_remediate": True
        },
        
        # Data Exfiltration Detection
        {
            "rule_name": "large_data_transfer",
            "rule_type": "anomaly",
            "pattern": r".*",
            "severity": "high",
            "action": "alert",
            "description": "Alert on data transfers >100MB in single request",
            "auto_remediate": False,
            "metadata": {"threshold_bytes": 104857600}
        },
        {
            "rule_name": "sensitive_data_regex",
            "rule_type": "pattern_match",
            "pattern": r".*(ssn|social.security|\b\d{3}-\d{2}-\d{4}\b|credit.card|\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b).*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect and redact SSN/credit card numbers",
            "auto_remediate": True
        },
        
        # Privilege Escalation Detection
        {
            "rule_name": "privilege_escalation_attempts",
            "rule_type": "pattern_match",
            "pattern": r".*(sudo|su -|pkexec|chmod 777|chown root).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect privilege escalation attempts",
            "auto_remediate": True
        },
        {
            "rule_name": "unauthorized_admin_access",
            "rule_type": "access_control",
            "pattern": r".*/admin/.*",
            "severity": "high",
            "action": "alert",
            "description": "Alert on non-admin users accessing admin endpoints",
            "auto_remediate": False
        }
    ]
    
    async with async_session() as session:
        # Check which rules already exist
        existing = await session.execute(select(SecurityRule))
        existing_names = {r.rule_name for r in existing.scalars().all()}
        
        new_count = 0
        for rule_data in rules:
            if rule_data["rule_name"] not in existing_names:
                rule = SecurityRule(**rule_data)
                session.add(rule)
                new_count += 1
        
        await session.commit()
        print(f"✓ Seeded {new_count} Hunter security rules ({len(existing_names)} already existed)")
        print(f"✓ Total rules: {len(rules)}")
        
        # Show summary by severity
        severity_counts = {}
        for r in rules:
            sev = r["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        print("\nRule breakdown by severity:")
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                print(f"  - {severity}: {count}")
        
        # Show auto-remediate stats
        auto_remediate_count = sum(1 for r in rules if r.get("auto_remediate", False))
        print(f"\nAuto-remediate enabled: {auto_remediate_count}/{len(rules)}")

if __name__ == "__main__":
    print("Seeding Hunter security rules...")
    asyncio.run(seed_hunter_rules())
    print("\n✅ Hunter security rules seeded successfully!")
