"""
AVN (Autonomous Validation Network) Integration for Immutable Log
Logs all anomalies, healing actions, and self-healing outcomes with full audit trail
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .immutable_log import immutable_log


class AVNLogger:
    """
    Specialized logger for AVN system (anomaly detection and self-healing)
    Ensures all anomalies and healing actions are logged to immutable audit trail
    """
    
    def __init__(self):
        self.log = immutable_log
    
    async def log_anomaly_detected(
        self,
        anomaly_id: str,
        detector: str,
        anomaly_type: str,
        severity: str,
        affected_resource: str,
        anomaly_score: float,
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log an anomaly detection
        
        Args:
            anomaly_id: Unique anomaly identifier
            detector: Which detector found it
            anomaly_type: Type of anomaly (drift, spike, pattern, etc.)
            severity: Severity level (low, medium, high, critical)
            affected_resource: What resource is affected
            anomaly_score: Anomaly score (typically 0.0 - 1.0)
            details: Detailed anomaly information
            metadata: Additional context
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "anomaly_id": anomaly_id,
            "detector": detector,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "anomaly_score": anomaly_score,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        return await self.log.append(
            actor=f"avn_detector:{detector}",
            action="ANOMALY_DETECTED",
            resource=affected_resource,
            subsystem="avn",
            payload=payload,
            result=severity
        )
    
    async def log_healing_action(
        self,
        healing_id: str,
        anomaly_id: str,
        healer: str,
        action_type: str,
        action_description: str,
        affected_resource: str,
        success: bool,
        execution_time_seconds: float,
        side_effects: Optional[List[str]] = None
    ) -> int:
        """
        Log a self-healing action
        
        Args:
            healing_id: Unique healing action identifier
            anomaly_id: Related anomaly ID
            healer: Which healing component executed this
            action_type: Type of healing action (restart, rollback, patch, etc.)
            action_description: Human-readable description
            affected_resource: What resource was healed
            success: Whether healing succeeded
            execution_time_seconds: How long it took
            side_effects: Any side effects observed
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "healing_id": healing_id,
            "anomaly_id": anomaly_id,
            "healer": healer,
            "action_type": action_type,
            "action_description": action_description,
            "success": success,
            "execution_time_seconds": execution_time_seconds,
            "side_effects": side_effects or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=f"avn_healer:{healer}",
            action="HEALING_ACTION_EXECUTED",
            resource=affected_resource,
            subsystem="avn",
            payload=payload,
            result="success" if success else "failed"
        )
    
    async def log_healing_cycle(
        self,
        cycle_id: str,
        anomalies_detected: int,
        actions_taken: int,
        actions_successful: int,
        cycle_duration_seconds: float,
        outcome: str,
        summary: str
    ) -> int:
        """
        Log a complete healing cycle
        
        Args:
            cycle_id: Unique cycle identifier
            anomalies_detected: Number of anomalies detected
            actions_taken: Number of healing actions executed
            actions_successful: Number of successful healing actions
            cycle_duration_seconds: Total cycle duration
            outcome: Overall outcome (resolved, partial, failed)
            summary: Summary of the cycle
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "cycle_id": cycle_id,
            "anomalies_detected": anomalies_detected,
            "actions_taken": actions_taken,
            "actions_successful": actions_successful,
            "success_rate": actions_successful / actions_taken if actions_taken > 0 else 0.0,
            "cycle_duration_seconds": cycle_duration_seconds,
            "outcome": outcome,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor="avn_orchestrator",
            action="HEALING_CYCLE_COMPLETED",
            resource=f"cycle:{cycle_id}",
            subsystem="avn",
            payload=payload,
            result=outcome
        )
    
    async def log_drift_detection(
        self,
        drift_id: str,
        detector: str,
        baseline_metric: str,
        baseline_value: float,
        current_value: float,
        drift_magnitude: float,
        drift_direction: str
    ) -> int:
        """
        Log drift detection (gradual anomaly)
        
        Args:
            drift_id: Unique drift identifier
            detector: Which detector found it
            baseline_metric: Metric being monitored
            baseline_value: Expected baseline value
            current_value: Current observed value
            drift_magnitude: How much drift occurred
            drift_direction: Direction of drift (increase, decrease)
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "drift_id": drift_id,
            "detector": detector,
            "baseline_metric": baseline_metric,
            "baseline_value": baseline_value,
            "current_value": current_value,
            "drift_magnitude": drift_magnitude,
            "drift_direction": drift_direction,
            "drift_percent": abs((current_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=f"avn_detector:{detector}",
            action="DRIFT_DETECTED",
            resource=f"metric:{baseline_metric}",
            subsystem="avn",
            payload=payload,
            result="drift"
        )
    
    async def log_rollback(
        self,
        rollback_id: str,
        trigger_anomaly_id: str,
        rollback_target: str,
        from_version: str,
        to_version: str,
        success: bool,
        rollback_duration_seconds: float
    ) -> int:
        """
        Log a rollback action
        
        Args:
            rollback_id: Unique rollback identifier
            trigger_anomaly_id: Anomaly that triggered rollback
            rollback_target: What was rolled back
            from_version: Version being rolled back from
            to_version: Version being rolled back to
            success: Whether rollback succeeded
            rollback_duration_seconds: How long it took
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "rollback_id": rollback_id,
            "trigger_anomaly_id": trigger_anomaly_id,
            "rollback_target": rollback_target,
            "from_version": from_version,
            "to_version": to_version,
            "success": success,
            "rollback_duration_seconds": rollback_duration_seconds,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor="avn_healer:rollback",
            action="ROLLBACK_EXECUTED",
            resource=rollback_target,
            subsystem="avn",
            payload=payload,
            result="success" if success else "failed"
        )
    
    async def log_escalation(
        self,
        escalation_id: str,
        anomaly_id: str,
        escalation_reason: str,
        severity: str,
        escalated_to: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log an escalation (when self-healing can't resolve)
        
        Args:
            escalation_id: Unique escalation identifier
            anomaly_id: Related anomaly
            escalation_reason: Why escalation was needed
            severity: Severity of the issue
            escalated_to: Who/what it was escalated to
            metadata: Additional context
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "escalation_id": escalation_id,
            "anomaly_id": anomaly_id,
            "escalation_reason": escalation_reason,
            "severity": severity,
            "escalated_to": escalated_to,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        return await self.log.append(
            actor="avn_orchestrator",
            action="ESCALATED",
            resource=f"anomaly:{anomaly_id}",
            subsystem="avn",
            payload=payload,
            result="escalated"
        )
    
    async def log_learning_update(
        self,
        update_id: str,
        learning_type: str,
        learned_pattern: str,
        confidence: float,
        based_on_cycles: int,
        model_updated: str
    ) -> int:
        """
        Log a learning/adaptation update
        
        Args:
            update_id: Unique update identifier
            learning_type: Type of learning (pattern, threshold, strategy)
            learned_pattern: What was learned
            confidence: Confidence in the learning
            based_on_cycles: Number of cycles this learning is based on
            model_updated: Which model/component was updated
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "update_id": update_id,
            "learning_type": learning_type,
            "learned_pattern": learned_pattern,
            "confidence": confidence,
            "based_on_cycles": based_on_cycles,
            "model_updated": model_updated,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor="avn_learning",
            action="LEARNING_UPDATE_APPLIED",
            resource=model_updated,
            subsystem="avn",
            payload=payload,
            result="applied"
        )
    
    async def get_anomaly_history(
        self,
        hours_back: int = 24,
        limit: int = 100
    ) -> list:
        """
        Get anomaly detection history
        
        Args:
            hours_back: How many hours to look back
            limit: Maximum number of entries to return
            
        Returns:
            List of anomaly log entries
        """
        
        entries = await self.log.get_entries(
            subsystem="avn",
            limit=limit * 2
        )
        
        # Filter for anomalies
        anomalies = [
            entry for entry in entries
            if 'ANOMALY_DETECTED' in entry['action'] or 'DRIFT_DETECTED' in entry['action']
        ]
        
        return anomalies[:limit]
    
    async def get_healing_history(
        self,
        hours_back: int = 24,
        limit: int = 100
    ) -> list:
        """
        Get healing action history
        
        Args:
            hours_back: How many hours to look back
            limit: Maximum number of entries to return
            
        Returns:
            List of healing log entries
        """
        
        entries = await self.log.get_entries(
            subsystem="avn",
            limit=limit * 2
        )
        
        # Filter for healing actions
        healing = [
            entry for entry in entries
            if 'HEALING' in entry['action'] or 'ROLLBACK' in entry['action']
        ]
        
        return healing[:limit]
    
    async def get_cycle_history(
        self,
        limit: int = 50
    ) -> list:
        """
        Get healing cycle history
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of cycle log entries
        """
        
        entries = await self.log.get_entries(
            subsystem="avn",
            limit=limit * 2
        )
        
        # Filter for cycles
        cycles = [
            entry for entry in entries
            if 'CYCLE_COMPLETED' in entry['action']
        ]
        
        return cycles[:limit]


avn_logger = AVNLogger()
