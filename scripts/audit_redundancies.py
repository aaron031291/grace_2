"""
Redundancy Audit Script
Identifies all code that needs cleanup after integrating the six production systems
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


class RedundancyAuditor:
    """Scans codebase for redundant patterns after system integration"""
    
    def __init__(self, backend_path: Path = None):
        self.backend = backend_path or Path('backend/')
        self.redundancies = defaultdict(list)
        self.stats = defaultdict(int)
    
    def audit_all(self) -> Dict[str, List[str]]:
        """Run all audits and return results"""
        
        print("=" * 80)
        print("REDUNDANCY AUDIT - Post-Integration Cleanup")
        print("=" * 80)
        print()
        
        self.audit_event_publishing()
        self.audit_governance_checks()
        self.audit_file_logging()
        self.audit_healing_triggers()
        self.audit_mode_flags()
        self.audit_duplicate_imports()
        
        self.print_report()
        self.save_report()
        
        return dict(self.redundancies)
    
    def audit_event_publishing(self):
        """Find direct event bus publishes that should use trigger mesh"""
        
        print("[1/6] Auditing event publishing...")
        
        patterns = [
            (r'event_bus\.publish\(', 'event_bus.publish'),
            (r'message_bus\.publish\(', 'message_bus.publish'),
            (r'domain_event_bus\.publish\(', 'domain_event_bus.publish'),
        ]
        
        for py_file in self.backend.rglob('*.py'):
            # Skip event bus files themselves
            if 'event_bus.py' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern, name in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.redundancies['direct_event_publish'].append(
                            f"{py_file}:{line_num} - {name}"
                        )
                        self.stats['direct_event_publish'] += 1
            
            except Exception as e:
                pass
        
        print(f"  Found {self.stats['direct_event_publish']} direct event publishes")
    
    def audit_governance_checks(self):
        """Find direct governance checks that should use governance gate"""
        
        print("[2/6] Auditing governance checks...")
        
        patterns = [
            r'governance_engine\.check\(',
            r'governance\.check_policy\(',
            r'await.*governance.*check.*\(',
        ]
        
        for py_file in self.backend.rglob('*.py'):
            # Skip governance system files
            if 'governance_system' in str(py_file) or 'governance_gate.py' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.redundancies['direct_governance'].append(
                            f"{py_file}:{line_num}"
                        )
                        self.stats['direct_governance'] += 1
            
            except Exception as e:
                pass
        
        # Deduplicate
        self.redundancies['direct_governance'] = list(set(self.redundancies['direct_governance']))
        self.stats['direct_governance'] = len(self.redundancies['direct_governance'])
        
        print(f"  Found {self.stats['direct_governance']} direct governance checks")
    
    def audit_file_logging(self):
        """Find direct file logging that should use immutable log"""
        
        print("[3/6] Auditing file logging...")
        
        patterns = [
            (r"with open\([^)]*log[^)]*['\"]a['\"]", "append to log file"),
            (r"audit.*\.append\(", "audit.append()"),
            (r"json\.dump\([^)]*log", "json dump to log"),
        ]
        
        for py_file in self.backend.rglob('*.py'):
            # Skip immutable log files and log services
            if 'immutable_log.py' in str(py_file) or 'log_service.py' in str(py_file):
                continue
            
            # Skip guardian incident logs (operational, not audit)
            if 'guardian/incident_log.py' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern, desc in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.redundancies['file_logging'].append(
                            f"{py_file}:{line_num} - {desc}"
                        )
                        self.stats['file_logging'] += 1
            
            except Exception as e:
                pass
        
        print(f"  Found {self.stats['file_logging']} file logging instances")
    
    def audit_healing_triggers(self):
        """Find direct healing calls that should emit events to AVN"""
        
        print("[4/6] Auditing healing triggers...")
        
        patterns = [
            r'healing_orchestrator\.execute_playbook\(',
            r'playbook_engine\.execute\(',
            r'self_heal.*\.run\(',
        ]
        
        for py_file in self.backend.rglob('*.py'):
            # Skip AVN/healing core files
            if 'immune_kernel.py' in str(py_file) or 'healing_orchestrator.py' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.redundancies['direct_healing'].append(
                            f"{py_file}:{line_num}"
                        )
                        self.stats['direct_healing'] += 1
            
            except Exception as e:
                pass
        
        print(f"  Found {self.stats['direct_healing']} direct healing calls")
    
    def audit_mode_flags(self):
        """Find local mode flags that should use consciousness state"""
        
        print("[5/6] Auditing mode flags...")
        
        patterns = [
            (r'self\.mode\s*=', 'self.mode assignment'),
            (r'learning_mode\s*=\s*True', 'learning_mode flag'),
            (r'exploration_mode', 'exploration_mode flag'),
        ]
        
        for py_file in self.backend.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern, desc in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.redundancies['mode_flags'].append(
                            f"{py_file}:{line_num} - {desc}"
                        )
                        self.stats['mode_flags'] += 1
            
            except Exception as e:
                pass
        
        print(f"  Found {self.stats['mode_flags']} mode flags")
    
    def audit_duplicate_imports(self):
        """Find duplicate trigger mesh imports"""
        
        print("[6/6] Auditing duplicate imports...")
        
        for py_file in self.backend.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check for both trigger mesh imports
                has_simple = 'from backend.misc.trigger_mesh import' in content
                has_enhanced = 'from backend.routing.trigger_mesh_enhanced import' in content
                
                if has_simple and has_enhanced:
                    self.redundancies['duplicate_imports'].append(str(py_file))
                    self.stats['duplicate_imports'] += 1
            
            except Exception as e:
                pass
        
        print(f"  Found {self.stats['duplicate_imports']} files with duplicate imports")
    
    def print_report(self):
        """Print comprehensive report"""
        
        print()
        print("=" * 80)
        print("AUDIT RESULTS")
        print("=" * 80)
        print()
        
        total_issues = sum(self.stats.values())
        
        print(f"Total redundancies found: {total_issues}")
        print()
        
        # Summary by category
        categories = [
            ('direct_event_publish', 'Direct Event Publishes', 'P4'),
            ('direct_governance', 'Direct Governance Checks', 'P1'),
            ('file_logging', 'File-Based Logging', 'P2'),
            ('direct_healing', 'Direct Healing Calls', 'P3'),
            ('mode_flags', 'Local Mode Flags', 'P5'),
            ('duplicate_imports', 'Duplicate Imports', 'P0'),
        ]
        
        for key, name, priority in categories:
            count = self.stats.get(key, 0)
            if count > 0:
                print(f"{priority} - {name}: {count}")
                
                # Show top 5 examples
                examples = self.redundancies.get(key, [])[:5]
                for ex in examples:
                    print(f"      {ex}")
                
                if len(self.redundancies.get(key, [])) > 5:
                    print(f"      ... and {len(self.redundancies[key]) - 5} more")
                print()
        
        # Recommendations
        print()
        print("RECOMMENDED CLEANUP ORDER:")
        print("-" * 80)
        print("1. Phase 0: Bridge event bus to trigger mesh (1 file)")
        print(f"2. Phase 1: Refactor governance checks ({self.stats.get('direct_governance', 0)} files)")
        print(f"3. Phase 2: Consolidate logging ({self.stats.get('file_logging', 0)} files)")
        print(f"4. Phase 3: Consolidate healing ({self.stats.get('direct_healing', 0)} files)")
        print(f"5. Phase 4: Clean up event publishes ({self.stats.get('direct_event_publish', 0)} files)")
        print(f"6. Phase 5: Remove mode flags ({self.stats.get('mode_flags', 0)} files)")
        print()
    
    def save_report(self):
        """Save detailed report to file"""
        
        report_path = Path('REDUNDANCY_AUDIT_REPORT.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Redundancy Audit Report\n\n")
            f.write(f"Generated: {Path.cwd()}\n\n")
            f.write(f"Total redundancies: {sum(self.stats.values())}\n\n")
            
            f.write("## Summary\n\n")
            for category, count in self.stats.items():
                f.write(f"- **{category}**: {count} instances\n")
            
            f.write("\n## Detailed Findings\n\n")
            
            for category, files in self.redundancies.items():
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                f.write(f"Found {len(files)} instances:\n\n")
                
                for item in files:
                    f.write(f"- `{item}`\n")
                
                f.write("\n")
        
        print(f"Detailed report saved to: {report_path}")


if __name__ == '__main__':
    auditor = RedundancyAuditor()
    results = auditor.audit_all()
