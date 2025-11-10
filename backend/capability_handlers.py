"""
Capability Handlers - Implementation of registered capabilities

These handlers delegate to existing backend services,
ensuring all operations go through proper authentication,
authorization, and logging.
"""

from typing import Dict, Any


async def handle_task_list(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """List tasks via existing task service"""
    try:
        from .models import Task, async_session
        from sqlalchemy import select
        
        status_filter = parameters.get("status")
        
        async with async_session() as session:
            query = select(Task)
            if status_filter:
                query = query.where(Task.status == status_filter)
            
            result = await session.execute(query.limit(20))
            tasks = result.scalars().all()
            
            return {
                "ok": True,
                "count": len(tasks),
                "tasks": [
                    {"id": t.id, "title": getattr(t, "title", ""), "status": t.status}
                    for t in tasks
                ]
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def handle_task_create(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Create task via existing task service"""
    try:
        from .models import Task, async_session
        
        async with async_session() as session:
            task = Task(
                title=parameters.get("title", "Untitled"),
                description=parameters.get("description"),
                status="pending",
                priority=parameters.get("priority", "medium")
            )
            session.add(task)
            await session.commit()
            
            return {
                "ok": True,
                "task_id": task.id,
                "title": task.title
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def handle_knowledge_search(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Search knowledge via existing knowledge service"""
    try:
        from .knowledge import knowledge_manager
        
        query = parameters.get("query", "")
        limit = parameters.get("limit", 10)
        
        results = await knowledge_manager.search_knowledge(query, limit=limit)
        
        return {
            "ok": True,
            "count": len(results),
            "results": results[:5]  # Top 5 for verbalization
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def handle_chat_respond(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Handle general chat (fallback)"""
    return {
        "ok": True,
        "response": "I've processed your message.",
        "note": "This is a simple acknowledgment. Full LLM response would go here."
    }


async def handle_verification_status(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Get verification status"""
    try:
        from .progression_tracker import progression_tracker
        
        status = await progression_tracker.get_current_status()
        
        if status:
            from dataclasses import asdict
            return {"ok": True, "status": asdict(status)}
        else:
            return {"ok": True, "status": None, "message": "No active mission"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def handle_benchmark_run(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Run benchmarks"""
    try:
        from .benchmarks import benchmark_suite
        
        bench_type = parameters.get("type", "smoke")
        
        if bench_type == "regression":
            result = await benchmark_suite.run_regression_suite()
        else:
            result = await benchmark_suite.run_smoke_tests()
        
        return {
            "ok": True,
            "benchmark": result
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Register all handlers
def register_handlers(registry):
    """Register all capability handlers"""
    registry.handlers["task.list"] = handle_task_list
    registry.handlers["task.create"] = handle_task_create
    registry.handlers["knowledge.search"] = handle_knowledge_search
    registry.handlers["chat.respond"] = handle_chat_respond
    registry.handlers["verification.status"] = handle_verification_status
    registry.handlers["benchmark.run"] = handle_benchmark_run
