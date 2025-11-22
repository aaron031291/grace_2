# Import logging configuration first 
from backend.logging_config import get_logger, log_request, log_error, log_performance 
from fastapi import FastAPI, HTTPException, UploadFile
from datetime import datetime
import asyncio

app = FastAPI()

# Self-Healing Collaborative Co-pilot API Endpoints
@app.get("/api/self_healing/playbooks")
async def get_self_healing_playbooks():
    """Get all self-healing playbooks"""
    try:
        from backend.memory_tables.registry import table_registry
        return await table_registry.query_table("memory_self_healing_playbooks", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/self_healing/playbooks")
async def create_self_healing_playbook(playbook_data: dict):
    """Create new self-healing playbook"""
    try:
        from backend.memory_tables.registry import table_registry
        from backend.unified_logic_hub import submit_schema_update
        
        # Submit for governance approval if high-risk
        risk_level = "high" if playbook_data.get("target_components", []) else "medium"
        
        if risk_level == "high":
            update_id = await submit_schema_update(
                endpoint="/api/self_healing/playbooks",
                current_schema={},
                proposed_schema=playbook_data,
                created_by="self_healing_dashboard",
                risk_level=risk_level
            )
            return {"status": "pending_approval", "update_id": update_id}
        else:
            result = await table_registry.insert_row("memory_self_healing_playbooks", playbook_data)
            return {"status": "created", "id": result["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/self_healing/playbooks/{playbook_id}")
async def update_self_healing_playbook(playbook_id: str, playbook_data: dict):
    """Update self-healing playbook"""
    try:
        from backend.memory_tables.registry import table_registry
        result = await table_registry.update_row("memory_self_healing_playbooks", playbook_id, playbook_data)
        return {"status": "updated", "id": playbook_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/self_healing/playbooks/{playbook_id}/run")
async def run_self_healing_playbook(playbook_id: str, run_params: dict = None):
    """Execute a self-healing playbook"""
    try:
        from backend.memory_tables.registry import table_registry
        
        # Get playbook details
        playbook = await table_registry.get_row("memory_self_healing_playbooks", playbook_id)
        if not playbook:
            raise HTTPException(status_code=404, detail="Playbook not found")
        
        # Create execution log entry
        execution_log = {
            "playbook_id": playbook_id,
            "playbook_name": playbook["playbook_name"],
            "started_at": datetime.now().isoformat(),
            "status": "running",
            "triggered_by": "manual",
            "parameters": run_params or {}
        }
        
        log_result = await table_registry.insert_row("memory_execution_logs", execution_log)
        execution_id = log_result["id"]
        
        # Execute playbook (async)
        asyncio.create_task(_execute_playbook_async(playbook_id, execution_id, playbook, run_params))
        
        return {
            "status": "started",
            "execution_id": execution_id,
            "playbook_name": playbook["playbook_name"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/self_healing/runs")
async def get_self_healing_runs(limit: int = 50):
    """Get self-healing execution history"""
    try:
        from backend.memory_tables.registry import table_registry
        return await table_registry.query_table("memory_execution_logs", {"limit": limit})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/self_healing/runs/{execution_id}")
async def get_self_healing_run(execution_id: str):
    """Get specific execution details"""
    try:
        from backend.memory_tables.registry import table_registry
        return await table_registry.get_row("memory_execution_logs", execution_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/self_healing/incidents")
async def create_incident(incident_data: dict):
    """Create new incident report"""
    try:
        from backend.memory_tables.registry import table_registry
        
        incident_data.update({
            "created_at": datetime.now().isoformat(),
            "status": "open",
            "severity": incident_data.get("severity", "medium")
        })
        
        result = await table_registry.insert_row("memory_incidents", incident_data)
        return {"status": "created", "incident_id": result["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/self_healing/incidents")
async def get_incidents(status: str = None, severity: str = None):
    """Get incident reports"""
    try:
        from backend.memory_tables.registry import table_registry
        filters = {}
        if status:
            filters["status"] = status
        if severity:
            filters["severity"] = severity
        return await table_registry.query_table("memory_incidents", filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/self_healing/agents")
async def get_self_healing_agents():
    """Get self-healing agent fleet"""
    try:
        from backend.memory_tables.registry import table_registry
        return await table_registry.query_table("memory_sub_agents", {"domain": "self_healing"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/self_healing/agents")
async def register_self_healing_agent(agent_data: dict):
    """Register new self-healing agent"""
    try:
        from backend.memory_tables.registry import table_registry
        
        agent_data.update({
            "domain": "self_healing",
            "created_at": datetime.now().isoformat(),
            "status": "active"
        })
        
        result = await table_registry.insert_row("memory_sub_agents", agent_data)
        return {"status": "registered", "agent_id": result["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/self_healing/insights")
async def get_self_healing_insights():
    """Get Grace's self-healing insights"""
    try:
        from backend.memory_tables.registry import table_registry
        return await table_registry.query_table("memory_insights", {"domain": "self_healing"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/self_healing/insights")
async def add_self_healing_insight(insight_data: dict):
    """Add Grace's insight about self-healing"""
    try:
        from backend.memory_tables.registry import table_registry
        
        insight_data.update({
            "domain": "self_healing",
            "created_at": datetime.now().isoformat(),
            "confidence": insight_data.get("confidence", 0.8)
        })
        
        result = await table_registry.insert_row("memory_insights", insight_data)
        return {"status": "added", "insight_id": result["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/self_healing/dashboard")
async def get_self_healing_dashboard():
    """Get complete self-healing dashboard data"""
    try:
        from backend.memory_tables.registry import table_registry
        
        # Get summary data
        playbooks = await table_registry.query_table("memory_self_healing_playbooks", {"limit": 10})
        recent_runs = await table_registry.query_table("memory_execution_logs", {"limit": 20})
        open_incidents = await table_registry.query_table("memory_incidents", {"status": "open"})
        active_agents = await table_registry.query_table("memory_sub_agents", {"status": "active", "domain": "self_healing"})
        recent_insights = await table_registry.query_table("memory_insights", {"domain": "self_healing", "limit": 10})
        
        # Calculate stats
        total_playbooks = len(playbooks.get("rows", []))
        successful_runs = len([r for r in recent_runs.get("rows", []) if r.get("status") == "success"])
        total_runs = len(recent_runs.get("rows", []))
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        return {
            "summary": {
                "total_playbooks": total_playbooks,
                "success_rate": round(success_rate, 1),
                "open_incidents": len(open_incidents.get("rows", [])),
                "active_agents": len(active_agents.get("rows", []))
            },
            "playbooks": playbooks,
            "recent_runs": recent_runs,
            "open_incidents": open_incidents,
            "active_agents": active_agents,
            "recent_insights": recent_insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/self_healing/approve/{item_type}/{item_id}")
async def approve_self_healing_item(item_type: str, item_id: str, approval_data: dict):
    """Approve self-healing playbook/rule/agent"""
    try:
        from backend.unified_logic_hub import approve_update
        
        result = await approve_update(
            update_id=item_id,
            approved_by=approval_data.get("approved_by", "user"),
            notes=approval_data.get("notes", "")
        )
        
        return {"status": "approved", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _execute_playbook_async(playbook_id: str, execution_id: str, playbook: dict, params: dict):
    """Execute playbook asynchronously and update execution log"""
    try:
        from backend.memory_tables.registry import table_registry
        
        # Simulate playbook execution
        await asyncio.sleep(2)  # Simulate work
        
        # Update execution log
        await table_registry.update_row("memory_execution_logs", execution_id, {
            "status": "success",
            "completed_at": datetime.now().isoformat(),
            "duration_ms": 2000,
            "result": "Playbook executed successfully"
        })
        
        # Update playbook success stats
        current_stats = playbook.get("execution_stats", {"total_runs": 0, "successful_runs": 0})
        current_stats["total_runs"] += 1
        current_stats["successful_runs"] += 1
        current_stats["last_run"] = datetime.now().isoformat()
        
        await table_registry.update_row("memory_self_healing_playbooks", playbook_id, {
            "execution_stats": current_stats
        })
        
    except Exception as e:
        # Update execution log with error
        await table_registry.update_row("memory_execution_logs", execution_id, {
            "status": "failed",
            "completed_at": datetime.now().isoformat(),
            "error": str(e)
        })

# Memory File Service API Endpoints
@app.get("/api/memory/tree")
async def get_memory_tree(path: str = ""):
    """Get hierarchical file tree"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.get_file_tree(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/files")
async def get_memory_files():
    """List all files (alias for tree)"""
    return await get_memory_tree()

@app.get("/api/memory/file")
async def get_memory_file(path: str):
    """Get file content"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.get_file(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/file")
async def save_memory_file(path: str, content: str):
    """Save file content"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.save_file(path, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory/file")
async def delete_memory_file(path: str):
    """Delete file"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.delete_file(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/folder")
async def create_memory_folder(path: str):
    """Create folder"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.create_folder(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/status")
async def get_memory_status():
    """Get memory workspace status"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        
        # Get basic stats
        root_path = service.root_path
        total_files = sum(1 for _ in root_path.rglob("*") if _.is_file())
        total_size = sum(_.stat().st_size for _ in root_path.rglob("*") if _.is_file())
        
        return {
            "component_id": f"memory_file_service_{service.root_path.name}",
            "status": "active",
            "root_path": str(service.root_path),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/search")
async def search_memory_files(q: str, types: str = None):
    """Search files by name or content"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        file_types = types.split(',') if types else None
        return await service.search_files(q, file_types)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/upload")
async def upload_memory_file(file: UploadFile, path: str = ""):
    """Upload file to memory workspace"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        
        # Read file content
        content = await file.read()
        
        # Determine target path
        target_path = f"{path}/{file.filename}" if path else file.filename
        
        # Save file
        if file.content_type and file.content_type.startswith('text/'):
            content_str = content.decode('utf-8')
        else:
            # For binary files, save as base64
            import base64
            content_str = base64.b64encode(content).decode('utf-8')
        
        return await service.save_file(target_path, content_str, {
            "original_filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "is_binary": not (file.content_type and file.content_type.startswith('text/'))
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

