import random
from datetime import datetime
from typing import List, Dict, Any
from .models import async_session
from .temporal_models import Simulation
import statistics

class SimulationEngine:
    """Run what-if simulations and scenario analysis"""
    
    def __init__(self):
        self.simulation_cache: Dict[str, Dict] = {}
    
    async def simulate_action(
        self,
        proposed_action: Dict[str, Any],
        iterations: int = 1000
    ) -> Dict[str, Any]:
        """Monte Carlo simulation of proposed action"""
        action_type = proposed_action.get("type")
        
        if action_type == "change_reflection_interval":
            return await self._simulate_interval_change(proposed_action, iterations)
        elif action_type == "change_task_threshold":
            return await self._simulate_threshold_change(proposed_action, iterations)
        elif action_type == "add_worker":
            return await self._simulate_worker_change(proposed_action, iterations)
        else:
            return await self._generic_simulation(proposed_action, iterations)
    
    async def _simulate_interval_change(self, action: Dict, iterations: int) -> Dict:
        """Simulate changing reflection interval"""
        new_interval = action.get("new_interval", 60)
        current_interval = action.get("current_interval", 30)
        
        results = {
            "response_time": [],
            "task_completion": [],
            "resource_usage": []
        }
        
        for i in range(iterations):
            base_response = random.gauss(5.0, 1.5)
            interval_impact = (new_interval - current_interval) / current_interval
            
            response_time = base_response * (1 + interval_impact * 0.1)
            response_time = max(0.5, response_time)
            results["response_time"].append(response_time)
            
            base_completion = random.gauss(0.75, 0.15)
            completion = base_completion * (1 - interval_impact * 0.05)
            completion = max(0.1, min(1.0, completion))
            results["task_completion"].append(completion)
            
            base_cpu = random.gauss(0.4, 0.1)
            cpu_usage = base_cpu * (1 - interval_impact * 0.2)
            cpu_usage = max(0.1, min(1.0, cpu_usage))
            results["resource_usage"].append(cpu_usage)
        
        outcome = {
            "response_time": {
                "mean": statistics.mean(results["response_time"]),
                "std": statistics.stdev(results["response_time"]),
                "percentile_95": sorted(results["response_time"])[int(iterations * 0.95)]
            },
            "task_completion": {
                "mean": statistics.mean(results["task_completion"]),
                "std": statistics.stdev(results["task_completion"]),
                "percentile_5": sorted(results["task_completion"])[int(iterations * 0.05)]
            },
            "resource_usage": {
                "mean": statistics.mean(results["resource_usage"]),
                "std": statistics.stdev(results["resource_usage"]),
                "percentile_95": sorted(results["resource_usage"])[int(iterations * 0.95)]
            }
        }
        
        response_change = ((outcome["response_time"]["mean"] - 5.0) / 5.0) * 100
        completion_change = ((outcome["task_completion"]["mean"] - 0.75) / 0.75) * 100
        resource_change = ((outcome["resource_usage"]["mean"] - 0.4) / 0.4) * 100
        
        outcome["summary"] = {
            "response_time_change_pct": response_change,
            "completion_rate_change_pct": completion_change,
            "resource_usage_change_pct": resource_change,
            "recommendation": self._make_recommendation(response_change, completion_change, resource_change)
        }
        
        await self._save_simulation(action, outcome)
        
        return outcome
    
    async def _simulate_threshold_change(self, action: Dict, iterations: int) -> Dict:
        """Simulate changing task creation threshold"""
        new_threshold = action.get("new_threshold", 5)
        current_threshold = action.get("current_threshold", 3)
        
        results = {
            "tasks_created": [],
            "false_positives": [],
            "task_quality": []
        }
        
        for i in range(iterations):
            base_tasks = random.gauss(10, 3)
            
            threshold_ratio = current_threshold / new_threshold
            tasks_created = base_tasks * threshold_ratio
            tasks_created = max(0, tasks_created)
            results["tasks_created"].append(tasks_created)
            
            quality_improvement = (new_threshold - current_threshold) / current_threshold
            base_quality = random.gauss(0.7, 0.15)
            quality = base_quality * (1 + quality_improvement * 0.3)
            quality = max(0.1, min(1.0, quality))
            results["task_quality"].append(quality)
            
            false_positive_rate = 1 - quality
            results["false_positives"].append(false_positive_rate)
        
        outcome = {
            "tasks_created": {
                "mean": statistics.mean(results["tasks_created"]),
                "std": statistics.stdev(results["tasks_created"])
            },
            "task_quality": {
                "mean": statistics.mean(results["task_quality"]),
                "std": statistics.stdev(results["task_quality"])
            },
            "false_positive_rate": {
                "mean": statistics.mean(results["false_positives"]),
                "std": statistics.stdev(results["false_positives"])
            }
        }
        
        task_change = ((outcome["tasks_created"]["mean"] - 10) / 10) * 100
        quality_change = ((outcome["task_quality"]["mean"] - 0.7) / 0.7) * 100
        
        outcome["summary"] = {
            "task_count_change_pct": task_change,
            "quality_change_pct": quality_change,
            "expected_value": outcome["tasks_created"]["mean"] * outcome["task_quality"]["mean"],
            "recommendation": "Increase threshold" if quality_change > 10 else "Keep current threshold"
        }
        
        await self._save_simulation(action, outcome)
        
        return outcome
    
    async def _simulate_worker_change(self, action: Dict, iterations: int) -> Dict:
        """Simulate adding/removing workers"""
        new_workers = action.get("new_workers", 3)
        current_workers = action.get("current_workers", 3)
        
        results = {
            "throughput": [],
            "latency": [],
            "cpu_usage": []
        }
        
        for i in range(iterations):
            base_throughput = random.gauss(50, 10)
            worker_ratio = new_workers / current_workers
            throughput = base_throughput * worker_ratio * random.uniform(0.85, 1.0)
            results["throughput"].append(throughput)
            
            base_latency = random.gauss(2.0, 0.5)
            latency = base_latency / (worker_ratio ** 0.7)
            results["latency"].append(latency)
            
            base_cpu = random.gauss(0.6, 0.1)
            cpu = base_cpu * worker_ratio * 0.8
            results["cpu_usage"].append(min(1.0, cpu))
        
        outcome = {
            "throughput": {
                "mean": statistics.mean(results["throughput"]),
                "std": statistics.stdev(results["throughput"])
            },
            "latency": {
                "mean": statistics.mean(results["latency"]),
                "std": statistics.stdev(results["latency"])
            },
            "cpu_usage": {
                "mean": statistics.mean(results["cpu_usage"]),
                "std": statistics.stdev(results["cpu_usage"])
            }
        }
        
        throughput_change = ((outcome["throughput"]["mean"] - 50) / 50) * 100
        latency_change = ((outcome["latency"]["mean"] - 2.0) / 2.0) * 100
        
        outcome["summary"] = {
            "throughput_change_pct": throughput_change,
            "latency_change_pct": latency_change,
            "cost_benefit_ratio": throughput_change / (new_workers - current_workers) if new_workers != current_workers else 0,
            "recommendation": "Add workers" if throughput_change > 20 else "Keep current workers"
        }
        
        await self._save_simulation(action, outcome)
        
        return outcome
    
    async def _generic_simulation(self, action: Dict, iterations: int) -> Dict:
        """Generic simulation for unknown action types"""
        results = []
        
        for i in range(iterations):
            impact = random.gauss(0.05, 0.15)
            results.append(impact)
        
        outcome = {
            "predicted_impact": {
                "mean": statistics.mean(results),
                "std": statistics.stdev(results),
                "confidence_interval": (
                    statistics.mean(results) - 1.96 * statistics.stdev(results),
                    statistics.mean(results) + 1.96 * statistics.stdev(results)
                )
            },
            "summary": {
                "expected_improvement_pct": statistics.mean(results) * 100,
                "recommendation": "Proceed with caution - limited simulation data"
            }
        }
        
        await self._save_simulation(action, outcome)
        
        return outcome
    
    def _make_recommendation(self, response_change: float, completion_change: float, resource_change: float) -> str:
        """Generate recommendation based on simulation results"""
        if completion_change > 5 and resource_change < -10:
            return "Recommended: Improves completion and reduces resource usage"
        elif completion_change > 0 and response_change < 10:
            return "Recommended: Net positive impact"
        elif completion_change < -10:
            return "Not recommended: Significant completion rate degradation"
        elif response_change > 20:
            return "Caution: May significantly increase response time"
        else:
            return "Neutral: Minimal impact expected"
    
    async def simulate_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple scenarios and find the best"""
        results = []
        
        for i, scenario in enumerate(scenarios):
            outcome = await self.simulate_action(scenario, iterations=500)
            
            score = 0
            if "summary" in outcome:
                summary = outcome["summary"]
                score += summary.get("completion_rate_change_pct", 0) * 2
                score -= summary.get("response_time_change_pct", 0) * 1
                score -= summary.get("resource_usage_change_pct", 0) * 0.5
            
            results.append({
                "scenario_id": i,
                "scenario": scenario,
                "outcome": outcome,
                "score": score
            })
        
        best = max(results, key=lambda x: x["score"])
        
        return {
            "scenarios": results,
            "best_scenario": best,
            "recommendation": f"Scenario {best['scenario_id']} has highest expected value (score: {best['score']:.2f})"
        }
    
    async def run_planning_simulation(self, goal: str, max_steps: int = 5) -> Dict[str, Any]:
        """Find action sequence to achieve goal"""
        
        action_space = [
            {"type": "change_reflection_interval", "new_interval": 60, "current_interval": 30},
            {"type": "change_reflection_interval", "new_interval": 45, "current_interval": 30},
            {"type": "change_task_threshold", "new_threshold": 4, "current_threshold": 3},
            {"type": "change_task_threshold", "new_threshold": 5, "current_threshold": 3},
            {"type": "add_worker", "new_workers": 4, "current_workers": 3},
            {"type": "add_worker", "new_workers": 5, "current_workers": 3}
        ]
        
        if "completion rate to 90%" in goal.lower():
            target_metric = "task_completion"
            target_value = 0.9
        elif "response time" in goal.lower():
            target_metric = "response_time"
            target_value = 3.0
        else:
            target_metric = "overall_score"
            target_value = 100
        
        best_sequence = []
        best_score = float('-inf')
        
        for action in action_space[:3]:
            outcome = await self.simulate_action(action, iterations=200)
            
            score = 0
            if "task_completion" in outcome:
                completion = outcome["task_completion"]["mean"]
                score = -(abs(completion - target_value)) * 100
            elif "summary" in outcome:
                score = outcome["summary"].get("completion_rate_change_pct", 0)
            
            if score > best_score:
                best_score = score
                best_sequence = [action]
        
        return {
            "goal": goal,
            "recommended_sequence": best_sequence,
            "predicted_outcome": f"Expected improvement: {best_score:.1f}%",
            "confidence": 0.7,
            "steps": [
                {
                    "step": i + 1,
                    "action": action,
                    "rationale": f"Predicted to improve {target_metric}"
                }
                for i, action in enumerate(best_sequence)
            ]
        }
    
    async def _save_simulation(self, action: Dict, outcome: Dict):
        """Save simulation to database"""
        async with async_session() as session:
            sim = Simulation(
                scenario=action.get("type", "unknown"),
                parameters=action,
                predicted_outcome=outcome,
                confidence=0.7
            )
            session.add(sim)
            await session.commit()
    
    async def compare_prediction_vs_actual(self, simulation_id: int, actual_outcome: Dict) -> Dict:
        """Compare simulation prediction with actual outcome"""
        async with async_session() as session:
            from sqlalchemy import select, update
            result = await session.execute(
                select(Simulation).where(Simulation.id == simulation_id)
            )
            sim = result.scalar_one_or_none()
            
            if not sim:
                return {"error": "Simulation not found"}
            
            predicted = sim.predicted_outcome
            
            accuracy_scores = []
            
            if "summary" in predicted and "summary" in actual_outcome:
                for metric in ["completion_rate_change_pct", "response_time_change_pct"]:
                    if metric in predicted["summary"] and metric in actual_outcome["summary"]:
                        pred_val = predicted["summary"][metric]
                        actual_val = actual_outcome["summary"][metric]
                        
                        error = abs(pred_val - actual_val)
                        accuracy = max(0, 1 - error / 100)
                        accuracy_scores.append(accuracy)
            
            overall_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0.5
            
            await session.execute(
                update(Simulation)
                .where(Simulation.id == simulation_id)
                .values(
                    actual_outcome=actual_outcome,
                    accuracy_score=overall_accuracy,
                    executed_at=datetime.utcnow()
                )
            )
            await session.commit()
            
            return {
                "simulation_id": simulation_id,
                "predicted": predicted,
                "actual": actual_outcome,
                "accuracy": overall_accuracy,
                "accuracy_pct": overall_accuracy * 100,
                "verdict": "Accurate" if overall_accuracy > 0.7 else "Needs calibration"
            }

simulation_engine = SimulationEngine()
