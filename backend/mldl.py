from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from datetime import datetime
from .models import Base, async_session

class MLEvent(Base):
    """Machine Learning / Deep Learning lifecycle events"""
    __tablename__ = "ml_events"
    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), nullable=False)
    model_name = Column(String(128))
    version = Column(String(32))
    accuracy = Column(Float)
    validation_score = Column(Float)
    deployment_status = Column(String(32))
    event_metadata = Column(Text)
    actor = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MLDLManager:
    """Meta-learning and model lifecycle management"""
    
    async def log_training_event(
        self,
        model_name: str,
        event_type: str,
        accuracy: float = None,
        actor: str = "grace"
    ):
        """Log ML training/validation event"""
        async with async_session() as session:
            event = MLEvent(
                event_type=event_type,
                model_name=model_name,
                accuracy=accuracy,
                actor=actor
            )
            session.add(event)
            await session.commit()
            
            print(f"📊 MLDL: {event_type} for {model_name}")
            
            from .trigger_mesh import trigger_mesh, TriggerEvent
            await trigger_mesh.publish(TriggerEvent(
                event_type=f"mldl.{event_type}",
                source="mldl",
                actor=actor,
                resource=model_name,
                payload={"accuracy": accuracy},
                timestamp=datetime.utcnow()
            ))
    
    async def check_deployment_approval(self, model_name: str, accuracy: float) -> bool:
        """Check if model deployment needs governance approval"""
        if accuracy < 0.7:
            print(f"[WARN] MLDL: {model_name} accuracy {accuracy} requires approval")
            return False
        return True

mldl_manager = MLDLManager()
