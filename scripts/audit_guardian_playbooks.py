#!/usr/bin/env python3
"""
Audit Guardian Playbooks - Phase 1 Task 1
Inventory all playbooks, verify they're loadable and have required metadata
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.guardian_playbooks import GuardianPlaybookRegistry
import json
from datetime import datetime

def audit_playbooks():
    """Audit all registered Guardian playbooks"""
    
    print("=" * 80)
    print("GUARDIAN PLAYBOOK AUDIT")
    print("=" * 80)
    print()
    
    # Initialize registry
    registry = GuardianPlaybookRegistry()
    
    playbooks = registry.playbooks
    total = len(playbooks)
    
    print(f"Total playbooks registered: {total}")
    print()
    
    # Audit results
    results = {
        "audit_timestamp": datetime.utcnow().isoformat(),
        "total_playbooks": total,
        "playbooks": [],
        "issues": []
    }
    
    # Check each playbook
    for i, (playbook_id, playbook) in enumerate(sorted(playbooks.items()), 1):
        print(f"[{i}/{total}] Auditing: {playbook_id}")
        
        playbook_info = {
            "id": playbook_id,
            "name": playbook.name,
            "description": playbook.description,
            "trigger_pattern": playbook.trigger_pattern,
            "priority": playbook.priority,
            "max_retries": playbook.max_retries,
            "requires_approval": playbook.requires_approval,
            "executions": playbook.executions,
            "successes": playbook.successes,
            "failures": playbook.failures,
            "has_remediation_function": playbook.remediation_function is not None,
            "issues": []
        }
        
        # Validation checks
        if not playbook.name:
            playbook_info["issues"].append("Missing name")
            results["issues"].append(f"{playbook_id}: Missing name")
        
        if not playbook.description:
            playbook_info["issues"].append("Missing description")
            results["issues"].append(f"{playbook_id}: Missing description")
        
        if not playbook.trigger_pattern:
            playbook_info["issues"].append("Missing trigger pattern")
            results["issues"].append(f"{playbook_id}: Missing trigger pattern")
        
        if not playbook.remediation_function:
            playbook_info["issues"].append("Missing remediation function")
            results["issues"].append(f"{playbook_id}: Missing remediation function")
        
        if playbook.priority < 1 or playbook.priority > 10:
            playbook_info["issues"].append(f"Invalid priority: {playbook.priority}")
            results["issues"].append(f"{playbook_id}: Invalid priority {playbook.priority}")
        
        # Status
        status = "OK" if not playbook_info["issues"] else f"ISSUES: {len(playbook_info['issues'])}"
        print(f"  Status: {status}")
        
        if playbook_info["issues"]:
            for issue in playbook_info["issues"]:
                print(f"    - {issue}")
        
        print(f"  Name: {playbook.name}")
        print(f"  Priority: {playbook.priority}")
        print(f"  Requires Approval: {playbook.requires_approval}")
        print(f"  Executions: {playbook.executions}")
        print()
        
        results["playbooks"].append(playbook_info)
    
    # Summary
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Playbooks: {total}")
    print(f"Playbooks with Issues: {len([p for p in results['playbooks'] if p['issues']])}")
    print(f"Total Issues Found: {len(results['issues'])}")
    
    if results["issues"]:
        print()
        print("Issues:")
        for issue in results["issues"]:
            print(f"  - {issue}")
    else:
        print()
        print("[OK] All playbooks passed audit!")
    
    # Save results
    output_file = Path("reports/guardian_playbook_audit.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"Full audit saved to: {output_file}")
    print()
    
    # Return exit code
    return 0 if not results["issues"] else 1

if __name__ == "__main__":
    sys.exit(audit_playbooks())
