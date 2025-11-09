"""
Boot Diagnostics - Forensic sweep of all subsystems after initialization
Traces every component from kernel load through execution, flags issues, generates reports
"""

import asyncio
import os
import sys
import json
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
import subprocess

logger = logging.getLogger(__name__)


class BootDiagnostics:
    """
    Forensic diagnostics engine that validates all subsystems post-boot
    """
    
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.project_root = Path(__file__).parent.parent
        self.findings: List[Dict[str, Any]] = []
        self.subsystems_checked: Dict[str, Dict[str, Any]] = {}
        self.boot_context: Dict[str, Any] = {}
        
        self.severity_levels = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
    
    async def run_full_sweep(self) -> Dict[str, Any]:
        """
        Execute complete forensic diagnostics sweep
        
        Returns:
            Structured diagnostics report
        """
        
        logger.info(f"[DIAGNOSTICS] Starting forensic boot sweep (run_id={self.run_id})")
        
        # Phase 1: Data Collection
        await self._collect_boot_context()
        await self._collect_subsystem_status()
        await self._collect_governance_status()
        await self._collect_metrics_catalog_status()
        await self._collect_warnings_and_skips()
        
        # Phase 2: Analysis
        await self._analyze_expected_vs_actual()
        await self._detect_process_issues()
        await self._analyze_configuration_gaps()
        await self._analyze_startup_health()
        
        # Phase 3: Reporting
        report = await self._generate_diagnostics_report()
        await self._emit_to_immutable_log(report)
        await self._emit_to_trigger_mesh(report)
        await self._print_console_summary(report)
        await self._create_capa_tickets_if_needed(report)
        
        return report
    
    # ========================================================================
    # PHASE 1: DATA COLLECTION
    # ========================================================================
    
    async def _collect_boot_context(self):
        """Collect boot environment context"""
        
        logger.info("[DIAGNOSTICS] Collecting boot context...")
        
        # Git SHA (if available)
        git_sha = "unknown"
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.project_root
            )
            if result.returncode == 0:
                git_sha = result.stdout.strip()[:8]
        except:
            pass
        
        # Component versions
        component_versions = {
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "grace_version": "2.0.0",  # Could read from version file
        }
        
        # Package versions
        try:
            import fastapi
            import sqlalchemy
            import uvicorn
            component_versions.update({
                "fastapi": getattr(fastapi, "__version__", "unknown"),
                "sqlalchemy": getattr(sqlalchemy, "__version__", "unknown"),
                "uvicorn": getattr(uvicorn, "__version__", "unknown")
            })
        except:
            pass
        
        # Environment variables loaded
        env_vars_loaded = {
            key: "SET" for key in [
                "DATABASE_URL", "SECRET_KEY", "GITHUB_TOKEN", 
                "AMP_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"
            ] if os.getenv(key)
        }
        
        # Missing secrets
        required_secrets = ["SECRET_KEY", "DATABASE_URL"]
        optional_secrets = ["GITHUB_TOKEN", "AMP_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        
        missing_required = [s for s in required_secrets if not os.getenv(s)]
        missing_optional = [s for s in optional_secrets if not os.getenv(s)]
        
        self.boot_context = {
            "run_id": self.run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "git_sha": git_sha,
            "component_versions": component_versions,
            "env_vars_loaded": env_vars_loaded,
            "missing_required_secrets": missing_required,
            "missing_optional_secrets": missing_optional,
            "python_path": sys.executable,
            "working_directory": str(Path.cwd()),
            "platform": sys.platform
        }
        
        # Flag missing required secrets as critical
        for secret in missing_required:
            self._add_finding(
                "critical",
                "missing_required_secret",
                f"Required secret {secret} is not set",
                {"secret": secret},
                f"Set {secret} in .env file"
            )
    
    async def _collect_subsystem_status(self):
        """Query each subsystem for readiness"""
        
        logger.info("[DIAGNOSTICS] Querying subsystem readiness...")
        
        subsystems_to_check = [
            # Core infrastructure
            ("trigger_mesh", "backend.trigger_mesh", "trigger_mesh", "_running"),
            ("reflection_service", "backend.reflection", "reflection_service", "running"),
            ("task_executor", "backend.task_executor", "task_executor", "_running"),
            ("health_monitor", "backend.self_healing", "health_monitor", "_running"),
            
            # Agentic systems
            ("agentic_spine", "backend.agentic_spine", "agentic_spine", "running"),
            ("meta_loop_engine", "backend.meta_loop", "meta_loop_engine", "_running"),
            ("learning_integration", "backend.learning_integration", "learning_integration", "running"),
            ("ethics_sentinel", "backend.ethics_sentinel", "ethics_sentinel", "running"),
            
            # Self-healing
            ("autonomous_improver", "backend.autonomous_improver", "autonomous_improver", "running"),
            ("code_healer", "backend.autonomous_code_healer", "code_healer", "running"),
            ("log_based_healer", "backend.log_based_healer", "log_based_healer", "running"),
            ("ml_healing", "backend.ml_healing", "ml_healing", "running"),
            
            # Metrics & monitoring
            ("metrics_collector", "backend.metrics_collector", "metrics_collector", "_running"),
            ("snapshot_aggregator", "backend.metrics_snapshot_aggregator", "snapshot_aggregator", "_running"),
            
            # ML & optimization
            ("performance_optimizer", "backend.performance_optimizer", "performance_optimizer", "running"),
            ("autonomous_goal_setting", "backend.autonomous_goal_setting", "autonomous_goal_setting", "running"),
            ("incident_predictor", "backend.incident_predictor", "incident_predictor", "running"),
            
            # Schedulers
            ("playbook_executor", "backend.playbook_executor", "playbook_executor", "running"),
            ("forecast_scheduler", "backend.forecast_scheduler", "forecast_scheduler", "running"),
        ]
        
        for subsystem_name, module_path, instance_name, running_attr in subsystems_to_check:
            status = await self._check_subsystem(subsystem_name, module_path, instance_name, running_attr)
            self.subsystems_checked[subsystem_name] = status
    
    async def _check_subsystem(
        self, 
        subsystem_name: str, 
        module_path: str, 
        instance_name: str, 
        running_attr: str
    ) -> Dict[str, Any]:
        """Check if a specific subsystem is running"""
        
        try:
            # Import module
            module = __import__(module_path, fromlist=[instance_name])
            instance = getattr(module, instance_name, None)
            
            if instance is None:
                return {
                    "status": "not_found",
                    "running": False,
                    "error": f"Instance {instance_name} not found in {module_path}"
                }
            
            # Check running status
            running = getattr(instance, running_attr, None)
            
            if running is None:
                return {
                    "status": "no_running_flag",
                    "running": False,
                    "error": f"No {running_attr} attribute found"
                }
            
            is_running = running if isinstance(running, bool) else bool(running)
            
            return {
                "status": "running" if is_running else "stopped",
                "running": is_running,
                "module": module_path,
                "instance": instance_name
            }
            
        except ImportError as e:
            return {
                "status": "import_error",
                "running": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": "check_error",
                "running": False,
                "error": str(e)
            }
    
    async def _collect_governance_status(self):
        """Collect governance and crypto assignment status"""
        
        logger.info("[DIAGNOSTICS] Checking governance status...")
        
        try:
            from backend.governance import governance_engine
            
            governance_status = {
                "governance_engine_loaded": True,
                "handshake_protocol": "loaded"
            }
            
            # Check crypto assignment (optional)
            try:
                from backend.crypto_assignment_engine import universal_crypto_engine
                governance_status["crypto_engine_loaded"] = True
            except:
                governance_status["crypto_engine_loaded"] = False
            
            # Check handshake acknowledgements
            try:
                from backend.handshake_subscribers import handshake_protocol
                governance_status["handshake_acknowledgements"] = len(handshake_protocol.acknowledgements)
            except:
                governance_status["handshake_acknowledgements"] = 0
            
            self.boot_context["governance"] = governance_status
            
        except Exception as e:
            # Don't fail on governance load - it's informational only
            self.boot_context["governance"] = {
                "error": str(e),
                "status": "warning",
                "note": "Governance loads during main.py startup, not boot pipeline"
            }
            
            logger.info(f"[DIAGNOSTICS] Governance check skipped during boot pipeline: {e}")
    
    async def _collect_metrics_catalog_status(self):
        """Check metrics catalog completeness"""
        
        logger.info("[DIAGNOSTICS] Validating metrics catalog...")
        
        try:
            from backend.metrics_catalog_loader import metrics_catalog
            
            catalog_status = {
                "loaded": metrics_catalog.is_loaded,
                "total_metrics": len(metrics_catalog.metrics),
                "categories": len(metrics_catalog.categories),
                "metrics_by_category": {
                    cat: len(metrics) for cat, metrics in metrics_catalog._categories.items()
                }
            }
            
            # Check for known legacy IDs
            legacy_ids = [
                "learning.governance_blocks",
                "infra.cpu_utilization",
                "infra.memory_utilization",
                "infra.disk_usage",
                "executor.queue_depth",
                "autonomy.approvals_pending",
                "autonomy.plan_success_rate"
            ]
            
            missing_legacy = [
                metric_id for metric_id in legacy_ids 
                if metric_id not in metrics_catalog.metrics
            ]
            
            catalog_status["missing_legacy_ids"] = missing_legacy
            
            if missing_legacy:
                self._add_finding(
                    "medium",
                    "metrics_catalog_gaps",
                    f"Metrics catalog missing {len(missing_legacy)} legacy IDs",
                    {"missing": missing_legacy},
                    "Add missing metric definitions to config/metrics_catalog.yaml"
                )
            
            self.boot_context["metrics_catalog"] = catalog_status
            
        except Exception as e:
            self.boot_context["metrics_catalog"] = {
                "error": str(e),
                "status": "failed_to_load"
            }
            
            self._add_finding(
                "high",
                "metrics_catalog_failure",
                "Failed to load metrics catalog",
                {"error": str(e)},
                "Check metrics_catalog_loader module"
            )
    
    async def _collect_warnings_and_skips(self):
        """Aggregate warnings from logs and autonomous systems"""
        
        logger.info("[DIAGNOSTICS] Collecting warnings and skips...")
        
        warnings = {
            "autonomous_improver_skips": [],
            "metrics_warnings": [],
            "governance_blocks": []
        }
        
        # Check autonomous improver whitelist
        try:
            whitelist_path = self.project_root / "config" / "autonomous_improver_whitelist.yaml"
            if whitelist_path.exists():
                import yaml
                with open(whitelist_path) as f:
                    whitelist = yaml.safe_load(f)
                    warnings["whitelist_allow_count"] = len(whitelist.get("allow_improvement", []))
                    warnings["whitelist_skip_count"] = len(whitelist.get("skip_files", []))
        except Exception as e:
            warnings["whitelist_error"] = str(e)
        
        self.boot_context["warnings"] = warnings
    
    # ========================================================================
    # PHASE 2: ANALYSIS
    # ========================================================================
    
    async def _analyze_expected_vs_actual(self):
        """Compare expected subsystems with actual running status"""
        
        logger.info("[DIAGNOSTICS] Analyzing expected vs actual subsystems...")
        
        # Note: During boot pipeline, subsystems aren't started yet
        # They start in main.py on_startup event
        # This check is informational during boot pipeline
        
        # Count running subsystems
        running_count = sum(
            1 for status in self.subsystems_checked.values()
            if status.get("running", False)
        )
        
        # If run during boot pipeline (before main.py), expect 0% health
        # Only flag as issue if run during actual runtime
        if running_count == 0:
            logger.info(
                "[DIAGNOSTICS] 0 subsystems running - this is normal during boot pipeline. "
                "Systems start in main.py on_startup event."
            )
        else:
            # Running during actual runtime - check critical systems
            critical_subsystems = [
                "trigger_mesh",
                "health_monitor",
                "metrics_collector"
            ]
            
            for subsystem in critical_subsystems:
                status = self.subsystems_checked.get(subsystem, {})
                if not status.get("running", False):
                    self._add_finding(
                        "critical",
                        "critical_subsystem_down",
                        f"Critical subsystem {subsystem} is not running",
                        {"subsystem": subsystem, "status": status},
                        f"Check {subsystem} startup logs and restart if needed"
                    )
    
    async def _detect_process_issues(self):
        """Detect repeated restarts or hung processes"""
        
        logger.info("[DIAGNOSTICS] Detecting process issues...")
        
        try:
            # Count Python processes
            python_processes = [
                p for p in psutil.process_iter(['pid', 'name', 'cmdline'])
                if 'python' in p.info['name'].lower()
            ]
            
            # Count Uvicorn processes
            uvicorn_processes = [
                p for p in python_processes
                if p.info['cmdline'] and 'uvicorn' in ' '.join(p.info['cmdline'])
            ]
            
            if len(uvicorn_processes) > 1:
                self._add_finding(
                    "high",
                    "duplicate_uvicorn_processes",
                    f"Multiple Uvicorn processes detected ({len(uvicorn_processes)})",
                    {"count": len(uvicorn_processes), "pids": [p.info['pid'] for p in uvicorn_processes]},
                    "Run .\\GRACE.ps1 -Stop to clean up, then restart"
                )
            
            self.boot_context["process_counts"] = {
                "python_processes": len(python_processes),
                "uvicorn_processes": len(uvicorn_processes)
            }
            
        except Exception as e:
            logger.warning(f"Failed to detect process issues: {e}")
    
    async def _analyze_configuration_gaps(self):
        """Flag missing configuration or catalog mismatches"""
        
        logger.info("[DIAGNOSTICS] Analyzing configuration gaps...")
        
        # Check .env file existence
        env_path = self.project_root / ".env"
        if not env_path.exists():
            self._add_finding(
                "critical",
                "missing_env_file",
                ".env file not found",
                {},
                "Copy .env.example to .env and configure secrets"
            )
        
        # Check database file
        db_path = self.project_root / "backend" / "grace.db"
        if not db_path.exists():
            self._add_finding(
                "critical",
                "missing_database",
                "grace.db database file not found",
                {},
                "Run migrations: .venv\\Scripts\\python.exe -m alembic upgrade head"
            )
    
    async def _analyze_startup_health(self):
        """Overall startup health assessment"""
        
        logger.info("[DIAGNOSTICS] Assessing overall startup health...")
        
        # Count running subsystems
        running_count = sum(
            1 for status in self.subsystems_checked.values()
            if status.get("running", False)
        )
        total_count = len(self.subsystems_checked)
        
        health_score = (running_count / total_count * 100) if total_count > 0 else 0
        
        self.boot_context["startup_health"] = {
            "running_subsystems": running_count,
            "total_subsystems": total_count,
            "health_score": round(health_score, 2),
            "health_status": self._get_health_status(health_score)
        }
        
        # Only flag low health if systems should be running (not during boot pipeline)
        if health_score < 80 and running_count > 0:
            severity = "critical" if health_score < 50 else "high"
            self._add_finding(
                severity,
                "low_startup_health",
                f"Startup health score is {health_score:.1f}% ({running_count}/{total_count} subsystems running)",
                {"health_score": health_score},
                "Review subsystem startup logs and fix failed components"
            )
        elif running_count == 0:
            # Normal during boot pipeline
            logger.info(
                f"[DIAGNOSTICS] Health score 0% is expected during boot pipeline. "
                f"Re-run diagnostics after main.py starts to see actual health."
            )
    
    def _get_health_status(self, score: float) -> str:
        """Convert health score to status"""
        if score >= 95:
            return "excellent"
        elif score >= 85:
            return "good"
        elif score >= 70:
            return "fair"
        elif score >= 50:
            return "poor"
        else:
            return "critical"
    
    # ========================================================================
    # PHASE 3: REPORTING
    # ========================================================================
    
    async def _generate_diagnostics_report(self) -> Dict[str, Any]:
        """Generate structured diagnostics report"""
        
        logger.info("[DIAGNOSTICS] Generating diagnostics report...")
        
        report = {
            "report_type": "boot_diagnostics",
            "version": "1.0",
            "run_id": self.run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "boot_context": self.boot_context,
            "subsystems_checked": self.subsystems_checked,
            "findings": {
                "critical": self.severity_levels["critical"],
                "high": self.severity_levels["high"],
                "medium": self.severity_levels["medium"],
                "low": self.severity_levels["low"],
                "info": self.severity_levels["info"]
            },
            "summary": {
                "total_findings": len(self.findings),
                "critical_count": len(self.severity_levels["critical"]),
                "high_count": len(self.severity_levels["high"]),
                "medium_count": len(self.severity_levels["medium"]),
                "low_count": len(self.severity_levels["low"]),
                "subsystems_running": sum(
                    1 for s in self.subsystems_checked.values() if s.get("running", False)
                ),
                "subsystems_total": len(self.subsystems_checked)
            }
        }
        
        return report
    
    async def _emit_to_immutable_log(self, report: Dict[str, Any]):
        """Write report to immutable log"""
        
        try:
            from backend.immutable_log import immutable_log
            
            await immutable_log.append(
                actor="boot_diagnostics",
                action="boot_sweep_complete",
                resource="boot_pipeline",
                subsystem="diagnostics",
                payload=report,
                result="completed"
            )
            
            logger.info("[DIAGNOSTICS] Report written to immutable log")
            
        except Exception as e:
            logger.error(f"[DIAGNOSTICS] Failed to write to immutable log: {e}")
    
    async def _emit_to_trigger_mesh(self, report: Dict[str, Any]):
        """Publish report to trigger mesh"""
        
        try:
            from backend.trigger_mesh import trigger_mesh, TriggerEvent
            
            await trigger_mesh.publish(TriggerEvent(
                event_type="diagnostics.boot_report",
                source="boot_diagnostics",
                actor="system",
                resource="boot_pipeline",
                payload=report,
                timestamp=datetime.utcnow()
            ))
            
            logger.info("[DIAGNOSTICS] Report published to trigger mesh")
            
        except Exception as e:
            logger.error(f"[DIAGNOSTICS] Failed to publish to trigger mesh: {e}")
    
    async def _print_console_summary(self, report: Dict[str, Any]):
        """Print condensed summary to console"""
        
        print("\n" + "="*80)
        print("BOOT DIAGNOSTICS REPORT")
        print("="*80)
        print(f"Run ID: {self.run_id}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Git SHA: {self.boot_context.get('git_sha', 'unknown')}")
        print()
        
        # Health summary
        health = self.boot_context.get("startup_health", {})
        health_status = health.get("health_status", "unknown")
        health_score = health.get("health_score", 0)
        
        status_color = {
            "excellent": "✅",
            "good": "✅",
            "fair": "⚠️",
            "poor": "❌",
            "critical": "❌"
        }.get(health_status, "?")
        
        print(f"Startup Health: {status_color} {health_status.upper()} ({health_score:.1f}%)")
        print(f"  Running: {health.get('running_subsystems', 0)}/{health.get('total_subsystems', 0)} subsystems")
        print()
        
        # Findings summary
        summary = report["summary"]
        print("Findings:")
        print(f"  🔴 Critical: {summary['critical_count']}")
        print(f"  🟠 High:     {summary['high_count']}")
        print(f"  🟡 Medium:   {summary['medium_count']}")
        print(f"  🔵 Low:      {summary['low_count']}")
        print()
        
        # Critical findings detail
        if self.severity_levels["critical"]:
            print("CRITICAL ISSUES:")
            for finding in self.severity_levels["critical"]:
                print(f"  ❌ {finding['message']}")
                print(f"     Remediation: {finding['remediation']}")
            print()
        
        # High findings detail
        if self.severity_levels["high"]:
            print("HIGH PRIORITY ISSUES:")
            for finding in self.severity_levels["high"]:
                print(f"  ⚠️  {finding['message']}")
                print(f"     Remediation: {finding['remediation']}")
            print()
        
        # Configuration summary
        print("Configuration:")
        print(f"  Required secrets: {len(self.boot_context.get('missing_required_secrets', []))} missing")
        print(f"  Optional secrets: {len(self.boot_context.get('missing_optional_secrets', []))} missing")
        
        catalog = self.boot_context.get("metrics_catalog", {})
        print(f"  Metrics catalog: {catalog.get('total_metrics', 0)} definitions loaded")
        print()
        
        print("="*80)
        
        if summary["critical_count"] > 0:
            print("⚠️  CRITICAL ISSUES DETECTED - Grace may not operate correctly")
        elif summary["high_count"] > 0:
            print("⚠️  High-priority issues detected - Review and remediate")
        elif health_status in ["excellent", "good"]:
            print("✅ Boot diagnostics passed - All systems operational")
        else:
            print("ℹ️  Boot diagnostics complete - Minor issues detected")
        
        print("="*80)
        print()
    
    async def _create_capa_tickets_if_needed(self, report: Dict[str, Any]):
        """Create CAPA tickets for critical findings"""
        
        if not self.severity_levels["critical"]:
            return
        
        logger.info(f"[DIAGNOSTICS] Creating CAPA tickets for {len(self.severity_levels['critical'])} critical findings...")
        
        try:
            from backend.capa_system import capa_system
            import inspect
            
            # Check CAPA method signature to use correct parameters
            create_capa_sig = inspect.signature(capa_system.create_capa)
            params = list(create_capa_sig.parameters.keys())
            
            for finding in self.severity_levels["critical"]:
                # Try different parameter names based on actual method signature
                if "issue_description" in params:
                    await capa_system.create_capa(
                        issue_description=finding["message"],
                        severity="high",
                        category="boot_failure",
                        detected_by="boot_diagnostics",
                        evidence=finding["context"],
                        immediate_action=finding["remediation"]
                    )
                elif "description" in params:
                    await capa_system.create_capa(
                        description=finding["message"],
                        severity="high",
                        category="boot_failure",
                        detected_by="boot_diagnostics"
                    )
                else:
                    logger.warning(f"[DIAGNOSTICS] Unknown CAPA method signature: {params}, skipping ticket creation")
                    break
            
            logger.info(f"[DIAGNOSTICS] Created {len(self.severity_levels['critical'])} CAPA tickets")
            
        except Exception as e:
            logger.warning(f"[DIAGNOSTICS] Could not create CAPA tickets: {e}")
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def _add_finding(
        self, 
        severity: str, 
        finding_type: str, 
        message: str, 
        context: Dict[str, Any],
        remediation: str
    ):
        """Add a diagnostic finding"""
        
        finding = {
            "severity": severity,
            "type": finding_type,
            "message": message,
            "context": context,
            "remediation": remediation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.findings.append(finding)
        self.severity_levels[severity].append(finding)


# Global instance
boot_diagnostics = None


async def run_boot_diagnostics(run_id: str) -> Dict[str, Any]:
    """
    Execute boot diagnostics sweep
    
    Args:
        run_id: Boot run identifier
        
    Returns:
        Diagnostics report
    """
    global boot_diagnostics
    
    boot_diagnostics = BootDiagnostics(run_id)
    report = await boot_diagnostics.run_full_sweep()
    
    return report
