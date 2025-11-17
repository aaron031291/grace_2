"""
Alert System for Memory Tables
Monitors conditions and triggers alerts for dashboard
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert:
    """Represents an alert"""
    
    def __init__(
        self,
        alert_id: str,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str,
        metadata: Dict[str, Any] = None
    ):
        self.alert_id = alert_id
        self.severity = severity
        self.title = title
        self.message = message
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        self.acknowledged = False
        self.resolved = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'source': self.source,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'resolved': self.resolved
        }


class AlertSystem:
    """
    Monitors memory tables and triggers alerts based on conditions.
    """
    
    def __init__(self):
        self.registry = None
        self.trust_engine = None
        self.contradiction_detector = None
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_history = 1000
        self._initialized = False
        self._monitoring = False
        self._monitor_task = None
    
    async def initialize(self):
        """Initialize dependencies"""
        if self._initialized:
            return
        
        from backend.memory_tables.registry import table_registry
        from backend.memory_tables.trust_scoring import trust_scoring_engine
        from backend.memory_tables.contradiction_detector import contradiction_detector
        
        self.registry = table_registry
        self.trust_engine = trust_scoring_engine
        self.contradiction_detector = contradiction_detector
        
        if not self.registry.list_tables():
            self.registry.load_all_schemas()
        
        if not self.trust_engine._initialized:
            await self.trust_engine.initialize()
        
        if not self.contradiction_detector._initialized:
            await self.contradiction_detector.initialize()
        
        self._initialized = True
        logger.info("✅ Alert system initialized")
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring"""
        if self._monitoring:
            return
        
        if not self._initialized:
            await self.initialize()
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(interval_seconds))
        logger.info(f"🔔 Alert monitoring started (interval: {interval_seconds}s)")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("🔕 Alert monitoring stopped")
    
    async def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                await self._check_all_conditions()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                await asyncio.sleep(interval)
    
    async def _check_all_conditions(self):
        """Check all alert conditions"""
        # Check trust scores
        await self._check_low_trust()
        
        # Check contradictions
        await self._check_contradictions()
        
        # Check table health
        await self._check_table_health()
        
        # Check ingestion rates
        await self._check_ingestion_rates()
    
    async def _check_low_trust(self):
        """Check for tables with low average trust scores"""
        trust_report = await self.trust_engine.get_trust_report()
        
        for table_name, stats in trust_report['tables'].items():
            avg_trust = stats['avg_trust']
            low_trust_count = stats['low_trust_count']
            total_rows = stats['total_rows']
            
            # Alert if average trust below 0.5
            if avg_trust < 0.5:
                self._create_alert(
                    alert_id=f"low_trust_{table_name}",
                    severity=AlertSeverity.WARNING,
                    title=f"Low Trust Score: {table_name}",
                    message=f"Average trust score is {avg_trust:.1%} (threshold: 50%)",
                    source="trust_monitoring",
                    metadata={
                        'table': table_name,
                        'avg_trust': avg_trust,
                        'low_trust_rows': low_trust_count,
                        'total_rows': total_rows
                    }
                )
            
            # Alert if >30% of rows have low trust
            elif total_rows > 0 and (low_trust_count / total_rows) > 0.3:
                self._create_alert(
                    alert_id=f"high_low_trust_ratio_{table_name}",
                    severity=AlertSeverity.WARNING,
                    title=f"High Low-Trust Ratio: {table_name}",
                    message=f"{low_trust_count}/{total_rows} rows ({(low_trust_count/total_rows)*100:.1f}%) have low trust",
                    source="trust_monitoring",
                    metadata={
                        'table': table_name,
                        'low_trust_count': low_trust_count,
                        'total_rows': total_rows,
                        'ratio': low_trust_count / total_rows
                    }
                )
    
    async def _check_contradictions(self):
        """Check for critical contradictions"""
        summary = await self.contradiction_detector.get_contradiction_summary()
        
        critical_count = summary.get('critical_count', 0)
        total_contradictions = summary.get('total_contradictions', 0)
        
        # Alert on critical contradictions
        if critical_count > 0:
            self._create_alert(
                alert_id="critical_contradictions",
                severity=AlertSeverity.CRITICAL,
                title=f"{critical_count} Critical Contradictions Detected",
                message=f"Found {critical_count} critical contradictions that require immediate attention",
                source="contradiction_detection",
                metadata={
                    'critical_count': critical_count,
                    'total_contradictions': total_contradictions,
                    'by_severity': summary.get('by_severity', {}),
                    'by_table': summary.get('by_table', {})
                }
            )
        
        # Alert if total contradictions exceed threshold
        elif total_contradictions > 50:
            self._create_alert(
                alert_id="high_contradiction_count",
                severity=AlertSeverity.WARNING,
                title=f"{total_contradictions} Contradictions Detected",
                message=f"High number of contradictions detected across tables",
                source="contradiction_detection",
                metadata={
                    'total_contradictions': total_contradictions,
                    'by_table': summary.get('by_table', {})
                }
            )
    
    async def _check_table_health(self):
        """Check overall table health metrics"""
        for table_name in self.registry.list_tables():
            try:
                rows = self.registry.query_rows(table_name, limit=1)
                
                # Alert if table is empty (for critical tables)
                critical_tables = [
                    'memory_self_healing_playbooks',
                    'memory_coding_work_orders',
                    'memory_documents'
                ]
                
                if table_name in critical_tables and not rows:
                    self._create_alert(
                        alert_id=f"empty_table_{table_name}",
                        severity=AlertSeverity.INFO,
                        title=f"Empty Table: {table_name}",
                        message=f"Critical table {table_name} has no data",
                        source="table_health",
                        metadata={'table': table_name}
                    )
            
            except Exception as e:
                # Alert on table access errors
                self._create_alert(
                    alert_id=f"table_error_{table_name}",
                    severity=AlertSeverity.ERROR,
                    title=f"Table Access Error: {table_name}",
                    message=f"Error accessing table: {str(e)}",
                    source="table_health",
                    metadata={'table': table_name, 'error': str(e)}
                )
    
    async def _check_ingestion_rates(self):
        """Check data ingestion rates"""
        # This would integrate with ingestion service
        # For now, placeholder
        pass
    
    def _create_alert(
        self,
        alert_id: str,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str,
        metadata: Dict[str, Any] = None
    ):
        """Create or update an alert"""
        # Check if alert already exists
        if alert_id in self.active_alerts:
            existing = self.active_alerts[alert_id]
            # Update timestamp
            existing.timestamp = datetime.utcnow()
            existing.metadata.update(metadata or {})
            logger.debug(f"Updated alert: {alert_id}")
        else:
            # Create new alert
            alert = Alert(alert_id, severity, title, message, source, metadata)
            self.active_alerts[alert_id] = alert
            
            # Add to history
            self.alert_history.append(alert)
            if len(self.alert_history) > self.max_history:
                self.alert_history.pop(0)
            
            logger.warning(f"🔔 NEW ALERT [{severity.value.upper()}]: {title}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve and remove an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.acknowledged = True
            
            # Move to history only
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None
    ) -> List[Dict[str, Any]]:
        """Get all active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Sort by severity (critical first) then timestamp
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.ERROR: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.INFO: 3
        }
        
        alerts.sort(key=lambda a: (severity_order[a.severity], a.timestamp), reverse=True)
        
        return [a.to_dict() for a in alerts]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alerts"""
        by_severity = defaultdict(int)
        by_source = defaultdict(int)
        
        for alert in self.active_alerts.values():
            by_severity[alert.severity.value] += 1
            by_source[alert.source] += 1
        
        return {
            'total_active': len(self.active_alerts),
            'by_severity': dict(by_severity),
            'by_source': dict(by_source),
            'critical_count': by_severity.get(AlertSeverity.CRITICAL.value, 0),
            'needs_attention': (
                by_severity.get(AlertSeverity.CRITICAL.value, 0) +
                by_severity.get(AlertSeverity.ERROR.value, 0)
            ),
            'timestamp': datetime.utcnow().isoformat()
        }


# Singleton instance
alert_system = AlertSystem()
