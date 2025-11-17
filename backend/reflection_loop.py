"""
Reflection Loop - Plan-Act-Reflect-Revise for continuous improvement
Grace learns from outcomes and updates her strategies
"""

from typing import Dict, Any, List
from datetime import datetime
from backend.event_bus import event_bus, Event, EventType
from backend.action_gateway import action_gateway

class ReflectionLoop:
    """
    Plan-Act-Reflect-Revise loop for Grace's continuous improvement
    After each action, reflect on outcomes and update strategies
    """
    
    def __init__(self):
        self.reflections = []
        self.trust_scores = {}
        self.strategy_updates = []
        
        event_bus.subscribe(EventType.LEARNING_OUTCOME, self.on_learning_outcome)
    
    async def on_learning_outcome(self, event: Event) -> None:
        """Handle learning outcome events"""
        outcome = event.data
        trace_id = outcome.get("trace_id")
        
        if trace_id:
            await self.reflect_on_outcome(trace_id, outcome)
    
    async def reflect_on_outcome(
        self,
        trace_id: str,
        outcome: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on action outcome and generate insights
        """
        
        action_log = action_gateway.get_action_log()
        action = next((a for a in action_log if a["trace_id"] == trace_id), None)
        
        if not action:
            return {"error": "Action not found"}
        
        reflection = {
            "trace_id": trace_id,
            "action_type": action["action_type"],
            "agent": action["agent"],
            "success": outcome.get("success", False),
            "timestamp": datetime.now().isoformat(),
            "insights": [],
            "strategy_updates": []
        }
        
        if outcome.get("success"):
            reflection["insights"].append(
                f"Action '{action['action_type']}' succeeded - reinforce this pattern"
            )
            
            agent_key = f"{action['agent']}:{action['action_type']}"
            current_trust = self.trust_scores.get(agent_key, 0.5)
            self.trust_scores[agent_key] = min(1.0, current_trust + 0.1)
            
        else:
            reflection["insights"].append(
                f"Action '{action['action_type']}' failed - analyze and adjust"
            )
            
            agent_key = f"{action['agent']}:{action['action_type']}"
            current_trust = self.trust_scores.get(agent_key, 0.5)
            self.trust_scores[agent_key] = max(0.0, current_trust - 0.15)
            
            if outcome.get("error"):
                reflection["insights"].append(f"Error: {outcome['error']}")
                reflection["strategy_updates"].append({
                    "type": "error_mitigation",
                    "action": action["action_type"],
                    "recommendation": "Add validation or fallback strategy"
                })
        
        self.reflections.append(reflection)
        
        await event_bus.publish(Event(
            event_type=EventType.WORLD_MODEL_UPDATE,
            source="reflection_loop",
            data=reflection,
            trace_id=trace_id
        ))
        
        print(f"[ReflectionLoop] Reflected on {trace_id}: {len(reflection['insights'])} insights")
        
        return reflection
    
    async def plan_action(
        self,
        agent: str,
        action_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan action based on past reflections and trust scores
        """
        
        agent_key = f"{agent}:{action_type}"
        trust_score = self.trust_scores.get(agent_key, 0.5)
        
        similar_reflections = [
            r for r in self.reflections[-100:]
            if r["agent"] == agent and r["action_type"] == action_type
        ]
        
        success_rate = 0.5
        if similar_reflections:
            successes = sum(1 for r in similar_reflections if r["success"])
            success_rate = successes / len(similar_reflections)
        
        plan = {
            "agent": agent,
            "action_type": action_type,
            "trust_score": trust_score,
            "success_rate": success_rate,
            "confidence": (trust_score + success_rate) / 2,
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if plan["confidence"] < 0.3:
            plan["recommendations"].append("Low confidence - consider alternative approach")
        elif plan["confidence"] < 0.6:
            plan["recommendations"].append("Moderate confidence - proceed with caution")
        else:
            plan["recommendations"].append("High confidence - proceed")
        
        recent_failures = [r for r in similar_reflections[-5:] if not r["success"]]
        if len(recent_failures) >= 3:
            plan["recommendations"].append("Multiple recent failures - review strategy")
        
        print(f"[ReflectionLoop] Planned {action_type} for {agent}: confidence={plan['confidence']:.2f}")
        
        return plan
    
    def get_agent_trust_score(self, agent: str, action_type: str) -> float:
        """Get trust score for agent/action combination"""
        agent_key = f"{agent}:{action_type}"
        return self.trust_scores.get(agent_key, 0.5)
    
    def get_reflections(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent reflections"""
        return self.reflections[-limit:]
    
    def get_strategy_updates(self) -> List[Dict[str, Any]]:
        """Get recommended strategy updates"""
        all_updates = []
        for reflection in self.reflections[-100:]:
            all_updates.extend(reflection.get("strategy_updates", []))
        return all_updates

reflection_loop = ReflectionLoop()
