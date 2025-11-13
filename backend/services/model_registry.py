"""
Model Registry & Lifecycle Management

Centralized registry for all ML/DL models with:
- Version control and provenance tracking
- Deployment status management (sandbox → canary → production)
- Performance metrics tracking
- Automated rollback triggers
- Model card generation
- PyTorch/Deep Learning model support with GPU metrics
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import yaml
import json
import hashlib
from pathlib import Path
import logging
import asyncio

logger = logging.getLogger(__name__)


# Check for PyTorch availability
try:
    import torch
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("PyTorch not available - some features limited")


class DeploymentStage(Enum):
    """Model deployment stages"""
    DEVELOPMENT = "development"
    SANDBOX = "sandbox"
    CANARY = "canary"
    STAGED = "staged"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ROLLBACK = "rollback"


@dataclass
class ModelRegistryEntry:
    """Entry in the model registry"""
    # Identity
    model_id: str
    name: str
    version: str
    
    # Artifacts
    artifact_path: str
    framework: str  # sklearn, pytorch, tensorflow, etc.
    model_type: str  # classification, regression, clustering, etc.
    
    # Ownership
    owner: str
    team: str
    
    # Training provenance
    training_data_hash: str
    training_dataset_size: int
    training_timestamp: datetime
    training_duration_minutes: Optional[float] = None
    git_commit_hash: Optional[str] = None
    
    # Evaluation metrics
    evaluation_metrics: Dict[str, float] = field(default_factory=dict)
    calibration_error: Optional[float] = None
    
    # Deployment
    deploy_status: DeploymentStage = DeploymentStage.DEVELOPMENT
    deployed_at: Optional[datetime] = None
    canary_percentage: float = 0.0  # 0-100
    
    # Performance
    expected_latency_p50_ms: Optional[float] = None
    expected_latency_p95_ms: Optional[float] = None
    expected_throughput_rps: Optional[float] = None
    
    # Governance
    model_card_path: Optional[str] = None
    signature_hash: Optional[str] = None
    constitutional_compliance: bool = False
    bias_check_passed: bool = False
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Runtime metrics (populated during serving)
    runtime_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelPerformanceSnapshot:
    """Snapshot of model performance at a point in time"""
    model_id: str
    version: str
    timestamp: datetime
    
    # Latency metrics
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    
    # Throughput
    requests_per_second: float
    
    # Quality metrics
    accuracy: Optional[float] = None
    calibration_error: Optional[float] = None
    
    # Operational
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    
    # Distribution drift
    input_drift_score: Optional[float] = None  # KL divergence
    output_drift_score: Optional[float] = None
    
    # OOD detection
    ood_rate: float = 0.0  # Percentage of OOD samples
    
    # Sample size
    num_requests: int = 0
    
    # GPU metrics (for deep learning models)
    gpu_memory_mb: Optional[float] = None
    gpu_utilization_percent: Optional[float] = None
    device: Optional[str] = None  # cuda, mps, cpu


class ModelRegistry:
    """
    Centralized registry for ML/DL models.
    
    Stores in YAML file: ml/registry/models.yaml
    
    Integrations:
    - Incident management for tracking model issues
    - Monitoring events for observability
    - Self-healing for automated rollback
    """
    
    def __init__(self, registry_path: str = "ml/registry/models.yaml"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.models: Dict[str, ModelRegistryEntry] = {}
        self.performance_history: Dict[str, List[ModelPerformanceSnapshot]] = {}
        
        # Integration callbacks
        self._incident_callback: Optional[Callable] = None
        self._monitoring_callback: Optional[Callable] = None
        self._self_healing_callback: Optional[Callable] = None
        
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from YAML file"""
        if not self.registry_path.exists():
            logger.info(f"Registry file not found, creating new: {self.registry_path}")
            self._save_registry()
            return
        
        try:
            with open(self.registry_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            models_data = data.get('models', [])
            for model_dict in models_data:
                # Convert string timestamps back to datetime
                if 'training_timestamp' in model_dict:
                    model_dict['training_timestamp'] = datetime.fromisoformat(model_dict['training_timestamp'])
                if 'deployed_at' in model_dict and model_dict['deployed_at']:
                    model_dict['deployed_at'] = datetime.fromisoformat(model_dict['deployed_at'])
                if 'created_at' in model_dict:
                    model_dict['created_at'] = datetime.fromisoformat(model_dict['created_at'])
                if 'updated_at' in model_dict:
                    model_dict['updated_at'] = datetime.fromisoformat(model_dict['updated_at'])
                
                # Convert deploy_status back to enum
                if 'deploy_status' in model_dict:
                    model_dict['deploy_status'] = DeploymentStage(model_dict['deploy_status'])
                
                entry = ModelRegistryEntry(**model_dict)
                self.models[entry.model_id] = entry
            
            logger.info(f"Loaded {len(self.models)} models from registry")
            
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            self.models = {}
    
    def _save_registry(self):
        """Save registry to YAML file"""
        models_list = []
        for entry in self.models.values():
            entry_dict = asdict(entry)
            # Convert datetime to ISO format string
            entry_dict['training_timestamp'] = entry.training_timestamp.isoformat()
            if entry.deployed_at:
                entry_dict['deployed_at'] = entry.deployed_at.isoformat()
            entry_dict['created_at'] = entry.created_at.isoformat()
            entry_dict['updated_at'] = entry.updated_at.isoformat()
            # Convert enum to string
            entry_dict['deploy_status'] = entry.deploy_status.value
            
            models_list.append(entry_dict)
        
        data = {'models': models_list}
        
        with open(self.registry_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved {len(self.models)} models to registry")
    
    def register_model(self, entry: ModelRegistryEntry) -> bool:
        """
        Register a new model or update existing.
        
        Args:
            entry: Model registry entry
        
        Returns:
            True if successful
        """
        entry.updated_at = datetime.now()
        self.models[entry.model_id] = entry
        self._save_registry()
        
        logger.info(f"Registered model: {entry.model_id} v{entry.version}")
        return True
    
    async def register_pytorch_model(
        self,
        model_id: str,
        model: Any,
        metrics: Dict[str, float],
        metadata: Dict[str, Any],
        checkpoint_path: Optional[str] = None
    ) -> bool:
        """
        Register a PyTorch deep learning model.
        
        Args:
            model_id: Unique model identifier
            model: PyTorch model instance or specialist
            metrics: Training/evaluation metrics
            metadata: Additional metadata (device, train_samples, etc.)
            checkpoint_path: Path to saved checkpoint
            
        Returns:
            True if successful
        """
        if not PYTORCH_AVAILABLE:
            logger.warning("PyTorch not available - registering as generic model")
        
        # Extract model info
        model_type = type(model).__name__
        framework = "pytorch" if PYTORCH_AVAILABLE else "unknown"
        
        # GPU metrics if available
        device = metadata.get('device', 'cpu')
        gpu_memory_mb = None
        gpu_util = None
        
        if PYTORCH_AVAILABLE and device in ['cuda', 'mps']:
            try:
                from grace.mldl_specialists.deep_learning import DeviceManager
                mem_info = DeviceManager.get_memory_usage()
                gpu_memory_mb = mem_info.get('allocated_mb', 0.0)
                gpu_util = mem_info.get('utilization_percent')
            except Exception as e:
                logger.warning(f"Could not get GPU metrics: {e}")
        
        # Create registry entry
        entry = ModelRegistryEntry(
            model_id=model_id,
            name=model_id,
            version=metadata.get('version', '1.0'),
            artifact_path=checkpoint_path or f"models/{model_id}.pt",
            framework=framework,
            model_type=model_type,
            owner=metadata.get('owner', 'system'),
            team=metadata.get('team', 'ml'),
            training_data_hash=metadata.get('training_data_hash', ''),
            training_dataset_size=metadata.get('train_samples', 0),
            training_timestamp=datetime.fromisoformat(metadata['last_trained']) if 'last_trained' in metadata else datetime.now(),
            training_duration_minutes=metadata.get('training_duration_minutes'),
            evaluation_metrics=metrics,
            deploy_status=DeploymentStage.DEVELOPMENT,
            tags=metadata.get('tags', ['pytorch', 'deep_learning']),
            description=metadata.get('description', f'{model_type} deep learning model'),
            runtime_metrics={
                'device': device,
                'gpu_memory_mb': gpu_memory_mb,
                'gpu_utilization_percent': gpu_util
            }
        )
        
        return self.register_model(entry)
    
    async def update_model(
        self,
        model_id: str,
        metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing model's metrics and metadata.
        
        Args:
            model_id: Model identifier
            metrics: New metrics to add/update
            metadata: New metadata to add/update
            
        Returns:
            True if successful
        """
        if model_id not in self.models:
            logger.error(f"Model not found: {model_id}")
            return False
        
        entry = self.models[model_id]
        
        if metrics:
            entry.evaluation_metrics.update(metrics)
        
        if metadata:
            entry.runtime_metrics.update(metadata)
            
            # Update specific fields if present
            if 'last_trained' in metadata:
                entry.training_timestamp = datetime.fromisoformat(metadata['last_trained'])
            if 'device' in metadata:
                entry.runtime_metrics['device'] = metadata['device']
        
        entry.updated_at = datetime.now()
        self._save_registry()
        
        logger.info(f"Updated model: {model_id}")
        return True
    
    def get_model(self, model_id: str) -> Optional[ModelRegistryEntry]:
        """Get model entry by ID"""
        return self.models.get(model_id)
    
    def list_models(
        self,
        deploy_status: Optional[DeploymentStage] = None,
        framework: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ModelRegistryEntry]:
        """
        List models with optional filtering.
        
        Args:
            deploy_status: Filter by deployment status
            framework: Filter by framework
            tags: Filter by tags (any match)
        
        Returns:
            List of matching models
        """
        models = list(self.models.values())
        
        if deploy_status:
            models = [m for m in models if m.deploy_status == deploy_status]
        
        if framework:
            models = [m for m in models if m.framework == framework]
        
        if tags:
            models = [m for m in models if any(tag in m.tags for tag in tags)]
        
        return models
    
    def update_deployment_status(
        self,
        model_id: str,
        new_status: DeploymentStage,
        canary_percentage: float = 0.0
    ) -> bool:
        """
        Update model deployment status.
        
        Args:
            model_id: Model identifier
            new_status: New deployment stage
            canary_percentage: Percentage for canary deployment
        
        Returns:
            True if successful
        """
        if model_id not in self.models:
            logger.error(f"Model not found: {model_id}")
            return False
        
        entry = self.models[model_id]
        old_status = entry.deploy_status
        
        entry.deploy_status = new_status
        entry.canary_percentage = canary_percentage
        entry.updated_at = datetime.now()
        
        if new_status in [DeploymentStage.CANARY, DeploymentStage.PRODUCTION]:
            entry.deployed_at = datetime.now()
        
        self._save_registry()
        
        logger.info(
            f"Updated {model_id} deployment: {old_status.value} → {new_status.value}"
        )
        return True
    
    async def record_performance_snapshot(
        self,
        snapshot: ModelPerformanceSnapshot
    ):
        """Record performance metrics snapshot and emit monitoring event"""
        model_id = snapshot.model_id
        
        if model_id not in self.performance_history:
            self.performance_history[model_id] = []
        
        self.performance_history[model_id].append(snapshot)
        
        # Update runtime metrics in registry entry
        if model_id in self.models:
            entry = self.models[model_id]
            entry.runtime_metrics = {
                'last_snapshot': snapshot.timestamp.isoformat(),
                'latency_p95_ms': snapshot.latency_p95_ms,
                'error_rate': snapshot.error_rate,
                'ood_rate': snapshot.ood_rate
            }
            self._save_registry()
        
        # Emit monitoring event
        await self._emit_monitoring_event(
            event_type="model.performance_snapshot",
            model_id=model_id,
            data={
                'version': snapshot.version,
                'latency_p50_ms': snapshot.latency_p50_ms,
                'latency_p95_ms': snapshot.latency_p95_ms,
                'latency_p99_ms': snapshot.latency_p99_ms,
                'error_rate': snapshot.error_rate,
                'ood_rate': snapshot.ood_rate,
                'requests_per_second': snapshot.requests_per_second,
                'drift_score': snapshot.input_drift_score
            }
        )
    
    async def check_rollback_triggers(
        self,
        model_id: str,
        window_minutes: int = 10,
        auto_remediate: bool = True
    ) -> tuple[bool, List[str]]:
        """
        Check if model should be rolled back based on performance.
        
        Args:
            model_id: Model to check
            window_minutes: Time window to analyze
            auto_remediate: Whether to trigger self-healing automatically
        
        Returns:
            (should_rollback, reasons)
        """
        if model_id not in self.models:
            return False, []
        
        if model_id not in self.performance_history:
            return False, []
        
        entry = self.models[model_id]
        recent_snapshots = self._get_recent_snapshots(model_id, window_minutes)
        
        if not recent_snapshots:
            return False, []
        
        reasons = []
        should_rollback = False
        severity = "low"
        
        # Check error rate
        avg_error_rate = sum(s.error_rate for s in recent_snapshots) / len(recent_snapshots)
        if avg_error_rate > 0.05:  # 5% error rate
            reasons.append(f"High error rate: {avg_error_rate:.2%}")
            should_rollback = True
            severity = "high" if avg_error_rate > 0.10 else "medium"
        
        # Check latency degradation
        if entry.expected_latency_p95_ms:
            avg_latency_p95 = sum(s.latency_p95_ms for s in recent_snapshots) / len(recent_snapshots)
            if avg_latency_p95 > entry.expected_latency_p95_ms * 1.5:
                reasons.append(
                    f"Latency degradation: {avg_latency_p95:.1f}ms "
                    f"(expected {entry.expected_latency_p95_ms:.1f}ms)"
                )
                should_rollback = True
                if severity == "low":
                    severity = "medium"
        
        # Check OOD rate
        avg_ood_rate = sum(s.ood_rate for s in recent_snapshots) / len(recent_snapshots)
        if avg_ood_rate > 0.2:  # 20% OOD samples
            reasons.append(f"High OOD rate: {avg_ood_rate:.2%}")
            should_rollback = True
            if severity == "low":
                severity = "medium"
        
        # Check input drift
        recent_drift = [s.input_drift_score for s in recent_snapshots if s.input_drift_score]
        if recent_drift:
            avg_drift = sum(recent_drift) / len(recent_drift)
            if avg_drift > 0.3:  # Significant drift
                reasons.append(f"Input distribution drift: {avg_drift:.3f}")
                should_rollback = True
                if severity == "low":
                    severity = "medium"
        
        # If rollback needed, create incident and trigger self-healing
        if should_rollback:
            # Create incident
            await self._create_incident(
                model_id=model_id,
                severity=severity,
                title=f"Model performance degradation detected: {entry.name}",
                description=f"Model {model_id} (v{entry.version}) triggered rollback conditions:\n" + 
                           "\n".join(f"- {r}" for r in reasons),
                context={
                    'model_version': entry.version,
                    'deploy_status': entry.deploy_status.value,
                    'reasons': reasons,
                    'avg_error_rate': avg_error_rate,
                    'avg_ood_rate': avg_ood_rate,
                    'window_minutes': window_minutes
                }
            )
            
            # Trigger self-healing if enabled
            if auto_remediate:
                await self._trigger_self_healing(
                    model_id=model_id,
                    playbook="model_rollback",
                    context={
                        'current_version': entry.version,
                        'current_status': entry.deploy_status.value,
                        'reasons': reasons,
                        'severity': severity
                    }
                )
        
        return should_rollback, reasons
    
    def _get_recent_snapshots(
        self,
        model_id: str,
        window_minutes: int
    ) -> List[ModelPerformanceSnapshot]:
        """Get performance snapshots within time window"""
        if model_id not in self.performance_history:
            return []
        
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        return [
            s for s in self.performance_history[model_id]
            if s.timestamp >= cutoff
        ]
    
    def generate_model_card(
        self,
        model_id: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate model card documentation.
        
        Args:
            model_id: Model to document
            output_path: Where to save (default: docs/model_cards/{model_id}.md)
        
        Returns:
            Path to generated model card
        """
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        entry = self.models[model_id]
        
        if output_path is None:
            output_path = f"docs/model_cards/{model_id}.md"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate markdown content
        content = self._generate_model_card_content(entry)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        # Update registry with model card path
        entry.model_card_path = str(output_file)
        self._save_registry()
        
        logger.info(f"Generated model card: {output_file}")
        return str(output_file)
    
    def _generate_model_card_content(self, entry: ModelRegistryEntry) -> str:
        """Generate model card markdown content"""
        return f"""# Model Card: {entry.name}

## Model Details

- **Model ID**: {entry.model_id}
- **Version**: {entry.version}
- **Type**: {entry.model_type}
- **Framework**: {entry.framework}
- **Owner**: {entry.owner} ({entry.team})
- **Status**: {entry.deploy_status.value}

## Description

{entry.description or "No description provided"}

## Training Data

- **Dataset Hash**: `{entry.training_data_hash}`
- **Dataset Size**: {entry.training_dataset_size:,} samples
- **Trained**: {entry.training_timestamp.isoformat()}
- **Training Duration**: {entry.training_duration_minutes:.1f} minutes
- **Git Commit**: {entry.git_commit_hash or "N/A"}

## Evaluation Metrics

{self._format_metrics(entry.evaluation_metrics)}

- **Calibration Error (ECE)**: {entry.calibration_error:.4f if entry.calibration_error else "N/A"}

## Performance Characteristics

- **Expected Latency (p50)**: {entry.expected_latency_p50_ms:.1f} ms
- **Expected Latency (p95)**: {entry.expected_latency_p95_ms:.1f} ms
- **Expected Throughput**: {entry.expected_throughput_rps:.0f} req/s

## Governance

- **Constitutional Compliance**: {"✅ Passed" if entry.constitutional_compliance else "❌ Not verified"}
- **Bias Check**: {"✅ Passed" if entry.bias_check_passed else "❌ Not verified"}
- **Signature Hash**: `{entry.signature_hash or "N/A"}`

## Deployment

- **Deployed At**: {entry.deployed_at.isoformat() if entry.deployed_at else "Not deployed"}
- **Canary Percentage**: {entry.canary_percentage}%

## Tags

{', '.join(f"`{tag}`" for tag in entry.tags)}

## Artifacts

- **Model Path**: `{entry.artifact_path}`
- **Model Card**: `{entry.model_card_path or "This file"}`

---

*Generated: {datetime.now().isoformat()}*
"""
    
    def _format_metrics(self, metrics: Dict[str, float]) -> str:
        """Format metrics dictionary as markdown list"""
        if not metrics:
            return "No metrics recorded"
        
        lines = []
        for key, value in metrics.items():
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value:.4f}")
        return '\n'.join(lines)
    
    # ========== Integration Methods ==========
    
    def set_incident_callback(self, callback: Callable):
        """Set callback for incident creation (integration with incident registry)"""
        self._incident_callback = callback
        logger.info("Incident callback registered")
    
    def set_monitoring_callback(self, callback: Callable):
        """Set callback for monitoring events (integration with observability)"""
        self._monitoring_callback = callback
        logger.info("Monitoring callback registered")
    
    def set_self_healing_callback(self, callback: Callable):
        """Set callback for self-healing triggers (integration with self-healing kernel)"""
        self._self_healing_callback = callback
        logger.info("Self-healing callback registered")
    
    async def _create_incident(
        self,
        model_id: str,
        severity: str,
        title: str,
        description: str,
        context: Dict[str, Any]
    ):
        """Create incident via callback"""
        if self._incident_callback:
            try:
                await self._incident_callback(
                    source="model_registry",
                    resource_type="ml_model",
                    resource_id=model_id,
                    severity=severity,
                    title=title,
                    description=description,
                    context=context
                )
                logger.info(f"Incident created for model {model_id}: {title}")
            except Exception as e:
                logger.error(f"Failed to create incident: {e}")
    
    async def _emit_monitoring_event(
        self,
        event_type: str,
        model_id: str,
        data: Dict[str, Any]
    ):
        """Emit monitoring event via callback"""
        if self._monitoring_callback:
            try:
                await self._monitoring_callback(
                    event_type=event_type,
                    source="model_registry",
                    resource_id=model_id,
                    timestamp=datetime.now(),
                    data=data
                )
                logger.debug(f"Monitoring event emitted: {event_type} for {model_id}")
            except Exception as e:
                logger.error(f"Failed to emit monitoring event: {e}")
    
    async def _trigger_self_healing(
        self,
        model_id: str,
        playbook: str,
        context: Dict[str, Any]
    ):
        """Trigger self-healing playbook via callback"""
        if self._self_healing_callback:
            try:
                await self._self_healing_callback(
                    resource_type="ml_model",
                    resource_id=model_id,
                    playbook=playbook,
                    context=context
                )
                logger.info(f"Self-healing triggered for {model_id}: {playbook}")
            except Exception as e:
                logger.error(f"Failed to trigger self-healing: {e}")
    
    # ========== Automated Monitoring & Health Checks ==========
    
    async def monitor_production_models(self, window_minutes: int = 10) -> Dict[str, Any]:
        """
        Monitor all production models for issues.
        
        Returns:
            Summary of health status across all production models
        """
        production_models = self.list_models(deploy_status=DeploymentStage.PRODUCTION)
        
        results = {
            'total_models': len(production_models),
            'healthy': 0,
            'degraded': 0,
            'failing': 0,
            'issues': []
        }
        
        for model in production_models:
            should_rollback, reasons = await self.check_rollback_triggers(
                model_id=model.model_id,
                window_minutes=window_minutes,
                auto_remediate=True
            )
            
            if should_rollback:
                results['failing'] += 1
                results['issues'].append({
                    'model_id': model.model_id,
                    'version': model.version,
                    'reasons': reasons
                })
            elif model.model_id in self.performance_history:
                recent = self._get_recent_snapshots(model.model_id, window_minutes)
                if recent:
                    avg_error_rate = sum(s.error_rate for s in recent) / len(recent)
                    if avg_error_rate > 0.01:  # 1% warning threshold
                        results['degraded'] += 1
                    else:
                        results['healthy'] += 1
                else:
                    results['healthy'] += 1
            else:
                results['healthy'] += 1
        
        logger.info(
            f"Production model health: {results['healthy']} healthy, "
            f"{results['degraded']} degraded, {results['failing']} failing"
        )
        
        return results
    
    async def perform_rollback(
        self,
        model_id: str,
        target_version: Optional[str] = None
    ) -> bool:
        """
        Perform model rollback to previous stable version.
        
        Args:
            model_id: Model to rollback
            target_version: Target version (if None, finds last stable)
            
        Returns:
            True if successful
        """
        if model_id not in self.models:
            logger.error(f"Model not found: {model_id}")
            return False
        
        current_entry = self.models[model_id]
        
        # Find target version if not specified
        if target_version is None:
            # Logic to find previous stable version
            # For now, just mark as rollback status
            target_version = "previous"
        
        # Update deployment status
        old_status = current_entry.deploy_status
        current_entry.deploy_status = DeploymentStage.ROLLBACK
        current_entry.updated_at = datetime.now()
        self._save_registry()
        
        # Create incident for rollback action
        await self._create_incident(
            model_id=model_id,
            severity="high",
            title=f"Model rollback executed: {current_entry.name}",
            description=f"Model {model_id} v{current_entry.version} rolled back from {old_status.value}",
            context={
                'action': 'rollback',
                'from_version': current_entry.version,
                'to_version': target_version,
                'from_status': old_status.value
            }
        )
        
        # Emit monitoring event
        await self._emit_monitoring_event(
            event_type="model.rollback",
            model_id=model_id,
            data={
                'from_version': current_entry.version,
                'to_version': target_version,
                'reason': 'performance_degradation'
            }
        )
        
        logger.warning(f"Model {model_id} rolled back from {old_status.value}")
        return True
    
    def get_model_health_summary(self, model_id: str) -> Dict[str, Any]:
        """
        Get comprehensive health summary for a model.
        
        Returns:
            Health metrics and status
        """
        if model_id not in self.models:
            return {'error': 'Model not found'}
        
        entry = self.models[model_id]
        recent_snapshots = self._get_recent_snapshots(model_id, window_minutes=60)
        
        summary = {
            'model_id': model_id,
            'version': entry.version,
            'status': entry.deploy_status.value,
            'deployed_at': entry.deployed_at.isoformat() if entry.deployed_at else None,
            'health_status': 'unknown',
            'metrics': {}
        }
        
        if recent_snapshots:
            avg_error_rate = sum(s.error_rate for s in recent_snapshots) / len(recent_snapshots)
            avg_latency_p95 = sum(s.latency_p95_ms for s in recent_snapshots) / len(recent_snapshots)
            avg_ood_rate = sum(s.ood_rate for s in recent_snapshots) / len(recent_snapshots)
            
            summary['metrics'] = {
                'avg_error_rate': avg_error_rate,
                'avg_latency_p95_ms': avg_latency_p95,
                'avg_ood_rate': avg_ood_rate,
                'snapshot_count': len(recent_snapshots)
            }
            
            # Determine health status
            if avg_error_rate > 0.05:
                summary['health_status'] = 'critical'
            elif avg_error_rate > 0.01 or avg_ood_rate > 0.15:
                summary['health_status'] = 'degraded'
            else:
                summary['health_status'] = 'healthy'
        
        return summary


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """Get global model registry instance"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
