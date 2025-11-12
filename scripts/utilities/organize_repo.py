"""
Repository Organization Script
Moves files into proper folder structure
"""
import os
import sys
import shutil
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Mapping of patterns to destination folders
ORGANIZATION_MAP = {
    'docs/collaboration': [
        'COLLABORATION_*.md',
    ],
    'docs/memory': [
        'MEMORY_*.md',
        'GRACE_MEMORY_*.md',
    ],
    'docs/clarity': [
        'CLARITY_*.md',
        'README_CLARITY.md',
    ],
    'docs/autonomous': [
        'AUTONOMOUS_*.md',
        'AGENT_LIFECYCLE_SYSTEM.md',
    ],
    'docs/deployment': [
        'DEPLOYMENT_*.md',
        'PRODUCTION_*.md',
        'READY_FOR_PRODUCTION.md',
    ],
    'docs/testing': [
        'TEST_*.md',
    ],
    'docs/status_archive': [
        'COMPLETE_*.md',
        'FINAL_*.md',
        'SESSION_*.md',
        '*_COMPLETE.md',
        '*_SUMMARY.md',
        '*_VERIFICATION.md',
        '*_STATUS.md',
        'WARNINGS_FIXED.md',
        'WHATS_WORKING_NOW.md',
        'WORKFLOW_STATUS.md',
        'BOOT_DIAGNOSTICS_ADDED.md',
        'BOOT_VERIFICATION.md',
        'IMPORT_CLEANUP_COMPLETE.md',
        'INTEGRATION_*.md',
        'SELF_HEAL_UNBLOCKED.md',
        'SUBSYSTEM_SCHEMAS_COMPLETE.md',
        'ALL_SUBSYSTEMS_VERIFIED.md',
        'AUTO_INGESTION_COMPLETE.md',
        'SCHEMA_INFERENCE_COMPLETE.md',
        'METRICS_CATALOG_*.md',
        'ELITE_SYSTEMS_*.md',
        'MISSION_CONTROL_COMPLETE.md',
    ],
    'docs/guides': [
        'QUICK_*.md',
        'MANUAL_*.md',
        '*_QUICKSTART.md',
        '*_GUIDE.md',
        '*_CHEATSHEET.md',
        'FOR_JUNIE.md',
        'FRONTEND_DEBUG_STEPS.md',
        'FULL_PIPELINE_GUIDE.md',
        'START_GRACE.md',
        'NEXT_*.md',
        'GRACE_PRIORITY_ROADMAP.md',
        'GRACE_SELF_ASSESSMENT.md',
    ],
    'docs/restart': [
        'RESTART_*.md',
        'POST_BOOT_FIXES.md',
        'GRACE_IS_RUNNING.md',
    ],
    'docs/misc': [
        'ADD_TO_ENV.txt',
        'TODO_AND_SECRET_AUDIT.md',
        'FILETREE_FIX_SUMMARY.md',
        'PIPELINE_COMPLETE_SUMMARY.md',
    ],
    'scripts/boot': [
        'BOOT_*.ps1',
        'start_grace.*',
        'grace-universal.ps1',
        'GRACE_SAFE.ps1',
        'GRACE_PRODUCTION.ps1',
        'install-grace.ps1',
        'boot_grace.py',
        'restart_grace.ps1',
        'start_grace.bat',
    ],
    'scripts/deployment': [
        'deploy_*.ps1',
        'commit_and_push.*',
    ],
    'scripts/utilities': [
        'check_*.py',
        'debug_*.py',
        'diagnose_*.py',
        'fix_*.py',
        'scan_*.py',
        'seed_*.py',
        'show_*.py',
        'validate_*.py',
        'open_correct_files.py',
        'grace_memory_examples.py',
        'create_and_run_test.py',
        'frontend.py',
        'minimal_backend.py',
        'simple_grace.py',
        'chat_with_grace.py',
        'cockpit.py',
    ],
    'scripts/maintenance': [
        'batch_*.ps1',
        'enhanced_batch_resolve.ps1',
        'remove_bom.ps1',
        'resolve_*.ps1',
        'resolve_*.py',
        'one_command.ps1',
        'cockpit.ps1',
    ],
    'scripts/testing': [
        'run_*_tests.py',
    ],
    'tests': [
        'test_*.py',
    ],
    'logs_archive': [
        '*.log',
        'temp_logs.txt',
    ],
}

# Files to keep in root
KEEP_IN_ROOT = [
    'README.md',
    'REPO_ORGANIZATION.md',
    'GRACE.ps1',
    'serve.py',
    'pyproject.toml',
    'alembic.ini',
    'docker-compose.yml',
    'docker-compose.complete.yml',
    'Dockerfile',
    '.env',
    '.env.example',
    '.gitignore',
    '.gitattributes',
    'grace_state.json',
    'grace.cmd',
    'REPO_CLEANUP_PLAN.md',
    'organize_repo.py',
]

def matches_pattern(filename: str, pattern: str) -> bool:
    """Check if filename matches glob pattern"""
    import fnmatch
    return fnmatch.fnmatch(filename, pattern)

def organize_repository():
    """Organize repository files"""
    root = Path('.')
    moved = []
    errors = []
    
    print("🧹 Starting repository organization...")
    print("=" * 60)
    
    # Create all destination directories
    for dest_folder in ORGANIZATION_MAP.keys():
        dest_path = root / dest_folder
        dest_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {dest_folder}/")
    
    print("\n" + "=" * 60)
    print("📦 Moving files...")
    print("=" * 60 + "\n")
    
    # Process each file in root
    for item in root.iterdir():
        if not item.is_file():
            continue
        
        filename = item.name
        
        # Skip files that should stay in root
        if filename in KEEP_IN_ROOT:
            continue
        
        # Skip hidden files and Python cache
        if filename.startswith('.') or filename.startswith('__'):
            continue
        
        # Find matching destination
        destination = None
        for dest_folder, patterns in ORGANIZATION_MAP.items():
            for pattern in patterns:
                if matches_pattern(filename, pattern):
                    destination = dest_folder
                    break
            if destination:
                break
        
        if destination:
            try:
                dest_path = root / destination / filename
                
                # If file already exists, rename with suffix
                if dest_path.exists():
                    base = dest_path.stem
                    ext = dest_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = root / destination / f"{base}_{counter}{ext}"
                        counter += 1
                
                shutil.move(str(item), str(dest_path))
                moved.append((filename, destination))
                print(f"✓ {filename:60} → {destination}/")
            except Exception as e:
                errors.append((filename, str(e)))
                print(f"✗ {filename:60} → ERROR: {e}")
        else:
            # Unmatched files - move to docs/misc
            try:
                dest_path = root / 'docs/misc' / filename
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(dest_path))
                moved.append((filename, 'docs/misc'))
                print(f"? {filename:60} → docs/misc/")
            except Exception as e:
                errors.append((filename, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ORGANIZATION COMPLETE")
    print("=" * 60)
    print(f"📦 Files moved: {len(moved)}")
    print(f"❌ Errors: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for filename, error in errors:
            print(f"  - {filename}: {error}")
    
    print("\n📊 Files by destination:")
    from collections import Counter
    destinations = Counter(dest for _, dest in moved)
    for dest, count in sorted(destinations.items()):
        print(f"  {dest:40} {count:3} files")
    
    print("\n✅ Repository is now organized!")
    print("Next: git add . && git commit -m 'Organize repository structure'")

if __name__ == "__main__":
    organize_repository()
