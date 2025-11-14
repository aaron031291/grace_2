"""
Layer 3: Context Memory & Provenance
Persistent store for task context, source lineage, agent ownership, SLA history

Ensures:
- Lossless handoffs between components
- Complete audit trails
- Provenance tracking for all decisions
- Task context preservation across restarts

The W's coverage:
- WHY: Intent and reasoning context
- WHAT: Task details and outcomes
- WHERE: Source and destination
- WHEN: Timestamps and SLAs
- WHO: Agent ownership
- HOW: Execution details and workflows

All components reference this layer for decisions.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
import sqlite3

from backend.core.message_bus import message_bus, MessagePriority


class TaskContext:
    """Complete task context with all W's answered"""
    
    def __init__(
        self,
        task_id: str,
        why: Dict[str, Any],      # Intent, reasoning, goals
        what: Dict[str, Any],     # Task details, payload
        where: Dict[str, Any],    # Source, destination, lineage
        when: Dict[str, Any],     # Timestamps, deadlines, SLAs
        who: Dict[str, Any],      # Agent ownership, assignments
        how: Dict[str, Any]       # Execution details, workflows
    ):
        self.task_id = task_id
        self.why = why
        self.what = what
        self.where = where
        self.when = when
        self.who = who
        self.how = how
        
        # Metadata
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "task_id": self.task_id,
            "why": self.why,
            "what": self.what,
            "where": self.where,
            "when": self.when,
            "who": self.who,
            "how": self.how,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }
    
    def update(self, field: str, data: Dict[str, Any]):
        """Update context field"""
        if hasattr(self, field):
            current = getattr(self, field)
            current.update(data)
            self.updated_at = datetime.utcnow()
            self.version += 1


class Provenance:
    """Track source lineage and data provenance"""
    
    def __init__(
        self,
        entity_id: str,
        entity_type: str,  # task, chunk, decision, etc.
        source_chain: List[Dict[str, Any]]
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.source_chain = source_chain  # List of sources from origin to current
        self.created_at = datetime.utcnow()
    
    def add_transformation(
        self,
        actor: str,
        action: str,
        metadata: Dict[str, Any]
    ):
        """Add transformation to provenance chain"""
        self.source_chain.append({
            "actor": actor,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "source_chain": self.source_chain,
            "created_at": self.created_at.isoformat(),
            "chain_length": len(self.source_chain)
        }


class ContextMemoryStore:
    """
    Persistent context memory with provenance tracking
    
    Stores:
    - Task contexts (all W's)
    - Source lineage
    - Agent ownership
    - SLA history
    - Handoff data
    
    Enables:
    - Lossless handoffs
    - Audit trails
    - Decision traceability
    - Context recovery
    """
    
    def __init__(self, db_path: str = "databases/context_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self.contexts: Dict[str, TaskContext] = {}
        self.provenance: Dict[str, Provenance] = {}
        
        # Initialize database
        self._init_database()
        
        # Statistics
        self.stats = {
            "contexts_stored": 0,
            "contexts_retrieved": 0,
            "provenance_chains": 0,
            "handoffs_tracked": 0
        }
    
    def _init_database(self):
        """Initialize SQLite database"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Task contexts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_contexts (
                task_id TEXT PRIMARY KEY,
                why_json TEXT,
                what_json TEXT,
                where_json TEXT,
                when_json TEXT,
                who_json TEXT,
                how_json TEXT,
                created_at TEXT,
                updated_at TEXT,
                version INTEGER
            )
        """)
        
        # Provenance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS provenance (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                source_chain_json TEXT,
                created_at TEXT,
                chain_length INTEGER
            )
        """)
        
        # SLA history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sla_history (
                task_id TEXT,
                event_type TEXT,
                timestamp TEXT,
                sla_seconds INTEGER,
                time_remaining REAL,
                escalated BOOLEAN,
                breached BOOLEAN,
                PRIMARY KEY (task_id, timestamp)
            )
        """)
        
        # Agent ownership table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_ownership (
                task_id TEXT,
                agent_id TEXT,
                role TEXT,
                assigned_at TEXT,
                completed_at TEXT,
                PRIMARY KEY (task_id, agent_id)
            )
        """)
        
        # Handoff log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS handoff_log (
                handoff_id TEXT PRIMARY KEY,
                task_id TEXT,
                from_agent TEXT,
                to_agent TEXT,
                reason TEXT,
                context_snapshot TEXT,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("[CONTEXT-MEMORY] Database initialized")
    
    async def store_context(self, context: TaskContext):
        """Store task context"""
        
        self.contexts[context.task_id] = context
        self.stats["contexts_stored"] += 1
        
        # Persist to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO task_contexts
            (task_id, why_json, what_json, where_json, when_json, who_json, how_json,
             created_at, updated_at, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            context.task_id,
            json.dumps(context.why),
            json.dumps(context.what),
            json.dumps(context.where),
            json.dumps(context.when),
            json.dumps(context.who),
            json.dumps(context.how),
            context.created_at.isoformat(),
            context.updated_at.isoformat(),
            context.version
        ))
        
        conn.commit()
        conn.close()
        
        # Publish event
        await message_bus.publish(
            source="context_memory",
            topic="context.stored",
            payload={"task_id": context.task_id},
            priority=MessagePriority.LOW
        )
    
    async def retrieve_context(self, task_id: str) -> Optional[TaskContext]:
        """Retrieve task context"""
        
        # Check cache first
        if task_id in self.contexts:
            self.stats["contexts_retrieved"] += 1
            return self.contexts[task_id]
        
        # Query database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT why_json, what_json, where_json, when_json, who_json, how_json,
                   created_at, updated_at, version
            FROM task_contexts
            WHERE task_id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Reconstruct context
        context = TaskContext(
            task_id=task_id,
            why=json.loads(row[0]),
            what=json.loads(row[1]),
            where=json.loads(row[2]),
            when=json.loads(row[3]),
            who=json.loads(row[4]),
            how=json.loads(row[5])
        )
        
        context.created_at = datetime.fromisoformat(row[6])
        context.updated_at = datetime.fromisoformat(row[7])
        context.version = row[8]
        
        # Cache it
        self.contexts[task_id] = context
        self.stats["contexts_retrieved"] += 1
        
        return context
    
    async def store_provenance(self, provenance: Provenance):
        """Store provenance chain"""
        
        self.provenance[provenance.entity_id] = provenance
        self.stats["provenance_chains"] += 1
        
        # Persist to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO provenance
            (entity_id, entity_type, source_chain_json, created_at, chain_length)
            VALUES (?, ?, ?, ?, ?)
        """, (
            provenance.entity_id,
            provenance.entity_type,
            json.dumps(provenance.source_chain),
            provenance.created_at.isoformat(),
            len(provenance.source_chain)
        ))
        
        conn.commit()
        conn.close()
    
    async def track_handoff(
        self,
        task_id: str,
        from_agent: str,
        to_agent: str,
        reason: str,
        context_snapshot: Dict[str, Any]
    ):
        """Track lossless handoff between agents"""
        
        handoff_id = f"handoff_{task_id}_{datetime.utcnow().timestamp()}"
        self.stats["handoffs_tracked"] += 1
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO handoff_log
            (handoff_id, task_id, from_agent, to_agent, reason, context_snapshot, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            handoff_id,
            task_id,
            from_agent,
            to_agent,
            reason,
            json.dumps(context_snapshot),
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[CONTEXT-MEMORY] Handoff: {from_agent} -> {to_agent} (task: {task_id})")
        
        # Publish event
        await message_bus.publish(
            source="context_memory",
            topic="agent.handoff.tracked",
            payload={
                "handoff_id": handoff_id,
                "task_id": task_id,
                "from_agent": from_agent,
                "to_agent": to_agent,
                "reason": reason
            },
            priority=MessagePriority.NORMAL
        )
    
    async def record_sla_event(
        self,
        task_id: str,
        event_type: str,
        sla_seconds: int,
        time_remaining: float,
        escalated: bool = False,
        breached: bool = False
    ):
        """Record SLA-related event"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sla_history
            (task_id, event_type, timestamp, sla_seconds, time_remaining, escalated, breached)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            event_type,
            datetime.utcnow().isoformat(),
            sla_seconds,
            time_remaining,
            escalated,
            breached
        ))
        
        conn.commit()
        conn.close()
    
    def get_task_history(self, task_id: str) -> Dict[str, Any]:
        """Get complete history for a task"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get context
        cursor.execute("SELECT * FROM task_contexts WHERE task_id = ?", (task_id,))
        context_row = cursor.fetchone()
        
        # Get SLA history
        cursor.execute("SELECT * FROM sla_history WHERE task_id = ? ORDER BY timestamp", (task_id,))
        sla_rows = cursor.fetchall()
        
        # Get agent ownership
        cursor.execute("SELECT * FROM agent_ownership WHERE task_id = ?", (task_id,))
        ownership_rows = cursor.fetchall()
        
        # Get handoffs
        cursor.execute("SELECT * FROM handoff_log WHERE task_id = ? ORDER BY timestamp", (task_id,))
        handoff_rows = cursor.fetchall()
        
        conn.close()
        
        return {
            "task_id": task_id,
            "context": dict(zip(["task_id", "why", "what", "where", "when", "who", "how"], context_row)) if context_row else None,
            "sla_events": len(sla_rows),
            "agents_involved": len(ownership_rows),
            "handoffs": len(handoff_rows)
        }


class ContextMemoryService:
    """
    Layer 3 Context Memory Service
    
    Provides:
    - Task context storage and retrieval
    - Provenance tracking
    - Agent ownership management
    - SLA history
    - Lossless handoff coordination
    """
    
    def __init__(self):
        self.store = ContextMemoryStore()
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start context memory service"""
        
        # Subscribe to events that need context tracking
        asyncio.create_task(self._track_task_events())
        asyncio.create_task(self._track_handoff_events())
        asyncio.create_task(self._track_sla_events())
        
        self._monitor_task = asyncio.create_task(self._publish_metrics())
        
        print("[CONTEXT-MEMORY] Service started")
        print("[CONTEXT-MEMORY] All W's tracked: WHY, WHAT, WHERE, WHEN, WHO, HOW")
    
    async def _track_task_events(self):
        """Track task lifecycle events"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="context_memory",
                topic="task.queued"
            )
            
            while True:
                msg = await queue.get()
                task_data = msg.payload
                
                # Create full context
                context = TaskContext(
                    task_id=task_data.get("task_id"),
                    why={
                        "intent": task_data.get("intent", "unknown"),
                        "reasoning": task_data.get("reasoning", ""),
                        "created_by": msg.source
                    },
                    what={
                        "task_type": task_data.get("task_type"),
                        "payload": task_data.get("payload", {}),
                        "expected_outcome": task_data.get("outcome", "")
                    },
                    where={
                        "source": msg.source,
                        "destination": task_data.get("handler", "unknown"),
                        "lineage": [msg.source]
                    },
                    when={
                        "created_at": datetime.utcnow().isoformat(),
                        "sla_seconds": task_data.get("sla_seconds"),
                        "deadline": task_data.get("deadline")
                    },
                    who={
                        "created_by": msg.source,
                        "assigned_to": task_data.get("handler"),
                        "ownership_chain": []
                    },
                    how={
                        "workflow": task_data.get("workflow", []),
                        "execution_plan": task_data.get("execution_plan", {}),
                        "prerequisites": task_data.get("prerequisites", [])
                    }
                )
                
                await self.store.store_context(context)
        
        except Exception as e:
            print(f"[CONTEXT-MEMORY] Task tracking error: {e}")
    
    async def _track_handoff_events(self):
        """Track agent handoffs"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="context_memory_handoffs",
                topic="agent.handoff.*"
            )
            
            while True:
                msg = await queue.get()
                
                task_id = msg.payload.get("task_id")
                from_agent = msg.payload.get("from_agent")
                to_agent = msg.payload.get("to_agent")
                reason = msg.payload.get("reason", "")
                
                # Get current context
                context = await self.store.retrieve_context(task_id)
                if context:
                    # Track handoff with full context snapshot
                    await self.store.track_handoff(
                        task_id,
                        from_agent,
                        to_agent,
                        reason,
                        context.to_dict()
                    )
        
        except Exception as e:
            print(f"[CONTEXT-MEMORY] Handoff tracking error: {e}")
    
    async def _track_sla_events(self):
        """Track SLA events"""
        
        try:
            topics = ["task.escalated", "task.sla.breached", "task.sla.approaching"]
            
            for topic in topics:
                asyncio.create_task(self._monitor_sla_topic(topic))
        
        except Exception as e:
            print(f"[CONTEXT-MEMORY] SLA tracking error: {e}")
    
    async def _monitor_sla_topic(self, topic: str):
        """Monitor specific SLA topic"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber=f"context_memory_sla_{topic}",
                topic=topic
            )
            
            while True:
                msg = await queue.get()
                
                task_id = msg.payload.get("task_id")
                sla_seconds = msg.payload.get("sla_seconds", 0)
                time_remaining = msg.payload.get("time_remaining", 0)
                
                event_type = topic.split('.')[-1]  # escalated, breached, approaching
                
                await self.store.record_sla_event(
                    task_id,
                    event_type,
                    sla_seconds,
                    time_remaining,
                    escalated=(event_type == "escalated"),
                    breached=(event_type == "breached")
                )
        
        except Exception as e:
            print(f"[CONTEXT-MEMORY] SLA topic {topic} error: {e}")
    
    async def _publish_metrics(self):
        """Publish context memory metrics"""
        
        while True:
            try:
                await asyncio.sleep(60)
                
                await message_bus.publish(
                    source="context_memory",
                    topic="layer3.context_memory.metrics",
                    payload={
                        "statistics": self.store.stats,
                        "active_contexts": len(self.store.contexts),
                        "provenance_chains": len(self.store.provenance),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=MessagePriority.LOW
                )
            
            except Exception as e:
                print(f"[CONTEXT-MEMORY] Metrics publish error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "statistics": self.store.stats,
            "active_contexts": len(self.store.contexts),
            "provenance_chains": len(self.store.provenance),
            "database": str(self.store.db_path)
        }


# Global instance
context_memory_service = ContextMemoryService()
