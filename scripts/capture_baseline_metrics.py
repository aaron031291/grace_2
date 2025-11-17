#!/usr/bin/env python3
"""
Capture Baseline Metrics for Grace - Phase 0 Completion
This script boots Grace and captures baseline performance metrics
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime
import psutil
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def capture_baseline_metrics():
    """Capture baseline boot metrics"""
    
    print("=" * 80)
    print("GRACE BASELINE METRICS CAPTURE")
    print("=" * 80)
    print()
    
    # Track metrics
    metrics = {
        "capture_timestamp": datetime.utcnow().isoformat(),
        "boot_metrics": {},
        "memory_metrics": {},
        "api_metrics": {},
        "system_info": {}
    }
    
    # Capture system info
    print("[SYSTEM] Capturing system information...")
    metrics["system_info"] = {
        "cpu_count": psutil.cpu_count(),
        "total_memory_mb": psutil.virtual_memory().total / (1024 * 1024),
        "python_version": sys.version,
        "platform": sys.platform
    }
    
    # Capture boot metrics
    print("[BOOT] Starting Grace boot sequence...")
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / (1024 * 1024)  # MB
    
    boot_start = time.time()
    
    try:
        # Import and run boot sequence
        from backend.core.guardian_boot_orchestrator import boot_orchestrator
        from backend.core.guardian import guardian
        
        # Boot Guardian (chunk 0)
        guardian_start = time.time()
        boot_result = await guardian.boot()
        guardian_time = time.time() - guardian_start
        
        print(f"  [OK] Guardian boot: {guardian_time:.2f}s")
        
        metrics["boot_metrics"]["guardian_boot_time_seconds"] = guardian_time
        metrics["boot_metrics"]["guardian_port"] = boot_result['phases']['phase3_ports']['port']
        
        # Boot remaining chunks
        chunks_start = time.time()
        
        # Import main app to trigger chunk registration
        from serve import boot_grace_minimal
        
        # Run full boot
        full_boot_result = await boot_grace_minimal()
        
        chunks_time = time.time() - chunks_start
        total_boot_time = time.time() - boot_start
        
        print(f"  [OK] Full boot: {total_boot_time:.2f}s")
        
        metrics["boot_metrics"]["total_boot_time_seconds"] = total_boot_time
        metrics["boot_metrics"]["chunks_boot_time_seconds"] = chunks_time
        metrics["boot_metrics"]["boot_success"] = True
        
    except Exception as e:
        print(f"  [ERROR] Boot failed: {e}")
        metrics["boot_metrics"]["boot_success"] = False
        metrics["boot_metrics"]["boot_error"] = str(e)
        total_boot_time = time.time() - boot_start
        metrics["boot_metrics"]["failed_at_seconds"] = total_boot_time
    
    # Capture memory metrics
    print("[MEMORY] Capturing memory usage...")
    memory_after = process.memory_info().rss / (1024 * 1024)  # MB
    memory_used = memory_after - memory_before
    
    metrics["memory_metrics"] = {
        "baseline_memory_mb": memory_before,
        "post_boot_memory_mb": memory_after,
        "boot_memory_increase_mb": memory_used,
        "system_memory_available_mb": psutil.virtual_memory().available / (1024 * 1024),
        "system_memory_percent_used": psutil.virtual_memory().percent
    }
    
    print(f"  [OK] Memory increase: {memory_used:.2f} MB")
    
    # Capture API endpoint metrics
    print("[API] Capturing API metrics...")
    try:
        from backend.main import app
        
        metrics["api_metrics"] = {
            "total_endpoints": len(app.routes),
            "endpoint_count": len([r for r in app.routes if hasattr(r, 'path')])
        }
        
        print(f"  [OK] Total endpoints: {metrics['api_metrics']['total_endpoints']}")
    
    except Exception as e:
        print(f"  [WARN] Could not capture API metrics: {e}")
        metrics["api_metrics"]["error"] = str(e)
    
    # Save metrics
    print()
    print("[SAVE] Saving baseline metrics...")
    
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Save timestamped version
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_file = reports_dir / f"baseline_metrics_{timestamp}.json"
    
    with open(timestamped_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"  [OK] Saved: {timestamped_file}")
    
    # Save latest version
    latest_file = reports_dir / "baseline_metrics_latest.json"
    with open(latest_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"  [OK] Saved: {latest_file}")
    
    # Print summary
    print()
    print("=" * 80)
    print("BASELINE METRICS SUMMARY")
    print("=" * 80)
    print()
    print(f"Boot Time: {metrics['boot_metrics'].get('total_boot_time_seconds', 'N/A'):.2f}s")
    print(f"Memory Used: {metrics['memory_metrics']['boot_memory_increase_mb']:.2f} MB")
    print(f"API Endpoints: {metrics['api_metrics'].get('total_endpoints', 'N/A')}")
    print(f"Boot Success: {metrics['boot_metrics']['boot_success']}")
    print()
    print("=" * 80)
    
    return metrics

if __name__ == "__main__":
    # Set offline mode for baseline capture
    os.environ["OFFLINE_MODE"] = "true"
    
    try:
        metrics = asyncio.run(capture_baseline_metrics())
        
        if metrics["boot_metrics"]["boot_success"]:
            print("\n[OK] Baseline metrics captured successfully!")
            sys.exit(0)
        else:
            print("\n[ERROR] Boot failed during baseline capture")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nBaseline capture interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error capturing baseline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
