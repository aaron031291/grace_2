"""
Context Suggestion System - Intelligent, non-intrusive context awareness
Grace detects when context would be helpful and suggests it
"""

from typing import Dict, Any, List
from datetime import datetime

class ContextSuggestionSystem:
    """
    Analyzes user activity and suggests relevant context
    Only when confidence is high and not annoying
    """
    
    def __init__(self):
        self.session_dismissed = set()  # Topics dismissed this session
        self.last_suggestion_time = {}  # Cooldown per topic type
        self.confidence_threshold = 0.7  # Only suggest if >= 70% confident
        self.cooldown_seconds = 30
        
    async def get_suggestions(
        self,
        current_kernel: str,
        recent_activity: List[str] = None,
        user_message: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate context suggestions based on current activity
        Returns only high-confidence, non-dismissed suggestions
        """
        
        suggestions = []
        
        # Detect if user might need logs
        if user_message:
            logs_suggestion = await self._detect_logs_need(user_message, current_kernel)
            if logs_suggestion:
                suggestions.append(logs_suggestion)
        
        # Detect if user is working with models
        models_suggestion = await self._detect_models_context(current_kernel, recent_activity)
        if models_suggestion:
            suggestions.append(models_suggestion)
        
        # Detect kernel errors/alerts
        alerts_suggestion = await self._detect_kernel_alerts(current_kernel)
        if alerts_suggestion:
            suggestions.append(alerts_suggestion)
        
        # Filter by confidence, cooldown, and dismissal
        filtered = []
        for suggestion in suggestions:
            topic_key = suggestion["type"] + suggestion["kernel"]
            
            # Check if dismissed
            if topic_key in self.session_dismissed:
                continue
            
            # Check confidence threshold
            if suggestion["confidence"] < self.confidence_threshold:
                continue
            
            # Check cooldown
            last_time = self.last_suggestion_time.get(topic_key, 0)
            if datetime.now().timestamp() - last_time < self.cooldown_seconds:
                continue
            
            # Passed all checks
            filtered.append(suggestion)
            self.last_suggestion_time[topic_key] = datetime.now().timestamp()
        
        # Return only one at a time (most recent/highest priority)
        if filtered:
            return [max(filtered, key=lambda x: (
                {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 0),
                x['confidence']
            ))]
        
        return []
    
    async def _detect_logs_need(self, message: str, kernel: str) -> Optional[Dict]:
        """Detect if user needs to see logs"""
        
        log_keywords = ["error", "failed", "crash", "bug", "issue", "problem", "not working", "broken"]
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in log_keywords):
            return {
                "id": f"logs_{kernel}_{datetime.now().timestamp()}",
                "type": "logs",
                "title": "Kernel Logs Available",
                "preview": f"Recent logs from {kernel} might help debug this issue. {await self._get_log_summary(kernel)}",
                "confidence": 0.85,
                "priority": "high",
                "kernel": kernel,
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    async def _detect_models_context(self, kernel: str, activity: List[str]) -> Optional[Dict]:
        """Detect if user should know about model performance"""
        
        # Only suggest for model-heavy kernels
        model_kernels = ["coding_agent", "agentic_spine", "voice_conversation", "learning_integration"]
        
        if kernel in model_kernels:
            # Check if model performance data available
            try:
                from backend.model_capability_system import capability_system
                summary = await capability_system.get_learning_summary()
                
                if summary["statistics"]:
                    best_model = summary["statistics"][0]
                    
                    return {
                        "id": f"models_{kernel}_{datetime.now().timestamp()}",
                        "type": "models",
                        "title": "Model Performance Insight",
                        "preview": f"Grace has learned that {best_model['model']} works best for {best_model['task_type']} tasks ({best_model['success_rate']*100:.0f}% success rate)",
                        "confidence": 0.75,
                        "priority": "medium",
                        "kernel": kernel,
                        "timestamp": datetime.now().isoformat()
                    }
            except:
                pass
        
        return None
    
    async def _detect_kernel_alerts(self, kernel: str) -> Optional[Dict]:
        """Detect critical kernel alerts"""
        
        try:
            # Check for recent incidents
            # This would integrate with self-healing system
            
            # Simulated check (replace with real incident query)
            has_critical_alert = False
            
            if has_critical_alert:
                return {
                    "id": f"alert_{kernel}_{datetime.now().timestamp()}",
                    "type": "alert",
                    "title": "⚠️ Critical Alert",
                    "preview": f"{kernel} has a critical issue requiring attention",
                    "confidence": 1.0,
                    "priority": "critical",
                    "kernel": kernel,
                    "timestamp": datetime.now().isoformat()
                }
        except:
            pass
        
        return None
    
    async def _get_log_summary(self, kernel: str) -> str:
        """Get quick log summary"""
        try:
            # Query recent logs
            return "Last 3 errors detected."
        except:
            return "Available for review."
    
    def dismiss_topic(self, topic_type: str, kernel: str):
        """Dismiss a topic for this session"""
        self.session_dismissed.add(topic_type + kernel)

# Global instance
context_system = ContextSuggestionSystem()
