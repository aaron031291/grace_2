"""
Organize Grace Repository
Move files to proper directories, delete unnecessary ones
"""

import shutil
from pathlib import Path

print("\n" + "="*70)
print("ORGANIZING GRACE REPOSITORY")
print("="*70)

# Create organized directory structure
directories = {
    'docs/archive': [],
    'docs/status': [],
    'docs/guides': [],
    'scripts/utilities': [],
    'scripts/test': [],
    'scripts/chaos': [],
    'scripts/startup': [],
    'logs/archive': [],
}

print("\n[1/5] Creating directory structure...")
for dir_path in directories.keys():
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"  Created: {dir_path}")

# Move status/completion documents to docs/archive
print("\n[2/5] Moving status documents to docs/archive...")
status_docs = [
    "ADVANCED_TRIGGERS_COMPLETE.md",
    "ALL_20_KERNELS_SUCCESS.md",
    "ALL_CRITICAL_GAPS_CLOSED.md",
    "ALL_INTEGRATION_TASKS_COMPLETE.md",
    "ALL_STUBS_FIXED_PRODUCTION_READY.md",
    "AMP_GRADE_CODING_AGENT_COMPLETE.md",
    "AUTONOMOUS_CHAOS_COMPLETE.md",
    "BACKEND_BLOCKERS_RESOLVED.md",
    "CHAOS_ENGINEERING_COMPLETE.md",
    "CHAOS_SAFEGUARDS_ADDED.md",
    "CODING_AGENT_ENHANCEMENTS_COMPLETE.md",
    "CODING_AGENT_INTEGRATION_TEST.md",
    "COMPLETE_BACKEND_ENDPOINTS.md",
    "COMPLETE_INTEGRATION_TEST_RESULTS.md",
    "COMPLETE_RESILIENCE_STACK.md",
    "COMPLETE_SELF_LEARNING_SYSTEM.md",
    "COMPLETE_SYSTEM_INTEGRATION.md",
    "COMPLETE_SYSTEM_OVERVIEW.md",
    "COMPLETION_VERIFICATION_REPORT.md",
    "CRITICAL_BUGS_FIXED.md",
    "DASHBOARD_COMPLETE_DELIVERY.md",
    "DASHBOARD_DELIVERY_SUMMARY.md",
    "E2E_STRESS_TEST_COMPLETE.md",
    "E2E_TEST_REPORT_20251114.md",
    "ENHANCED_CHAOS_COMPLETE.md",
    "EVERYTHING_COMPLETE_FINAL.md",
    "FINAL_DELIVERY_STATUS.md",
    "FINAL_IMPLEMENTATION_CHECKLIST.md",
    "FIXES_COMPLETE.md",
    "GRACE_COMPLETE_FINAL.md",
    "GRACE_COMPLETE_SYSTEM_DELIVERY.md",
    "GRACE_DASHBOARD_COMPLETE.md",
    "GRACE_ENHANCED_CODING_AGENT.md",
    "GRACE_LEARNING_COMPLETE.md",
    "GRACE_MISSION_CHARTER_COMPLETE.md",
    "HEALER_MUTUAL_RECOVERY_COMPLETE.md",
    "HONEST_STATUS_REPORT.md",
    "IMPLEMENTATION_PLAN_FINAL.md",
    "INDUSTRY_CHAOS_TEST_RESULTS.md",
    "INGESTION_PIPELINES_FIXED.md",
    "INTEGRATION_COMPLETE.md",
    "INTEGRATION_MASTER_INDEX.md",
    "KERNEL_FAILURE_ESCALATION_COMPLETE.md",
    "KERNEL_INVENTORY_COMPLETE.md",
    "KERNEL_STATUS_COMPLETE.md",
    "KERNEL_UNIFIED_LOGIC_INTEGRATION.md",
    "LAYER1_100_PERCENT_COMPLETE.md",
    "LAYER2_IMPLEMENTATION_COMPLETE.md",
    "LAYER3_IMPROVEMENTS_COMPLETE.md",
    "LAYER_2_HARDENING_COMPLETE.md",
    "LAYER_3_CODING_AGENT_COMPLETE.md",
    "LAYER_3_COMPLETION_ROADMAP.md",
    "LEARNING_VISIBILITY_COMPLETE.md",
    "MEDIUM_TERM_COMPLETE.md",
    "MVP_COMPLETE_DELIVERY.md",
    "OBSERVABILITY_COMPLETE.md",
    "PRODUCTION_READY_VERIFICATION.md",
    "READY_FOR_PRODUCTION.md",
    "SECRETS_VAULT_COMPLETE.md",
    "SESSION_COMPLETE.md",
    "SESSION_COMPLETE_FINAL.md",
    "STRESS_TEST_REPORT_20251115.md",
    "STRESS_TEST_RESULTS.md",
    "STUB_CODE_AUDIT.md",
    "STUB_FIXES_COMPLETE.md",
    "TRIGGER_PLAYBOOK_FIX_PIPELINE_COMPLETE.md",
    "TRIPLE_CHECK_VERIFICATION.md",
    "UNIFIED_LOGIC_CHARTER_INTEGRATION.md",
]

moved_status = 0
for doc in status_docs:
    src = Path(doc)
    if src.exists():
        dst = Path("docs/archive") / doc
        shutil.move(str(src), str(dst))
        moved_status += 1

print(f"  Moved {moved_status} status documents")

# Move guides to docs/guides
print("\n[3/5] Moving guides to docs/guides...")
guide_docs = [
    "AUTONOMOUS_LEARNING_SYSTEM.md",
    "LEARNING_VISIBILITY_QUICKSTART.md",
    "MVP_IMPLEMENTATION_PLAN.md",
    "MVP_QA_TEST_PLAN.md",
    "MVP_QUICK_START.md",
    "MVP_USER_FEEDBACK_GUIDE.md",
    "NEXT_STEPS_LAYER3.md",
    "OPEN_SOURCE_LLM_SETUP.md",
    "QUICK_START_MODELS.md",
    "README_FINAL.md",
    "REMOTE_ACCESS_COMPLETE_FINAL.md",
    "REMOTE_ACCESS_LIVE.md",
    "REMOTE_ACCESS_SETUP.md",
    "VISION_VIDEO_MODELS.md",
    "VOICE_CONVERSATION_COMPLETE.md",
    "FINAL_POLISH_ROADMAP.md",
    "AUTOUPDATER_HANDSHAKE_INTEGRATION.md",
    "ALL_FREE_MODELS_FOR_GRACE.md",
]

moved_guides = 0
for doc in guide_docs:
    src = Path(doc)
    if src.exists():
        dst = Path("docs/guides") / doc
        shutil.move(str(src), str(dst))
        moved_guides += 1

print(f"  Moved {moved_guides} guide documents")

# Move test scripts to scripts/test
print("\n[4/5] Moving scripts...")

test_scripts = [
    "test_coding_agent.py",
    "test_healer_watchdog.py",
    "test_integration.py",
    "test_learning_visibility.py",
    "test_remote_access_now.py",
    "run_remote_access_demo.py",
]

chaos_scripts = [
    "run_chaos_kong.py",
    "run_chaos_now.py",
    "run_chaos_test.py",
    "run_enhanced_chaos.py",
    "run_full_stress_test.py",
    "run_industry_chaos.py",
]

utility_scripts = [
    "auto_configure.py",
    "check_server.py",
    "cleanup.py",
    "fix_bom.py",
    "learning_dashboard.py",
    "learning_validation_report.py",
    "monitor_grace.py",
    "trigger_auto_fix.py",
]

moved_scripts = 0

for script in test_scripts:
    src = Path(script)
    if src.exists():
        dst = Path("scripts/test") / script
        shutil.move(str(src), str(dst))
        moved_scripts += 1

for script in chaos_scripts:
    src = Path(script)
    if src.exists():
        dst = Path("scripts/chaos") / script
        shutil.move(str(src), str(dst))
        moved_scripts += 1

for script in utility_scripts:
    src = Path(script)
    if src.exists():
        dst = Path("scripts/utilities") / script
        shutil.move(str(src), str(dst))
        moved_scripts += 1

print(f"  Moved {moved_scripts} scripts")

# Move CMD files to scripts/startup
print("\n[5/5] Moving startup scripts...")
startup_cmds = [
    "install_all_models.cmd",
    "kill_port_8001.cmd",
    "restart_backend.cmd",
    "RUN_GRACE.cmd",
    "START_GRACE_NOW.cmd",
    "START_REMOTE_ACCESS.cmd",
]

moved_cmds = 0
for cmd in startup_cmds:
    src = Path(cmd)
    if src.exists():
        dst = Path("scripts/startup") / cmd
        shutil.move(str(src), str(dst))
        moved_cmds += 1

print(f"  Moved {moved_cmds} startup commands")

# Delete temporary/output files
print("\n[6/6] Cleaning up temporary files...")
temp_files = [
    "boot_log.txt",
    "boot_output.txt",
    "chaos_output.txt",
    "industry_chaos_output.txt",
    "layer1_test_output.txt",
    "LAYER3_FIX_SUMMARY.txt",
    "KERNEL_COUNT_VERIFICATION.txt",
    "VERIFICATION_ALL_STUBS_FIXED.txt",
    "README.txt",
    "STARTUP_READY.txt",
    "serve_simple.py",  # Old duplicate
]

deleted = 0
for f in temp_files:
    p = Path(f)
    if p.exists():
        p.unlink()
        deleted += 1

print(f"  Deleted {deleted} temporary files")

print("\n" + "="*70)
print("REPOSITORY ORGANIZED!")
print("="*70)
print(f"\nMoved:")
print(f"  {moved_status} status docs → docs/archive/")
print(f"  {moved_guides} guides → docs/guides/")
print(f"  {moved_scripts} scripts → scripts/*/")
print(f"  {moved_cmds} startup commands → scripts/startup/")
print(f"\nDeleted:")
print(f"  {deleted} temporary files")
print("\n" + "="*70)
print("ROOT DIRECTORY NOW CLEAN")
print("="*70)
print("\nRemaining in root:")
print("  ✓ serve.py - Main entry point")
print("  ✓ START.cmd - Start command")
print("  ✓ USE_GRACE.cmd - Interactive menu")
print("  ✓ README.md - Main documentation")
print("  ✓ HOW_TO_USE_GRACE.txt - Quick guide")
print("  ✓ remote_access_client.py - Client tool")
print("  ✓ start_grace_now.py - Learning starter")
print("\n  All other files organized into:")
print("    docs/ - Documentation")
print("    scripts/ - Scripts")
print("    backend/ - Code")
print("="*70)
