"""
Show Evidence That Self-Healing Is Working

This script analyzes logs and database records to prove self-healing is functioning.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

def analyze_incidents_log():
    """Analyze the incidents.jsonl log file for self-healing activity"""
    log_file = Path("c:/Users/aaron/grace_2/logs/incidents.jsonl")
    
    if not log_file.exists():
        return None, "Log file not found"
    
    incidents = []
    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    incidents.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return incidents, None

def format_incident(incident):
    """Format incident for display"""
    detected = incident.get('detected_at', 'N/A')
    resolved = incident.get('resolved_at', 'N/A')
    status = incident.get('status', 'N/A')
    failure = incident.get('failure_mode', 'N/A')
    severity = incident.get('severity', 'N/A')
    mttr = incident.get('mttr_seconds', 'N/A')
    success = incident.get('success', False)
    
    return {
        'detected': detected,
        'resolved': resolved,
        'status': status,
        'failure_mode': failure,
        'severity': severity,
        'mttr': mttr,
        'success': success
    }

def main():
    print("=" * 80)
    print("GRACE SELF-HEALING EVIDENCE REPORT")
    print("=" * 80)
    print()
    
    # Analyze incidents log
    print("[1] Analyzing incidents log...")
    incidents, error = analyze_incidents_log()
    
    if error:
        print(f"ERROR: {error}")
        return 1
    
    print(f"Found {len(incidents)} total incidents in log")
    print()
    
    # Filter for resolved incidents (proof of self-healing)
    resolved_incidents = [i for i in incidents if i.get('status') == 'resolved']
    detected_incidents = [i for i in incidents if i.get('status') == 'detected']
    successful_healings = [i for i in resolved_incidents if i.get('success') == True]
    
    print("[2] SUMMARY STATISTICS:")
    print("-" * 80)
    print(f"Total Incidents:          {len(incidents)}")
    print(f"Detected (Active):        {len(detected_incidents)}")
    print(f"Resolved:                 {len(resolved_incidents)}")
    print(f"Successfully Healed:      {len(successful_healings)}")
    
    if resolved_incidents:
        avg_mttr = sum(i.get('mttr_seconds', 0) for i in resolved_incidents if i.get('mttr_seconds')) / len(resolved_incidents)
        print(f"Average MTTR:             {avg_mttr:.3f} seconds")
    print()
    
    # Show recent healing events
    print("[3] RECENT SELF-HEALING EVENTS (Last 10):")
    print("-" * 80)
    
    recent = incidents[-10:] if len(incidents) > 10 else incidents
    
    if not recent:
        print("No healing events found")
    else:
        for i, incident in enumerate(reversed(recent), 1):
            info = format_incident(incident)
            print(f"\nEvent {i}:")
            print(f"  Failure Mode:  {info['failure_mode']}")
            print(f"  Severity:      {info['severity']}")
            print(f"  Status:        {info['status']}")
            print(f"  Detected:      {info['detected']}")
            if info['resolved'] != 'N/A':
                print(f"  Resolved:      {info['resolved']}")
                print(f"  MTTR:          {info['mttr']} seconds")
                print(f"  Success:       {'YES' if info['success'] else 'NO'}")
    
    print()
    print("=" * 80)
    
    # Verdict
    if successful_healings:
        print("[PASS] SELF-HEALING IS WORKING!")
        print(f"       Evidence: {len(successful_healings)} successful automatic healing events")
        print("=" * 80)
        return 0
    elif resolved_incidents:
        print("[PARTIAL] Self-healing attempted but success unclear")
        print(f"          {len(resolved_incidents)} incidents were resolved")
        print("=" * 80)
        return 1
    else:
        print("[INCONCLUSIVE] No resolved incidents found")
        print("               System may not have encountered failures yet")
        print("=" * 80)
        return 2

if __name__ == "__main__":
    sys.exit(main())
