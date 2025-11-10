#!/usr/bin/env python3
"""Test Boot Diagnostics System"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_boot_diagnostics():
    """Test the boot diagnostics sweep"""
    
    print("=" * 80)
    print("BOOT DIAGNOSTICS TEST")
    print("=" * 80)
    print()
    
    try:
        from backend.boot_diagnostics import run_boot_diagnostics
        
        print("[TEST] Running boot diagnostics sweep...")
        print()
        
        # Run diagnostics
        report = await run_boot_diagnostics("test_run_001")
        
        print()
        print("=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print()
        
        # Validate report structure
        assert "report_type" in report, "Missing report_type"
        assert report["report_type"] == "boot_diagnostics", "Wrong report_type"
        
        assert "boot_context" in report, "Missing boot_context"
        assert "subsystems_checked" in report, "Missing subsystems_checked"
        assert "findings" in report, "Missing findings"
        assert "summary" in report, "Missing summary"
        
        print(f"[OK] Report structure validated")
        print(f"[OK] Run ID: {report['run_id']}")
        print()
        
        # Check boot context
        context = report["boot_context"]
        print(f"[OK] Git SHA: {context.get('git_sha', 'unknown')}")
        print(f"[OK] Python: {context.get('component_versions', {}).get('python', 'unknown')}")
        print()
        
        # Check subsystems
        subsystems = report["subsystems_checked"]
        print(f"[OK] Subsystems checked: {len(subsystems)}")
        
        running = sum(1 for s in subsystems.values() if s.get("running", False))
        print(f"[OK] Running subsystems: {running}/{len(subsystems)}")
        print()
        
        # Check findings
        summary = report["summary"]
        print(f"[OK] Total findings: {summary['total_findings']}")
        print(f"    Critical: {summary['critical_count']}")
        print(f"    High: {summary['high_count']}")
        print(f"    Medium: {summary['medium_count']}")
        print(f"    Low: {summary['low_count']}")
        print()
        
        # Check health
        health = context.get("startup_health", {})
        print(f"[OK] Health score: {health.get('health_score', 0):.1f}%")
        print(f"[OK] Health status: {health.get('health_status', 'unknown')}")
        print()
        
        # List non-running subsystems
        not_running = [
            name for name, status in subsystems.items()
            if not status.get("running", False)
        ]
        
        if not_running:
            print(f"[INFO] Non-running subsystems ({len(not_running)}):")
            for name in not_running[:10]:  # Show first 10
                status = subsystems[name]
                print(f"    - {name}: {status.get('status', 'unknown')}")
                if status.get('error'):
                    print(f"      Error: {status['error']}")
            if len(not_running) > 10:
                print(f"    ... and {len(not_running) - 10} more")
            print()
        
        # Test assertions
        print("=" * 80)
        print("ASSERTIONS")
        print("=" * 80)
        print()
        
        assert report["run_id"] == "test_run_001", "Wrong run_id"
        print("[PASS] Run ID matches")
        
        assert len(subsystems) > 0, "No subsystems checked"
        print(f"[PASS] Checked {len(subsystems)} subsystems")
        
        assert "startup_health" in context, "Missing startup_health"
        print("[PASS] Startup health calculated")
        
        assert "findings" in report, "Missing findings"
        print("[PASS] Findings collected")
        
        print()
        print("=" * 80)
        print("[SUCCESS] All tests passed!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("[FAIL] Test failed")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_boot_diagnostics())
    sys.exit(0 if success else 1)
