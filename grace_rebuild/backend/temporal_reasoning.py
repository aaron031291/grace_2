import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
from sqlalchemy import select, func
from .models import async_session, Task, ChatMessage
from .task_executor import ExecutionTask
from .temporal_models import EventPattern, DurationEstimate, TemporalAnomaly, PredictionRecord
from .governance_models import SecurityEvent
import statistics

class TemporalReasoner:
    """Analyzes temporal patterns and predicts future events"""
    
    def __init__(self):
        self.markov_chains: Dict[str, Dict[str, float]] = {}
        self.pattern_cache: Dict[str, List[Dict]] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize by loading historical patterns"""
        if not self._initialized:
            await self._build_markov_chains()
            await self._compute_duration_stats()
            self._initialized = True
            print("✓ Temporal reasoner initialized")
    
    async def analyze_sequences(self, lookback_hours: int = 24) -> List[Dict[str, Any]]:
        """Find common event patterns in recent history"""
        cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        sequences = []
        
        async with async_session() as session:
            task_result = await session.execute(
                select(Task)
                .where(Task.created_at >= cutoff)
                .order_by(Task.created_at)
            )
            tasks = task_result.scalars().all()
            
            exec_result = await session.execute(
                select(ExecutionTask)
                .where(ExecutionTask.created_at >= cutoff)
                .order_by(ExecutionTask.created_at)
            )
            exec_tasks = exec_result.scalars().all()
            
            sec_result = await session.execute(
                select(SecurityEvent)
                .where(SecurityEvent.created_at >= cutoff)
                .order_by(SecurityEvent.created_at)
            )
            security_events = sec_result.scalars().all()
        
        events = []
        for task in tasks:
            events.append({
                "type": "task_created",
                "status": task.status,
                "priority": task.priority,
                "timestamp": task.created_at,
                "completed_at": task.completed_at
            })
        
        for exec_task in exec_tasks:
            events.append({
                "type": "execution_task",
                "task_type": exec_task.task_type,
                "status": exec_task.status,
                "timestamp": exec_task.created_at,
                "completed_at": exec_task.completed_at
            })
        
        for sec_event in security_events:
            events.append({
                "type": "security_event",
                "event_type": sec_event.event_type,
                "severity": sec_event.severity,
                "timestamp": sec_event.created_at
            })
        
        events.sort(key=lambda e: e["timestamp"])
        
        patterns = self._find_sequential_patterns(events)
        
        await self._save_patterns(patterns)
        
        return patterns
    
    def _find_sequential_patterns(self, events: List[Dict]) -> List[Dict]:
        """Identify recurring sequences of events"""
        patterns = []
        window_size = 3
        
        sequence_counts = Counter()
        sequence_durations = defaultdict(list)
        
        for i in range(len(events) - window_size + 1):
            window = events[i:i+window_size]
            seq_types = tuple(e["type"] for e in window)
            sequence_counts[seq_types] += 1
            
            if len(window) >= 2:
                duration = (window[-1]["timestamp"] - window[0]["timestamp"]).total_seconds()
                sequence_durations[seq_types].append(duration)
        
        for seq, count in sequence_counts.most_common(10):
            if count >= 2:
                avg_duration = statistics.mean(sequence_durations[seq]) if sequence_durations[seq] else 0
                patterns.append({
                    "pattern_type": "sequence",
                    "sequence": list(seq),
                    "frequency": count,
                    "confidence": min(count / 10, 0.95),
                    "avg_duration": avg_duration
                })
        
        return patterns
    
    async def _save_patterns(self, patterns: List[Dict]):
        """Persist discovered patterns to database"""
        async with async_session() as session:
            for p in patterns:
                existing = await session.execute(
                    select(EventPattern).where(
                        EventPattern.sequence == p["sequence"]
                    )
                )
                pattern = existing.scalar_one_or_none()
                
                if pattern:
                    pattern.frequency = p["frequency"]
                    pattern.confidence = p["confidence"]
                    pattern.avg_duration = p.get("avg_duration")
                    pattern.last_seen = datetime.utcnow()
                else:
                    pattern = EventPattern(
                        pattern_type=p["pattern_type"],
                        sequence=p["sequence"],
                        frequency=p["frequency"],
                        confidence=p["confidence"],
                        avg_duration=p.get("avg_duration")
                    )
                    session.add(pattern)
            
            await session.commit()
    
    async def predict_next_event(self, current_state: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Predict what's likely to happen next using Markov chains"""
        current_event = current_state.get("last_event_type")
        
        if not current_event or current_event not in self.markov_chains:
            return await self._fallback_prediction(current_state)
        
        predictions = []
        transitions = self.markov_chains[current_event]
        
        for next_event, probability in sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]:
            predictions.append((next_event, probability))
        
        await self._record_prediction(current_event, predictions)
        
        return predictions
    
    async def _fallback_prediction(self, state: Dict) -> List[Tuple[str, float]]:
        """Predict based on overall frequency when no Markov data available"""
        async with async_session() as session:
            result = await session.execute(
                select(EventPattern).order_by(EventPattern.frequency.desc()).limit(3)
            )
            patterns = result.scalars().all()
            
            predictions = []
            for pattern in patterns:
                if pattern.sequence:
                    next_event = pattern.sequence[-1]
                    confidence = pattern.confidence * 0.5
                    predictions.append((next_event, confidence))
            
            return predictions
    
    async def _build_markov_chains(self):
        """Build Markov transition probabilities from historical data"""
        async with async_session() as session:
            result = await session.execute(select(EventPattern))
            patterns = result.scalars().all()
            
            transitions = defaultdict(lambda: defaultdict(int))
            
            for pattern in patterns:
                seq = pattern.sequence
                for i in range(len(seq) - 1):
                    current = seq[i]
                    next_event = seq[i + 1]
                    transitions[current][next_event] += pattern.frequency
            
            for current in transitions:
                total = sum(transitions[current].values())
                self.markov_chains[current] = {
                    next_e: count / total
                    for next_e, count in transitions[current].items()
                }
    
    async def estimate_duration(self, task_type: str, context: Optional[Dict] = None) -> Dict[str, float]:
        """Estimate how long a task will take based on historical data"""
        async with async_session() as session:
            result = await session.execute(
                select(DurationEstimate).where(DurationEstimate.task_type == task_type)
            )
            estimate = result.scalar_one_or_none()
            
            if estimate:
                confidence = min(estimate.sample_count / 10, 0.95)
                
                return {
                    "avg_duration": estimate.avg_duration,
                    "min": estimate.min_duration or estimate.avg_duration * 0.5,
                    "max": estimate.max_duration or estimate.avg_duration * 2,
                    "confidence": confidence,
                    "ci_lower": estimate.confidence_interval_lower or estimate.avg_duration * 0.8,
                    "ci_upper": estimate.confidence_interval_upper or estimate.avg_duration * 1.2
                }
            
            return {
                "avg_duration": 300.0,
                "min": 60.0,
                "max": 900.0,
                "confidence": 0.3,
                "ci_lower": 200.0,
                "ci_upper": 400.0
            }
    
    async def _compute_duration_stats(self):
        """Compute statistical duration estimates from completed tasks"""
        async with async_session() as session:
            result = await session.execute(
                select(ExecutionTask).where(
                    ExecutionTask.status == "completed",
                    ExecutionTask.completed_at.isnot(None),
                    ExecutionTask.started_at.isnot(None)
                )
            )
            tasks = result.scalars().all()
            
            by_type = defaultdict(list)
            for task in tasks:
                duration = (task.completed_at - task.started_at).total_seconds()
                by_type[task.task_type].append(duration)
            
            for task_type, durations in by_type.items():
                if len(durations) >= 2:
                    avg = statistics.mean(durations)
                    std = statistics.stdev(durations) if len(durations) > 1 else 0
                    
                    existing = await session.execute(
                        select(DurationEstimate).where(DurationEstimate.task_type == task_type)
                    )
                    estimate = existing.scalar_one_or_none()
                    
                    if estimate:
                        estimate.avg_duration = avg
                        estimate.std_deviation = std
                        estimate.min_duration = min(durations)
                        estimate.max_duration = max(durations)
                        estimate.sample_count = len(durations)
                        estimate.confidence_interval_lower = avg - 1.96 * std / (len(durations) ** 0.5)
                        estimate.confidence_interval_upper = avg + 1.96 * std / (len(durations) ** 0.5)
                        estimate.last_updated = datetime.utcnow()
                    else:
                        estimate = DurationEstimate(
                            task_type=task_type,
                            avg_duration=avg,
                            std_deviation=std,
                            min_duration=min(durations),
                            max_duration=max(durations),
                            sample_count=len(durations),
                            confidence_interval_lower=avg - 1.96 * std / (len(durations) ** 0.5),
                            confidence_interval_upper=avg + 1.96 * std / (len(durations) ** 0.5)
                        )
                        session.add(estimate)
            
            await session.commit()
    
    async def detect_anomalous_timing(self, lookback_hours: int = 1) -> List[Dict]:
        """Detect events that completed faster/slower than expected"""
        cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
        anomalies = []
        
        async with async_session() as session:
            result = await session.execute(
                select(ExecutionTask).where(
                    ExecutionTask.completed_at >= cutoff,
                    ExecutionTask.status == "completed",
                    ExecutionTask.started_at.isnot(None)
                )
            )
            tasks = result.scalars().all()
            
            for task in tasks:
                duration = (task.completed_at - task.started_at).total_seconds()
                estimate = await self.estimate_duration(task.task_type)
                
                expected = estimate["avg_duration"]
                std = (estimate["ci_upper"] - estimate["ci_lower"]) / 3.92
                
                if std > 0:
                    deviation = abs(duration - expected) / std
                    
                    if deviation > 2.5:
                        severity = "high" if deviation > 4 else "medium"
                        
                        anomaly = TemporalAnomaly(
                            event_type=task.task_type,
                            event_id=task.task_id,
                            expected_duration=expected,
                            actual_duration=duration,
                            deviation_sigma=deviation,
                            severity=severity,
                            details={
                                "task_id": task.task_id,
                                "description": task.description,
                                "faster": duration < expected
                            }
                        )
                        session.add(anomaly)
                        
                        anomalies.append({
                            "event_type": task.task_type,
                            "task_id": task.task_id,
                            "expected": expected,
                            "actual": duration,
                            "deviation_sigma": deviation,
                            "severity": severity,
                            "faster_than_expected": duration < expected
                        })
            
            await session.commit()
        
        return anomalies
    
    async def _record_prediction(self, current_event: str, predictions: List[Tuple[str, float]]):
        """Record predictions for later accuracy tracking"""
        async with async_session() as session:
            for predicted_event, probability in predictions[:3]:
                record = PredictionRecord(
                    prediction_type="next_event",
                    predicted_event=predicted_event,
                    predicted_probability=probability
                )
                session.add(record)
            await session.commit()
    
    async def find_recurring_patterns(self, period: str = "daily") -> List[Dict]:
        """Find daily/weekly/monthly patterns"""
        if period == "daily":
            hours = 24 * 7
        elif period == "weekly":
            hours = 24 * 7 * 4
        else:
            hours = 24 * 30
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            result = await session.execute(
                select(ExecutionTask).where(ExecutionTask.created_at >= cutoff)
            )
            tasks = result.scalars().all()
            
            hourly_counts = defaultdict(int)
            daily_counts = defaultdict(int)
            
            for task in tasks:
                hour = task.created_at.hour
                weekday = task.created_at.strftime("%A")
                
                hourly_counts[hour] += 1
                daily_counts[weekday] += 1
            
            patterns = []
            
            if hourly_counts:
                peak_hour = max(hourly_counts.items(), key=lambda x: x[1])
                patterns.append({
                    "type": "peak_hour",
                    "hour": peak_hour[0],
                    "count": peak_hour[1],
                    "description": f"Peak activity at {peak_hour[0]}:00"
                })
            
            if daily_counts:
                peak_day = max(daily_counts.items(), key=lambda x: x[1])
                patterns.append({
                    "type": "peak_day",
                    "day": peak_day[0],
                    "count": peak_day[1],
                    "description": f"Peak activity on {peak_day[0]}"
                })
            
            return patterns
    
    async def predict_peak_load(self) -> Dict[str, Any]:
        """Predict when system will be busiest"""
        patterns = await self.find_recurring_patterns("weekly")
        
        next_peak = None
        peak_hour = None
        
        for p in patterns:
            if p["type"] == "peak_hour":
                peak_hour = p["hour"]
        
        if peak_hour is not None:
            now = datetime.utcnow()
            if now.hour < peak_hour:
                next_peak = now.replace(hour=peak_hour, minute=0, second=0)
            else:
                next_peak = (now + timedelta(days=1)).replace(hour=peak_hour, minute=0, second=0)
        
        return {
            "next_peak_time": next_peak,
            "patterns": patterns,
            "recommendation": f"Schedule maintenance outside peak hours"
        }
    
    async def suggest_preventive_actions(self) -> List[Dict]:
        """Suggest actions based on predicted patterns"""
        patterns = await self.find_recurring_patterns("weekly")
        suggestions = []
        
        for pattern in patterns:
            if pattern["type"] == "peak_day":
                suggestions.append({
                    "action": "increase_monitoring",
                    "target": pattern["day"],
                    "reason": f"High activity expected on {pattern['day']}",
                    "confidence": 0.7
                })
        
        anomalies = await self.detect_anomalous_timing(lookback_hours=24)
        if len(anomalies) > 5:
            suggestions.append({
                "action": "investigate_performance",
                "target": "task_executor",
                "reason": f"{len(anomalies)} timing anomalies detected in last 24h",
                "confidence": 0.8
            })
        
        return suggestions

temporal_reasoner = TemporalReasoner()
