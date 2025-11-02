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
    elif msg_type == "security.fix":
        return await handle_auto_fix(client, message)
    elif msg_type == "security.quarantine":
        return await handle_quarantine(client, message)
    elif msg_type == "security.list_quarantined":
        return await handle_list_quarantined(client, message)
    elif msg_type == "security.restore":
        return await handle_restore_quarantined(client, message)
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
    """Scan file or code for security issues"""
    from backend.ide_security import security_scanner
    
    try:
        if message.get("file_path"):
            issues = await security_scanner.scan_file(message["file_path"])
        elif message.get("content"):
            language = message.get("language", "unknown")
            issues = await security_scanner.scan_code(message["content"], language)
        else:
            return {"type": "error", "message": "No file_path or content provided"}
        
        return {
            "type": "security.scan_results",
            "issues": issues,
            "total_issues": len(issues),
            "critical": len([i for i in issues if i['severity'] == 'critical']),
            "high": len([i for i in issues if i['severity'] == 'high']),
            "medium": len([i for i in issues if i['severity'] == 'medium']),
            "low": len([i for i in issues if i['severity'] == 'low']),
        }
    except Exception as e:
        return {"type": "error", "message": f"Scan failed: {str(e)}"}

async def handle_auto_fix(client, message):
    """Apply automated fix to file"""
    from backend.auto_fix import auto_fix
    from backend.governance import governance_engine
    
    file_path = message.get("file_path")
    fix_type = message.get("fix_type")
    
    if not file_path or not fix_type:
        return {"type": "error", "message": "file_path and fix_type required"}
    
    # Check governance
    decision = await governance_engine.check(
        actor=client.user,
        action="auto_fix",
        resource=file_path,
        payload={"fix_type": fix_type}
    )
    
    if decision["decision"] == "block":
        return {"type": "error", "message": f"Blocked: {decision['policy']}"}
    
    try:
        result = await auto_fix.apply_fix(file_path, fix_type)
        return {
            "type": "security.fix_applied",
            **result
        }
    except Exception as e:
        return {"type": "error", "message": f"Fix failed: {str(e)}"}

async def handle_quarantine(client, message):
    """Quarantine a suspicious file"""
    from backend.auto_quarantine import quarantine_manager
    
    file_path = message.get("file_path")
    reason = message.get("reason", "Security threat detected")
    
    if not file_path:
        return {"type": "error", "message": "file_path required"}
    
    try:
        result = await quarantine_manager.quarantine_file(file_path, reason, client.user)
        return {
            "type": "security.quarantined",
            **result
        }
    except Exception as e:
        return {"type": "error", "message": f"Quarantine failed: {str(e)}"}

async def handle_list_quarantined(client, message):
    """List all quarantined files"""
    from backend.auto_quarantine import quarantine_manager
    
    try:
        status = message.get("status")
        files = quarantine_manager.list_quarantined(status)
        return {
            "type": "security.quarantine_list",
            "files": files,
            "total": len(files)
        }
    except Exception as e:
        return {"type": "error", "message": f"List failed: {str(e)}"}

async def handle_restore_quarantined(client, message):
    """Restore a quarantined file"""
    from backend.auto_quarantine import quarantine_manager
    
    quarantine_id = message.get("quarantine_id")
    
    if not quarantine_id:
        return {"type": "error", "message": "quarantine_id required"}
    
    try:
        result = await quarantine_manager.restore_file(quarantine_id, client.user)
        return {
            "type": "security.restore_result",
            **result
        }
    except Exception as e:
        return {"type": "error", "message": f"Restore failed: {str(e)}"}

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
