import asyncio
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, select
from sqlalchemy.sql import func
from .models import Base, async_session, Task, Goal
from .reflection import Reflection

class MetaLoopConfig(Base):
    """Configurations for meta-loop behavior"""
    __tablename__ = "meta_loop_configs"
    id = Column(Integer, primary_key=True)
    config_key = Column(String(128), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(32))
    last_updated_by = Column(String(64))
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    approved = Column(Boolean, default=False)

class MetaAnalysis(Base):
    """Level 1 meta-loop: analyzes operational effectiveness"""
    __tablename__ = "meta_analyses"
    id = Column(Integer, primary_key=True)
    analysis_type = Column(String(64), nullable=False)
    subject = Column(String(128))
    findings = Column(Text, nullable=False)
    recommendation = Column(Text)
    confidence = Column(Float, default=0.5)
    applied = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetaMetaEvaluation(Base):
    """Level 2: evaluates meta-loop improvements"""
    __tablename__ = "meta_meta_evaluations"
    id = Column(Integer, primary_key=True)
    meta_analysis_id = Column(Integer)
    metric_name = Column(String(128))
    before_value = Column(Float)
    after_value = Column(Float)
    improvement = Column(Float)
    conclusion = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetaLoopEngine:
    """Level 1: Optimizes operational loops"""
    
    def __init__(self, interval_seconds: int = 300):
        self.interval = interval_seconds
        self._task = None
        self._running = False
    
    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            print(f"✓ Meta-loop started (Level 1 optimization, interval: {self.interval}s)")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        print("✓ Meta-loop stopped")
    
    async def _loop(self):
        try:
            while self._running:
                await self.analyze_and_optimize()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass
    
    async def analyze_and_optimize(self):
        """Level 1: Analyze operational effectiveness"""
        
        analyses = []
        
        task_effectiveness = await self._analyze_task_completion_rate()
        if task_effectiveness:
            analyses.append(task_effectiveness)
        
        reflection_quality = await self._analyze_reflection_utility()
        if reflection_quality:
            analyses.append(reflection_quality)
        
        async with async_session() as session:
            for analysis in analyses:
                meta = MetaAnalysis(
                    analysis_type=analysis["type"],
                    subject=analysis["subject"],
                    findings=analysis["findings"],
                    recommendation=analysis["recommendation"],
                    confidence=analysis["confidence"]
                )
                session.add(meta)
            
            if analyses:
                await session.commit()
                print(f"🔄 Meta-loop: Generated {len(analyses)} optimizations")
    
    async def _analyze_task_completion_rate(self):
        """Analyze if auto-generated tasks are being completed"""
        lookback = datetime.utcnow() - timedelta(days=1)
        
        async with async_session() as session:
            result = await session.execute(
                select(Task).where(
                    Task.created_at >= lookback,
                    Task.auto_generated == True
                )
            )
            auto_tasks = result.scalars().all()
            
            if not auto_tasks:
                return None
            
            completed = len([t for t in auto_tasks if t.status == "completed"])
            completion_rate = completed / len(auto_tasks) if auto_tasks else 0
            
            if completion_rate < 0.3:
                return {
                    "type": "task_effectiveness",
                    "subject": "auto_task_generation",
                    "findings": f"Only {completion_rate*100:.1f}% of auto-tasks completed. May be generating too many or wrong priorities.",
                    "recommendation": "Increase threshold for task creation from 3 to 5 mentions, or improve task descriptions.",
                    "confidence": 0.7
                }
            
            return None
    
    async def _analyze_reflection_utility(self):
        """Check if reflections are leading to useful actions"""
        lookback = datetime.utcnow() - timedelta(hours=24)
        
        async with async_session() as session:
            ref_result = await session.execute(
                select(Reflection).where(Reflection.generated_at >= lookback)
            )
            reflections = ref_result.scalars().all()
            
            task_result = await session.execute(
                select(Task).where(
                    Task.created_at >= lookback,
                    Task.auto_generated == True
                )
            )
            auto_tasks = task_result.scalars().all()
            
            if len(reflections) > 10 and len(auto_tasks) == 0:
                return {
                    "type": "reflection_utility",
                    "subject": "reflection_to_task_ratio",
                    "findings": f"{len(reflections)} reflections generated but 0 tasks created. Thresholds may be too high.",
                    "recommendation": "Lower task creation threshold from current 3 mentions to 2.",
                    "confidence": 0.8
                }
            
            return None

class MetaMetaEngine:
    """Level 2: Evaluates meta-loop improvements"""
    
    async def evaluate_improvement(self, meta_analysis_id: int, metric_name: str, before: float, after: float):
        """Check if a meta-loop change actually helped"""
        
        improvement = ((after - before) / before * 100) if before > 0 else 0
        
        conclusion = "Improvement" if improvement > 10 else "No significant change" if improvement > -10 else "Regression"
        
        async with async_session() as session:
            eval = MetaMetaEvaluation(
                meta_analysis_id=meta_analysis_id,
                metric_name=metric_name,
                before_value=before,
                after_value=after,
                improvement=improvement,
                conclusion=conclusion
            )
            session.add(eval)
            await session.commit()
            
            print(f"🔄🔄 Meta-meta: {metric_name} changed {improvement:+.1f}% - {conclusion}")
            
            if improvement < -20:
                from .trigger_mesh import trigger_mesh, TriggerEvent
                await trigger_mesh.publish(TriggerEvent(
                    event_type="meta.regression_detected",
                    source="meta_meta",
                    actor="system",
                    resource=metric_name,
                    payload={"improvement": improvement, "before": before, "after": after},
                    timestamp=datetime.utcnow()
                ))

meta_loop_engine = MetaLoopEngine(interval_seconds=300)
meta_meta_engine = MetaMetaEngine()
