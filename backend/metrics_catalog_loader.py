"""
Metrics Catalog Loader

Provides:
- load_metrics_catalog(): Loads and validates the metrics/playbooks catalog from config/ (YAML or JSON)
- metrics_catalog: Eagerly-loaded, validated catalog export for convenient imports

Behavior:
- Looks for path from env var GRACE_METRICS_CATALOG first.
- Otherwise searches config/metrics_catalog.yaml|yml|json in project root.
- Validates required fields for each playbook entry so downstream bootstrap stages don't fail.
- Returns a normalized dict with key "playbooks": List[Dict[str, Any]].

This module is import-safe: failures raise clear exceptions; callers can catch if desired.
"""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# PyYAML is already used elsewhere in the repo (cli/config.py)
try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    yaml = None  # type: ignore


REQUIRED_FIELDS: Tuple[str, ...] = (
    "playbook_id",
    "risk_level",
    "autonomy_tier",
    "verification_hooks",
)


class MetricsCatalogError(Exception):
    """Raised when the metrics catalog is missing or invalid"""


def _find_catalog_path(explicit: Optional[Path] = None) -> Path:
    """Find the metrics catalog file path.

    Search order:
    1) Explicit path (if provided)
    2) Env var GRACE_METRICS_CATALOG (absolute or relative to project root)
    3) config/metrics_catalog.yaml
    4) config/metrics_catalog.yml
    5) config/metrics_catalog.json
    """
    if explicit:
        path = explicit
        if not path.exists():
            raise MetricsCatalogError(f"Metrics catalog file not found: {path}")
        return path

    env_path = os.getenv("GRACE_METRICS_CATALOG")
    if env_path:
        env_p = Path(env_path)
        if not env_p.is_absolute():
            env_p = Path.cwd() / env_p
        if not env_p.exists():
            raise MetricsCatalogError(f"GRACE_METRICS_CATALOG points to missing file: {env_p}")
        return env_p

    # Default locations under project config/
    candidates = [
        Path("config") / "metrics_catalog.yaml",
        Path("config") / "metrics_catalog.yml",
        Path("config") / "metrics_catalog.json",
    ]
    for cand in candidates:
        if cand.exists():
            return cand

    raise MetricsCatalogError(
        "Metrics catalog not found. Expected one of: "
        "config/metrics_catalog.yaml|yml|json or set GRACE_METRICS_CATALOG"
    )


def _load_any(path: Path) -> Any:
    """Load YAML or JSON file by extension"""
    suffix = path.suffix.lower()
    try:
        with path.open("r", encoding="utf-8") as f:
            if suffix in (".yaml", ".yml"):
                if yaml is None:
                    raise MetricsCatalogError("PyYAML not installed; required to parse YAML catalog")
                return yaml.safe_load(f)
            elif suffix == ".json":
                return json.load(f)
            else:
                raise MetricsCatalogError(f"Unsupported catalog file type: {suffix}")
    except MetricsCatalogError:
        raise
    except Exception as e:
        raise MetricsCatalogError(f"Failed to read catalog {path}: {e}")


def _normalize_catalog(raw: Any) -> Dict[str, Any]:
    """Normalize into a dict with key 'playbooks': list, preserving metadata if present."""
    if raw is None:
        raise MetricsCatalogError("Catalog file is empty")

    if isinstance(raw, list):
        catalog = {"playbooks": raw}
    elif isinstance(raw, dict):
        # Accept either 'playbooks' key or a flat dict that represents a single entry
        if "playbooks" in raw and isinstance(raw["playbooks"], list):
            catalog = dict(raw)
        else:
            # Heuristic: treat as single-entry catalog if required fields present at top level
            if all(k in raw for k in REQUIRED_FIELDS):
                catalog = {"playbooks": [dict(raw)]}
            else:
                # Otherwise try common alias 'items'
                items = raw.get("items")
                if isinstance(items, list):
                    catalog = {**raw, "playbooks": items}
                else:
                    raise MetricsCatalogError(
                        "Catalog dict must contain a 'playbooks' list or a single playbook entry"
                    )
    else:
        raise MetricsCatalogError("Catalog must be a list or dict")

    return catalog


def _validate_catalog(catalog: Dict[str, Any]) -> Dict[str, Any]:
    playbooks = catalog.get("playbooks")
    if not isinstance(playbooks, list) or not playbooks:
        raise MetricsCatalogError("Catalog 'playbooks' must be a non-empty list")

    errors: List[str] = []
    for idx, pb in enumerate(playbooks):
        if not isinstance(pb, dict):
            errors.append(f"playbooks[{idx}] is not an object")
            continue
        missing = [k for k in REQUIRED_FIELDS if k not in pb]
        if missing:
            errors.append(f"playbooks[{idx}] missing required fields: {', '.join(missing)}")
        # verification_hooks should be a list
        hooks = pb.get("verification_hooks")
        if hooks is not None and not isinstance(hooks, list):
            errors.append(f"playbooks[{idx}].verification_hooks must be a list")

        # Normalize some types
        if "autonomy_tier" in pb:
            try:
                pb["autonomy_tier"] = int(pb["autonomy_tier"])  # type: ignore
            except Exception:
                errors.append(f"playbooks[{idx}].autonomy_tier must be an integer")

    if errors:
        raise MetricsCatalogError("Invalid metrics catalog:\n- " + "\n- ".join(errors))

    return catalog


def load_metrics_catalog(path: Optional[Path | str] = None) -> Dict[str, Any]:
    """Load, normalize, and validate the metrics catalog.

    Args:
        path: Optional explicit path; may be str or Path.
    Returns:
        Dict with keys: 'playbooks' (list), plus any metadata from file.
    Raises:
        MetricsCatalogError: when missing/invalid.
    """
    explicit = Path(path) if isinstance(path, str) else path
    catalog_path = _find_catalog_path(explicit)
    raw = _load_any(catalog_path)
    catalog = _normalize_catalog(raw)
    catalog = _validate_catalog(catalog)
    # Attach resolved path for diagnostics
    catalog.setdefault("_source", str(catalog_path))
    return catalog


# Eagerly load at import time so users can simply `from backend.metrics_catalog_loader import metrics_catalog`
try:
    metrics_catalog: Dict[str, Any] = load_metrics_catalog()
except Exception as e:  # keep import resilient for optional paths
    # Defer error to explicit calls if desired; export a helpful placeholder
    metrics_catalog = {  # type: ignore
        "playbooks": [],
        "_error": str(e),
    }


def get_metrics_catalog() -> Dict[str, Any]:
    """Accessor that always (re)loads catalog from disk.

    Use when you want the latest content rather than the cached module variable.
    """
    return load_metrics_catalog()
