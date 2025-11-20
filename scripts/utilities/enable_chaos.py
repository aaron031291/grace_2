"""
Enable Chaos Engineering
Configures Grace to allow chaos campaigns

Default: DISABLED (safe)
Run this script to enable chaos testing
"""

import sys
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def enable_chaos():
    """Enable chaos engineering campaigns"""
    
    print()
    print("=" * 80)
    print("ENABLE CHAOS ENGINEERING")
    print("=" * 80)
    print()
    
    print("Chaos engineering allows Grace to:")
    print("  • Red-team components with domain-specific attacks")
    print("  • Verify guardrails (rate limits, auth, validation)")
    print("  • Test resilience (OWASP, load, config chaos)")
    print("  • Auto-raise healing tasks for failures")
    print("  • Feed results to learning loop")
    print()
    print("Safety controls:")
    print("  • Default environment: staging (not production)")
    print("  • Governance approval required")
    print("  • RBAC permissions enforced")
    print("  • Guardian can halt instantly")
    print("  • All actions logged to immutable log")
    print()
    print("=" * 80)
    
    response = input("\nEnable chaos engineering? (y/N): ").strip().lower()
    
    if response != 'y':
        print("Cancelled")
        return
    
    print()
    print("Chaos engineering configuration:")
    print()
    
    # Environment
    env = input("Environment (staging/shadow/production) [staging]: ").strip() or 'staging'
    
    if env not in ['staging', 'shadow', 'production']:
        print(f"Invalid environment: {env}")
        return
    
    # Auto-run
    auto_run_response = input("Enable auto-run? (y/N) [N]: ").strip().lower()
    auto_run = auto_run_response == 'y'
    
    # Blast radius
    blast_radius = input("Max components per campaign [3]: ").strip() or '3'
    try:
        blast_radius = int(blast_radius)
    except:
        blast_radius = 3
    
    print()
    print("=" * 80)
    print("CONFIGURATION")
    print("=" * 80)
    print(f"Environment: {env}")
    print(f"Auto-run: {auto_run}")
    print(f"Blast radius: {blast_radius} components")
    print()
    
    # Create config file
    config = {
        'chaos_enabled': True,
        'environment': env,
        'auto_run': auto_run,
        'blast_radius_limit': blast_radius,
        'enabled_at': datetime.now().isoformat()
    }
    
    config_path = Path('config/chaos_config.json')
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    from datetime import datetime
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to: {config_path}")
    print()
    
    # Show how to use
    print("=" * 80)
    print("USAGE")
    print("=" * 80)
    print()
    print("Start Grace normally:")
    print("  python server.py")
    print()
    print("Run a chaos campaign via API:")
    print("  POST http://localhost:8000/api/chaos/run")
    print("  {")
    print('    "environment": "staging",')
    print('    "approved_by": "admin"')
    print("  }")
    print()
    print("Monitor campaigns:")
    print("  GET http://localhost:8000/api/chaos/dashboard")
    print()
    print("Emergency halt:")
    print("  POST http://localhost:8000/api/chaos/halt")
    print()
    print("View resilience rankings:")
    print("  GET http://localhost:8000/api/chaos/resilience")
    print()
    print("=" * 80)
    print("CHAOS ENGINEERING ENABLED")
    print("=" * 80)
    print()


if __name__ == "__main__":
    enable_chaos()
