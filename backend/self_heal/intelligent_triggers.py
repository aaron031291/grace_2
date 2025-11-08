"""
Intelligent Self-Healing Triggers

Integrates multiple intelligent subsystems to trigger self-healing actions:
- Meta Loop Supervisor (systemic issues detection)
- Proactive Intelligence (ML/DL anomaly detection)
- Agentic Spine (cross-domain intelligence)
- Immutable Log Analysis (pattern detection)

Each subsystem publishes events that the self-healing system reacts to,
creating a unified, multi-source intelligent healing system.
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

from ..trigger_mesh import trigger_mesh, TriggerEvent
from ..immutable_log import immutable_log


@dataclass
class IntelligentTrigger:
    """Unified trigger from any intelligent subsystem"""
    trigger_id: str
    source_subsystem: str
    trigger_type: str
    service: str
    diagnosis_code: str
    confidence: float
    impact: str
    reasoning: List[str]
    suggested_playbooks: List[str]
    metadata: Dict[str, Any]
    created_at: datetime


class IntelligentTriggerManager:
    """
    Manages intelligent triggers from multiple subsystems.
    
    Subscribes to events from:
    - Meta loop (systemic optimization directives)
    - Proactive intelligence (ML/DL predictions)
    - Agentic spine (cross-domain insights)
    - Immutable log (pattern analysis)
    """
    
    def __init__(self):
        self.running = False
        self._subscriptions = []
        self.trigger_history: List[IntelligentTrigger] = []
        self.max_history = 1000
    
    async def start(self):
        """Subscribe to all intelligent subsystems"""
        if self.running:
            return
        
        print("\n[Intelligent Triggers] Subscribing to intelligent subsystems...")
        
        # Meta Loop Supervisor triggers
        trigger_mesh.subscribe("meta_loop.directive", self._handle_meta_loop_directive)
        trigger_mesh.subscribe("meta_loop.systemic_issue", self._handle_systemic_issue)
        
        # Proactive Intelligence triggers (ML/DL)
        trigger_mesh.subscribe("proactive.anomaly_forecast", self._handle_anomaly_forecast)
        trigger_mesh.subscribe("proactive.capacity_prediction", self._handle_capacity_prediction)
        trigger_mesh.subscribe("proactive.risk_assessment", self._handle_risk_assessment)
        trigger_mesh.subscribe("proactive.drift_detected", self._handle_drift_detection)
        
        # Agentic Spine triggers
        trigger_mesh.subscribe("agentic_spine.cross_domain_alert", self._handle_cross_domain_alert)
        trigger_mesh.subscribe("agentic_spine.health_degradation", self._handle_health_degradation)
        
        # Immutable Log pattern triggers
        trigger_mesh.subscribe("immutable_log.pattern_detected", self._handle_pattern_detection)
        trigger_mesh.subscribe("immutable_log.anomaly_sequence", self._handle_anomaly_sequence)
        
        self.running = True
        
        await immutable_log.append(
            actor="intelligent_triggers",
            action="manager_started",
            resource="self_heal",
            subsystem="intelligent_triggers",
            payload={"subscriptions": 8},
            result="started"
        )
        
        print("  [OK] Intelligent trigger manager started (8 event types)")
    
    async def stop(self):
        """Stop listening to triggers"""
        self.running = False
        await immutable_log.append(
            actor="intelligent_triggers",
            action="manager_stopped",
            resource="self_heal",
            subsystem="intelligent_triggers",
            payload={"triggers_processed": len(self.trigger_history)},
            result="stopped"
        )
        print("  [OK] Intelligent trigger manager stopped")
    
    # ========== META LOOP TRIGGERS ==========
    
    async def _handle_meta_loop_directive(self, event: TriggerEvent):
        """Handle directives from meta loop supervisor"""
        try:
            directive = event.payload
            directive_type = directive.get("directive_type")
            
            # Check if directive indicates a systemic health issue
            if directive_type in ["adjust_threshold", "disable_playbook", "rollback_change"]:
                # This indicates meta loop detected something wrong
                
                trigger = IntelligentTrigger(
                    trigger_id=f"meta_{directive.get('directive_id')}",
                    source_subsystem="meta_loop",
                    trigger_type="systemic_issue",
                    service=directive.get("target_domain", "core"),
                    diagnosis_code="meta_loop_optimization",
                    confidence=0.9,  # Meta loop has high confidence
                    impact=directive.get("change_impact", "moderate"),
                    reasoning=[
                        f"Meta loop directive: {directive_type}",
                        f"Justification: {directive.get('justification', 'N/A')}",
                        f"Expected impact: {directive.get('expected_impact', 'N/A')}"
                    ],
                    suggested_playbooks=self._infer_playbooks_from_directive(directive),
                    metadata=directive,
                    created_at=datetime.now(timezone.utc)
                )
                
                await self._emit_healing_trigger(trigger)
        
        except Exception as e:
            print(f"  Warning: Meta loop directive handler error: {e}")
    
    async def _handle_systemic_issue(self, event: TriggerEvent):
        """Handle systemic issues detected by meta loop"""
        try:
            issue = event.payload
            
            trigger = IntelligentTrigger(
                trigger_id=f"systemic_{event.resource}_{int(datetime.now().timestamp())}",
                source_subsystem="meta_loop",
                trigger_type="systemic_pattern",
                service=event.resource,
                diagnosis_code=issue.get("pattern_code", "systemic_degradation"),
                confidence=float(issue.get("confidence", 0.85)),
                impact=issue.get("severity", "high"),
                reasoning=issue.get("patterns", []),
                suggested_playbooks=issue.get("recommended_actions", []),
                metadata=issue,
                created_at=datetime.now(timezone.utc)
            )
            
            await self._emit_healing_trigger(trigger)
        
        except Exception as e:
            print(f"  Warning: Systemic issue handler error: {e}")
    
    # ========== PROACTIVE INTELLIGENCE TRIGGERS (ML/DL) ==========
    
    async def _handle_anomaly_forecast(self, event: TriggerEvent):
        """Handle ML/DL anomaly forecasts"""
        try:
            forecast = event.payload
            
            trigger = IntelligentTrigger(
                trigger_id=f"ml_forecast_{forecast.get('forecast_id')}",
                source_subsystem="proactive_ml",
                trigger_type="ml_anomaly_forecast",
                service=forecast.get("node_id", "unknown"),
                diagnosis_code=forecast.get("anomaly_type", "predicted_anomaly"),
                confidence=float(forecast.get("confidence", 0.7)),
                impact=forecast.get("severity", "moderate"),
                reasoning=forecast.get("contributing_factors", []),
                suggested_playbooks=[forecast.get("recommended_action", "increase_logging")],
                metadata={
                    **forecast,
                    "ml_model": "anomaly_forecaster",
                    "predicted_time": forecast.get("predicted_time")
                },
                created_at=datetime.now(timezone.utc)
            )
            
            await self._emit_healing_trigger(trigger)
            
            print(f"  [AI] ML Forecast: {forecast.get('node_id')} - {forecast.get('anomaly_type')} (conf: {forecast.get('confidence')})")
        
        except Exception as e:
            print(f"  Warning: Anomaly forecast handler error: {e}")
    
    async def _handle_capacity_prediction(self, event: TriggerEvent):
        """Handle ML capacity predictions"""
        try:
            prediction = event.payload
            shortfall = float(prediction.get("shortfall", 0))
            
            if shortfall > 0:  # Only trigger if capacity shortfall predicted
                trigger = IntelligentTrigger(
                    trigger_id=f"ml_capacity_{prediction.get('prediction_id')}",
                    source_subsystem="proactive_ml",
                    trigger_type="ml_capacity_prediction",
                    service=prediction.get("resource_type", "unknown"),
                    diagnosis_code="capacity_shortage_predicted",
                    confidence=float(prediction.get("confidence", 0.8)),
                    impact="medium" if shortfall < 0.3 else "high",
                    reasoning=[
                        f"Predicted shortfall: {shortfall:.1%}",
                        f"Current: {prediction.get('current_capacity')}",
                        f"Predicted demand: {prediction.get('predicted_demand')}",
                        f"Time: {prediction.get('predicted_time')}"
                    ],
                    suggested_playbooks=["scale_up_instances", "warm_cache"],
                    metadata=prediction,
                    created_at=datetime.now(timezone.utc)
                )
                
                await self._emit_healing_trigger(trigger)
                
                print(f"  [AI] ML Capacity: {prediction.get('resource_type')} - {shortfall:.1%} shortfall predicted")
        
        except Exception as e:
            print(f"  Warning: Capacity prediction handler error: {e}")
    
    async def _handle_risk_assessment(self, event: TriggerEvent):
        """Handle ML risk assessments"""
        try:
            assessment = event.payload
            risk_level = assessment.get("risk_level", "low")
            
            if risk_level in ["high", "critical"]:
                trigger = IntelligentTrigger(
                    trigger_id=f"ml_risk_{assessment.get('assessment_id')}",
                    source_subsystem="proactive_ml",
                    trigger_type="ml_risk_assessment",
                    service=assessment.get("node_id", "unknown"),
                    diagnosis_code="high_risk_detected",
                    confidence=float(assessment.get("risk_score", 0.75)),
                    impact=risk_level,
                    reasoning=[f"{k}: {v}" for k, v in assessment.get("risk_factors", {}).items()],
                    suggested_playbooks=assessment.get("recommended_maintenance", ["increase_logging"]),
                    metadata=assessment,
                    created_at=datetime.now(timezone.utc)
                )
                
                await self._emit_healing_trigger(trigger)
                
                print(f"  [AI] ML Risk: {assessment.get('node_id')} - {risk_level} risk detected")
        
        except Exception as e:
            print(f"  Warning: Risk assessment handler error: {e}")
    
    async def _handle_drift_detection(self, event: TriggerEvent):
        """Handle ML drift detection"""
        try:
            drift = event.payload
            
            trigger = IntelligentTrigger(
                trigger_id=f"ml_drift_{event.resource}_{int(datetime.now().timestamp())}",
                source_subsystem="proactive_ml",
                trigger_type="ml_drift_detected",
                service=event.resource,
                diagnosis_code=drift.get("drift_type", "performance_drift"),
                confidence=float(drift.get("confidence", 0.75)),
                impact=drift.get("severity", "medium"),
                reasoning=[
                    f"Baseline: {drift.get('baseline_value')}",
                    f"Current: {drift.get('current_value')}",
                    f"Drift: {drift.get('drift_magnitude')}"
                ],
                suggested_playbooks=["restart_service", "rollback_flag"],
                metadata=drift,
                created_at=datetime.now(timezone.utc)
            )
            
            await self._emit_healing_trigger(trigger)
            
            print(f"  [AI] ML Drift: {event.resource} - {drift.get('drift_type')} detected")
        
        except Exception as e:
            print(f"  Warning: Drift detection handler error: {e}")
    
    # ========== AGENTIC SPINE TRIGGERS ==========
    
    async def _handle_cross_domain_alert(self, event: TriggerEvent):
        """Handle cross-domain alerts from agentic spine"""
        try:
            alert = event.payload
            
            trigger = IntelligentTrigger(
                trigger_id=f"agentic_{alert.get('alert_id')}",
                source_subsystem="agentic_spine",
                trigger_type="cross_domain_alert",
                service=event.resource,
                diagnosis_code=alert.get("issue_type", "cross_domain_issue"),
                confidence=float(alert.get("confidence", 0.8)),
                impact=alert.get("impact", "moderate"),
                reasoning=alert.get("affected_domains", []),
                suggested_playbooks=alert.get("suggested_actions", []),
                metadata=alert,
                created_at=datetime.now(timezone.utc)
            )
            
            await self._emit_healing_trigger(trigger)
            
            print(f"  🧠 Agentic: {event.resource} - cross-domain alert")
        
        except Exception as e:
            print(f"  Warning: Cross-domain alert handler error: {e}")
    
    async def _handle_health_degradation(self, event: TriggerEvent):
        """Handle health degradation from agentic spine"""
        try:
            degradation = event.payload
            
            trigger = IntelligentTrigger(
                trigger_id=f"health_deg_{event.resource}_{int(datetime.now().timestamp())}",
                source_subsystem="agentic_spine",
                trigger_type="health_degradation",
                service=event.resource,
                diagnosis_code="general_degradation",
                confidence=float(degradation.get("confidence", 0.75)),
                impact=degradation.get("severity", "medium"),
                reasoning=degradation.get("symptoms", []),
                suggested_playbooks=["increase_logging", "restart_service"],
                metadata=degradation,
                created_at=datetime.now(timezone.utc)
            )
            
            await self._emit_healing_trigger(trigger)
        
        except Exception as e:
            print(f"  Warning: Health degradation handler error: {e}")
    
    # ========== IMMUTABLE LOG PATTERN TRIGGERS ==========
    
    async def _handle_pattern_detection(self, event: TriggerEvent):
        """Handle patterns detected in immutable log"""
        try:
            pattern = event.payload
            
            trigger = IntelligentTrigger(
                trigger_id=f"pattern_{pattern.get('pattern_id')}",
                source_subsystem="immutable_log",
                trigger_type="pattern_detected",
                service=pattern.get("resource", "unknown"),
                diagnosis_code=pattern.get("pattern_type", "recurring_pattern"),
                confidence=float(pattern.get("confidence", 0.7)),
                impact=pattern.get("severity", "medium"),
                reasoning=[
                    f"Pattern: {pattern.get('pattern_description')}",
                    f"Occurrences: {pattern.get('occurrence_count')}",
                    f"Timespan: {pattern.get('timespan')}"
                ],
                suggested_playbooks=pattern.get("recommended_actions", []),
                metadata=pattern,
                created_at=datetime.now(timezone.utc)
            )
            
            await self._emit_healing_trigger(trigger)
            
            print(f"  📜 Log Pattern: {pattern.get('pattern_type')} detected")
        
        except Exception as e:
            print(f"  Warning: Pattern detection handler error: {e}")
    
    async def _handle_anomaly_sequence(self, event: TriggerEvent):
        """Handle anomaly sequences in immutable log"""
        try:
            sequence = event.payload
            
            trigger = IntelligentTrigger(
                trigger_id=f"seq_{sequence.get('sequence_id')}",
                source_subsystem="immutable_log",
                trigger_type="anomaly_sequence",
                service=event.resource,
                diagnosis_code="anomalous_sequence",
                confidence=float(sequence.get("confidence", 0.75)),
                impact=sequence.get("severity", "high"),
                reasoning=sequence.get("sequence_events", []),
                suggested_playbooks=["rollback_flag", "restart_service"],
                metadata=sequence,
                created_at=datetime.now(timezone.utc)
            )
            
            await self._emit_healing_trigger(trigger)
        
        except Exception as e:
            print(f"  Warning: Anomaly sequence handler error: {e}")
    
    # ========== HELPER METHODS ==========
    
    async def _emit_healing_trigger(self, trigger: IntelligentTrigger):
        """Emit a unified self-healing trigger event"""
        
        # Store in history
        self.trigger_history.append(trigger)
        if len(self.trigger_history) > self.max_history:
            self.trigger_history.pop(0)
        
        # Log to immutable ledger
        await immutable_log.append(
            actor=trigger.source_subsystem,
            action="intelligent_trigger",
            resource=trigger.service,
            subsystem="intelligent_triggers",
            payload={
                "trigger_id": trigger.trigger_id,
                "trigger_type": trigger.trigger_type,
                "diagnosis_code": trigger.diagnosis_code,
                "confidence": trigger.confidence,
                "impact": trigger.impact,
                "suggested_playbooks": trigger.suggested_playbooks
            },
            result="emitted"
        )
        
        # Publish as self_heal.prediction for scheduler to handle
        await trigger_mesh.publish(TriggerEvent(
            event_type="self_heal.prediction",
            source=trigger.source_subsystem,
            actor="intelligent_triggers",
            resource=trigger.service,
            payload={
                "code": trigger.diagnosis_code,
                "title": f"{trigger.trigger_type.replace('_', ' ').title()}",
                "likelihood": trigger.confidence,
                "impact": trigger.impact,
                "suggested_playbooks": trigger.suggested_playbooks,
                "reasons": trigger.reasoning,
                "source": trigger.source_subsystem,
                "metadata": trigger.metadata
            },
            timestamp=datetime.now(timezone.utc)
        ))
    
    def _infer_playbooks_from_directive(self, directive: Dict) -> List[str]:
        """Infer appropriate playbooks from meta loop directive"""
        directive_type = directive.get("directive_type", "")
        
        mapping = {
            "adjust_threshold": ["increase_logging"],
            "disable_playbook": ["rollback_flag"],
            "rollback_change": ["rollback_flag", "restart_service"],
            "enable_probe": ["increase_logging"],
        }
        
        return mapping.get(directive_type, ["increase_logging"])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about intelligent triggers"""
        
        if not self.trigger_history:
            return {
                "total_triggers": 0,
                "by_source": {},
                "by_type": {},
                "avg_confidence": 0.0
            }
        
        by_source = {}
        by_type = {}
        confidences = []
        
        for trigger in self.trigger_history:
            by_source[trigger.source_subsystem] = by_source.get(trigger.source_subsystem, 0) + 1
            by_type[trigger.trigger_type] = by_type.get(trigger.trigger_type, 0) + 1
            confidences.append(trigger.confidence)
        
        return {
            "total_triggers": len(self.trigger_history),
            "by_source": by_source,
            "by_type": by_type,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
            "last_trigger": self.trigger_history[-1].created_at.isoformat() if self.trigger_history else None
        }


# Singleton instance
intelligent_trigger_manager = IntelligentTriggerManager()
