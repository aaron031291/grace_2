"""Generate synthetic security events for ML training"""

import asyncio
import json
from datetime import datetime, timedelta
import random
from sqlalchemy import select

from backend.governance_models import SecurityEvent
from backend.models import async_session, init_db


ALERT_PATTERNS = [
    {
        'action': 'file_access',
        'resources': ['/etc/passwd', '/etc/shadow', '/root/.ssh/id_rsa', '/etc/sudoers'],
        'severity': 'critical',
        'actors': ['suspicious_user', 'root', 'admin'],
        'weight': 5
    },
    {
        'action': 'config_change',
        'resources': ['/config/security.yaml', '/config/firewall.conf', '/admin/settings'],
        'severity': 'high',
        'actors': ['admin', 'devops', 'system'],
        'weight': 10
    },
    {
        'action': 'api_call',
        'resources': ['/api/admin/users', '/api/admin/permissions', '/api/billing/delete'],
        'severity': 'high',
        'actors': ['api_client', 'admin', 'service_account'],
        'weight': 8
    },
    {
        'action': 'login_attempt',
        'resources': ['/auth/login', '/admin/login', '/api/auth'],
        'severity': 'medium',
        'actors': ['unknown', 'guest', 'user_123'],
        'weight': 15
    },
    {
        'action': 'data_export',
        'resources': ['/api/export/users', '/api/download/database', '/admin/backup'],
        'severity': 'high',
        'actors': ['admin', 'backup_service', 'analyst'],
        'weight': 7
    },
    {
        'action': 'permission_change',
        'resources': ['/api/roles/update', '/admin/permissions', '/api/acl/modify'],
        'severity': 'critical',
        'actors': ['admin', 'root', 'security_team'],
        'weight': 6
    },
    {
        'action': 'file_read',
        'resources': ['/api/documents', '/files/reports', '/data/analytics'],
        'severity': 'low',
        'actors': ['user_1', 'user_2', 'analyst', 'viewer'],
        'weight': 20
    },
    {
        'action': 'api_query',
        'resources': ['/api/search', '/api/list', '/api/dashboard'],
        'severity': 'low',
        'actors': ['user_1', 'user_2', 'user_3', 'guest'],
        'weight': 25
    },
    {
        'action': 'network_scan',
        'resources': ['/network/scan', '/api/ports', '/admin/network'],
        'severity': 'critical',
        'actors': ['scanner', 'security_test', 'attacker'],
        'weight': 4
    },
    {
        'action': 'privilege_escalation',
        'resources': ['/api/sudo', '/admin/elevate', '/system/root'],
        'severity': 'critical',
        'actors': ['user_1', 'compromised_account', 'malicious'],
        'weight': 3
    },
    {
        'action': 'config_view',
        'resources': ['/config/app.yaml', '/settings/view', '/api/config'],
        'severity': 'medium',
        'actors': ['developer', 'admin', 'support'],
        'weight': 12
    },
    {
        'action': 'log_access',
        'resources': ['/logs/application', '/logs/audit', '/admin/logs'],
        'severity': 'medium',
        'actors': ['admin', 'security_team', 'support'],
        'weight': 10
    }
]


async def generate_security_events(count: int = 200):
    """Generate synthetic security events with realistic patterns"""
    
    await init_db()
    
    async with async_session() as session:
        result = await session.execute(select(SecurityEvent))
        existing = result.scalars().all()
        print(f"Existing events: {len(existing)}")
        
        if len(existing) >= count:
            print(f"Already have {len(existing)} events, skipping generation")
            return
    
    weights = [p['weight'] for p in ALERT_PATTERNS]
    
    events_to_create = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(count):
        pattern = random.choices(ALERT_PATTERNS, weights=weights)[0]
        
        actor = random.choice(pattern['actors'])
        resource = random.choice(pattern['resources'])
        action = pattern['action']
        severity = pattern['severity']
        
        if random.random() < 0.1:
            severities = ['low', 'medium', 'high', 'critical']
            severity = random.choice(severities)
        
        timestamp = base_time + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        details = {
            'ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            'user_agent': random.choice(['curl/7.68', 'python-requests/2.28', 'Mozilla/5.0']),
            'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
            'status_code': random.choice([200, 201, 401, 403, 404, 500])
        }
        
        events_to_create.append({
            'actor': actor,
            'action': action,
            'resource': resource,
            'severity': severity,
            'details': json.dumps(details),
            'status': random.choice(['open', 'open', 'open', 'resolved']),
            'created_at': timestamp
        })
    
    async with async_session() as session:
        for event_data in events_to_create:
            event = SecurityEvent(**event_data)
            session.add(event)
        
        await session.commit()
    
    severity_counts = {}
    for event in events_to_create:
        severity = event['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"[OK] Generated {len(events_to_create)} synthetic security events:")
    for severity, count in sorted(severity_counts.items()):
        print(f"  - {severity}: {count}")


if __name__ == "__main__":
    asyncio.run(generate_security_events(200))
