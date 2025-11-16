"""
Log Summarizer - Convert JSON logs to natural language
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def summarize_logs(log_file: str, window: int = 50):
    """Summarize recent log entries in plain English"""
    
    log_path = Path(log_file)
    if not log_path.exists():
        print(f"Log file not found: {log_file}")
        return
    
    # Read last N lines
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()[-window:]
    
    events_by_subsystem = defaultdict(list)
    errors = []
    decisions = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to parse as JSON
        try:
            if line.startswith('{'):
                event = json.loads(line)
                subsystem = event.get('subsystem', 'unknown')
                events_by_subsystem[subsystem].append(event)
                
                if 'error' in event.get('level', '').lower():
                    errors.append(event)
                
                if 'decision' in event.get('action', ''):
                    decisions.append(event)
        except json.JSONDecodeError:
            # Plain text log line
            if 'ERROR' in line or 'FAIL' in line:
                errors.append({'message': line, 'type': 'text'})
    
    # Generate summary
    print(f"\n=== GRACE Activity Summary (last {window} entries) ===\n")
    
    # Subsystem activity
    print("Activity by Subsystem:")
    for subsystem, events in sorted(events_by_subsystem.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  {subsystem}: {len(events)} events")
        
        # Sample recent action
        if events:
            recent = events[-1]
            action = recent.get('action', 'activity')
            timestamp = recent.get('timestamp', 'recent')
            print(f"    Latest: {action} at {timestamp}")
    
    print()
    
    # Errors
    if errors:
        print(f"Errors Detected: {len(errors)}")
        for err in errors[-5:]:
            if err.get('type') == 'text':
                print(f"  - {err['message'][:100]}")
            else:
                print(f"  - [{err.get('subsystem', 'unknown')}] {err.get('message', 'error')}")
        print()
    
    # Autonomous decisions
    if decisions:
        print(f"Autonomous Decisions: {len(decisions)}")
        for dec in decisions[-5:]:
            actor = dec.get('actor', 'grace')
            action = dec.get('action', 'decision')
            resource = dec.get('resource', 'system')
            print(f"  - {actor} decided to {action} on {resource}")
        print()
    
    # Overall assessment
    total_events = sum(len(e) for e in events_by_subsystem.values())
    active_subsystems = len(events_by_subsystem)
    
    print(f"Summary:")
    print(f"  Total events: {total_events}")
    print(f"  Active subsystems: {active_subsystems}")
    print(f"  Errors: {len(errors)}")
    print(f"  Autonomous decisions: {len(decisions)}")
    
    if len(errors) > 10:
        print(f"  Status: HIGH ERROR RATE - needs attention")
    elif len(errors) > 0:
        print(f"  Status: OPERATIONAL with warnings")
    else:
        print(f"  Status: HEALTHY")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Summarize GRACE logs in plain English')
    parser.add_argument('--input', default='logs/backend.log', help='Log file to summarize')
    parser.add_argument('--window', type=int, default=50, help='Number of recent entries to analyze')
    
    args = parser.parse_args()
    
    summarize_logs(args.input, args.window)
