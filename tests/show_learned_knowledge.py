"""
Show What Grace Has Actually Learned

Analyzes concrete learning outcomes:
1. Configuration improvements made
2. Knowledge artifacts created
3. Model training completed
4. Specific changes implemented
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

def analyze_config_improvements():
    """Analyze configuration improvements from audit log"""
    log_file = Path("c:/Users/aaron/grace_2/logs/immutable_audit.jsonl")
    
    if not log_file.exists():
        return []
    
    config_updates = []
    
    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    event = json.loads(line)
                    
                    # Look for logic/config updates
                    if event.get('action') in ['logic_update_proposed', 'logic_update_distributed', 'config_update']:
                        decision = event.get('decision', {})
                        config_updates.append({
                            'timestamp': event.get('timestamp'),
                            'update_id': decision.get('update_id'),
                            'update_type': decision.get('update_type'),
                            'component': decision.get('component_targets', []),
                            'version': decision.get('version'),
                            'risk_level': decision.get('risk_level')
                        })
                except:
                    continue
    
    return config_updates

def analyze_knowledge_artifacts():
    """Check what knowledge has been stored"""
    training_dir = Path("c:/Users/aaron/grace_2/grace_training")
    
    if not training_dir.exists():
        return {}
    
    artifacts = defaultdict(list)
    
    for item in training_dir.rglob('*'):
        if item.is_file():
            category = item.parent.name
            artifacts[category].append({
                'file': item.name,
                'size': item.stat().st_size,
                'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
            })
    
    return dict(artifacts)

def analyze_model_artifacts():
    """Check ML model artifacts"""
    ml_dir = Path("c:/Users/aaron/grace_2/ml_artifacts")
    
    if not ml_dir.exists():
        return {}
    
    models = {}
    
    for model_dir in ml_dir.iterdir():
        if model_dir.is_dir():
            files = list(model_dir.rglob('*'))
            models[model_dir.name] = {
                'files': len([f for f in files if f.is_file()]),
                'total_size': sum(f.stat().st_size for f in files if f.is_file()),
                'last_modified': max(
                    (f.stat().st_mtime for f in files if f.is_file()),
                    default=0
                )
            }
    
    return models

def analyze_learning_outcomes():
    """Analyze specific learning outcomes from audit log"""
    log_file = Path("c:/Users/aaron/grace_2/logs/immutable_audit.jsonl")
    
    if not log_file.exists():
        return {}
    
    outcomes = {
        'system_starts': 0,
        'service_accounts_created': 0,
        'permissions_granted': 0,
        'logic_improvements': 0,
        'config_optimizations': 0
    }
    
    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    event = json.loads(line)
                    actor = event.get('actor', '')
                    action = event.get('action', '')
                    
                    if actor == 'continuous_learning_loop' and action == 'system_start':
                        outcomes['system_starts'] += 1
                    elif action == 'create_service_account':
                        outcomes['service_accounts_created'] += 1
                    elif 'permission' in action.lower():
                        outcomes['permissions_granted'] += 1
                    elif action == 'logic_update_proposed':
                        outcomes['logic_improvements'] += 1
                    elif action == 'logic_update_distributed':
                        outcomes['config_optimizations'] += 1
                except:
                    continue
    
    return outcomes

def main():
    print("=" * 80)
    print("WHAT GRACE HAS ACTUALLY LEARNED")
    print("=" * 80)
    print()
    
    # 1. Configuration Improvements
    print("[1/5] Configuration Improvements:")
    print("-" * 80)
    
    config_updates = analyze_config_improvements()
    
    if config_updates:
        # Group by component
        by_component = defaultdict(list)
        for update in config_updates:
            components = update.get('component', [])
            for comp in components:
                by_component[comp].append(update)
        
        print(f"Total configuration updates: {len(config_updates)}")
        print(f"\nUpdates by component:")
        for component, updates in sorted(by_component.items()):
            print(f"  {component}: {len(updates)} updates")
            
            # Show version progression
            versions = [u.get('version') for u in updates if u.get('version')]
            if versions:
                print(f"    Versions: {versions[0]} -> {versions[-1]}")
        
        # Show recent updates
        print(f"\nMost recent updates:")
        for update in config_updates[-5:]:
            print(f"  -> {update.get('timestamp', 'N/A')[:19]}")
            print(f"     Component: {', '.join(update.get('component', ['Unknown']))}")
            print(f"     Version: {update.get('version', 'N/A')}")
            print(f"     Risk: {update.get('risk_level', 'N/A')}")
    else:
        print("No configuration updates found")
    print()
    
    # 2. Knowledge Artifacts
    print("[2/5] Knowledge Artifacts:")
    print("-" * 80)
    
    artifacts = analyze_knowledge_artifacts()
    
    if artifacts:
        total_files = sum(len(files) for files in artifacts.values())
        total_size = sum(
            sum(f['size'] for f in files)
            for files in artifacts.values()
        )
        
        print(f"Total knowledge files: {total_files}")
        print(f"Total storage used: {total_size / 1024:.2f} KB")
        print(f"\nBy category:")
        for category, files in sorted(artifacts.items()):
            cat_size = sum(f['size'] for f in files)
            print(f"  {category}: {len(files)} files ({cat_size / 1024:.2f} KB)")
    else:
        print("No knowledge artifacts stored yet")
    print()
    
    # 3. ML Models
    print("[3/5] ML Model Artifacts:")
    print("-" * 80)
    
    models = analyze_model_artifacts()
    
    if models:
        for model_name, info in sorted(models.items()):
            print(f"\n  {model_name}:")
            print(f"    Files: {info['files']}")
            print(f"    Size: {info['total_size'] / 1024:.2f} KB")
            if info['last_modified']:
                mod_time = datetime.fromtimestamp(info['last_modified'])
                print(f"    Last modified: {mod_time.isoformat()}")
    else:
        print("No ML model artifacts yet")
    print()
    
    # 4. Learning Outcomes
    print("[4/5] Learning Outcomes Summary:")
    print("-" * 80)
    
    outcomes = analyze_learning_outcomes()
    
    print(f"  System restarts (learning loop): {outcomes['system_starts']}")
    print(f"  Service accounts created: {outcomes['service_accounts_created']}")
    print(f"  Permissions granted: {outcomes['permissions_granted']}")
    print(f"  Logic improvements proposed: {outcomes['logic_improvements']}")
    print(f"  Config optimizations deployed: {outcomes['config_optimizations']}")
    print()
    
    # 5. What She Learned
    print("[5/5] WHAT SHE LEARNED:")
    print("-" * 80)
    
    learned = []
    
    if config_updates:
        learned.append(f"[+] Improved {len(set(c for u in config_updates for c in u.get('component', [])))} system components")
        learned.append(f"[+] Applied {len(config_updates)} configuration optimizations")
    
    if outcomes['service_accounts_created'] > 0:
        learned.append(f"[+] Configured {outcomes['service_accounts_created']} service accounts for autonomy")
    
    if outcomes['config_optimizations'] > 0:
        learned.append(f"[+] Distributed {outcomes['config_optimizations']} config improvements to kernels")
    
    if artifacts:
        total_files = sum(len(files) for files in artifacts.values())
        learned.append(f"[+] Stored {total_files} knowledge artifacts")
    
    if models:
        learned.append(f"[+] Trained {len(models)} ML model(s)")
    
    if learned:
        print("\n".join(learned))
        print()
        print("=" * 80)
        print(f"[SUMMARY] Grace has made {len(learned)} types of learning progress")
        print("=" * 80)
        return 0
    else:
        print("Minimal learning artifacts found")
        print("This is normal for a new system - learning accumulates over time")
        print()
        print("=" * 80)
        print("[INFO] System is ready to learn as it operates")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
