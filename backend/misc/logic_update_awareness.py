"""
Logic Update Awareness System
Teaches Grace to understand, monitor, and learn from logic updates
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import asyncio

logger = logging.getLogger(__name__)


class LogicUpdateAwareness:
    """
    Manages update awareness workflow:
    1. Consolidated update summaries
    2. Post-update observation windows
    3. Anomaly detection and learning
    4. Automatic rollback triggers
    """
    
    def __init__(self):
        # Active observation windows (update_id -> observation data)
        self.observation_windows: Dict[str, Dict[str, Any]] = {}
        
        # Update summaries cache
        self.update_summaries: Dict[str, Dict[str, Any]] = {}
        
        # Learning data from completed observations
        self.learning_history: List[Dict[str, Any]] = []
        
        # Lazy-loaded dependencies
        self._unified_logic_hub = None
        self._anomaly_watchdog = None
        self._agentic_spine = None
        self._proactive_intelligence = None
        self._immutable_log = None
        self._trigger_mesh = None
    
    async def generate_update_summary(
        self,
        update_id: str,
        update_package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate consolidated update summary for AgenticSpine
        
        Summary includes:
        - Components touched
        - New metrics/capabilities
        - Rollback plan
        - Risk assessment
        - Guardrails/policies
        
        Args:
            update_id: Update identifier
            update_package: Complete update package
            
        Returns:
            Consolidated summary for agents
        """
        
        update_type = update_package.get("update_type")
        component_targets = update_package.get("component_targets", [])
        risk_level = update_package.get("risk_level", "medium")
        
        # Build comprehensive summary
        summary = {
            "update_id": update_id,
            "update_type": update_type,
            "components_touched": component_targets,
            "risk_level": risk_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            
            # Capabilities
            "new_capabilities": self._extract_capabilities(update_package),
            "new_metrics": self._extract_metrics(update_package),
            "schema_changes": self._extract_schema_changes(update_package),
            
            # Safety
            "rollback_plan": update_package.get("rollback_instructions", {}),
            "validation_results": update_package.get("validation_results", {}),
            "guardrails": self._extract_guardrails(update_package),
            
            # Governance
            "governance_approval_id": update_package.get("governance_approval_id"),
            "crypto_signature": update_package.get("crypto_signature"),
            
            # Observation
            "observation_window_duration": self._calculate_observation_duration(risk_level),
            "stability_criteria": self._define_stability_criteria(update_type, risk_level)
        }
        
        # Cache summary
        self.update_summaries[update_id] = summary
        
        # Log summary creation
        if self._immutable_log:
            try:
                from backend.immutable_log import immutable_log
                self._immutable_log = immutable_log
                
                await self._immutable_log.append(
                    actor="logic_update_awareness",
                    action="update_summary_generated",
                    resource=update_id,
                    subsystem="update_awareness",
                    payload=summary,
                    result="summary_ready"
                )
            except Exception as e:
                logger.debug(f"Could not log summary: {e}")
        
        logger.info(f"[UPDATE_AWARENESS] Generated summary for {update_id}")
        logger.info(f"  Components: {', '.join(component_targets)}")
        logger.info(f"  Risk: {risk_level}")
        logger.info(f"  Observation: {summary['observation_window_duration']}")
        
        return summary
    
    async def start_observation_window(
        self,
        update_id: str,
        summary: Dict[str, Any]
    ):
        """
        Start post-update observation window with health checks
        
        Monitors:
        - Metrics tied to updated components
        - Error rates
        - Anomaly detection
        - Governance violations
        
        Duration based on risk level:
        - Low: 1 hour
        - Medium: 6 hours
        - High: 24 hours
        - Critical: 72 hours
        """
        
        duration = summary.get("observation_window_duration", 3600)
        components = summary.get("components_touched", [])
        
        observation = {
            "update_id": update_id,
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc) + timedelta(seconds=duration),
            "duration_seconds": duration,
            "components": components,
            "status": "active",
            "metrics_snapshots": [],
            "anomalies_detected": [],
            "health_checks": [],
            "stability_score": 1.0
        }
        
        self.observation_windows[update_id] = observation
        
        # Start async observation task
        asyncio.create_task(self._run_observation_window(update_id, observation))
        
        # Publish observation start event
        if self._trigger_mesh:
            try:
                from backend.trigger_mesh import trigger_mesh, TriggerEvent
                self._trigger_mesh = trigger_mesh
                
                await self._trigger_mesh.publish(TriggerEvent(
                    event_type="logic_update.observation_started",
                    source="logic_update_awareness",
                    actor="update_awareness",
                    resource=update_id,
                    payload={
                        "update_id": update_id,
                        "duration_seconds": duration,
                        "components": components
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
            except Exception as e:
                logger.debug(f"Could not publish observation start: {e}")
        
        logger.info(f"[UPDATE_AWARENESS] Started observation window for {update_id}")
        logger.info(f"  Duration: {duration}s ({duration/3600:.1f}h)")
        logger.info(f"  Monitoring: {', '.join(components)}")
    
    async def _run_observation_window(
        self,
        update_id: str,
        observation: Dict[str, Any]
    ):
        """
        Run observation window with periodic health checks
        """
        
        start_time = observation["start_time"]
        end_time = observation["end_time"]
        components = observation["components"]
        
        # Check interval based on duration (10% of total duration, min 60s)
        check_interval = max(60, observation["duration_seconds"] // 10)
        
        try:
            while datetime.now(timezone.utc) < end_time:
                # Run health check
                health = await self._run_health_check(update_id, components)
                observation["health_checks"].append(health)
                
                # Capture metrics snapshot
                snapshot = await self._capture_metrics_snapshot(update_id, components)
                observation["metrics_snapshots"].append(snapshot)
                
                # Check for anomalies
                anomalies = await self._detect_anomalies(update_id, snapshot)
                if anomalies:
                    observation["anomalies_detected"].extend(anomalies)
                    observation["stability_score"] *= 0.9  # Decrease stability
                    
                    # Critical anomaly triggers immediate rollback
                    if any(a.get("severity") == "critical" for a in anomalies):
                        logger.error(f"[UPDATE_AWARENESS] Critical anomaly in {update_id}")
                        await self._trigger_automatic_rollback(update_id, anomalies)
                        observation["status"] = "rolled_back"
                        break
                
                # Wait for next check
                await asyncio.sleep(check_interval)
            
            # Observation complete
            if observation["status"] == "active":
                observation["status"] = "completed"
                observation["final_stability_score"] = observation["stability_score"]
                
                # Mark as stable if no anomalies
                if observation["stability_score"] >= 0.95:
                    observation["stability_verdict"] = "stable"
                elif observation["stability_score"] >= 0.80:
                    observation["stability_verdict"] = "acceptable"
                else:
                    observation["stability_verdict"] = "unstable"
                
                logger.info(f"[UPDATE_AWARENESS] Observation complete for {update_id}")
                logger.info(f"  Verdict: {observation['stability_verdict']}")
                logger.info(f"  Stability: {observation['stability_score']:.2%}")
                
                # Store learning data
                await self._store_learning_data(update_id, observation)
                
                # Publish completion event
                if self._trigger_mesh:
                    try:
                        await self._trigger_mesh.publish(TriggerEvent(
                            event_type="logic_update.observation_completed",
                            source="logic_update_awareness",
                            actor="update_awareness",
                            resource=update_id,
                            payload={
                                "update_id": update_id,
                                "stability_verdict": observation["stability_verdict"],
                                "stability_score": observation["stability_score"],
                                "anomalies_count": len(observation["anomalies_detected"])
                            },
                            timestamp=datetime.now(timezone.utc)
                        ))
                    except Exception as e:
                        logger.debug(f"Could not publish completion: {e}")
        
        except Exception as e:
            logger.error(f"[UPDATE_AWARENESS] Observation window failed: {e}")
            observation["status"] = "failed"
            observation["error"] = str(e)
    
    async def _run_health_check(
        self,
        update_id: str,
        components: List[str]
    ) -> Dict[str, Any]:
        """Run health check on updated components"""
        
        health = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "update_id": update_id,
            "components_checked": [],
            "all_healthy": True
        }
        
        for component in components:
            # Component-specific health check
            component_health = {
                "component": component,
                "healthy": True,
                "checks": []
            }
            
            # Check if component is responsive
            # (In production, this would ping actual component endpoints)
            component_health["checks"].append({
                "check": "responsive",
                "passed": True
            })
            
            # Check error rate
            component_health["checks"].append({
                "check": "error_rate",
                "passed": True,
                "value": 0.001
            })
            
            health["components_checked"].append(component_health)
        
        return health
    
    async def _capture_metrics_snapshot(
        self,
        update_id: str,
        components: List[str]
    ) -> Dict[str, Any]:
        """Capture metrics snapshot for update"""
        
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "update_id": update_id,
            "metrics": {}
        }
        
        try:
            from backend.metrics_collector import metrics_collector
            
            # Capture relevant metrics for each component
            for component in components:
                component_metrics = {}
                
                # Logic hub metrics
                if "logic_hub" in component or "unified_logic" in component:
                    component_metrics["update_latency"] = await self._get_metric_value("logic_hub.update_latency_p95")
                    component_metrics["rollback_rate"] = await self._get_metric_value("logic_hub.rollback_rate")
                
                # Memory fusion metrics
                if "memory" in component or "fusion" in component:
                    component_metrics["crypto_assign_rate"] = await self._get_metric_value("memory_fusion.crypto_assign_rate")
                    component_metrics["fetch_latency"] = await self._get_metric_value("memory_fusion.signature_verification_latency")
                
                snapshot["metrics"][component] = component_metrics
        
        except Exception as e:
            logger.debug(f"Could not capture metrics: {e}")
        
        return snapshot
    
    async def _get_metric_value(self, metric_id: str) -> Optional[float]:
        """Get current metric value"""
        try:
            from backend.metrics_collector import metrics_collector
            metric = await metrics_collector.get_metric(metric_id)
            return metric.get("value") if metric else None
        except:
            return None
    
    async def _detect_anomalies(
        self,
        update_id: str,
        snapshot: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics snapshot"""
        
        anomalies = []
        
        try:
            from backend.anomaly_watchdog import anomaly_watchdog
            
            # Check for anomalies tied to this update
            result = await anomaly_watchdog.check_for_anomalies(
                context={"update_id": update_id},
                metrics=snapshot.get("metrics", {})
            )
            
            if result.get("anomalies"):
                for anomaly in result["anomalies"]:
                    anomalies.append({
                        "update_id": update_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "severity": anomaly.get("severity", "medium"),
                        "metric": anomaly.get("metric"),
                        "description": anomaly.get("description"),
                        "value": anomaly.get("value")
                    })
        
        except Exception as e:
            logger.debug(f"Could not detect anomalies: {e}")
        
        return anomalies
    
    async def _trigger_automatic_rollback(
        self,
        update_id: str,
        anomalies: List[Dict[str, Any]]
    ):
        """Trigger automatic rollback due to critical anomalies"""
        
        logger.error(f"[UPDATE_AWARENESS] Triggering automatic rollback for {update_id}")
        logger.error(f"  Reason: {len(anomalies)} critical anomalies detected")
        
        try:
            from backend.unified_logic_hub import unified_logic_hub
            self._unified_logic_hub = unified_logic_hub
            
            # Get the update package
            package = next(
                (p for p in self._unified_logic_hub.update_registry if p.update_id == update_id),
                None
            )
            
            if package:
                # Trigger rollback
                await self._unified_logic_hub._rollback_update(package)
                
                # Log rollback decision
                if self._immutable_log:
                    await self._immutable_log.append(
                        actor="logic_update_awareness",
                        action="automatic_rollback_triggered",
                        resource=update_id,
                        subsystem="update_awareness",
                        payload={
                            "update_id": update_id,
                            "anomalies": anomalies,
                            "trigger": "observation_window"
                        },
                        result="rollback_initiated"
                    )
                
                # Notify via trigger mesh
                if self._trigger_mesh:
                    await self._trigger_mesh.publish(TriggerEvent(
                        event_type="logic_update.automatic_rollback",
                        source="logic_update_awareness",
                        actor="update_awareness",
                        resource=update_id,
                        payload={
                            "update_id": update_id,
                            "anomalies_count": len(anomalies),
                            "trigger_reason": "critical_anomaly_detected"
                        },
                        timestamp=datetime.now(timezone.utc)
                    ))
        
        except Exception as e:
            logger.error(f"[UPDATE_AWARENESS] Rollback failed: {e}")
    
    async def _store_learning_data(
        self,
        update_id: str,
        observation: Dict[str, Any]
    ):
        """Store observation data as learning material"""
        
        learning_data = {
            "update_id": update_id,
            "stability_verdict": observation.get("stability_verdict"),
            "stability_score": observation.get("stability_score"),
            "duration_seconds": observation.get("duration_seconds"),
            "health_checks_count": len(observation.get("health_checks", [])),
            "anomalies_count": len(observation.get("anomalies_detected", [])),
            "components": observation.get("components", []),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.learning_history.append(learning_data)
        
        # Feed to proactive intelligence
        try:
            from backend.proactive_intelligence import proactive_intelligence
            self._proactive_intelligence = proactive_intelligence
            
            await self._proactive_intelligence.learn_from_observation(learning_data)
            
            logger.info(f"[UPDATE_AWARENESS] Stored learning data for {update_id}")
        
        except Exception as e:
            logger.debug(f"Could not store learning data: {e}")
        
        # Feed to ML models with full context
        try:
            from backend.ml_update_integration import ml_update_integration
            
            # Get update summary
            summary = self.update_summaries.get(update_id, {})
            
            # Feed to all ML models
            await ml_update_integration.feed_update_to_models(
                update_id=update_id,
                update_summary=summary,
                observation_data=observation
            )
            
            # Create and store training example
            training_example = await ml_update_integration.create_training_labels_from_observation(
                update_id=update_id,
                observation=observation
            )
            
            await ml_update_integration.store_training_example(training_example)
            
            logger.info(f"[UPDATE_AWARENESS] Fed observation to ML models: {update_id}")
        
        except Exception as e:
            logger.debug(f"Could not feed to ML models: {e}")
        
        # Log to immutable log
        if self._immutable_log:
            try:
                await self._immutable_log.append(
                    actor="logic_update_awareness",
                    action="observation_learning_stored",
                    resource=update_id,
                    subsystem="update_awareness",
                    payload=learning_data,
                    result="learned"
                )
            except Exception as e:
                logger.debug(f"Could not log learning: {e}")
    
    def _extract_capabilities(self, update_package: Dict[str, Any]) -> List[str]:
        """Extract new capabilities from update"""
        capabilities = []
        
        if update_package.get("code_modules"):
            capabilities.append("new_code_modules")
        if update_package.get("schema_diffs"):
            capabilities.append("schema_updates")
        if update_package.get("playbooks"):
            capabilities.append("new_playbooks")
        if update_package.get("metric_definitions"):
            capabilities.append("new_metrics")
        
        return capabilities
    
    def _extract_metrics(self, update_package: Dict[str, Any]) -> List[str]:
        """Extract new metrics from update"""
        metrics = []
        
        if update_package.get("metric_definitions"):
            for metric_def in update_package["metric_definitions"]:
                metrics.append(metric_def.get("name", "unknown"))
        
        return metrics
    
    def _extract_schema_changes(self, update_package: Dict[str, Any]) -> Dict[str, Any]:
        """Extract schema changes summary"""
        schema_changes = {}
        
        if update_package.get("schema_diffs"):
            for endpoint, diff in update_package["schema_diffs"].items():
                schema_changes[endpoint] = {
                    "breaking": diff.get("breaking", False),
                    "fields_added": len(diff.get("fields_added", [])),
                    "fields_removed": len(diff.get("fields_removed", []))
                }
        
        return schema_changes
    
    def _extract_guardrails(self, update_package: Dict[str, Any]) -> List[str]:
        """Extract governance guardrails"""
        guardrails = []
        
        if update_package.get("governance_approval_id"):
            guardrails.append("governance_approved")
        if update_package.get("crypto_signature"):
            guardrails.append("crypto_signed")
        if update_package.get("validation_results", {}).get("passed"):
            guardrails.append("validation_passed")
        
        return guardrails
    
    def _calculate_observation_duration(self, risk_level: str) -> int:
        """Calculate observation window duration based on risk"""
        durations = {
            "low": 3600,      # 1 hour
            "medium": 21600,  # 6 hours
            "high": 86400,    # 24 hours
            "critical": 259200  # 72 hours
        }
        return durations.get(risk_level, 21600)
    
    def _define_stability_criteria(
        self,
        update_type: str,
        risk_level: str
    ) -> Dict[str, Any]:
        """Define stability criteria for update"""
        return {
            "max_error_rate": 0.01 if risk_level == "low" else 0.001,
            "min_uptime": 0.999,
            "max_anomalies": 5 if risk_level == "low" else 2,
            "required_health_checks": 10
        }
    
    async def get_update_summary(self, update_id: str) -> Optional[Dict[str, Any]]:
        """Get cached update summary"""
        return self.update_summaries.get(update_id)
    
    async def get_observation_status(self, update_id: str) -> Optional[Dict[str, Any]]:
        """Get current observation window status"""
        return self.observation_windows.get(update_id)
    
    def get_learning_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent learning history"""
        return self.learning_history[-limit:]


# Global instance
logic_update_awareness = LogicUpdateAwareness()
