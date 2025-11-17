"""
Core Skills - Essential skills for Grace's agents
Memory, web search, code operations, system commands
"""

from typing import Dict, Any
from backend.skills.registry import skill_registry, Skill, SkillCategory

async def read_memory_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Read from Grace's memory"""
    try:
        from backend.memory_services.memory import memory_service
        
        query = params.get("query", "")
        limit = params.get("limit", 5)
        
        results = await memory_service.semantic_search(query, limit=limit)
        
        return {
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {"error": str(e), "results": []}

async def write_memory_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Write to Grace's memory"""
    try:
        from backend.memory_services.memory import memory_service
        
        content = params.get("content", "")
        metadata = params.get("metadata", {})
        
        result = await memory_service.store(content, metadata)
        
        return {"stored": True, "id": result.get("id")}
    except Exception as e:
        return {"error": str(e), "stored": False}

async def web_search_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search the web"""
    try:
        query = params.get("query", "")
        max_results = params.get("max_results", 5)
        
        return {
            "query": query,
            "results": [],
            "note": "Web search integration pending"
        }
    except Exception as e:
        return {"error": str(e), "results": []}

async def execute_code_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute code in sandbox"""
    try:
        code = params.get("code", "")
        language = params.get("language", "python")
        
        return {
            "executed": False,
            "note": "Sandbox execution pending",
            "code": code
        }
    except Exception as e:
        return {"error": str(e), "executed": False}

async def run_tests_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run tests"""
    try:
        test_path = params.get("test_path", "")
        
        return {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "note": "Test runner integration pending"
        }
    except Exception as e:
        return {"error": str(e)}

async def start_screen_share_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Start screen sharing"""
    try:
        from backend.world_model import world_model_service
        
        user_id = params.get("user_id", "user")
        quality_settings = params.get("quality_settings", {})
        
        session_id = await world_model_service.start_screen_share(
            user_id=user_id,
            quality_settings=quality_settings
        )
        
        return {
            "session_id": session_id,
            "status": "active",
            "message": "Screen sharing started"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

async def stop_screen_share_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Stop screen sharing"""
    try:
        from backend.world_model import world_model_service
        
        session_id = params.get("session_id", "")
        
        success = await world_model_service.stop_screen_share(session_id)
        
        return {
            "success": success,
            "session_id": session_id,
            "message": "Screen sharing stopped" if success else "Session not found"
        }
    except Exception as e:
        return {"error": str(e), "success": False}

async def start_recording_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Start recording"""
    try:
        from backend.world_model import world_model_service
        
        user_id = params.get("user_id", "user")
        media_type = params.get("media_type", "screen_recording")
        metadata = params.get("metadata", {})
        
        session_id = await world_model_service.start_recording(
            user_id=user_id,
            media_type=media_type,
            metadata=metadata
        )
        
        return {
            "session_id": session_id,
            "status": "recording",
            "message": f"{media_type} started"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

async def stop_recording_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Stop recording"""
    try:
        from backend.world_model import world_model_service
        
        session_id = params.get("session_id", "")
        
        result = await world_model_service.stop_recording(session_id)
        
        if result:
            return {
                "success": True,
                "session_id": session_id,
                "file_path": result.get("file_path"),
                "duration": result.get("duration"),
                "message": "Recording stopped"
            }
        else:
            return {
                "success": False,
                "message": "Session not found"
            }
    except Exception as e:
        return {"error": str(e), "success": False}

async def toggle_voice_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Toggle voice control"""
    try:
        from backend.world_model import world_model_service
        
        user_id = params.get("user_id", "user")
        enable = params.get("enable", True)
        
        enabled = await world_model_service.toggle_voice(user_id, enable)
        
        return {
            "voice_enabled": enabled,
            "user_id": user_id,
            "message": f"Voice {'enabled' if enabled else 'disabled'}"
        }
    except Exception as e:
        return {"error": str(e), "voice_enabled": False}

async def create_background_task_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create background task"""
    try:
        from backend.world_model import world_model_service
        
        task_type = params.get("task_type", "general")
        metadata = params.get("metadata", {})
        
        task_id = await world_model_service.create_background_task(
            task_type=task_type,
            metadata=metadata
        )
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Background task created"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

def register_core_skills():
    """Register all core skills"""
    
    skill_registry.register(Skill(
        name="read_memory",
        category=SkillCategory.MEMORY,
        description="Search and retrieve information from Grace's memory",
        input_schema={
            "query": {"type": "string", "required": True},
            "limit": {"type": "integer", "default": 5}
        },
        output_schema={
            "results": {"type": "array"},
            "count": {"type": "integer"}
        },
        handler=read_memory_handler,
        governance_action_type="read_memory",
        capability_tags=["memory", "retrieval", "rag"]
    ))
    
    skill_registry.register(Skill(
        name="write_memory",
        category=SkillCategory.MEMORY,
        description="Store information in Grace's memory",
        input_schema={
            "content": {"type": "string", "required": True},
            "metadata": {"type": "object", "default": {}}
        },
        output_schema={
            "stored": {"type": "boolean"},
            "id": {"type": "string"}
        },
        handler=write_memory_handler,
        governance_action_type="write_memory",
        capability_tags=["memory", "storage"]
    ))
    
    skill_registry.register(Skill(
        name="web_search",
        category=SkillCategory.WEB,
        description="Search the web for information",
        input_schema={
            "query": {"type": "string", "required": True},
            "max_results": {"type": "integer", "default": 5}
        },
        output_schema={
            "results": {"type": "array"},
            "query": {"type": "string"}
        },
        handler=web_search_handler,
        governance_action_type="external_api_call",
        capability_tags=["web", "search", "external"]
    ))
    
    skill_registry.register(Skill(
        name="execute_code",
        category=SkillCategory.CODE,
        description="Execute code in a sandbox environment",
        input_schema={
            "code": {"type": "string", "required": True},
            "language": {"type": "string", "default": "python"}
        },
        output_schema={
            "executed": {"type": "boolean"},
            "output": {"type": "string"}
        },
        handler=execute_code_handler,
        governance_action_type="execute_code",
        timeout_seconds=60,
        capability_tags=["code", "execution", "sandbox"]
    ))
    
    skill_registry.register(Skill(
        name="run_tests",
        category=SkillCategory.CODE,
        description="Run tests to verify code changes",
        input_schema={
            "test_path": {"type": "string", "required": True}
        },
        output_schema={
            "tests_run": {"type": "integer"},
            "passed": {"type": "integer"},
            "failed": {"type": "integer"}
        },
        handler=run_tests_handler,
        governance_action_type="execute_code",
        timeout_seconds=120,
        capability_tags=["code", "testing", "verification"]
    ))
    
    skill_registry.register(Skill(
        name="start_screen_share",
        category=SkillCategory.SYSTEM,
        description="Start screen sharing session",
        input_schema={
            "user_id": {"type": "string", "required": True},
            "quality_settings": {"type": "object", "default": {}}
        },
        output_schema={
            "session_id": {"type": "string"},
            "status": {"type": "string"}
        },
        handler=start_screen_share_handler,
        governance_action_type="multimodal_operation",
        capability_tags=["orb", "multimodal", "screen-share"]
    ))
    
    skill_registry.register(Skill(
        name="stop_screen_share",
        category=SkillCategory.SYSTEM,
        description="Stop screen sharing session",
        input_schema={
            "session_id": {"type": "string", "required": True}
        },
        output_schema={
            "success": {"type": "boolean"},
            "message": {"type": "string"}
        },
        handler=stop_screen_share_handler,
        governance_action_type="multimodal_operation",
        capability_tags=["orb", "multimodal", "screen-share"]
    ))
    
    skill_registry.register(Skill(
        name="start_recording",
        category=SkillCategory.SYSTEM,
        description="Start recording session (video/audio/screen)",
        input_schema={
            "user_id": {"type": "string", "required": True},
            "media_type": {"type": "string", "default": "screen_recording"},
            "metadata": {"type": "object", "default": {}}
        },
        output_schema={
            "session_id": {"type": "string"},
            "status": {"type": "string"}
        },
        handler=start_recording_handler,
        governance_action_type="multimodal_operation",
        capability_tags=["orb", "multimodal", "recording"]
    ))
    
    skill_registry.register(Skill(
        name="stop_recording",
        category=SkillCategory.SYSTEM,
        description="Stop recording session",
        input_schema={
            "session_id": {"type": "string", "required": True}
        },
        output_schema={
            "success": {"type": "boolean"},
            "file_path": {"type": "string"},
            "duration": {"type": "number"}
        },
        handler=stop_recording_handler,
        governance_action_type="multimodal_operation",
        capability_tags=["orb", "multimodal", "recording"]
    ))
    
    skill_registry.register(Skill(
        name="toggle_voice",
        category=SkillCategory.SYSTEM,
        description="Toggle voice control on/off",
        input_schema={
            "user_id": {"type": "string", "required": True},
            "enable": {"type": "boolean", "required": True}
        },
        output_schema={
            "voice_enabled": {"type": "boolean"},
            "message": {"type": "string"}
        },
        handler=toggle_voice_handler,
        governance_action_type="multimodal_operation",
        capability_tags=["orb", "multimodal", "voice"]
    ))
    
    skill_registry.register(Skill(
        name="create_background_task",
        category=SkillCategory.SYSTEM,
        description="Create a background task",
        input_schema={
            "task_type": {"type": "string", "required": True},
            "metadata": {"type": "object", "default": {}}
        },
        output_schema={
            "task_id": {"type": "string"},
            "status": {"type": "string"}
        },
        handler=create_background_task_handler,
        governance_action_type="system_operation",
        capability_tags=["orb", "tasks", "background"]
    ))
    
    print("[CoreSkills] Registered 11 core skills (5 base + 6 Orb)")
