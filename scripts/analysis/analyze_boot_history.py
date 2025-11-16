"""
Analyze boot history and generate improvement recommendations
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.boot_learning_system import boot_learning

def main():
    print("\n" + "="*80)
    print("BOOT HISTORY ANALYSIS")
    print("="*80)
    print()
    
    # Get boot health score
    health = boot_learning.get_boot_health_score()
    
    print("BOOT HEALTH SCORE")
    print("-" * 40)
    print(f"  Score: {health.get('score', 'unknown').upper()}")
    print(f"  Success Rate: {health.get('success_rate', 'N/A')}")
    print(f"  Avg Issues/Boot: {health.get('avg_issues_per_boot', 'N/A')}")
    print(f"  Boots Analyzed: {health.get('boots_analyzed', 0)}")
    print(f"  Trend: {health.get('trend', 'unknown')}")
    print()
    
    # Get patterns
    patterns = boot_learning.patterns
    
    print("KNOWN FAILURE PATTERNS")
    print("-" * 40)
    print(f"  Total Incidents: {len(patterns.get('incidents', []))}")
    print()
    
    for incident in patterns.get("incidents", []):
        occurrences = incident.get("occurrences", 1)
        print(f"  [{incident['id']}]")
        print(f"    Pattern: {incident['pattern'][:60]}...")
        print(f"    Occurrences: {occurrences}")
        print(f"    Playbook: {incident['fix']['playbook']}")
        print(f"    Risk: {incident['fix']['risk_level']} | Tier: {incident['fix']['autonomy_tier']}")
        print()
    
    # Get improvement suggestions
    print("IMPROVEMENT SUGGESTIONS")
    print("-" * 40)
    
    suggestions = boot_learning.suggest_improvements()
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    else:
        print("  No improvements needed - boot pipeline is healthy!")
    
    print()
    print("="*80)
    print()
    
    # Analyze latest boot if available
    boot_logs = sorted((Path(__file__).parent.parent / "grace_training" / "startup_failures").glob("boot_*.json"))
    
    if boot_logs:
        latest_boot = boot_logs[-1]
        print(f"ANALYZING LATEST BOOT: {latest_boot.name}")
        print("-" * 40)
        
        analysis = boot_learning.analyze_boot_session(latest_boot)
        
        print(f"  Boot ID: {analysis.get('boot_id', 'unknown')}")
        print(f"  Success: {analysis.get('success', False)}")
        print(f"  New Patterns: {analysis.get('new_patterns_found', 0)}")
        print(f"  Known Patterns: {analysis.get('known_patterns_seen', 0)}")
        print(f"  Playbooks Auto-Generated: {analysis.get('playbooks_auto_generated', 0)}")
        print()
        
        if analysis.get("recommendations"):
            print("  Recommendations:")
            for rec in analysis["recommendations"]:
                print(f"    - {rec}")
        
        print()
        print("="*80)

if __name__ == "__main__":
    main()
