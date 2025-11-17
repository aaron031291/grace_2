#!/usr/bin/env python3
"""
Capture Baseline Metrics
Records system performance baselines for comparison
"""

import time
import json
import psutil
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

def capture_boot_time() -> float:
    """Measure boot time for core system"""
    print("Measuring boot time...", end=" ")
    
    start = time.time()
    try:
        import backend.misc.main
        elapsed = time.time() - start
        print(f"{elapsed:.2f}s")
        return elapsed
    except Exception as e:
        print(f"FAILED: {e}")
        return -1.0

def capture_memory_usage() -> Dict[str, float]:
    """Capture current memory usage"""
    print("Measuring memory usage...", end=" ")
    
    process = psutil.Process()
    mem_info = process.memory_info()
    
    metrics = {
        "rss_mb": mem_info.rss / 1024 / 1024,  # Resident Set Size
        "vms_mb": mem_info.vms / 1024 / 1024,  # Virtual Memory Size
    }
    
    print(f"RSS={metrics['rss_mb']:.1f}MB, VMS={metrics['vms_mb']:.1f}MB")
    return metrics

def capture_import_time() -> Dict[str, float]:
    """Measure import times for key modules"""
    print("Measuring import times...")
    
    imports = {
        "metrics_service": "from backend.metrics_service import get_metrics_collector",
        "cognition_metrics": "from backend.cognition_metrics import get_metrics_engine",
        "models": "from backend.misc.models import Base",
        "fastapi_app": "import backend.misc.main",
    }
    
    times = {}
    for name, import_stmt in imports.items():
        start = time.time()
        try:
            exec(import_stmt)
            elapsed = time.time() - start
            times[name] = elapsed
            print(f"  {name}: {elapsed:.3f}s")
        except Exception as e:
            times[name] = -1.0
            print(f"  {name}: FAILED ({e})")
    
    return times

def capture_system_info() -> Dict[str, Any]:
    """Capture system information"""
    print("Capturing system info...", end=" ")
    
    info = {
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
        "memory_available_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024,
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "python_version": sys.version,
    }
    
    print("✓")
    return info

def save_baseline(metrics: Dict[str, Any], output_path: Path):
    """Save baseline metrics to file"""
    print(f"\nSaving baseline to {output_path}...", end=" ")
    
    baseline = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(baseline, f, indent=2)
    
    print("✓")

def main():
    """Capture and save baseline metrics"""
    print("=" * 60)
    print("GRACE BASELINE METRICS CAPTURE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    metrics = {
        "boot_time_seconds": capture_boot_time(),
        "memory_usage": capture_memory_usage(),
        "import_times": capture_import_time(),
        "system_info": capture_system_info(),
    }
    
    # Save to multiple locations
    output_dir = ROOT / "reports"
    save_baseline(metrics, output_dir / "baseline_metrics.json")
    save_baseline(metrics, output_dir / f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    print("\n" + "=" * 60)
    print("BASELINE SUMMARY")
    print("=" * 60)
    print(f"Boot Time: {metrics['boot_time_seconds']:.2f}s")
    print(f"Memory RSS: {metrics['memory_usage']['rss_mb']:.1f}MB")
    print(f"CPU Usage: {metrics['system_info']['cpu_percent']:.1f}%")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
