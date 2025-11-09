"""
Metrics Catalog Loader & Manager
Loads, validates, and manages metrics definitions with KPIs, thresholds, playbook mappings
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

CATALOG_PATH = Path(__file__).parent.parent / "config" / "metrics_catalog.json"
CATALOG_YAML_PATH = Path(__file__).parent.parent / "config" / "metrics_catalog.yaml"


class MetricsCatalogManager:
    """
    Manages metrics catalog with validation and caching
    
    Features:
    - Loads from YAML or JSON
    - Validates required fields
    - Provides defaults for missing fields
    - Caches definitions
    - Structured access methods
    """
    
    def __init__(self):
        self._raw_catalog: Optional[Dict[str, Any]] = None
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._playbooks: List[Dict[str, Any]] = []
        self._loaded = False
    
    def load(self) -> bool:
        """
        Load and parse metrics catalog
        
        Returns:
            True if loaded successfully, False otherwise
        """
        
        try:
            # Try YAML first (preferred)
            if CATALOG_YAML_PATH.exists():
                with CATALOG_YAML_PATH.open("r", encoding="utf-8") as f:
                    self._raw_catalog = yaml.safe_load(f)
                    logger.info(f"[METRICS_CATALOG] Loaded from {CATALOG_YAML_PATH}")
            # Try JSON fallback
            elif CATALOG_PATH.exists():
                with CATALOG_PATH.open("r", encoding="utf-8") as f:
                    self._raw_catalog = json.load(f)
                    logger.info(f"[METRICS_CATALOG] Loaded from {CATALOG_PATH}")
            else:
                logger.warning("[METRICS_CATALOG] No catalog file found, using empty catalog")
                self._raw_catalog = {"metrics": [], "playbooks": []}
                return False
            
            # Parse and validate
            self._parse_catalog()
            self._loaded = True
            
            logger.info(f"[METRICS_CATALOG] ✅ Loaded {len(self._metrics)} metric definitions")
            return True
            
        except Exception as e:
            logger.error(f"[METRICS_CATALOG] Failed to load: {e}")
            self._raw_catalog = {"metrics": [], "playbooks": []}
            self._loaded = False
            return False
    
    def _parse_catalog(self):
        """Parse and validate catalog structure"""
        
        if not self._raw_catalog:
            return
        
        # Parse metrics
        metrics_list = self._raw_catalog.get("metrics", [])
        
        for metric in metrics_list:
            metric_id = metric.get("metric_id")
            
            if not metric_id:
                logger.warning("[METRICS_CATALOG] Skipping metric without metric_id")
                continue
            
            # Validate and set defaults
            validated_metric = self._validate_metric(metric)
            
            self._metrics[metric_id] = validated_metric
            
            # Add to category index
            category = validated_metric.get("category", "uncategorized")
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(metric_id)
        
        # Parse playbooks
        self._playbooks = self._raw_catalog.get("playbooks", [])
    
    def _validate_metric(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate metric definition and provide defaults
        
        Required fields: metric_id, category, description, unit, aggregation
        Optional fields: playbook_id, risk_level, autonomy_tier, verification_hooks
        """
        
        validated = metric.copy()
        
        # Required fields (must exist)
        required = ["metric_id", "category", "description", "unit", "aggregation"]
        for field in required:
            if field not in validated:
                logger.warning(f"[METRICS_CATALOG] Metric {metric.get('metric_id', 'unknown')} missing {field}")
        
        # Optional fields with defaults
        defaults = {
            "playbook_id": None,
            "risk_level": "low",
            "autonomy_tier": 1,
            "verification_hooks": [],
            "playbooks": [],
            "thresholds": {},
            "tags": [],
            "source": "internal",
            "resource_scope": "service"
        }
        
        for field, default_value in defaults.items():
            if field not in validated:
                validated[field] = default_value
        
        return validated
    
    def get_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get metric definition by ID"""
        return self._metrics.get(metric_id)
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all metrics in a category"""
        metric_ids = self._categories.get(category, [])
        return [self._metrics[mid] for mid in metric_ids]
    
    def get_thresholds(self, metric_id: str) -> Dict[str, Any]:
        """Get thresholds for metric"""
        metric = self._metrics.get(metric_id)
        return metric.get("thresholds", {}) if metric else {}
    
    def get_playbook_for_metric(self, metric_id: str) -> Optional[str]:
        """Get associated playbook ID for metric"""
        metric = self._metrics.get(metric_id)
        return metric.get("playbook_id") if metric else None
    
    def list_all_metrics(self) -> List[Dict[str, Any]]:
        """Get all metric definitions"""
        return list(self._metrics.values())
    
    def list_playbooks(self) -> List[Dict[str, Any]]:
        """Get all playbook definitions"""
        return self._playbooks
    
    @property
    def metrics(self) -> Dict[str, Dict[str, Any]]:
        """Access to all metrics dictionary"""
        return self._metrics
    
    @property
    def definitions(self) -> List[Dict[str, Any]]:
        """Access to metrics as list"""
        return list(self._metrics.values())
    
    @property
    def categories(self) -> List[str]:
        """List of all categories"""
        return list(self._categories.keys())
    
    @property
    def is_loaded(self) -> bool:
        """Check if catalog is loaded"""
        return self._loaded
    
    def get_stats(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        return {
            "loaded": self._loaded,
            "total_metrics": len(self._metrics),
            "categories": len(self._categories),
            "playbooks": len(self._playbooks),
            "metrics_by_category": {
                cat: len(metrics) for cat, metrics in self._categories.items()
            }
        }


# Global instance
metrics_catalog = MetricsCatalogManager()

# Auto-load on import
try:
    metrics_catalog.load()
except Exception as e:
    logger.error(f"[METRICS_CATALOG] Auto-load failed: {e}")


# Legacy compatibility functions
async def load_metrics_catalog() -> Dict[str, Any]:
    """Legacy async load function"""
    if not metrics_catalog.is_loaded:
        metrics_catalog.load()
    return {"metrics": metrics_catalog.definitions}


def load_metrics_catalog_sync() -> Dict[str, Any]:
    """Legacy sync load function"""
    if not metrics_catalog.is_loaded:
        metrics_catalog.load()
    return {"metrics": metrics_catalog.definitions}


def list_playbooks(catalog: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Legacy playbook list function"""
    return metrics_catalog.list_playbooks()


def list_metrics(catalog: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Legacy metrics list function"""
    return metrics_catalog.list_all_metrics()


def get_metric_thresholds(catalog: Dict[str, Any], metric_id: str) -> Dict[str, Any]:
    """Legacy threshold getter"""
    return metrics_catalog.get_thresholds(metric_id)
