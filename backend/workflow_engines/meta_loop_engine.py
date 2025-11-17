"""
Meta-Loop Recommendation Application Engine
Applies meta-loop recommendations with safety checks and metrics
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, select
from sqlalchemy.sql import func
from .models import Base, async_session

class AppliedRecommendation(Base):
    """Track applied meta-loop recommendations with before/after metrics"""
    __tablename__ = "applied_recommendations"
    id = Column(Integer, primary_key=True)
    meta_analysis_id = Column(Integer, nullable=False)
    recommendation_type = Column(String(64), nullable=False)
    target = Column(String(128), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    before_metrics = Column(JSON)
    after_metrics = Column(JSON)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    applied_by = Column(String(64), default="system")
    rolled_back = Column(Boolean, default=False)
    rollback_reason = Column(Text)
    effectiveness_score = Column(Float)

class RecommendationApplicator:
    """Applies meta-loop recommendations with safety and measurement"""
    
    async def start(self):
        """Start the applicator (compatibility method)"""
        pass
    
    async def stop(self):
        """Stop the applicator (compatibility method)"""
        pass
    
    def __init__(self):
        self.pending_rollbacks = {}
        self.safety_limits = {
            "task_threshold": {"min": 1, "max": 10},
            "reflection_interval": {"min": 10, "max": 3600},
            "task_priority": {"min": 1, "max": 10},
            "completion_threshold": {"min": 0.1, "max": 1.0}
        }
    
    async def apply_threshold_change(
        self, 
        component: str, 
        threshold_name: str, 
        new_value: float,
        meta_analysis_id: int,
        approver: str = "system"
    ) -> Dict[str, Any]:
        """Apply threshold change with validation and tracking"""
        
        if not await self._validate_threshold(threshold_name, new_value):
            return {
                "success": False,
                "error": f"Value {new_value} outside safety limits for {threshold_name}"
            }
        
        before_metrics = await self.measure_before_metrics(component)
        
        from .meta_loop import MetaLoopConfig
        async with async_session() as session:
            config_key = f"{component}.{threshold_name}"
            
            result = await session.execute(
                select(MetaLoopConfig).where(MetaLoopConfig.config_key == config_key)
            )
            config = result.scalar_one_or_none()
            
            old_value = None
            if config:
                old_value = config.config_value
                config.config_value = str(new_value)
                config.last_updated_by = approver
                config.last_updated_at = datetime.utcnow()
            else:
                config = MetaLoopConfig(
                    config_key=config_key,
                    config_value=str(new_value),
                    config_type="threshold",
                    last_updated_by=approver,
                    approved=True
                )
                session.add(config)
            
            applied = AppliedRecommendation(
                meta_analysis_id=meta_analysis_id,
                recommendation_type="threshold_change",
                target=config_key,
                old_value=old_value,
                new_value=str(new_value),
                before_metrics=before_metrics,
                applied_by=approver
            )
            session.add(applied)
            await session.commit()
            
            print(f"✓ Applied threshold change: {config_key} = {new_value} (was {old_value})")
            
            return {
                "success": True,
                "applied_id": applied.id,
                "old_value": old_value,
                "new_value": new_value,
                "before_metrics": before_metrics
            }
    
    async def apply_interval_change(
        self, 
        loop_name: str, 
        new_interval: int,
        meta_analysis_id: int,
        approver: str = "system"
    ) -> Dict[str, Any]:
        """Change interval for a reflection/meta loop"""
        
        if not self.safety_limits["reflection_interval"]["min"] <= new_interval <= self.safety_limits["reflection_interval"]["max"]:
            return {
                "success": False,
                "error": f"Interval {new_interval}s outside safe range"
            }
        
        before_metrics = await self.measure_before_metrics(f"loop.{loop_name}")
        
        from .meta_loop import MetaLoopConfig
        async with async_session() as session:
            config_key = f"{loop_name}.interval"
            
            result = await session.execute(
                select(MetaLoopConfig).where(MetaLoopConfig.config_key == config_key)
            )
            config = result.scalar_one_or_none()
            
            old_value = None
            if config:
                old_value = config.config_value
                config.config_value = str(new_interval)
                config.last_updated_by = approver
                config.last_updated_at = datetime.utcnow()
            else:
                config = MetaLoopConfig(
                    config_key=config_key,
                    config_value=str(new_interval),
                    config_type="interval",
                    last_updated_by=approver,
                    approved=True
                )
                session.add(config)
            
            applied = AppliedRecommendation(
                meta_analysis_id=meta_analysis_id,
                recommendation_type="interval_change",
                target=loop_name,
                old_value=old_value,
                new_value=str(new_interval),
                before_metrics=before_metrics,
                applied_by=approver
            )
            session.add(applied)
            await session.commit()
            
            if loop_name == "reflection":
                from .reflection import reflection_service
                await reflection_service.stop()
                reflection_service.interval = new_interval
                await reflection_service.start()
                print(f"✓ Reflection loop interval changed to {new_interval}s")
            elif loop_name == "meta_loop":
                from .meta_loop import meta_loop_engine
                await meta_loop_engine.stop()
                meta_loop_engine.interval = new_interval
                await meta_loop_engine.start()
                print(f"✓ Meta-loop interval changed to {new_interval}s")
            
            return {
                "success": True,
                "applied_id": applied.id,
                "old_value": old_value,
                "new_value": new_interval,
                "before_metrics": before_metrics
            }
    
    async def apply_priority_change(
        self, 
        task_type: str, 
        new_priority: int,
        meta_analysis_id: int,
        approver: str = "system"
    ) -> Dict[str, Any]:
        """Change default priority for auto-generated task type"""
        
        if not self.safety_limits["task_priority"]["min"] <= new_priority <= self.safety_limits["task_priority"]["max"]:
            return {
                "success": False,
                "error": f"Priority {new_priority} outside safe range (1-10)"
            }
        
        before_metrics = await self.measure_before_metrics(f"tasks.{task_type}")
        
        from .meta_loop import MetaLoopConfig
        async with async_session() as session:
            config_key = f"task_priority.{task_type}"
            
            result = await session.execute(
                select(MetaLoopConfig).where(MetaLoopConfig.config_key == config_key)
            )
            config = result.scalar_one_or_none()
            
            old_value = None
            if config:
                old_value = config.config_value
                config.config_value = str(new_priority)
                config.last_updated_by = approver
                config.last_updated_at = datetime.utcnow()
            else:
                config = MetaLoopConfig(
                    config_key=config_key,
                    config_value=str(new_priority),
                    config_type="priority",
                    last_updated_by=approver,
                    approved=True
                )
                session.add(config)
            
            applied = AppliedRecommendation(
                meta_analysis_id=meta_analysis_id,
                recommendation_type="priority_change",
                target=task_type,
                old_value=old_value,
                new_value=str(new_priority),
                before_metrics=before_metrics,
                applied_by=approver
            )
            session.add(applied)
            await session.commit()
            
            print(f"✓ Task priority changed: {task_type} = {new_priority}")
            
            return {
                "success": True,
                "applied_id": applied.id,
                "old_value": old_value,
                "new_value": new_priority,
                "before_metrics": before_metrics
            }
    
    async def validate_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform safety checks on a recommendation before applying"""
        
        rec_type = recommendation.get("type")
        
        if rec_type == "threshold_change":
            threshold = recommendation.get("threshold_name")
            new_val = recommendation.get("new_value")
            
            if threshold not in self.safety_limits:
                return {"valid": False, "reason": f"Unknown threshold: {threshold}"}
            
            limits = self.safety_limits[threshold]
            if not limits["min"] <= new_val <= limits["max"]:
                return {"valid": False, "reason": f"Value {new_val} outside limits {limits}"}
        
        elif rec_type == "interval_change":
            interval = recommendation.get("new_interval")
            limits = self.safety_limits["reflection_interval"]
            if not limits["min"] <= interval <= limits["max"]:
                return {"valid": False, "reason": f"Interval {interval}s outside safe range"}
        
        elif rec_type == "priority_change":
            priority = recommendation.get("new_priority")
            limits = self.safety_limits["task_priority"]
            if not limits["min"] <= priority <= limits["max"]:
                return {"valid": False, "reason": f"Priority {priority} outside range 1-10"}
        
        else:
            return {"valid": False, "reason": f"Unknown recommendation type: {rec_type}"}
        
        return {"valid": True, "risk_level": self._assess_risk(recommendation)}
    
    def _assess_risk(self, recommendation: Dict[str, Any]) -> str:
        """Assess risk level of recommendation"""
        
        rec_type = recommendation.get("type")
        
        if rec_type == "interval_change":
            interval = recommendation.get("new_interval", 0)
            if interval < 30:
                return "high"
            elif interval < 60:
                return "medium"
            else:
                return "low"
        
        confidence = recommendation.get("confidence", 0.5)
        if confidence < 0.5:
            return "high"
        elif confidence < 0.7:
            return "medium"
        else:
            return "low"
    
    async def _validate_threshold(self, threshold_name: str, new_value: float) -> bool:
        """Validate threshold change against safety limits"""
        if threshold_name not in self.safety_limits:
            return True
        
        limits = self.safety_limits[threshold_name]
        return limits["min"] <= new_value <= limits["max"]
    
    async def measure_before_metrics(self, component: str) -> Dict[str, Any]:
        """Capture current performance metrics before applying change"""
        
        from .models import Task
        from .reflection import Reflection
        
        lookback = datetime.utcnow() - timedelta(hours=24)
        
        async with async_session() as session:
            task_result = await session.execute(
                select(Task).where(Task.created_at >= lookback)
            )
            tasks = task_result.scalars().all()
            
            ref_result = await session.execute(
                select(Reflection).where(Reflection.generated_at >= lookback)
            )
            reflections = ref_result.scalars().all()
            
            completed_tasks = len([t for t in tasks if t.status == "completed"])
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "component": component,
                "total_tasks_24h": len(tasks),
                "completed_tasks_24h": completed_tasks,
                "completion_rate": completed_tasks / len(tasks) if tasks else 0,
                "reflections_24h": len(reflections),
                "auto_tasks_24h": len([t for t in tasks if t.auto_generated])
            }
    
    async def measure_after_metrics(self, applied_id: int, wait_hours: int = 24) -> Dict[str, Any]:
        """Measure metrics after change has been in effect"""
        
        async with async_session() as session:
            result = await session.execute(
                select(AppliedRecommendation).where(AppliedRecommendation.id == applied_id)
            )
            applied = result.scalar_one_or_none()
            
            if not applied:
                return {"error": "Applied recommendation not found"}
            
            after_metrics = await self.measure_before_metrics(applied.target)
            
            before = applied.before_metrics
            effectiveness = 0
            
            if before and "completion_rate" in before and "completion_rate" in after_metrics:
                before_rate = before["completion_rate"]
                after_rate = after_metrics["completion_rate"]
                
                if before_rate > 0:
                    effectiveness = ((after_rate - before_rate) / before_rate) * 100
            
            applied.after_metrics = after_metrics
            applied.effectiveness_score = effectiveness
            await session.commit()
            
            print(f"📊 Effectiveness: {effectiveness:+.1f}% for recommendation {applied_id}")
            
            from .meta_loop import meta_meta_engine
            await meta_meta_engine.evaluate_improvement(
                applied.meta_analysis_id,
                f"{applied.recommendation_type}_{applied.target}",
                before.get("completion_rate", 0),
                after_metrics.get("completion_rate", 0)
            )
            
            if effectiveness < -20:
                await self.rollback_change(applied_id, "Performance degraded significantly")
            
            return {
                "before": before,
                "after": after_metrics,
                "effectiveness": effectiveness
            }
    
    async def rollback_change(self, applied_id: int, reason: str = "Manual rollback") -> Dict[str, Any]:
        """Revert a change if it made things worse"""
        
        async with async_session() as session:
            result = await session.execute(
                select(AppliedRecommendation).where(AppliedRecommendation.id == applied_id)
            )
            applied = result.scalar_one_or_none()
            
            if not applied:
                return {"success": False, "error": "Applied recommendation not found"}
            
            if applied.rolled_back:
                return {"success": False, "error": "Already rolled back"}
            
            from .meta_loop import MetaLoopConfig
            config_result = await session.execute(
                select(MetaLoopConfig).where(MetaLoopConfig.config_key.like(f"%{applied.target}%"))
            )
            config = config_result.scalar_one_or_none()
            
            if config and applied.old_value:
                config.config_value = applied.old_value
                config.last_updated_by = "rollback_system"
                config.last_updated_at = datetime.utcnow()
            
            applied.rolled_back = True
            applied.rollback_reason = reason
            await session.commit()
            
            print(f"⏮️  Rolled back recommendation {applied_id}: {reason}")
            
            return {
                "success": True,
                "rolled_back_to": applied.old_value,
                "reason": reason
            }

recommendation_applicator = RecommendationApplicator()
