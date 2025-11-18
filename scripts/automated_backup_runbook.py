#!/usr/bin/env python3
"""
Automated Backup Runbook - Scheduled backup operations
"""
import asyncio
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.backup.backup_restore_manager import backup_restore_manager
from backend.security.retention_policies import retention_policy_manager

async def run_automated_backup_runbook():
    """Execute automated backup runbook"""
    print("🔄 AUTOMATED BACKUP RUNBOOK")
    print("=" * 50)
    
    runbook_result = {
        "start_time": datetime.utcnow().isoformat(),
        "operations": [],
        "success": True,
        "errors": []
    }
    
    try:
        # Step 1: Check if backup is needed
        print("📅 Step 1: Checking backup schedule...")
        backup_stats = backup_restore_manager.get_backup_stats()
        
        needs_backup = True
        if backup_stats["last_backup"]:
            last_backup = datetime.fromisoformat(backup_stats["last_backup"])
            time_since_backup = datetime.utcnow() - last_backup
            needs_backup = time_since_backup > timedelta(hours=6)  # 6-hour threshold
        
        if needs_backup:
            print("✅ Backup needed - proceeding...")
            
            # Step 2: Run retention policy cleanup
            print("🧹 Step 2: Running retention policy cleanup...")
            cleanup_result = await retention_policy_manager.enforce_retention_policies(dry_run=False)
            runbook_result["operations"].append({
                "operation": "retention_cleanup",
                "result": cleanup_result,
                "success": cleanup_result.get("errors", []) == []
            })
            
            if cleanup_result["artifacts_cleaned"] > 0:
                print(f"   Cleaned {cleanup_result['artifacts_cleaned']} expired artifacts")
            
            # Step 3: Create full backup
            print("💾 Step 3: Creating full backup...")
            backup_result = await backup_restore_manager.create_full_backup()
            runbook_result["operations"].append({
                "operation": "full_backup",
                "result": backup_result,
                "success": backup_result["success"]
            })
            
            if backup_result["success"]:
                print(f"   ✅ Backup created: {backup_result['backup_id']}")
                print(f"   📊 Size: {backup_result['total_size']} bytes")
                print(f"   🗜️ Compression: {backup_result.get('compression_ratio', 0):.2%}")
            else:
                print(f"   ❌ Backup failed: {backup_result['errors']}")
                runbook_result["success"] = False
                runbook_result["errors"].extend(backup_result["errors"])
            
            # Step 4: Run integrity test
            print("🔍 Step 4: Running integrity tests...")
            integrity_result = await backup_restore_manager.run_periodic_integrity_test()
            runbook_result["operations"].append({
                "operation": "integrity_test",
                "result": integrity_result,
                "success": integrity_result["tests_failed"] == 0
            })
            
            if integrity_result["tests_failed"] > 0:
                print(f"   ⚠️ {integrity_result['tests_failed']} integrity tests failed")
                runbook_result["success"] = False
                runbook_result["errors"].append(f"Integrity test failures: {integrity_result['failed_backups']}")
            else:
                print(f"   ✅ All {integrity_result['tests_passed']} integrity tests passed")
            
            # Step 5: Cleanup old backups
            print("🗑️ Step 5: Cleaning up old backups...")
            cleanup_count = await cleanup_old_backups()
            runbook_result["operations"].append({
                "operation": "backup_cleanup",
                "result": {"backups_cleaned": cleanup_count},
                "success": True
            })
            
            if cleanup_count > 0:
                print(f"   🗑️ Cleaned up {cleanup_count} old backups")
            
        else:
            print("⏭️ Backup not needed - skipping...")
            runbook_result["operations"].append({
                "operation": "backup_check",
                "result": {"backup_needed": False, "reason": "Recent backup exists"},
                "success": True
            })
        
        runbook_result["end_time"] = datetime.utcnow().isoformat()
        
        # Save runbook results
        results_dir = Path("reports/backup_runbooks")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"backup_runbook_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(runbook_result, f, indent=2)
        
        print(f"\n📊 RUNBOOK COMPLETE")
        print(f"   Success: {runbook_result['success']}")
        print(f"   Operations: {len(runbook_result['operations'])}")
        print(f"   Results saved: {results_file}")
        
        return runbook_result["success"]
        
    except Exception as e:
        print(f"❌ Runbook failed: {e}")
        runbook_result["success"] = False
        runbook_result["errors"].append(str(e))
        runbook_result["end_time"] = datetime.utcnow().isoformat()
        return False

async def cleanup_old_backups(retention_days: int = 90) -> int:
    """Cleanup backups older than retention period"""
    backup_root = Path("backups")
    if not backup_root.exists():
        return 0
    
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    cleaned_count = 0
    
    for backup_file in backup_root.glob("*.tar.gz"):
        # Get file modification time
        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        if file_time < cutoff_date:
            backup_file.unlink()
            cleaned_count += 1
            print(f"   🗑️ Removed old backup: {backup_file.name}")
    
    return cleaned_count

if __name__ == "__main__":
    success = asyncio.run(run_automated_backup_runbook())
    sys.exit(0 if success else 1)