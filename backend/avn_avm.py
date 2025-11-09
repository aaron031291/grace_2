from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from .models import Base, async_session
from datetime import datetime

class VerificationEvent(Base):
    """Autonomous Verification Network/Mesh events"""
    __tablename__ = "verification_events"
    id = Column(Integer, primary_key=True)
    verification_type = Column(String(64), nullable=False)
    target_component = Column(String(128))
    verification_method = Column(String(64))
    result = Column(String(32))
    passed = Column(Boolean, default=False)  # Whether verification passed
    anomaly_score = Column(Float)
    confidence = Column(Float)
    details = Column(Text)
    verified_by = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AVNManager:
    """Autonomous Verification Network"""
    
    async def verify_component(
        self,
        component: str,
        method: str = "health_check"
    ) -> dict:
        """Verify component integrity"""
        
        anomaly_score = 0.0
        result = "pass"
        
        if component == "reflection_service":
            from .reflection import reflection_service
            if not reflection_service._running:
                anomaly_score = 1.0
                result = "fail"
        
        elif component == "task_executor":
            from .task_executor import task_executor
            if len(task_executor.workers) == 0:
                anomaly_score = 1.0
                result = "fail"
        
        async with async_session() as session:
            event = VerificationEvent(
                verification_type=method,
                target_component=component,
                verification_method=method,
                result=result,
                passed=(result == "pass"),
                anomaly_score=anomaly_score,
                confidence=1.0 - anomaly_score,
                details=f"Verified {component} via {method}",
                verified_by="avn"
            )
            session.add(event)
            await session.commit()
        
        if anomaly_score > 0.5:
            print(f"🔍 AVN: Anomaly detected in {component} (score: {anomaly_score})")
            
            from .trigger_mesh import trigger_mesh, TriggerEvent
            await trigger_mesh.publish(TriggerEvent(
                event_type="avn.anomaly_detected",
                source="avn",
                actor="system",
                resource=component,
                payload={"anomaly_score": anomaly_score, "method": method},
                timestamp=datetime.utcnow()
            ))
        
        return {
            "component": component,
            "result": result,
            "anomaly_score": anomaly_score,
            "confidence": 1.0 - anomaly_score
        }

avn_manager = AVNManager()
