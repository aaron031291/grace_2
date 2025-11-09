"""
Metrics Catalog Loader
Loads and validates metrics definitions from config/metrics_catalog.yaml
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MetricThreshold:
    """Threshold definition for a metric"""
    good_upper: Optional[float] = None
    good_lower: Optional[float] = None
    warning_upper: Optional[float] = None
    warning_lower: Optional[float] = None
    critical_upper: Optional[float] = None
    critical_lower: Optional[float] = None


@dataclass
class MetricDefinition:
    """Complete metric definition from catalog"""
    metric_id: str
    category: str
    description: str
    unit: str
    aggregation: str
    thresholds: MetricThreshold
    playbooks: List[str]
    recommended_interval_seconds: int
    source: str
    resource_scope: str
    tags: List[str]
    
    def compute_band(self, value: float) -> str:
        """Determine which band a value falls into"""
        t = self.thresholds
        
        # Check critical
        if t.critical_lower is not None and value < t.critical_lower:
            return "critical"
        if t.critical_upper is not None and value > t.critical_upper:
            return "critical"
        
        # Check warning
        if t.warning_lower is not None and value < t.warning_lower:
            return "warning"
        if t.warning_upper is not None and value > t.warning_upper:
            return "warning"
        
        # Default to good
        return "good"


class MetricsCatalogLoader:
    """Loads and manages the metrics catalog"""
    
    def __init__(self, catalog_path: str = "config/metrics_catalog.yaml"):
        self.catalog_path = Path(catalog_path)
        self.metrics: Dict[str, MetricDefinition] = {}
        self.playbook_to_metrics: Dict[str, List[str]] = {}
        self.category_index: Dict[str, List[str]] = {}
    
    def load(self) -> bool:
        """Load metrics catalog from YAML"""
        try:
            if not self.catalog_path.exists():
                logger.warning(f"[CATALOG] Metrics catalog not found: {self.catalog_path}")
                return False
            
            with open(self.catalog_path, 'r') as f:
                catalog_data = yaml.safe_load(f)
            
            if not catalog_data or 'metrics' not in catalog_data:
                logger.error("[CATALOG] Invalid catalog format: missing 'metrics' key")
                return False
            
            # Parse each metric
            for metric_data in catalog_data['metrics']:
                metric_def = self._parse_metric(metric_data)
                if metric_def:
                    self.metrics[metric_def.metric_id] = metric_def
                    
                    # Build indexes
                    category = metric_def.category
                    if category not in self.category_index:
                        self.category_index[category] = []
                    self.category_index[category].append(metric_def.metric_id)
                    
                    # Index playbooks
                    for playbook in metric_def.playbooks:
                        if playbook not in self.playbook_to_metrics:
                            self.playbook_to_metrics[playbook] = []
                        self.playbook_to_metrics[playbook].append(metric_def.metric_id)
            
            logger.info(f"[CATALOG] ✅ Loaded {len(self.metrics)} metrics from catalog")
            print(f"[CATALOG] ✅ Loaded {len(self.metrics)} metric definitions")
            print(f"[CATALOG]    Categories: {', '.join(self.category_index.keys())}")
            print(f"[CATALOG]    Playbooks: {len(self.playbook_to_metrics)}")
            
            return True
        
        except Exception as e:
            logger.error(f"[CATALOG] Error loading catalog: {e}", exc_info=True)
            print(f"[CATALOG] ❌ Failed to load catalog: {e}")
            return False
    
    def _parse_metric(self, data: Dict[str, Any]) -> Optional[MetricDefinition]:
        """Parse metric definition from YAML data"""
        try:
            thresholds_data = data.get('thresholds', {})
            
            threshold = MetricThreshold(
                good_upper=thresholds_data.get('good', {}).get('upper'),
                good_lower=thresholds_data.get('good', {}).get('lower'),
                warning_upper=thresholds_data.get('warning', {}).get('upper'),
                warning_lower=thresholds_data.get('warning', {}).get('lower'),
                critical_upper=thresholds_data.get('critical', {}).get('upper'),
                critical_lower=thresholds_data.get('critical', {}).get('lower')
            )
            
            return MetricDefinition(
                metric_id=data['metric_id'],
                category=data.get('category', 'unknown'),
                description=data.get('description', ''),
                unit=data.get('unit', 'count'),
                aggregation=data.get('aggregation', 'avg'),
                thresholds=threshold,
                playbooks=data.get('playbooks', []),
                recommended_interval_seconds=data.get('recommended_interval_seconds', 60),
                source=data.get('source', 'internal'),
                resource_scope=data.get('resource_scope', 'service'),
                tags=data.get('tags', [])
            )
        
        except Exception as e:
            logger.error(f"[CATALOG] Error parsing metric: {e}")
            return None
    
    def get_metric(self, metric_id: str) -> Optional[MetricDefinition]:
        """Get metric definition by ID"""
        return self.metrics.get(metric_id)
    
    def get_metrics_by_category(self, category: str) -> List[MetricDefinition]:
        """Get all metrics in a category"""
        metric_ids = self.category_index.get(category, [])
        return [self.metrics[mid] for mid in metric_ids if mid in self.metrics]
    
    def get_playbooks_for_metric(self, metric_id: str) -> List[str]:
        """Get playbooks associated with a metric"""
        metric = self.metrics.get(metric_id)
        return metric.playbooks if metric else []
    
    def get_metrics_for_playbook(self, playbook_id: str) -> List[str]:
        """Get metrics that trigger a playbook"""
        return self.playbook_to_metrics.get(playbook_id, [])
    
    def validate_value(self, metric_id: str, value: float) -> Dict[str, Any]:
        """Validate a metric value against thresholds"""
        metric = self.metrics.get(metric_id)
        
        if not metric:
            return {
                "valid": False,
                "error": f"Unknown metric: {metric_id}"
            }
        
        band = metric.compute_band(value)
        
        return {
            "valid": True,
            "metric_id": metric_id,
            "value": value,
            "unit": metric.unit,
            "band": band,
            "playbooks": metric.playbooks if band != "good" else [],
            "severity": band
        }
    
    def get_all_metrics(self) -> List[MetricDefinition]:
        """Get all metric definitions"""
        return list(self.metrics.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        return {
            "total_metrics": len(self.metrics),
            "categories": list(self.category_index.keys()),
            "total_playbooks": len(self.playbook_to_metrics),
            "metrics_by_category": {
                cat: len(metrics) for cat, metrics in self.category_index.items()
            },
            "metrics_by_source": self._group_by_source()
        }
    
    def _group_by_source(self) -> Dict[str, int]:
        """Group metrics by source"""
        by_source = {}
        for metric in self.metrics.values():
            by_source[metric.source] = by_source.get(metric.source, 0) + 1
        return by_source


# Global singleton
metrics_catalog = MetricsCatalogLoader()
