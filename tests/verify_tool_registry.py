# tests/verify_tool_registry.py
import asyncio
import sys
import os

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tool_registry import TOOL_REGISTRY, ToolRegistry

async def test_register_and_dispatch():
    print("Testing register and dispatch...")
    registry = ToolRegistry()
    
    async def dummy_tool(arg1: str) -> dict:
        return {"result": f"echo {arg1}"}
    
    registry.register("dummy", dummy_tool)
    
    result = await registry.dispatch("dummy", arg1="hello")
    assert result == {"result": "echo hello"}
    print("  [OK] Register and dispatch")

async def test_dispatch_unknown_tool():
    print("Testing unknown tool dispatch...")
    registry = ToolRegistry()
    try:
        await registry.dispatch("unknown")
        print("  [FAIL] Should have raised ValueError")
    except ValueError as e:
        print(f"  [OK] Caught expected error: {e}")

async def test_builtin_tools():
    print("Testing built-in tools...")
    # Test search_web placeholder
    result = await TOOL_REGISTRY.dispatch("search_web", query="test")
    assert result["status"] == "ok"
    assert "Results for 'test'" in result["data"]
    print("  [OK] search_web")

    # Test run_command placeholder
    # Note: This runs a real command, so keep it simple
    result = await TOOL_REGISTRY.dispatch("run_command", command="echo test")
    assert result["status"] == "ok"
    assert "test" in result["stdout"]
    print("  [OK] run_command")

async def main():
    print("=== Verifying Tool Registry ===")
    await test_register_and_dispatch()
    await test_dispatch_unknown_tool()
    await test_builtin_tools()
    print("\nAll tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
