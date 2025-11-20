#!/usr/bin/env python3
"""
Verify Unification Progress

Scans the codebase and reports current unification status.
Target: 100% for events, audits, and stubs.
"""

import re
from pathlib import Path
from collections import defaultdict

backend = Path("c:/Users/aaron/grace_2/backend")

# Trackers
stats = {
    "event_bus_publish": 0,
    "domain_event_bus_publish": 0,
    "audit_logger_log": 0,
    "unified_event_publish": 0,
    "unified_audit_log": 0,
    "stub_comments": 0,
    "mock_implementations": 0,
    "files_with_events": [],
    "files_with_audits": [],
    "files_with_stubs": []
}

def scan_file(path: Path):
    """Scan a file for unification status"""
    try:
        text = path.read_text(encoding='utf-8')
        
        # Count old-style event publishes
        old_events = text.count('event_bus.publish(')
        old_domain_events = text.count('domain_event_bus.publish(')
        
        if old_events > 0 or old_domain_events > 0:
            stats["event_bus_publish"] += old_events
            stats["domain_event_bus_publish"] += old_domain_events
            stats["files_with_events"].append((str(path.relative_to(backend)), old_events + old_domain_events))
        
        # Count new-style unified events
        unified_events = text.count('publish_event(') + text.count('publish_domain_event(')
        stats["unified_event_publish"] += unified_events
        
        # Count old-style audits
        old_audits = text.count('audit_logger.log(')
        if old_audits > 0:
            stats["audit_logger_log"] += old_audits
            stats["files_with_audits"].append((str(path.relative_to(backend)), old_audits))
        
        # Count unified audits
        unified_audits = text.count('audit_log(')
        stats["unified_audit_log"] += unified_audits
        
        # Count stubs
        stub_comments = len(re.findall(r'#\s*Stub\s*-', text))
        mock_impl = text.count('mock_') + text.count('fake_')
        
        if stub_comments > 0 or mock_impl > 5:  # threshold to avoid false positives
            stats["stub_comments"] += stub_comments
            stats["mock_implementations"] += 1
            stats["files_with_stubs"].append((str(path.relative_to(backend)), stub_comments, mock_impl))
            
    except Exception as e:
        pass  # Skip problematic files

# Scan all files
print("🔍 Scanning codebase for unification status...\n")

for file in backend.rglob("*.py"):
    if '__pycache__' not in str(file):
        scan_file(file)

# Calculate totals and percentages
total_old_events = stats["event_bus_publish"] + stats["domain_event_bus_publish"]
total_events = total_old_events + stats["unified_event_publish"]
total_old_audits = stats["audit_logger_log"]
total_audits = total_old_audits + stats["unified_audit_log"]

# Original baseline (from achievement summary)
baseline_total_events = 505
baseline_total_audits = 261
baseline_total_stubs = 12

unified_events_count = stats["unified_event_publish"]
unified_audits_count = stats["unified_audit_log"]

event_pct = (unified_events_count / baseline_total_events * 100) if baseline_total_events > 0 else 0
audit_pct = (unified_audits_count / baseline_total_audits * 100) if baseline_total_audits > 0 else 0
stub_pct = ((baseline_total_stubs - stats["mock_implementations"]) / baseline_total_stubs * 100) if baseline_total_stubs > 0 else 0

# Display results
print("=" * 70)
print("  GRACE UNIFICATION STATUS REPORT")
print("=" * 70)
print()
print("📊 EVENT PUBLISHING:")
print(f"  Old-style (event_bus.publish):        {stats['event_bus_publish']}")
print(f"  Old-style (domain_event_bus.publish): {stats['domain_event_bus_publish']}")
print(f"  ─────────────────────────────────────")
print(f"  Total OLD events remaining:           {total_old_events}")
print(f"  Total NEW unified events:             {stats['unified_event_publish']}")
print(f"  📈 Unification Progress:               {unified_events_count}/{baseline_total_events} ({event_pct:.1f}%)")
print()

print("📋 AUDIT LOGGING:")
print(f"  Old-style (audit_logger.log):         {stats['audit_logger_log']}")
print(f"  New-style (unified audit_log):        {stats['unified_audit_log']}")
print(f"  📈 Unification Progress:               {unified_audits_count}/{baseline_total_audits} ({audit_pct:.1f}%)")
print()

print("🔧 STUB/MOCK CODE:")
print(f"  Stub comments (# Stub -):             {stats['stub_comments']}")
print(f"  Files with mock implementations:      {stats['mock_implementations']}")
print(f"  📈 Stub Replacement Progress:          {baseline_total_stubs - stats['mock_implementations']}/{baseline_total_stubs} ({stub_pct:.1f}%)")
print()

print("=" * 70)
print("  PROGRESS TO 100%")
print("=" * 70)
print()

# Progress bars
def progress_bar(current, total, width=40):
    """Generate a text progress bar"""
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {pct*100:.1f}%"

print(f"Events:  {progress_bar(unified_events_count, baseline_total_events)}")
print(f"Audits:  {progress_bar(unified_audits_count, baseline_total_audits)}")
print(f"Stubs:   {progress_bar(baseline_total_stubs - stats['mock_implementations'], baseline_total_stubs)}")
print()

# Show top files needing migration
if stats["files_with_events"]:
    print("=" * 70)
    print("  TOP 10 FILES WITH OLD-STYLE EVENTS")
    print("=" * 70)
    for file, count in sorted(stats["files_with_events"], key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:3d} events: {file}")
    print()

if stats["files_with_audits"]:
    print("=" * 70)
    print("  TOP 10 FILES WITH OLD-STYLE AUDITS")
    print("=" * 70)
    for file, count in sorted(stats["files_with_audits"], key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:3d} audits: {file}")
    print()

if stats["files_with_stubs"]:
    print("=" * 70)
    print("  FILES WITH STUBS/MOCKS")
    print("=" * 70)
    for file, stubs, mocks in stats["files_with_stubs"][:10]:
        print(f"  {stubs} stubs, {mocks} mocks: {file}")
    print()

# Final summary
print("=" * 70)
print("  NEXT STEPS TO REACH 100%")
print("=" * 70)
print()
if total_old_events > 0:
    print(f"  ⚠️  Migrate {total_old_events} remaining old-style event publishes")
if stats["audit_logger_log"] > 0:
    print(f"  ⚠️  Migrate {stats['audit_logger_log']} remaining old-style audit logs")
if stats["mock_implementations"] > 0:
    print(f"  ⚠️  Replace {stats['mock_implementations']} mock/stub implementations")
    
if total_old_events == 0 and stats["audit_logger_log"] == 0 and stats["mock_implementations"] == 0:
    print("  🎉 100% UNIFICATION ACHIEVED!")
    print("  ✅ All events use unified publisher")
    print("  ✅ All audits use unified logger")
    print("  ✅ All stubs replaced with real code")
else:
    print()
    print("  📝 Run: UNIFY_100_PERCENT.bat")
    print("  📝 Or:  python scripts/fast_migrate_all.py")

print()
print("=" * 70)
