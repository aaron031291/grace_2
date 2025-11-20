#!/usr/bin/env python3
"""Test metrics catalog loading"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.metrics_catalog_loader import metrics_catalog
import yaml

print("=" * 80)
print("METRICS CATALOG TEST")
print("=" * 80)
print()

# Check if loaded
print(f"Loaded: {metrics_catalog.is_loaded}")
print(f"Metrics in memory: {len(metrics_catalog.metrics)}")
print()

# Check YAML file
catalog_path = Path(__file__).parent / "config" / "metrics_catalog.yaml"
with open(catalog_path) as f:
    data = yaml.safe_load(f)
    yaml_count = len(data.get("metrics", []))
    print(f"Metrics in YAML file: {yaml_count}")
    print()

# Check for invalid units
print("Checking for invalid units...")
from backend.telemetry_schemas import MetricUnit
allowed_units = [u.value for u in MetricUnit]
print(f"Allowed units: {allowed_units}")
print()

invalid_units = []
for metric in data.get("metrics", []):
    unit = metric.get("unit")
    if unit and unit not in allowed_units:
        invalid_units.append((metric.get("metric_id"), unit))

if invalid_units:
    print(f"[FAIL] Found {len(invalid_units)} invalid units:")
    for metric_id, unit in invalid_units:
        print(f"  - {metric_id}: '{unit}' not in {allowed_units}")
    print()
else:
    print("[OK] All units are valid")
    print()

# Check for duplicates
print("Checking for duplicate metric IDs...")
metric_ids = [m.get("metric_id") for m in data.get("metrics", [])]
duplicates = [mid for mid in metric_ids if metric_ids.count(mid) > 1]
unique_duplicates = list(set(duplicates))

if unique_duplicates:
    print(f"[FAIL] Found {len(unique_duplicates)} duplicate metric IDs:")
    for mid in unique_duplicates:
        count = metric_ids.count(mid)
        print(f"  - {mid}: appears {count} times")
    print()
else:
    print("[OK] No duplicate metric IDs")
    print()

# List all metric IDs
print(f"All metric IDs ({len(metric_ids)}):")
for mid in sorted(set(metric_ids)):
    print(f"  - {mid}")
print()

print("=" * 80)
if invalid_units or unique_duplicates:
    print("[FAIL] Catalog has errors")
else:
    print("[PASS] Catalog is valid")
print("=" * 80)
