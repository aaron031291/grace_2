from typing import Dict, List, Any, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from collections import defaultdict

if TYPE_CHECKING:
    from .models import Task, ChatMessage, CausalEvent

from .causal_graph import CausalGraph, CausalNode

class CausalAnalyzer:
    """High-level causal analysis for system optimization"""
    
    async def analyze_task_completion(self, user: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Analyze what causes tasks to complete or fail"""
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        graph = CausalGraph()
        await graph.build_from_events(start_date, end_date, user)
        
        completed_tasks = []
        failed_tasks = []
        
        for node in graph.nodes.values():
            if node.event_type == "task_completed":
                causes = graph.find_causes(node.event_id, node.event_type, max_depth=2)
                completed_tasks.append({
                    "task_id": node.event_id,
                    "metadata": node.metadata,
                    "causes": causes[:5]
                })
            elif node.event_type == "task_created":
                if node.metadata.get("status") == "pending":
                    causes = graph.find_causes(node.event_id, node.event_type, max_depth=2)
                    failed_tasks.append({
                        "task_id": node.event_id,
                        "metadata": node.metadata,
                        "causes": causes[:5]
                    })
        
        completion_patterns = self._identify_completion_patterns(completed_tasks)
        failure_patterns = self._identify_failure_patterns(failed_tasks)
        
        return {
            "analysis_period": f"{days} days",
            "total_completed": len(completed_tasks),
            "total_pending": len(failed_tasks),
            "completion_rate": len(completed_tasks) / (len(completed_tasks) + len(failed_tasks)) if (completed_tasks or failed_tasks) else 0,
            "completion_patterns": completion_patterns,
            "failure_patterns": failure_patterns,
            "recommendations": self._generate_task_recommendations(completion_patterns, failure_patterns)
        }
    
    def _identify_completion_patterns(self, completed_tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Find common patterns in completed tasks"""
        patterns = defaultdict(int)
        
        for task in completed_tasks:
            for cause in task["causes"]:
                pattern_key = f"{cause['event_type']}->task_completed"
                patterns[pattern_key] += 1
        
        total = len(completed_tasks) if completed_tasks else 1
        return [
            {"pattern": pattern, "frequency": count / total, "count": count}
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _identify_failure_patterns(self, failed_tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Find common patterns in incomplete tasks"""
        patterns = defaultdict(int)
        
        for task in failed_tasks:
            auto_gen = task["metadata"].get("auto_generated", False)
            if auto_gen:
                patterns["auto_generated"] += 1
            else:
                patterns["user_created"] += 1
            
            for cause in task["causes"]:
                pattern_key = f"{cause['event_type']}->task_pending"
                patterns[pattern_key] += 1
        
        total = len(failed_tasks) if failed_tasks else 1
        return [
            {"pattern": pattern, "frequency": count / total, "count": count}
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _generate_task_recommendations(self, completion_patterns: List, failure_patterns: List) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for pattern in failure_patterns:
            if "auto_generated" in pattern["pattern"] and pattern["frequency"] > 0.7:
                recommendations.append(
                    f"High auto-task failure rate ({pattern['frequency']*100:.1f}%). "
                    "Consider increasing task creation threshold or improving task descriptions."
                )
        
        for pattern in completion_patterns:
            if pattern["frequency"] > 0.6:
                recommendations.append(
                    f"Pattern '{pattern['pattern']}' leads to {pattern['frequency']*100:.1f}% completion. "
                    "Encourage this interaction type."
                )
        
        return recommendations
    
    async def analyze_error_chains(self, user: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Trace errors to root cause"""
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        graph = CausalGraph()
        await graph.build_from_events(start_date, end_date, user)
        
        async with async_session() as session:
            result = await session.execute(
                select(CausalEvent).where(
                    and_(
                        CausalEvent.created_at >= start_date,
                        CausalEvent.outcome == "unhandled"
                    )
                )
            )
            errors = result.scalars().all()
        
        error_chains = []
        for error in errors:
            if error.response_message_id:
                causes = graph.find_causes(error.response_message_id, "message_assistant", max_depth=3)
                
                root_causes = [c for c in causes if c["depth"] >= 2]
                
                error_chains.append({
                    "error_event_id": error.id,
                    "error_type": error.event_type,
                    "timestamp": error.created_at.isoformat(),
                    "immediate_causes": causes[:2] if causes else [],
                    "root_causes": root_causes[:3] if root_causes else [],
                    "chain_length": len(causes)
                })
        
        common_roots = self._find_common_root_causes(error_chains)
        
        return {
            "total_errors": len(errors),
            "errors_with_chains": len(error_chains),
            "error_chains": error_chains[:10],
            "common_root_causes": common_roots,
            "recommendations": self._generate_error_recommendations(common_roots)
        }
    
    def _find_common_root_causes(self, error_chains: List[Dict]) -> List[Dict[str, Any]]:
        """Identify most common root causes"""
        root_cause_counts = defaultdict(int)
        
        for chain in error_chains:
            for root in chain.get("root_causes", []):
                key = root["event_type"]
                root_cause_counts[key] += 1
        
        return [
            {"root_cause_type": cause, "occurrence_count": count}
            for cause, count in sorted(root_cause_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _generate_error_recommendations(self, common_roots: List[Dict]) -> List[str]:
        """Generate error prevention recommendations"""
        recommendations = []
        
        for root in common_roots:
            if root["occurrence_count"] >= 3:
                recommendations.append(
                    f"Root cause '{root['root_cause_type']}' appears in {root['occurrence_count']} error chains. "
                    "Investigate and improve handling."
                )
        
        return recommendations
    
    async def analyze_optimization_paths(self, metric: str, user: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Find best ways to improve a metric (task completion, response quality, etc.)"""
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        graph = CausalGraph()
        await graph.build_from_events(start_date, end_date, user)
        
        if metric == "task_completion":
            target_events = [n for n in graph.nodes.values() if n.event_type == "task_completed"]
        elif metric == "user_engagement":
            target_events = [n for n in graph.nodes.values() if n.event_type == "message_user"]
        else:
            target_events = list(graph.nodes.values())
        
        optimization_paths = []
        for target in target_events[:20]:
            causes = graph.find_causes(target.event_id, target.event_type, max_depth=2)
            
            high_strength_causes = [c for c in causes if c["strength"] > 0.7]
            
            if high_strength_causes:
                optimization_paths.append({
                    "target_event_id": target.event_id,
                    "target_event_type": target.event_type,
                    "key_drivers": high_strength_causes[:3],
                    "path_strength": sum(c["strength"] for c in high_strength_causes) / len(high_strength_causes)
                })
        
        optimization_paths.sort(key=lambda x: x["path_strength"], reverse=True)
        
        action_recommendations = self._generate_optimization_actions(optimization_paths)
        
        return {
            "metric": metric,
            "optimization_paths": optimization_paths[:10],
            "action_recommendations": action_recommendations
        }
    
    def _generate_optimization_actions(self, paths: List[Dict]) -> List[str]:
        """Generate actionable optimization recommendations"""
        actions = []
        
        driver_counts = defaultdict(int)
        for path in paths[:10]:
            for driver in path["key_drivers"]:
                driver_counts[driver["event_type"]] += 1
        
        for driver_type, count in sorted(driver_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            actions.append(
                f"Optimize '{driver_type}' events - appears as key driver in {count} high-performing paths"
            )
        
        return actions
    
    async def analyze_feedback_loops(self, user: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Detect reinforcing and balancing feedback loops"""
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        graph = CausalGraph()
        await graph.build_from_events(start_date, end_date, user)
        
        cycles = graph.detect_cycles()
        
        reinforcing_loops = []
        balancing_loops = []
        
        for cycle in cycles:
            avg_strength = sum(edge["strength"] for edge in cycle) / len(cycle) if cycle else 0
            
            cycle_types = [edge["from_event_type"] for edge in cycle]
            
            if avg_strength > 0.6:
                reinforcing_loops.append({
                    "cycle": cycle,
                    "strength": avg_strength,
                    "length": len(cycle),
                    "event_types": list(set(cycle_types))
                })
            else:
                balancing_loops.append({
                    "cycle": cycle,
                    "strength": avg_strength,
                    "length": len(cycle),
                    "event_types": list(set(cycle_types))
                })
        
        return {
            "total_cycles": len(cycles),
            "reinforcing_loops": reinforcing_loops[:5],
            "balancing_loops": balancing_loops[:5],
            "loop_analysis": self._analyze_loop_dynamics(reinforcing_loops, balancing_loops)
        }
    
    def _analyze_loop_dynamics(self, reinforcing: List, balancing: List) -> Dict[str, Any]:
        """Analyze system stability from feedback loops"""
        return {
            "reinforcing_count": len(reinforcing),
            "balancing_count": len(balancing),
            "stability": "stable" if len(balancing) > len(reinforcing) else "potentially unstable",
            "recommendations": self._generate_loop_recommendations(reinforcing, balancing)
        }
    
    def _generate_loop_recommendations(self, reinforcing: List, balancing: List) -> List[str]:
        """Generate recommendations based on feedback loop analysis"""
        recommendations = []
        
        if len(reinforcing) > 3:
            recommendations.append(
                f"Found {len(reinforcing)} reinforcing loops. Monitor for runaway behavior."
            )
        
        if len(balancing) == 0 and len(reinforcing) > 0:
            recommendations.append(
                "No balancing loops detected. System may lack self-regulation. Add constraints."
            )
        
        for loop in reinforcing[:2]:
            if "task_created" in loop["event_types"]:
                recommendations.append(
                    f"Task creation loop detected (strength: {loop['strength']:.2f}). "
                    "May lead to task explosion if unchecked."
                )
        
        return recommendations

causal_analyzer = CausalAnalyzer()
