"""WebSocket message handlers for IDE"""

async def dispatch_message(client, message: dict):
    """Route messages to appropriate handlers"""
    
    msg_type = message.get("type")
    
    if msg_type == "file.read":
        return await handle_file_read(client, message)
    elif msg_type == "file.write":
        return await handle_file_write(client, message)
    elif msg_type == "file.list":
        return await handle_file_list(client, message)
    elif msg_type == "execute.run":
        return await handle_execute(client, message)
    elif msg_type == "security.scan":
        return await handle_security_scan(client, message)
    elif msg_type == "memory.search":
        return await handle_memory_search(client, message)
    else:
        return {"type": "error", "message": f"Unknown message type: {msg_type}"}

async def handle_file_read(client, message):
    """Read file from sandbox"""
    from backend.sandbox_manager import sandbox_manager
    
    try:
        content = await sandbox_manager.read_file(client.user, message["path"])
        return {
            "type": "file.content",
            "path": message["path"],
            "content": content
        }
    except Exception as e:
        return {"type": "error", "message": str(e)}

async def handle_file_write(client, message):
    """Write file to sandbox"""
    from backend.sandbox_manager import sandbox_manager
    from backend.governance import governance_engine
    
    decision = await governance_engine.check(
        actor=client.user,
        action="file_write",
        resource=message["path"],
        payload={"content_size": len(message.get("content", ""))}
    )
    
    if decision["decision"] != "allow":
        return {"type": "error", "message": f"Blocked: {decision['policy']}"}
    
    try:
        result = await sandbox_manager.write_file(
            client.user,
            message["path"],
            message["content"]
        )
        return {"type": "file.saved", "path": result["path"]}
    except Exception as e:
        return {"type": "error", "message": str(e)}

async def handle_file_list(client, message):
    """List sandbox files"""
    from backend.sandbox_manager import sandbox_manager
    
    files = await sandbox_manager.list_files(client.user)
    return {"type": "file.list", "files": files}

async def handle_execute(client, message):
    """Execute code in sandbox"""
    from backend.sandbox_manager import sandbox_manager
    from backend.governance import governance_engine
    from backend.hunter import hunter
    
    decision = await governance_engine.check(
        actor=client.user,
        action="execute_code",
        resource=message["command"],
        payload=message
    )
    
    if decision["decision"] == "block":
        return {"type": "execution.blocked", "reason": decision["policy"]}
    
    alerts = await hunter.inspect(client.user, "execute", message["command"], message)
    
    if alerts:
        return {"type": "execution.blocked", "reason": f"{len(alerts)} security alerts", "alerts": alerts}
    
    stdout, stderr, exit_code, duration = await sandbox_manager.run_command(
        client.user,
        message["command"],
        message.get("file_name")
    )
    
    return {
        "type": "execution.result",
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "duration_ms": duration,
        "success": exit_code == 0
    }

async def handle_security_scan(client, message):
    """Scan file for security issues"""
    from backend.hunter import hunter
    
    alerts = await hunter.inspect(
        client.user,
        "security_scan",
        message.get("path", ""),
        {"content": message.get("content", "")}
    )
    
    return {
        "type": "security.results",
        "alerts": len(alerts),
        "findings": [{"rule": a[0], "event_id": a[1]} for a in alerts]
    }

async def handle_memory_search(client, message):
    """Search memory/knowledge base"""
    from backend.knowledge import knowledge_manager
    
    results = await knowledge_manager.search_knowledge(
        message.get("query", ""),
        limit=message.get("limit", 5)
    )
    
    return {
        "type": "memory.results",
        "results": results
    }
