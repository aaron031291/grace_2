"""
ML Update Integration
Feeds logic update metadata into ML models for learning and prediction
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MLUpdateIntegration:
    """
    Integrates logic update data into ML training and inference:
    1. Feeds update metadata to proactive intelligence
    2. Converts observation windows to labeled training data
    3. Enriches model inputs with crypto/governance context
    4. Correlates regressions with specific rollouts
    """
    
    def __init__(self):
        # Lazy-loaded ML components
        self._proactive_intelligence = None
        self._causal_analyzer = None
        self._temporal_forecaster = None
        self._training_pipeline = None
        self._immutable_log = None
    
    async def feed_update_to_models(
        self,
        update_id: str,
        update_summary: Dict[str, Any],
        observation_data: Optional[Dict[str, Any]] = None
    ):
        """
        Feed update metadata to all ML models
        
        Args:
            update_id: Update identifier
            update_summary: Consolidated summary from awareness system
            observation_data: Optional observation window results
        """
        
        # Extract signals for ML
        signals = self._extract_ml_signals(update_summary, observation_data)
        
        # Feed to proactive intelligence
        await self._feed_to_proactive_intelligence(update_id, signals)
        
        # Feed to causal analyzer
        await self._feed_to_causal_analyzer(update_id, signals)
        
        # Feed to temporal forecaster
        await self._feed_to_temporal_forecaster(update_id, signals)
        
        logger.info(f"[ML_UPDATE] Fed update {update_id} to ML models")
    
    def _extract_ml_signals(
        self,
        summary: Dict[str, Any],
        observation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract ML-relevant signals from update data
        
        Returns feature dict for model consumption
        """
        
        signals = {
            # Update characteristics
            "update_type": summary.get("update_type"),
            "risk_level": self._encode_risk_level(summary.get("risk_level", "medium")),
            "components_count": len(summary.get("components_touched", [])),
            "components_touched": summary.get("components_touched", []),
            
            # Capabilities
            "new_capabilities_count": len(summary.get("new_capabilities", [])),
            "new_metrics_count": len(summary.get("new_metrics", [])),
            "schema_changes_count": len(summary.get("schema_changes", {})),
            
            # Governance & crypto
            "governance_approved": bool(summary.get("governance_approval_id")),
            "crypto_signed": bool(summary.get("crypto_signature")),
            "validation_passed": summary.get("validation_results", {}).get("passed", False),
            
            # Observation results (if available)
            "stability_score": 0.0,
            "anomalies_count": 0,
            "health_checks_passed": 0,
            "observation_completed": False
        }
        
        # Add observation data if available
        if observation:
            signals.update({
                "stability_score": observation.get("stability_score", 0.0),
                "anomalies_count": len(observation.get("anomalies_detected", [])),
                "health_checks_passed": len([c for c in observation.get("health_checks", []) if c.get("all_healthy")]),
                "observation_completed": observation.get("status") == "completed",
                "stability_verdict": observation.get("stability_verdict", "unknown")
            })
        
        return signals
    
    def _encode_risk_level(self, risk_level: str) -> float:
        """Encode risk level as numeric feature"""
        encoding = {
            "low": 0.25,
            "medium": 0.50,
            "high": 0.75,
            "critical": 1.0
        }
        return encoding.get(risk_level, 0.50)
    
    async def _feed_to_proactive_intelligence(
        self,
        update_id: str,
        signals: Dict[str, Any]
    ):
        """Feed update signals to proactive intelligence for correlation"""
        
        try:
            from backend.proactive_intelligence import proactive_intelligence
            self._proactive_intelligence = proactive_intelligence
            
            # Correlate update with metrics deltas
            await self._proactive_intelligence.correlate_update_with_metrics(
                update_id=update_id,
                components=signals["components_touched"],
                update_signals=signals
            )
            
            logger.info(f"[ML_UPDATE] Fed to proactive intelligence: {update_id}")
            
        except Exception as e:
            logger.debug(f"Could not feed to proactive intelligence: {e}")
    
    async def _feed_to_causal_analyzer(
        self,
        update_id: str,
        signals: Dict[str, Any]
    ):
        """Feed update signals to causal analyzer for graph updates"""
        
        try:
            from backend.causal_analyzer import causal_analyzer
            self._causal_analyzer = causal_analyzer
            
            # Add update node to causal graph
            await self._causal_analyzer.add_intervention_node(
                node_id=update_id,
                node_type="logic_update",
                attributes=signals
            )
            
            # Link to affected components
            for component in signals["components_touched"]:
                await self._causal_analyzer.add_causal_edge(
                    source=update_id,
                    target=component,
                    strength=signals["risk_level"],
                    evidence={"governance_approved": signals["governance_approved"]}
                )
            
            logger.info(f"[ML_UPDATE] Fed to causal analyzer: {update_id}")
            
        except Exception as e:
            logger.debug(f"Could not feed to causal analyzer: {e}")
    
    async def _feed_to_temporal_forecaster(
        self,
        update_id: str,
        signals: Dict[str, Any]
    ):
        """Feed update signals to temporal forecaster for prediction"""
        
        try:
            from backend.temporal_forecasting import temporal_forecaster
            self._temporal_forecaster = temporal_forecaster
            
            # Record update event in timeline
            await self._temporal_forecaster.record_event(
                event_type="logic_update",
                event_id=update_id,
                timestamp=datetime.now(timezone.utc),
                features=signals
            )
            
            logger.info(f"[ML_UPDATE] Fed to temporal forecaster: {update_id}")
            
        except Exception as e:
            logger.debug(f"Could not feed to temporal forecaster: {e}")
    
    async def create_training_labels_from_observation(
        self,
        update_id: str,
        observation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert observation window results into labeled training data
        
        Labels:
        - binary: success (stable) vs failure (unstable/rollback)
        - regression: stability score (0.0 - 1.0)
        - multi-class: stability verdict (stable/acceptable/unstable)
        
        Returns training example ready for model consumption
        """
        
        # Binary label
        success = observation.get("stability_verdict") == "stable"
        
        # Regression label
        stability_score = observation.get("stability_score", 0.0)
        
        # Multi-class label
        verdict_encoding = {
            "stable": 2,
            "acceptable": 1,
            "unstable": 0,
            "unknown": -1
        }
        verdict_label = verdict_encoding.get(
            observation.get("stability_verdict", "unknown"),
            -1
        )
        
        # Features from observation
        features = {
            "update_id": update_id,
            "duration_hours": observation.get("duration_seconds", 0) / 3600,
            "health_checks_count": len(observation.get("health_checks", [])),
            "anomalies_count": len(observation.get("anomalies_detected", [])),
            "components_count": len(observation.get("components", [])),
            "metrics_snapshots_count": len(observation.get("metrics_snapshots", []))
        }
        
        # Anomaly features
        anomalies = observation.get("anomalies_detected", [])
        if anomalies:
            features["has_critical_anomaly"] = any(a.get("severity") == "critical" for a in anomalies)
            features["has_high_anomaly"] = any(a.get("severity") == "high" for a in anomalies)
            features["anomaly_severity_max"] = self._encode_severity(
                max(a.get("severity", "low") for a in anomalies)
            )
        else:
            features["has_critical_anomaly"] = False
            features["has_high_anomaly"] = False
            features["anomaly_severity_max"] = 0.0
        
        training_example = {
            "update_id": update_id,
            "features": features,
            "labels": {
                "success": success,
                "stability_score": stability_score,
                "verdict": verdict_label
            },
            "metadata": {
                "observation_completed_at": observation.get("end_time"),
                "components": observation.get("components", []),
                "rollback_triggered": observation.get("status") == "rolled_back"
            }
        }
        
        return training_example
    
    def _encode_severity(self, severity: str) -> float:
        """Encode anomaly severity as numeric"""
        encoding = {
            "low": 0.25,
            "medium": 0.50,
            "high": 0.75,
            "critical": 1.0
        }
        return encoding.get(severity, 0.0)
    
    async def store_training_example(
        self,
        training_example: Dict[str, Any]
    ):
        """
        Store labeled training example for future model training
        
        Stores in training pipeline for:
        - Causal RL models
        - Forecasting models
        - Trust prediction models
        - Risk assessment models
        """
        
        try:
            from backend.training_pipeline import training_pipeline
            self._training_pipeline = training_pipeline
            
            await self._training_pipeline.add_training_example(
                example_type="logic_update_observation",
                example_data=training_example,
                labels=training_example["labels"],
                metadata=training_example["metadata"]
            )
            
            logger.info(f"[ML_UPDATE] Stored training example: {training_example['update_id']}")
            
        except Exception as e:
            logger.debug(f"Could not store training example: {e}")
    
    async def enrich_model_input_with_crypto_context(
        self,
        base_features: Dict[str, Any],
        crypto_id: Optional[str] = None,
        governance_approval_id: Optional[str] = None,
        audit_ref: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Enrich model input with crypto/governance context
        
        Improves:
        - Trust prediction interpretability
        - Risk assessment accuracy
        - Governance alignment
        
        Args:
            base_features: Base feature dict
            crypto_id: Cryptographic identity
            governance_approval_id: Governance approval ID
            audit_ref: Immutable log sequence number
            
        Returns:
            Enriched feature dict
        """
        
        enriched = base_features.copy()
        
        # Crypto context
        if crypto_id:
            enriched["has_crypto_signature"] = True
            enriched["crypto_age_minutes"] = await self._get_crypto_age(crypto_id)
        else:
            enriched["has_crypto_signature"] = False
            enriched["crypto_age_minutes"] = -1.0
        
        # Governance context
        if governance_approval_id:
            enriched["has_governance_approval"] = True
            enriched["governance_decision_time"] = await self._get_governance_decision_time(governance_approval_id)
        else:
            enriched["has_governance_approval"] = False
            enriched["governance_decision_time"] = -1.0
        
        # Audit context
        if audit_ref:
            enriched["has_audit_trail"] = True
            enriched["audit_sequence"] = audit_ref
            enriched["audit_integrity_verified"] = await self._verify_audit_integrity(audit_ref)
        else:
            enriched["has_audit_trail"] = False
            enriched["audit_sequence"] = -1
            enriched["audit_integrity_verified"] = False
        
        # Composite trust score
        enriched["composite_trust_score"] = self._calculate_composite_trust(enriched)
        
        return enriched
    
    async def _get_crypto_age(self, crypto_id: str) -> float:
        """Get age of crypto signature in minutes"""
        try:
            from backend.crypto_assignment_engine import crypto_engine
            trace = await crypto_engine.trace_entity_real_time(crypto_id)
            
            if trace.get("found"):
                assigned_at = trace["identity"]["assigned_at"]
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(assigned_at))
                return age.total_seconds() / 60
        except:
            pass
        return -1.0
    
    async def _get_governance_decision_time(self, approval_id: str) -> float:
        """Get governance decision time in seconds"""
        # In production, query governance DB for decision time
        return 10.0  # Placeholder
    
    async def _verify_audit_integrity(self, audit_ref: int) -> bool:
        """Verify audit trail integrity"""
        try:
            if not self._immutable_log:
                from backend.immutable_log import immutable_log
                self._immutable_log = immutable_log
            
            # Verify hash chain
            integrity = await self._immutable_log.verify_integrity(
                start_seq=audit_ref,
                end_seq=audit_ref + 10
            )
            return integrity.get("valid", False)
        except:
            return False
    
    def _calculate_composite_trust(self, features: Dict[str, Any]) -> float:
        """
        Calculate composite trust score from crypto/governance/audit features
        
        Used by ML models for trust prediction
        """
        trust_score = 0.0
        
        # Crypto signature present (+0.4)
        if features.get("has_crypto_signature"):
            trust_score += 0.4
            
            # Recent crypto signature (+0.1 bonus)
            if features.get("crypto_age_minutes", 999) < 60:
                trust_score += 0.1
        
        # Governance approval (+0.3)
        if features.get("has_governance_approval"):
            trust_score += 0.3
        
        # Audit trail verified (+0.2)
        if features.get("audit_integrity_verified"):
            trust_score += 0.2
        
        return min(trust_score, 1.0)
    
    async def correlate_regression_with_rollout(
        self,
        regression_data: Dict[str, Any],
        time_window_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Correlate detected regression with recent logic updates
        
        Uses:
        - Temporal correlation (regression time vs update time)
        - Component overlap (affected components)
        - Metric correlation (metrics impacted)
        
        Returns:
            Most likely causing update or None
        """
        
        regression_time = datetime.fromisoformat(regression_data["detected_at"])
        affected_components = regression_data.get("components", [])
        affected_metrics = regression_data.get("metrics", [])
        
        # Query recent updates
        try:
            from backend.misc.logic_update_awareness import logic_update_awareness
            
            # Get updates in time window
            recent_updates = [
                u for u in logic_update_awareness.update_summaries.values()
                if self._within_time_window(u, regression_time, time_window_hours)
            ]
            
            if not recent_updates:
                return None
            
            # Score each update for correlation
            correlations = []
            for update in recent_updates:
                score = self._calculate_correlation_score(
                    update,
                    affected_components,
                    affected_metrics,
                    regression_time
                )
                
                correlations.append({
                    "update_id": update["update_id"],
                    "correlation_score": score,
                    "components_overlap": self._count_overlap(
                        update.get("components_touched", []),
                        affected_components
                    ),
                    "temporal_proximity_hours": self._calculate_hours_between(
                        update["timestamp"],
                        regression_time.isoformat()
                    )
                })
            
            # Return highest correlation
            if correlations:
                best_match = max(correlations, key=lambda c: c["correlation_score"])
                
                if best_match["correlation_score"] > 0.5:  # Threshold
                    logger.info(f"[ML_UPDATE] Regression correlated with update {best_match['update_id']}")
                    return best_match
        
        except Exception as e:
            logger.debug(f"Could not correlate regression: {e}")
        
        return None
    
    def _within_time_window(
        self,
        update: Dict[str, Any],
        regression_time: datetime,
        window_hours: int
    ) -> bool:
        """Check if update is within time window of regression"""
        update_time = datetime.fromisoformat(update["timestamp"])
        time_diff = abs((regression_time - update_time).total_seconds() / 3600)
        return time_diff <= window_hours
    
    def _calculate_correlation_score(
        self,
        update: Dict[str, Any],
        affected_components: List[str],
        affected_metrics: List[str],
        regression_time: datetime
    ) -> float:
        """Calculate correlation score between update and regression"""
        
        score = 0.0
        
        # Component overlap (0-0.5)
        components_overlap = self._count_overlap(
            update.get("components_touched", []),
            affected_components
        )
        if components_overlap > 0:
            score += min(0.5, components_overlap / len(affected_components))
        
        # Metric overlap (0-0.3)
        metrics_overlap = self._count_overlap(
            update.get("new_metrics", []),
            affected_metrics
        )
        if metrics_overlap > 0:
            score += min(0.3, metrics_overlap / max(len(affected_metrics), 1))
        
        # Temporal proximity (0-0.2)
        hours_diff = self._calculate_hours_between(
            update["timestamp"],
            regression_time.isoformat()
        )
        if hours_diff < 1:
            score += 0.2
        elif hours_diff < 6:
            score += 0.1
        
        return score
    
    def _count_overlap(self, list1: List[str], list2: List[str]) -> int:
        """Count overlap between two lists"""
        return len(set(list1) & set(list2))
    
    def _calculate_hours_between(self, time1_iso: str, time2_iso: str) -> float:
        """Calculate hours between two ISO timestamps"""
        t1 = datetime.fromisoformat(time1_iso)
        t2 = datetime.fromisoformat(time2_iso)
        return abs((t2 - t1).total_seconds() / 3600)


# Global instance
ml_update_integration = MLUpdateIntegration()
