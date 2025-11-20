#!/usr/bin/env python3
"""Check what Grace is currently learning"""

import sys
import os
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(os.getcwd())))

from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager
from backend.learning_systems.governed_web_learning import learning_job_orchestrator

print("="*60)
print("WHAT IS GRACE LEARNING RIGHT NOW?")
print("="*60)

# 1. Current Learning Status
print("\n[1] Learning Status:")
status = learning_whitelist_manager.get_learning_status()
print(f"  - Current Domain: {status.get('current_domain') or 'None (Not started)'}")
print(f"  - Domains Mastered: {status.get('domains_mastered', 0)}")
print(f"  - Domains In Progress: {status.get('domains_in_progress', 0)}")
print(f"  - Total Projects Completed: {status.get('total_projects_completed', 0)}")

# 2. Next Topic to Learn
print("\n[2] Next Topic in Queue:")
next_topic = learning_whitelist_manager.get_next_topic()
if next_topic:
    print(f"  - Domain: {next_topic['domain']}")
    print(f"  - Priority: {next_topic['config'].get('priority', 'unknown')}")
    print(f"  - Topics to Study:")
    for topic in next_topic['topics'][:3]:
        print(f"    • {topic}")
    if len(next_topic['topics']) > 3:
        print(f"    ... and {len(next_topic['topics']) - 3} more")
    print(f"  - Practice Projects:")
    for project in next_topic['projects']:
        print(f"    • {project.get('name', 'Unknown')}")
else:
    print("  - All domains mastered!")

# 3. Active Learning Jobs
print("\n[3] Active Learning Jobs:")
active_jobs = learning_job_orchestrator.get_active_jobs()
if active_jobs:
    print(f"  - {len(active_jobs)} jobs running:")
    for job in active_jobs:
        print(f"    • Job ID: {job['job_id']}")
        print(f"      Query: {job['query']}")
        print(f"      Status: {job['status']}")
else:
    print("  - No active learning jobs")

# 4. Orchestrator Stats
print("\n[4] Learning System Stats:")
stats = learning_job_orchestrator.get_orchestrator_stats()
print(f"  - Total Jobs: {stats['total_jobs']}")
print(f"  - Completed: {stats['completed_jobs']}")
print(f"  - Failed: {stats['failed_jobs']}")
print(f"  - Pending Approvals: {stats['pending_approvals']}")

# 5. Recommendation
print("\n[5] Recommendation:")
if not status.get('current_domain'):
    print("  Grace has not started learning yet.")
    print("  To start, call: POST /api/remote-access/learning/start-domain")
    print(f"  Recommended domain: {next_topic['domain'] if next_topic else 'None'}")
else:
    print(f"  Grace is actively learning: {status.get('current_domain')}")

print("="*60)
