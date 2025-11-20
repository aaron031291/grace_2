"""
Create HTM Remediation Task from CI Failure

Called by GitHub Actions when stress tests fail
Automatically creates an HTM task for investigation
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.htm_models import HTMTask
from backend.models.base_models import async_session
from backend.core.message_bus import message_bus, MessagePriority


async def create_remediation_task(
    source: str,
    issue: str,
    priority: str = "high",
    context: str = ""
):
    """
    Create HTM task for CI failure remediation
    
    Args:
        source: Source of failure (e.g., "nightly_stress_ci")
        issue: Description of issue
        priority: Task priority
        context: Additional context (logs, errors)
    """
    
    task_id = f"remediate_{source}_{datetime.now(timezone.utc).timestamp()}"
    
    # Create HTM task
    async with async_session() as session:
        task = HTMTask(
            task_id=task_id,
            task_type="remediation",
            domain="ci_failures",
            priority=priority,
            payload={
                "source": source,
                "issue": issue,
                "context": context[:5000],  # Truncate long context
                "created_by_ci": True,
                "auto_remediation": True
            },
            status="queued",
            sla_ms=3600000,  # 1 hour to investigate
            sla_deadline=datetime.now(timezone.utc).timestamp() + 3600,
            created_by="ci_automation"
        )
        session.add(task)
        await session.commit()
        
        print(f"[HTM REMEDIATION] Created task: {task_id}")
        print(f"  Issue: {issue}")
        print(f"  Priority: {priority}")
        print(f"  Source: {source}")
    
    # Publish to message bus
    try:
        await message_bus.publish(
            source="ci_automation",
            topic="htm.task.remediation_created",
            payload={
                "task_id": task_id,
                "source": source,
                "issue": issue,
                "priority": priority,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            priority=MessagePriority.HIGH
        )
    except Exception as e:
        print(f"[WARNING] Failed to publish message bus event: {e}")
    
    return task_id


async def main():
    parser = argparse.ArgumentParser(description="Create HTM remediation task from CI failure")
    parser.add_argument("--source", required=True, help="Source of failure")
    parser.add_argument("--issue", required=True, help="Issue description")
    parser.add_argument("--priority", default="high", help="Task priority")
    parser.add_argument("--context", default="", help="Additional context")
    
    args = parser.parse_args()
    
    task_id = await create_remediation_task(
        source=args.source,
        issue=args.issue,
        priority=args.priority,
        context=args.context
    )
    
    print(f"\n✅ HTM remediation task created: {task_id}")
    print("Task will be picked up by HTM for investigation and auto-remediation.")


if __name__ == "__main__":
    asyncio.run(main())
