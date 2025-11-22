# tool_registry.py
"""Registry mapping tool names to async callables.
Each tool should be an async function that accepts **kwargs and returns a result dict.
"""
import asyncio
from typing import Callable, Dict, Any

# Example placeholder tool implementations – replace with real logic later
async def search_web(query: str) -> Dict[str, Any]:
    # Placeholder: simulate a web search result
    await asyncio.sleep(0.1)
    return {"status": "ok", "data": f"Results for '{query}'"}

async def read_file(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "ok", "content": content}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def write_file(path: str, content: str) -> Dict[str, Any]:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def run_command(command: str) -> Dict[str, Any]:
    # Very simple wrapper – in production add safety checks!
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

async def generate_image(name: str, prompt: str) -> Dict[str, Any]:
    # Placeholder – actual implementation will call the generate_image tool via the agent.
    await asyncio.sleep(0.1)
    return {"status": "ok", "image_name": name}

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
