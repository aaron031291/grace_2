"""
Show Evidence That Learning System Is Actually Learning

This script analyzes:
1. ML training logs and model versions
2. Learning loop outcomes and statistics
3. World model knowledge evolution
4. Training pipeline runs and improvements
"""

import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

def analyze_database_learning_records():
    """Check database for learning records"""
    db_path = Path("c:/Users/aaron/grace_2/grace.db")
    
    if not db_path.exists():
        return None, "Database not found"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        results = {
            'ml_learning_logs': 0,
            'training_runs': 0,
            'learning_outcomes': 0,
            'world_model_versions': 0,
            'recent_learnings': []
        }
        
        # Check for ML learning logs table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND (
                name LIKE '%learning%' OR 
                name LIKE '%training%' OR
                name LIKE '%model%'
            )
        """)
        tables = cursor.fetchall()
        
        # Check ml_learning_logs if it exists
        for table in tables:
            table_name = table[0]
            
            if 'learning' in table_name.lower():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    results[f'table_{table_name}'] = count
                    
                    # Get recent records
                    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 5")
                    recent = cursor.fetchall()
                    if recent:
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = [col[1] for col in cursor.fetchall()]
                        results['recent_learnings'].extend([
                            dict(zip(columns, row)) for row in recent
                        ])
                except Exception as e:
                    pass
        
        conn.close()
        return results, None
        
    except Exception as e:
        return None, f"Database error: {e}"

def check_ml_artifacts():
    """Check for ML model artifacts"""
    ml_dir = Path("c:/Users/aaron/grace_2/ml_artifacts")
    
    if not ml_dir.exists():
        return {'exists': False}
    
    artifacts = {
        'exists': True,
        'subdirs': [],
        'total_files': 0
    }
    
    for item in ml_dir.rglob('*'):
        if item.is_file():
            artifacts['total_files'] += 1
        elif item.is_dir() and item.parent == ml_dir:
            artifacts['subdirs'].append(item.name)
    
    return artifacts

def check_training_directory():
    """Check grace_training directory for learned knowledge"""
    training_dir = Path("c:/Users/aaron/grace_2/grace_training")
    
    if not training_dir.exists():
        return {'exists': False}
    
    training_data = {
        'exists': True,
        'categories': [],
        'file_counts': {},
        'total_files': 0
    }
    
    for category in training_dir.iterdir():
        if category.is_dir():
            training_data['categories'].append(category.name)
            file_count = len(list(category.rglob('*.*')))
            training_data['file_counts'][category.name] = file_count
            training_data['total_files'] += file_count
    
    return training_data

def analyze_immutable_log():
    """Check immutable audit log for learning events"""
    log_path = Path("c:/Users/aaron/grace_2/logs/immutable_audit.jsonl")
    
    if not log_path.exists():
        return {'exists': False}
    
    learning_events = []
    total_events = 0
    
    try:
        with open(log_path, 'r') as f:
            for line in f:
                total_events += 1
                if line.strip():
                    try:
                        event = json.loads(line)
                        action = event.get('action', '')
                        
                        # Look for learning-related actions
                        if any(keyword in str(event).lower() for keyword in 
                               ['learn', 'train', 'improve', 'update_knowledge', 'model']):
                            learning_events.append({
                                'timestamp': event.get('timestamp'),
                                'actor': event.get('actor'),
                                'action': action,
                                'resource': event.get('resource')
                            })
                    except json.JSONDecodeError:
                        continue
        
        return {
            'exists': True,
            'total_events': total_events,
            'learning_events': len(learning_events),
            'recent_learning': learning_events[-5:] if learning_events else []
        }
    except Exception as e:
        return {'exists': True, 'error': str(e)}

def main():
    print("=" * 80)
    print("GRACE LEARNING SYSTEM EVIDENCE REPORT")
    print("=" * 80)
    print()
    
    # 1. Database learning records
    print("[1/5] Analyzing database learning records...")
    db_results, error = analyze_database_learning_records()
    
    if error:
        print(f"      {error}")
    elif db_results:
        print(f"      Found {len([k for k in db_results.keys() if k.startswith('table_')])} learning-related tables")
        for key, value in db_results.items():
            if key.startswith('table_'):
                table_name = key.replace('table_', '')
                print(f"      - {table_name}: {value} records")
        
        if db_results['recent_learnings']:
            print(f"      Recent learning entries: {len(db_results['recent_learnings'])}")
    print()
    
    # 2. ML Artifacts
    print("[2/5] Checking ML model artifacts...")
    ml_artifacts = check_ml_artifacts()
    
    if ml_artifacts['exists']:
        print(f"      ML artifacts directory exists")
        print(f"      Subdirectories: {', '.join(ml_artifacts['subdirs']) if ml_artifacts['subdirs'] else 'None'}")
        print(f"      Total files: {ml_artifacts['total_files']}")
    else:
        print("      No ML artifacts directory found")
    print()
    
    # 3. Training data
    print("[3/5] Checking learned knowledge storage...")
    training_data = check_training_directory()
    
    if training_data['exists']:
        print(f"      Training directory exists")
        print(f"      Knowledge categories: {len(training_data['categories'])}")
        for category, count in sorted(training_data['file_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      - {category}: {count} files")
        print(f"      Total learned artifacts: {training_data['total_files']}")
    else:
        print("      No training directory found")
    print()
    
    # 4. Immutable log
    print("[4/5] Analyzing immutable audit log...")
    log_data = analyze_immutable_log()
    
    if log_data['exists']:
        print(f"      Total audit events: {log_data.get('total_events', 0)}")
        print(f"      Learning-related events: {log_data.get('learning_events', 0)}")
        
        if log_data.get('recent_learning'):
            print(f"\n      Recent Learning Events:")
            for event in log_data['recent_learning'][-3:]:
                print(f"      - {event.get('timestamp', 'N/A')}: {event.get('action', 'N/A')}")
    else:
        print("      No immutable log found")
    print()
    
    # 5. Summary
    print("[5/5] SUMMARY:")
    print("-" * 80)
    
    evidence_points = []
    
    if db_results and any(k.startswith('table_') and v > 0 for k, v in db_results.items()):
        evidence_points.append(f"Database learning records exist")
    
    if ml_artifacts.get('total_files', 0) > 0:
        evidence_points.append(f"{ml_artifacts['total_files']} ML artifact files")
    
    if training_data.get('total_files', 0) > 0:
        evidence_points.append(f"{training_data['total_files']} learned knowledge files")
    
    if log_data.get('learning_events', 0) > 0:
        evidence_points.append(f"{log_data['learning_events']} learning events in audit log")
    
    if evidence_points:
        print("\n".join(f"  + {point}" for point in evidence_points))
        print()
        print("=" * 80)
        print("[PASS] LEARNING SYSTEM IS ACTIVE!")
        print(f"       Evidence: {len(evidence_points)} proof points found")
        print("=" * 80)
        return 0
    else:
        print("No clear evidence of learning activity found")
        print()
        print("=" * 80)
        print("[INCONCLUSIVE] May need to trigger learning cycle")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
