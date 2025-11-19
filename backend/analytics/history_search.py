"""
History Search - Search Grace's activity logs and conversation history

Features:
- Natural language queries: "What did Grace do last Tuesday?"
- Search conversations, actions, tasks, learning events
- Time-based filtering
- Activity summaries
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import re

from backend.event_bus import event_bus
from backend.action_gateway import action_gateway


class HistorySearch:
    """
    Search Grace's activity history
    
    Supports queries like:
    - "What did Grace do last Tuesday?"
    - "Show me conversations from yesterday"
    - "What tasks ran this week?"
    - "What did I approve last month?"
    """
    
    def __init__(self):
        self.conversations_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    async def search(
        self,
        query: str,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search history with natural language query
        
        Args:
            query: Natural language search query
            user_id: User performing search
            limit: Max results
        
        Returns:
            Search results grouped by type
        """
        # Parse time range from query
        time_range = self._parse_time_range(query)
        
        # Determine what to search for
        search_conversations = "conversation" in query.lower() or "chat" in query.lower() or "said" in query.lower()
        search_actions = "action" in query.lower() or "did" in query.lower() or "approve" in query.lower()
        search_tasks = "task" in query.lower() or "job" in query.lower() or "ran" in query.lower()
        search_learning = "learn" in query.lower() or "upload" in query.lower() or "ingest" in query.lower()
        
        # If nothing specific mentioned, search everything
        if not any([search_conversations, search_actions, search_tasks, search_learning]):
            search_conversations = search_actions = search_tasks = search_learning = True
        
        results = {
            "query": query,
            "time_range": time_range,
            "conversations": [],
            "actions": [],
            "tasks": [],
            "learning_events": [],
            "summary": "",
        }
        
        # Search conversations
        if search_conversations:
            results["conversations"] = await self._search_conversations(
                time_range, user_id, limit
            )
        
        # Search actions
        if search_actions:
            results["actions"] = self._search_actions(time_range, user_id, limit)
        
        # Search tasks
        if search_tasks:
            results["tasks"] = await self._search_tasks(time_range, limit)
        
        # Search learning events
        if search_learning:
            results["learning_events"] = await self._search_learning(time_range, limit)
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _parse_time_range(self, query: str) -> Dict[str, datetime]:
        """
        Parse time range from natural language
        
        Supports:
        - "last Tuesday", "yesterday", "last week"
        - "this week", "this month"
        - "last 3 days", "past 7 days"
        """
        query_lower = query.lower()
        now = datetime.now()
        
        # Yesterday
        if "yesterday" in query_lower:
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
            end = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59)
            return {"start": start, "end": end, "label": "yesterday"}
        
        # Last Tuesday (or any day)
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(days):
            if f"last {day}" in query_lower:
                # Find the most recent occurrence of that day
                days_ago = (now.weekday() - i) % 7
                if days_ago == 0:
                    days_ago = 7  # Last week's occurrence
                target_date = now - timedelta(days=days_ago)
                start = target_date.replace(hour=0, minute=0, second=0)
                end = target_date.replace(hour=23, minute=59, second=59)
                return {"start": start, "end": end, "label": f"last {day}"}
        
        # This week
        if "this week" in query_lower:
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0)
            end = now
            return {"start": start, "end": end, "label": "this week"}
        
        # Last week
        if "last week" in query_lower:
            days_since_monday = now.weekday() + 7
            start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0)
            end = (now - timedelta(days=now.weekday() + 1)).replace(hour=23, minute=59, second=59)
            return {"start": start, "end": end, "label": "last week"}
        
        # This month
        if "this month" in query_lower:
            start = now.replace(day=1, hour=0, minute=0, second=0)
            end = now
            return {"start": start, "end": end, "label": "this month"}
        
        # Last X days
        match = re.search(r'(?:last|past) (\d+) days?', query_lower)
        if match:
            days = int(match.group(1))
            start = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0)
            end = now
            return {"start": start, "end": end, "label": f"last {days} days"}
        
        # Default: last 24 hours
        start = now - timedelta(days=1)
        end = now
        return {"start": start, "end": end, "label": "last 24 hours"}
    
    async def _search_conversations(
        self,
        time_range: Dict[str, datetime],
        user_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search conversation history"""
        # Get from chat_api conversations cache
        from backend.routes.chat_api import conversations
        
        results = []
        for session_id, messages in conversations.items():
            for msg in messages:
                timestamp = datetime.fromisoformat(msg.get("timestamp", ""))
                if time_range["start"] <= timestamp <= time_range["end"]:
                    results.append({
                        "session_id": session_id,
                        "role": msg.get("role"),
                        "content": msg.get("content", "")[:200] + "..." if len(msg.get("content", "")) > 200 else msg.get("content", ""),
                        "timestamp": msg.get("timestamp"),
                        "trace_id": msg.get("trace_id"),
                    })
        
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def _search_actions(
        self,
        time_range: Dict[str, datetime],
        user_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search action history"""
        action_log = action_gateway.get_action_log()
        
        results = []
        for action in action_log:
            timestamp = datetime.fromisoformat(action.get("timestamp", ""))
            if time_range["start"] <= timestamp <= time_range["end"]:
                results.append({
                    "action_type": action.get("action_type"),
                    "agent": action.get("agent"),
                    "approved": action.get("approved"),
                    "governance_tier": action.get("governance_tier"),
                    "timestamp": action.get("timestamp"),
                    "trace_id": action.get("trace_id"),
                })
        
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    async def _search_tasks(
        self,
        time_range: Dict[str, datetime],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search task history"""
        from backend.background_tasks.task_manager import background_task_manager
        
        results = []
        for task in background_task_manager.tasks.values():
            if task.started_at:
                if time_range["start"] <= task.started_at <= time_range["end"]:
                    results.append({
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "description": task.description,
                        "status": task.status.value,
                        "started_at": task.started_at.isoformat(),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    })
        
        return sorted(results, key=lambda x: x["started_at"], reverse=True)[:limit]
    
    async def _search_learning(
        self,
        time_range: Dict[str, datetime],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search learning events (uploads, ingestion)"""
        from backend.memory.memory_catalog import memory_catalog
        
        assets = memory_catalog.list_assets(limit=1000)
        
        results = []
        for asset in assets:
            ingestion_date = datetime.fromisoformat(asset.ingestion_date)
            if time_range["start"] <= ingestion_date <= time_range["end"]:
                results.append({
                    "asset_id": asset.asset_id,
                    "asset_type": asset.asset_type.value,
                    "filename": asset.metadata.get("original_filename", asset.path),
                    "status": asset.status.value,
                    "ingestion_date": asset.ingestion_date,
                })
        
        return sorted(results, key=lambda x: x["ingestion_date"], reverse=True)[:limit]
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary of results"""
        parts = []
        
        time_label = results["time_range"]["label"]
        parts.append(f"Activity summary for {time_label}:")
        
        if results["conversations"]:
            parts.append(f"- {len(results['conversations'])} conversation messages")
        
        if results["actions"]:
            approved = sum(1 for a in results["actions"] if a["approved"])
            parts.append(f"- {len(results['actions'])} actions ({approved} approved)")
        
        if results["tasks"]:
            completed = sum(1 for t in results["tasks"] if t["status"] == "completed")
            parts.append(f"- {len(results['tasks'])} tasks ({completed} completed)")
        
        if results["learning_events"]:
            parts.append(f"- {len(results['learning_events'])} files ingested")
        
        return "\n".join(parts)


# Global instance
history_search = HistorySearch()
