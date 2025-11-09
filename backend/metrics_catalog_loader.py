"""
Metrics Catalog Loader
Loads metrics definitions, KPIs, thresholds, and playbook mappings
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List

CATALOG_PATH = Path(__file__).parent.parent / "config" / "metrics_catalog.json"
CATALOG_YAML_PATH = Path(__file__).parent.parent / "config" / "metrics_catalog.yaml"


async def load_metrics_catalog() -> Dict[str, Any]:
    """Load metrics catalog from JSON or YAML"""
    
    # Try JSON first
    if CATALOG_PATH.exists():
        with CATALOG_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    
    # Try YAML
    if CATALOG_YAML_PATH.exists():
        with CATALOG_YAML_PATH.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    
    # Return empty catalog if not found (non-critical)
    return {
        "version": "1.0.0",
        "domains": [],
        "playbooks": []
    }


def load_metrics_catalog_sync() -> Dict[str, Any]:
    """Synchronous version for non-async contexts"""
    
    if CATALOG_PATH.exists():
        with CATALOG_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    
    if CATALOG_YAML_PATH.exists():
        with CATALOG_YAML_PATH.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    
    return {
        "version": "1.0.0",
        "domains": [],
        "playbooks": []
    }


def list_playbooks(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract playbook definitions from catalog"""
    return catalog.get("playbooks", [])


def list_metrics(catalog: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract metric definitions from catalog"""
    metrics = []
    for domain in catalog.get("domains", []):
        for metric in domain.get("metrics", []):
            metrics.append({
                **metric,
                "domain": domain.get("name")
            })
    return metrics


def get_metric_thresholds(catalog: Dict[str, Any], metric_id: str) -> Dict[str, Any]:
    """Get thresholds for specific metric"""
    for domain in catalog.get("domains", []):
        for metric in domain.get("metrics", []):
            if metric.get("id") == metric_id:
                return metric.get("thresholds", {})
    return {}


# Eagerly load catalog for legacy imports (e.g., from .metrics_catalog_loader import metrics_catalog)
try:
    metrics_catalog = load_metrics_catalog_sync()
except Exception:
    # If catalog doesn't exist, use empty catalog
    metrics_catalog = {
        "version": "1.0.0",
        "domains": [],
        "playbooks": []
    }
