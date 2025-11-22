# tests/test_tool_registry.py
import pytest
import asyncio
from tool_registry import TOOL_REGISTRY, ToolRegistry

@pytest.mark.asyncio
async def test_register_and_dispatch():
    registry = ToolRegistry()
    
    async def dummy_tool(arg1: str) -> dict:
        return {"result": f"echo {arg1}"}
    
    registry.register("dummy", dummy_tool)
    
    result = await registry.dispatch("dummy", arg1="hello")
    assert result == {"result": "echo hello"}

@pytest.mark.asyncio
async def test_dispatch_unknown_tool():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Tool 'unknown' is not registered"):
        await registry.dispatch("unknown")

@pytest.mark.asyncio
async def test_builtin_tools():
    # Test search_web placeholder
    result = await TOOL_REGISTRY.dispatch("search_web", query="test")
    assert result["status"] == "ok"
    assert "Results for 'test'" in result["data"]

    # Test run_command placeholder
    # Note: This runs a real command, so keep it simple
    result = await TOOL_REGISTRY.dispatch("run_command", command="echo test")
    assert result["status"] == "ok"
    assert "test" in result["stdout"]
