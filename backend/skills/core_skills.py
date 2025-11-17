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
    
    print("[CoreSkills] Registered 5 core skills")
