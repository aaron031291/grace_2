# tool_registry.py
"""Registry mapping tool names to async callables.
Each tool should be an async function that accepts **kwargs and returns a result dict.
"""
import asyncio
from typing import Callable, Dict, Any

# Real implementations
async def search_web(query: str) -> Dict[str, Any]:
    """
    Search for information. 
    Currently redirects to internal Knowledge Base (Vector Store) 
    as external search requires API keys not yet configured.
    """
    try:
        # 1. Embed query
        from backend.services.embedding_service import embedding_service
        embedding_result = await embedding_service.embed_text(query)
        query_vector = embedding_result["embedding_vector"]
        
        # 2. Search Vector Store
        from backend.services.vector_store import vector_store
        results = await vector_store.search(
            query_vector=query_vector,
            top_k=3,
            requested_by="grace_agent"
        )
        
        # 3. Format results
        formatted_results = []
        for r in results.get("results", []):
            formatted_results.append(f"- {r.get('text_content', 'No content')} (Score: {r.get('score', 0):.2f})")
            
        return {
            "status": "ok", 
            "data": "\n".join(formatted_results) if formatted_results else "No relevant information found in knowledge base."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def read_file(path: str) -> Dict[str, Any]:
    try:
        # Governance check could be added here
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "ok", "content": content}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def write_file(path: str, content: str) -> Dict[str, Any]:
    try:
        # Governance check
        from backend.governance_system.inline_approval_engine import inline_approval_engine, ResourceAccess
        
        access = ResourceAccess(
            resource_type="file_system",
            resource_id=path,
            action="write",
            requester="grace_agent",
            context={"content_length": len(content)}
        )
        
        approval = await inline_approval_engine.request_approval(access)
        
        if approval.decision != "auto_approved" and approval.decision != "approved":
            return {"status": "denied", "reason": approval.reason}

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def run_command(command: str) -> Dict[str, Any]:
    try:
        # Governance check
        from backend.governance_system.inline_approval_engine import inline_approval_engine, ResourceAccess
        
        access = ResourceAccess(
            resource_type="system",
            resource_id="shell",
            action="execute",
            requester="grace_agent",
            context={"command": command}
        )
        
        approval = await inline_approval_engine.request_approval(access)
        
        if approval.decision != "auto_approved" and approval.decision != "approved":
            return {"status": "denied", "reason": approval.reason}

        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return {
            "status": "ok" if proc.returncode == 0 else "error",
            "returncode": proc.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def generate_image(name: str, prompt: str) -> Dict[str, Any]:
    # Still a placeholder as image generation service is complex
    # But we can log it
    print(f"[Agent] Generating image '{name}': {prompt}")
    await asyncio.sleep(0.1)
    return {"status": "ok", "image_name": name, "note": "Image generation simulated"}

class ToolRegistry:
    def __init__(self):
        self._registry: Dict[str, Callable[..., Any]] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        self.register("search_web", search_web)
        self.register("read_file", read_file)
        self.register("write_file", write_file)
        self.register("run_command", run_command)
        self.register("generate_image", generate_image)

    def register(self, name: str, func: Callable[..., Any]):
        self._registry[name] = func

    async def dispatch(self, name: str, **kwargs) -> Any:
        if name not in self._registry:
            raise ValueError(f"Tool '{name}' is not registered.")
        return await self._registry[name](**kwargs)

# Export a singleton for easy import
TOOL_REGISTRY = ToolRegistry()
