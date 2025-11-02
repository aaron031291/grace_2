"""Seed default Hunter security rules"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from governance_models import SecurityRule, Base

DATABASE_URL = "sqlite+aiosqlite:///./grace.db"
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def seed_hunter_rules():
    """Create 15+ default Hunter security rules"""
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    rules = [
        # Injection Attack Detection
        {
            "name": "sql_injection_detection",
            "condition": r"pattern_match: .*(UNION SELECT|OR 1=1|DROP TABLE|--\s|;--|\bEXEC\b|\bUNION\b.*\bSELECT\b).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect SQL injection attempts in inputs"
        },
        {
            "name": "xss_detection",
            "condition": r"pattern_match: .*(<script|javascript:|onerror=|onload=|<iframe|eval\(|document\.cookie).*",
            "severity": "high",
            "action": "alert_and_block",
            "description": "Detect cross-site scripting (XSS) attempts"
        },
        {
            "name": "command_injection_detection",
            "condition": r"pattern_match: .*(;|\||&&|\$\(|\`).*(\brm\b|\bcat\b|\bwget\b|\bcurl\b|\bash\b).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect OS command injection attempts"
        },
        {
            "name": "path_traversal_detection",
            "condition": r"pattern_match: .*(\.\.\/|\.\.\\|%2e%2e|\.\.%2f|\.\.%5c).*",
            "severity": "high",
            "action": "alert_and_block",
            "description": "Detect path traversal attempts"
        },
        
        # Secret Exposure Detection
        {
            "name": "api_key_exposure",
            "condition": r"pattern_match: .*(api[_-]?key|apikey|access[_-]?token|secret[_-]?key).*[:=]\s*['\"]?[a-zA-Z0-9]{20,}['\"]?.*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect API keys or secrets in code/messages"
        },
        {
            "name": "aws_credentials_exposure",
            "condition": r"pattern_match: .*(AKIA[0-9A-Z]{16}|aws_access_key_id|aws_secret_access_key).*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect AWS credentials exposure"
        },
        {
            "name": "private_key_exposure",
            "condition": r"pattern_match: .*(-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----|BEGIN PRIVATE KEY).*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect private key exposure"
        },
        
        # Anomalous Behavior Detection
        {
            "name": "excessive_api_calls",
            "condition": r"rate_limit: api_calls > 100 per 60 seconds",
            "severity": "medium",
            "action": "alert",
            "description": "Alert on >100 API calls per minute from single user"
        },
        {
            "name": "repeated_authentication_failures",
            "condition": r"rate_limit: auth_failures > 5 per 300 seconds at /auth/login",
            "severity": "high",
            "action": "alert_and_block",
            "description": "Block after 5 failed login attempts in 5 minutes"
        },
        {
            "name": "unusual_file_access_volume",
            "condition": r"anomaly: file_access > 50 per 60 seconds",
            "severity": "medium",
            "action": "alert",
            "description": "Alert on >50 file access operations per minute"
        },
        
        # Malicious Content Detection
        {
            "name": "dangerous_python_functions",
            "condition": r"pattern_match: .*(eval\(|exec\(|compile\(|__import__\(|open\(.*['\"]w['\"]).*",
            "severity": "high",
            "action": "alert",
            "description": "Warn on dangerous Python functions in code"
        },
        {
            "name": "crypto_mining_indicators",
            "condition": r"pattern_match: .*(xmrig|ethminer|stratum\+tcp|mining\.pool|cryptonight).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect cryptocurrency mining attempts"
        },
        {
            "name": "reverse_shell_detection",
            "condition": r"pattern_match: .*(nc -e|/bin/sh|bash -i|socat.*exec|python.*socket\.connect).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect reverse shell attempts"
        },
        
        # Data Exfiltration Detection
        {
            "name": "large_data_transfer",
            "condition": r"anomaly: data_transfer > 104857600 bytes",
            "severity": "high",
            "action": "alert",
            "description": "Alert on data transfers >100MB in single request"
        },
        {
            "name": "sensitive_data_regex",
            "condition": r"pattern_match: .*(ssn|social.security|\b\d{3}-\d{2}-\d{4}\b|credit.card|\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b).*",
            "severity": "critical",
            "action": "alert_and_redact",
            "description": "Detect and redact SSN/credit card numbers"
        },
        
        # Privilege Escalation Detection
        {
            "name": "privilege_escalation_attempts",
            "condition": r"pattern_match: .*(sudo|su -|pkexec|chmod 777|chown root).*",
            "severity": "critical",
            "action": "alert_and_block",
            "description": "Detect privilege escalation attempts"
        },
        {
            "name": "unauthorized_admin_access",
            "condition": r"access_control: non_admin accessing /admin/.*",
            "severity": "high",
            "action": "alert",
            "description": "Alert on non-admin users accessing admin endpoints"
        }
    ]
    
    async with async_session_maker() as session:
        # Check which rules already exist
        existing = await session.execute(select(SecurityRule))
        existing_names = {r.name for r in existing.scalars().all()}
        
        new_count = 0
        for rule_data in rules:
            if rule_data["name"] not in existing_names:
                rule = SecurityRule(**rule_data)
                session.add(rule)
                new_count += 1
        
        await session.commit()
        print(f"[OK] Seeded {new_count} Hunter security rules ({len(existing_names)} already existed)")
        print(f"[OK] Total rules: {len(rules)}")
        
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

if __name__ == "__main__":
    print("Seeding Hunter security rules...")
    asyncio.run(seed_hunter_rules())
    print("\n[SUCCESS] Hunter security rules seeded successfully!")
