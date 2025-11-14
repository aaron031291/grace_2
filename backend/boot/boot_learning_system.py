"""
Boot Learning System
Captures every boot failure, analyzes patterns, generates playbooks automatically
Ensures failures only happen once
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import sqlite3
import re


class BootLearningSystem:
    """Learns from boot failures and prevents recurrence"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.training_dir = self.project_root / "grace_training" / "startup_failures"
        self.training_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.training_dir / "_metadata.json"
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, Any]:
        """Load known failure patterns"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {
            "training_set": "startup_failures",
            "version": "1.0.0",
            "incidents": []
        }
    
    def _save_patterns(self):
        """Save updated patterns"""
        with open(self.metadata_file, "w") as f:
            json.dump(self.patterns, f, indent=2)
    
    def record_failure(
        self,
        stage: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a boot failure and analyze if it's a new pattern
        
        Returns:
            - incident_id: Unique ID for this incident
            - is_new_pattern: Whether this is a new failure type
            - suggested_playbook: Auto-generated playbook if pattern recognized
        """
        
        # Generate incident signature
        signature = self._generate_signature(error_message)
        
        # Check if pattern exists
        existing_incident = self._find_matching_pattern(error_message)
        
        if existing_incident:
            # Known pattern - increment occurrence count
            existing_incident["occurrences"] = existing_incident.get("occurrences", 1) + 1
            existing_incident["last_seen"] = datetime.now().isoformat()
            self._save_patterns()
            
            return {
                "incident_id": existing_incident["id"],
                "is_new_pattern": False,
                "suggested_playbook": existing_incident.get("fix", {}).get("playbook"),
                "existing_fix": existing_incident.get("fix")
            }
        
        else:
            # New pattern - analyze and create incident
            incident = self._analyze_new_failure(
                stage=stage,
                error_message=error_message,
                signature=signature,
                stack_trace=stack_trace,
                context=context
            )
            
            self.patterns["incidents"].append(incident)
            self._save_patterns()
            
            return {
                "incident_id": incident["id"],
                "is_new_pattern": True,
                "suggested_playbook": incident.get("fix", {}).get("playbook"),
                "incident": incident
            }
    
    def _generate_signature(self, error_message: str) -> str:
        """Generate unique signature for error"""
        # Normalize error message (remove dynamic parts like timestamps, IDs)
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}', 'DATE', error_message)
        normalized = re.sub(r'\d+', 'NUM', normalized)
        normalized = re.sub(r'[a-f0-9]{8,}', 'HASH', normalized)
        
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _find_matching_pattern(self, error_message: str) -> Optional[Dict[str, Any]]:
        """Find if error matches known pattern"""
        
        for incident in self.patterns.get("incidents", []):
            pattern = incident.get("pattern", "")
            
            # Check if pattern matches
            if pattern in error_message:
                return incident
            
            # Check similarity by signature
            if incident.get("signature") == self._generate_signature(error_message):
                return incident
        
        return None
    
    def _analyze_new_failure(
        self,
        stage: str,
        error_message: str,
        signature: str,
        stack_trace: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze new failure and suggest fix"""
        
        incident_id = f"{stage.lower().replace(' ', '_')}_{signature}"
        
        # Pattern detection and auto-fix generation
        playbook_name = None
        fix_steps = []
        risk_level = "medium"
        autonomy_tier = "tier_2"
        
        # 1. Metrics catalog missing
        if "cannot import name 'load_metrics_catalog'" in error_message:
            playbook_name = "create_metrics_catalog_loader"
            fix_steps = [
                "Create backend/metrics_catalog_loader.py",
                "Implement load_metrics_catalog() function",
                "Create config/metrics_catalog.json with domains",
                "Add eager-loaded metrics_catalog object"
            ]
            risk_level = "low"
            autonomy_tier = "tier_1"
        
        # 2. Missing database column
        elif "has no attribute" in error_message or "missing" in error_message.lower():
            playbook_name = "apply_schema_migration"
            fix_steps = [
                "Run alembic upgrade head",
                "Verify column exists via PRAGMA table_info",
                "Restart affected services"
            ]
            risk_level = "medium"
            autonomy_tier = "tier_2"
        
        # 3. UTF-8 encoding errors
        elif "UnicodeEncodeError" in error_message or "charmap" in error_message:
            playbook_name = "fix_unicode_encoding"
            fix_steps = [
                "sys.stdout.reconfigure(encoding='utf-8')",
                "sys.stderr.reconfigure(encoding='utf-8')",
                "Set PYTHONIOENCODING=utf-8",
                "Run chcp 65001 in PowerShell"
            ]
            risk_level = "low"
            autonomy_tier = "tier_1"
        
        # 4. Circular import
        elif "partially initialized module" in error_message or "circular import" in error_message.lower():
            playbook_name = "fix_circular_import"
            fix_steps = [
                "Identify import cycle from stack trace",
                "Change one import to use base_models instead",
                "Verify import succeeds",
                "Check for other circular dependencies"
            ]
            risk_level = "high"
            autonomy_tier = "tier_3"
        
        # 5. Database locked
        elif "database is locked" in error_message.lower():
            playbook_name = "unlock_database"
            fix_steps = [
                "Remove .db-shm file",
                "Remove .db-wal file",
                "Wait 500ms",
                "Retry connection"
            ]
            risk_level = "low"
            autonomy_tier = "tier_1"
        
        # 6. Missing secrets
        elif "KeyError" in error_message and ("SECRET" in error_message or "KEY" in error_message):
            playbook_name = "configure_missing_secrets"
            fix_steps = [
                "Identify missing secret from error",
                "Check .env.example for template",
                "Generate default value if safe",
                "Add to .env file"
            ]
            risk_level = "medium"
            autonomy_tier = "tier_2"
        
        # 7. Missing TypeScript tooling
        elif "WinError 2" in error_message or "npm" in error_message.lower():
            playbook_name = "skip_typescript_when_unavailable"
            fix_steps = [
                "Check if npm is installed",
                "Skip TypeScript scan if unavailable",
                "Log warning instead of error"
            ]
            risk_level = "low"
            autonomy_tier = "tier_1"
        
        # Generic fallback
        else:
            playbook_name = f"generic_fix_{signature}"
            fix_steps = ["Manual investigation required"]
            risk_level = "high"
            autonomy_tier = "tier_4"
        
        # Build incident record
        incident = {
            "id": incident_id,
            "signature": signature,
            "pattern": error_message[:200],  # First 200 chars as pattern
            "stage": stage,
            "root_cause": "Auto-detected from error pattern",
            "symptoms": [
                error_message,
                f"Occurs during {stage}",
            ],
            "fix": {
                "playbook": playbook_name,
                "steps": fix_steps,
                "risk_level": risk_level,
                "autonomy_tier": autonomy_tier
            },
            "verification": self._suggest_verification(playbook_name),
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "occurrences": 1,
            "auto_generated": True
        }
        
        if stack_trace:
            incident["stack_trace"] = stack_trace
        
        if context:
            incident["context"] = context
        
        return incident
    
    def _suggest_verification(self, playbook_name: str) -> str:
        """Suggest verification step for playbook"""
        
        verifications = {
            "create_metrics_catalog_loader": "from backend.metrics_catalog_loader import load_metrics_catalog succeeds",
            "apply_schema_migration": "Database column exists",
            "fix_unicode_encoding": "print('✅') succeeds without error",
            "fix_circular_import": "Import succeeds without partially initialized module error",
            "unlock_database": "Database connection succeeds",
            "configure_missing_secrets": "Environment variable is set",
            "skip_typescript_when_unavailable": "No WinError 2 when npm missing"
        }
        
        return verifications.get(playbook_name, "Manual verification required")
    
    def generate_playbook_code(self, incident_id: str) -> Optional[str]:
        """Generate executable playbook code from incident"""
        
        incident = next(
            (i for i in self.patterns["incidents"] if i["id"] == incident_id),
            None
        )
        
        if not incident:
            return None
        
        playbook_name = incident["fix"]["playbook"]
        steps = incident["fix"]["steps"]
        
        # Generate Python code for playbook
        code = f'''"""
Auto-generated playbook: {playbook_name}
Pattern: {incident["pattern"][:100]}
Risk: {incident["fix"]["risk_level"]}
Autonomy: {incident["fix"]["autonomy_tier"]}
"""

import sys
import os
from pathlib import Path

async def execute():
    """Execute playbook steps"""
    results = []
    
'''
        
        # Add step implementations based on playbook type
        if playbook_name == "fix_unicode_encoding":
            code += '''    # Step 1: Reconfigure stdout/stderr
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        results.append({"step": 1, "success": True, "message": "Reconfigured stdio"})
    except Exception as e:
        results.append({"step": 1, "success": False, "error": str(e)})
    
    # Step 2: Set environment variable
    os.environ["PYTHONIOENCODING"] = "utf-8"
    results.append({"step": 2, "success": True, "message": "Set PYTHONIOENCODING"})
    
'''
        
        elif playbook_name == "unlock_database":
            code += '''    # Step 1: Remove lock files
    db_path = Path("backend/grace.db")
    shm = db_path.parent / f"{db_path.name}-shm"
    wal = db_path.parent / f"{db_path.name}-wal"
    
    removed = []
    if shm.exists():
        shm.unlink()
        removed.append("shm")
    if wal.exists():
        wal.unlink()
        removed.append("wal")
    
    results.append({"step": 1, "success": True, "removed": removed})
    
    # Step 2: Wait for locks to clear
    import asyncio
    await asyncio.sleep(0.5)
    results.append({"step": 2, "success": True, "message": "Waited 500ms"})
    
'''
        
        else:
            # Generic implementation
            for i, step in enumerate(steps, 1):
                code += f'''    # Step {i}: {step}
    results.append({{"step": {i}, "success": False, "message": "Not implemented"}})
    
'''
        
        code += '''    return {
        "success": all(r.get("success", False) for r in results),
        "results": results
    }

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(execute())
    print(result)
'''
        
        return code
    
    def register_playbook_in_db(self, incident_id: str) -> bool:
        """Register playbook in database from incident"""
        
        incident = next(
            (i for i in self.patterns["incidents"] if i["id"] == incident_id),
            None
        )
        
        if not incident:
            return False
        
        try:
            db_path = self.project_root / "backend" / "grace.db"
            conn = sqlite3.connect(str(db_path))
            
            fix = incident["fix"]
            
            # Insert or update playbook
            conn.execute(
                """INSERT OR REPLACE INTO playbooks 
                   (name, description, risk_level, autonomy_tier, service, severity) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    fix["playbook"],
                    incident["pattern"][:200],
                    fix["risk_level"],
                    fix["autonomy_tier"],
                    "boot_pipeline",
                    "high" if fix["risk_level"] in ["high", "critical"] else "medium"
                )
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Could not register playbook: {e}")
            return False
    
    def analyze_boot_session(self, boot_log_path: Path) -> Dict[str, Any]:
        """Analyze complete boot session and extract learnings"""
        
        if not boot_log_path.exists():
            return {"error": "Boot log not found"}
        
        with open(boot_log_path, "r") as f:
            boot_data = json.load(f)
        
        analysis = {
            "boot_id": boot_data.get("boot_timestamp"),
            "success": boot_data.get("summary", {}).get("success", False),
            "new_patterns_found": 0,
            "known_patterns_seen": 0,
            "playbooks_auto_generated": 0,
            "recommendations": []
        }
        
        # Analyze each stage
        for stage in boot_data.get("stages", []):
            if not stage.get("success"):
                for issue in stage.get("issues", []):
                    result = self.record_failure(
                        stage=stage["stage"],
                        error_message=issue,
                        context=stage.get("metrics", {})
                    )
                    
                    if result["is_new_pattern"]:
                        analysis["new_patterns_found"] += 1
                        
                        # Auto-generate playbook
                        playbook_code = self.generate_playbook_code(result["incident_id"])
                        if playbook_code:
                            playbook_path = self.project_root / "backend" / "self_heal" / "playbooks" / f"{result['suggested_playbook']}.py"
                            playbook_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(playbook_path, "w") as f:
                                f.write(playbook_code)
                            
                            analysis["playbooks_auto_generated"] += 1
                            analysis["recommendations"].append(
                                f"New playbook created: {result['suggested_playbook']}"
                            )
                        
                        # Register in database
                        if self.register_playbook_in_db(result["incident_id"]):
                            analysis["recommendations"].append(
                                f"Playbook registered in database: {result['suggested_playbook']}"
                            )
                    else:
                        analysis["known_patterns_seen"] += 1
                        analysis["recommendations"].append(
                            f"Known issue: Use playbook {result['suggested_playbook']}"
                        )
        
        return analysis
    
    def get_boot_health_score(self) -> Dict[str, Any]:
        """Calculate overall boot health based on history"""
        
        boot_logs = sorted(self.training_dir.glob("boot_*.json"))
        
        if len(boot_logs) < 2:
            return {
                "score": "insufficient_data",
                "boots_analyzed": len(boot_logs)
            }
        
        recent_boots = boot_logs[-10:]  # Last 10 boots
        
        successes = 0
        total_issues = 0
        
        for boot_log in recent_boots:
            try:
                with open(boot_log) as f:
                    data = json.load(f)
                    if data.get("summary", {}).get("success"):
                        successes += 1
                    
                    for stage in data.get("stages", []):
                        total_issues += len(stage.get("issues", []))
            except:
                continue
        
        success_rate = successes / len(recent_boots) if recent_boots else 0
        avg_issues = total_issues / len(recent_boots) if recent_boots else 0
        
        # Calculate score
        if success_rate >= 0.9 and avg_issues <= 1:
            score = "excellent"
        elif success_rate >= 0.7 and avg_issues <= 3:
            score = "good"
        elif success_rate >= 0.5:
            score = "fair"
        else:
            score = "poor"
        
        return {
            "score": score,
            "success_rate": f"{success_rate:.1%}",
            "avg_issues_per_boot": round(avg_issues, 1),
            "boots_analyzed": len(recent_boots),
            "trend": "improving" if successes > len(recent_boots) / 2 else "needs_attention"
        }
    
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements to boot pipeline based on patterns"""
        
        suggestions = []
        
        # Analyze incident frequencies
        incident_freq = {}
        for incident in self.patterns.get("incidents", []):
            freq = incident.get("occurrences", 1)
            if freq > 1:
                incident_freq[incident["id"]] = freq
        
        # High-frequency issues should be prioritized
        for incident_id, freq in sorted(incident_freq.items(), key=lambda x: x[1], reverse=True):
            incident = next((i for i in self.patterns["incidents"] if i["id"] == incident_id), None)
            if incident and freq > 2:
                suggestions.append(
                    f"High priority: '{incident['pattern'][:50]}...' occurred {freq} times. "
                    f"Playbook '{incident['fix']['playbook']}' should be tier_1 auto-execute."
                )
        
        # Check for missing playbooks
        for incident in self.patterns["incidents"]:
            if not incident.get("fix", {}).get("playbook"):
                suggestions.append(
                    f"Missing playbook for: {incident['id']}"
                )
        
        return suggestions


# Global instance
boot_learning = BootLearningSystem()
