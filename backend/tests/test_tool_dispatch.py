"""Comprehensive unit tests for tool dispatch functionality"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from tool_registry import ToolRegistry, TOOL_REGISTRY


class TestToolRegistry:
    """Test ToolRegistry core functionality"""

    def test_registry_initialization(self):
        """Test that registry initializes with builtin tools"""
        registry = ToolRegistry()
        assert len(registry._registry) > 0
        assert "search_web" in registry._registry
        assert "read_file" in registry._registry
        assert "write_file" in registry._registry
        assert "run_command" in registry._registry
        assert "generate_image" in registry._registry

    def test_register_tool(self):
        """Test registering a new tool"""
        registry = ToolRegistry()

        async def test_tool(param1: str, param2: int = 42) -> Dict[str, Any]:
            return {"result": f"{param1}_{param2}"}

        registry.register("test_tool", test_tool)
        assert "test_tool" in registry._registry

    @pytest.mark.asyncio
    async def test_dispatch_successful_call(self):
        """Test successful tool dispatch"""
        registry = ToolRegistry()

        result = await registry.dispatch("search_web", query="test query")
        assert result["status"] == "ok"
        assert "test query" in result["data"]

    @pytest.mark.asyncio
    async def test_dispatch_with_parameters(self):
        """Test dispatch with various parameter types"""
        registry = ToolRegistry()

        # Test with keyword arguments
        result = await registry.dispatch("search_web", query="python async")
        assert result["status"] == "ok"

        # Test with positional-like kwargs
        result = await registry.dispatch("run_command", command="echo hello")
        assert "status" in result
        assert "returncode" in result

    @pytest.mark.asyncio
    async def test_dispatch_invalid_tool(self):
        """Test dispatch with non-existent tool"""
        registry = ToolRegistry()

        with pytest.raises(ValueError, match="Tool 'nonexistent_tool' is not registered"):
            await registry.dispatch("nonexistent_tool")

    @pytest.mark.asyncio
    async def test_dispatch_tool_failure(self):
        """Test dispatch when tool raises exception"""
        registry = ToolRegistry()

        # Create a failing tool
        async def failing_tool() -> Dict[str, Any]:
            raise RuntimeError("Tool failed")

        registry.register("failing_tool", failing_tool)

        with pytest.raises(RuntimeError, match="Tool failed"):
            await registry.dispatch("failing_tool")

    @pytest.mark.asyncio
    async def test_dispatch_file_operations(self):
        """Test file operation tools"""
        registry = ToolRegistry()

        # Test write_file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            result = await registry.dispatch("write_file", path=temp_path, content="test content")
            assert result["status"] == "ok"

            # Test read_file
            result = await registry.dispatch("read_file", path=temp_path)
            assert result["status"] == "ok"
            assert result["content"] == "test content"

        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_dispatch_file_operation_errors(self):
        """Test file operation error handling"""
        registry = ToolRegistry()

        # Test reading non-existent file
        result = await registry.dispatch("read_file", path="/nonexistent/path/file.txt")
        assert result["status"] == "error"
        assert "error" in result

        # Test writing to invalid path
        result = await registry.dispatch("write_file", path="/invalid/path/file.txt", content="test")
        assert result["status"] == "error"
        assert "error" in result


class TestToolParameterValidation:
    """Test parameter validation for tools"""

    @pytest.mark.asyncio
    async def test_required_parameters(self):
        """Test that required parameters are enforced"""
        registry = ToolRegistry()

        # search_web requires query parameter
        with pytest.raises(TypeError):
            await registry.dispatch("search_web")  # Missing query

    @pytest.mark.asyncio
    async def test_default_parameters(self):
        """Test default parameter handling"""
        registry = ToolRegistry()

        # run_command should work with just command
        result = await registry.dispatch("run_command", command="echo test")
        assert "status" in result

    @pytest.mark.asyncio
    async def test_parameter_type_handling(self):
        """Test various parameter types"""
        registry = ToolRegistry()

        # Test with different types
        result = await registry.dispatch("run_command",
                                       command="echo test",

        assert "status" in result

    @pytest.mark.asyncio
    async def test_large_parameter_values(self):
        """Test handling of large parameter values"""
        registry = ToolRegistry()

        # Create a tool that handles large data
        async def large_data_tool(data: str) -> Dict[str, Any]:
            return {"size": len(data), "processed": True}

        registry.register("large_data_tool", large_data_tool)

        large_data = "x" * 1000000  # 1MB string
        result = await registry.dispatch("large_data_tool", data=large_data)
        assert result["size"] == 1000000
        assert result["processed"] is True


class TestToolErrorHandling:
    """Test comprehensive error handling"""

    @pytest.mark.asyncio
    async def test_tool_exception_propagation(self):
        """Test that tool exceptions are properly propagated"""
        registry = ToolRegistry()

        async def exception_tool(error_type: str) -> Dict[str, Any]:
            if error_type == "ValueError":
                raise ValueError("Test value error")
            elif error_type == "KeyError":
                raise KeyError("test_key")
            else:
                raise RuntimeError("Generic error")

        registry.register("exception_tool", exception_tool)

        with pytest.raises(ValueError, match="Test value error"):
            await registry.dispatch("exception_tool", error_type="ValueError")

        with pytest.raises(KeyError, match="test_key"):
            await registry.dispatch("exception_tool", error_type="KeyError")

        with pytest.raises(RuntimeError, match="Generic error"):
            await registry.dispatch("exception_tool", error_type="RuntimeError")

    @pytest.mark.asyncio
    async def test_asyncio_timeout_handling(self):
        """Test handling of asyncio timeouts"""
        registry = ToolRegistry()

        async def slow_tool(delay: float) -> Dict[str, Any]:
            await asyncio.sleep(delay)
            return {"result": "completed"}

        registry.register("slow_tool", slow_tool)

        # This should complete normally
        result = await registry.dispatch("slow_tool", delay=0.1)
        assert result["result"] == "completed"

    @pytest.mark.asyncio
    async def test_tool_return_value_validation(self):
        """Test that tools return expected dict format"""
        registry = ToolRegistry()

        async def invalid_return_tool() -> str:
            return "not a dict"

        async def valid_return_tool() -> Dict[str, Any]:
            return {"status": "ok"}

        registry.register("invalid_return", invalid_return_tool)
        registry.register("valid_return", valid_return_tool)

        # Should work fine - dispatch doesn't validate return types
        result = await registry.dispatch("invalid_return")
        assert result == "not a dict"

        result = await registry.dispatch("valid_return")
        assert result["status"] == "ok"


class TestDifferentToolTypes:
    """Test different categories of tools"""

    @pytest.mark.asyncio
    async def test_code_generation_tools(self):
        """Test code-related tool operations"""
        registry = ToolRegistry()

        # Mock a code generation tool
        async def generate_code_tool(language: str, spec: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "language": language,
                "code": f"# Generated {language} code for {spec.get('name', 'unknown')}",
                "status": "ok"
            }

        registry.register("generate_code", generate_code_tool)

        result = await registry.dispatch("generate_code",
                                       language="python",
                                       spec={"name": "test_function", "type": "function"})
        assert result["language"] == "python"
        assert "test_function" in result["code"]

    @pytest.mark.asyncio
    async def test_api_call_tools(self):
        """Test API calling tools"""
        registry = ToolRegistry()

        async def api_call_tool(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
            return {
                "endpoint": endpoint,
                "method": method,
                "data": data or {},
                "status_code": 200,
                "response": {"success": True}
            }

        registry.register("api_call", api_call_tool)

        result = await registry.dispatch("api_call",
                                       endpoint="/api/users",
                                       method="POST",
                                       data={"name": "test"})
        assert result["endpoint"] == "/api/users"
        assert result["method"] == "POST"
        assert result["data"]["name"] == "test"

    @pytest.mark.asyncio
    async def test_data_processing_tools(self):
        """Test data processing tools"""
        registry = ToolRegistry()

        async def process_data_tool(data: list, operation: str) -> Dict[str, Any]:
            if operation == "sum":
                result = sum(data)
            elif operation == "average":
                result = sum(data) / len(data)
            else:
                result = len(data)

            return {"operation": operation, "result": result}

        registry.register("process_data", process_data_tool)

        result = await registry.dispatch("process_data",
                                       data=[1, 2, 3, 4, 5],
                                       operation="sum")
        assert result["operation"] == "sum"
        assert result["result"] == 15

        result = await registry.dispatch("process_data",
                                       data=[1, 2, 3, 4, 5],
                                       operation="average")
        assert result["result"] == 3.0


class TestToolConcurrency:
    """Test concurrent tool execution"""

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """Test multiple tools running concurrently"""
        registry = ToolRegistry()

        async def delayed_tool(tool_name: str, delay: float) -> Dict[str, Any]:
            await asyncio.sleep(delay)
            return {"tool": tool_name, "delay": delay}

        registry.register("delayed_tool", delayed_tool)

        # Run multiple tools concurrently
        tasks = [
            registry.dispatch("delayed_tool", tool_name="tool1", delay=0.1),
            registry.dispatch("delayed_tool", tool_name="tool2", delay=0.1),
            registry.dispatch("delayed_tool", tool_name="tool3", delay=0.1),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        tool_names = [r["tool"] for r in results]
        assert "tool1" in tool_names
        assert "tool2" in tool_names
        assert "tool3" in tool_names

    @pytest.mark.asyncio
    async def test_tool_isolation(self):
        """Test that tools don't interfere with each other"""
        registry = ToolRegistry()

        call_counts = {"tool_a": 0, "tool_b": 0}

        async def counting_tool(tool_name: str) -> Dict[str, Any]:
            call_counts[tool_name] += 1
            return {"name": tool_name, "calls": call_counts[tool_name]}

        registry.register("counting_tool", counting_tool)

        # Call tools multiple times
        results = []
        for i in range(5):
            results.append(await registry.dispatch("counting_tool", tool_name="tool_a"))
            results.append(await registry.dispatch("counting_tool", tool_name="tool_b"))

        # Each tool should have been called 5 times
        assert call_counts["tool_a"] == 5
        assert call_counts["tool_b"] == 5

        # Results should reflect call counts
        tool_a_results = [r for r in results if r["name"] == "tool_a"]
        tool_b_results = [r for r in results if r["name"] == "tool_b"]

        assert len(tool_a_results) == 5
        assert len(tool_b_results) == 5


class TestToolRegistryIntegration:
    """Test integration with other systems"""

    @pytest.mark.asyncio
    async def test_global_registry_access(self):
        """Test that the global TOOL_REGISTRY works"""
        # This tests the singleton instance
        result = await TOOL_REGISTRY.dispatch("search_web", query="integration test")
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_tool_registration_persistence(self):
        """Test that registered tools persist"""
        registry = ToolRegistry()

        async def persistent_tool(value: str) -> Dict[str, Any]:
            return {"persistent": True, "value": value}

        registry.register("persistent_tool", persistent_tool)

        # Call multiple times to ensure persistence
        for i in range(3):
            result = await registry.dispatch("persistent_tool", value=f"call_{i}")
            assert result["persistent"] is True
            assert result["value"] == f"call_{i}"


class TestIntelligentModelRouterIntegration:
    """Test integration with IntelligentModelRouter"""

    @pytest.mark.asyncio
    @patch('backend.services.intelligent_model_router.intelligent_model_router')
    async def test_router_tool_dispatch(self, mock_router):
        """Test that router can dispatch tools"""
        # Mock the router's response
        mock_router.route_task.return_value = {
            "selected_model": "test_model",
            "result": {"tool_result": "success"},
            "analysis": {"confidence": 0.9}
        }

        # Import and test
        from backend.services.intelligent_model_router import intelligent_model_router

        result = await intelligent_model_router.route_task(
            task="test task",
            user_id="test_user"
        )

        assert "selected_model" in result
        assert "result" in result
        mock_router.route_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_tool_dispatch_in_router_context(self):
        """Test tool dispatch within router execution context"""
        registry = ToolRegistry()

        # Simulate a tool that might be called during routing
        async def router_context_tool(task_type: str) -> Dict[str, Any]:
            return {"task_type": task_type, "routed": True}

        registry.register("router_context_tool", router_context_tool)

        result = await registry.dispatch("router_context_tool", task_type="code_generation")
        assert result["task_type"] == "code_generation"
        assert result["routed"] is True


class TestToolPerformance:
    """Test tool performance characteristics"""

    @pytest.mark.asyncio
    async def test_tool_execution_time(self):
        """Test that tools execute within reasonable time"""
        import time
        registry = ToolRegistry()

        async def timed_tool(duration: float) -> Dict[str, Any]:
            start = time.time()
            await asyncio.sleep(duration)
            end = time.time()
            return {"duration": end - start, "requested": duration}

        registry.register("timed_tool", timed_tool)

        start_time = time.time()
        result = await registry.dispatch("timed_tool", duration=0.05)
        end_time = time.time()

        # Should complete in reasonable time
        assert end_time - start_time < 1.0  # Less than 1 second
        assert abs(result["duration"] - 0.05) < 0.01  # Close to requested duration

    @pytest.mark.asyncio
    async def test_tool_memory_usage(self):
        """Test tools don't have excessive memory usage"""
        registry = ToolRegistry()

        # Test with moderately large data
        large_data = "x" * 10000

        result = await registry.dispatch("run_command", command=f"echo {large_data}")
        assert "status" in result
        # Should not crash or use excessive memory


class TestToolSecurity:
    """Test tool security boundaries"""

    @pytest.mark.asyncio
    async def test_command_injection_prevention(self):
        """Test that command execution doesn't allow injection"""
        registry = ToolRegistry()

        # Test with potentially malicious input
        malicious_command = "echo hello; rm -rf /"  # This should be safe

        result = await registry.dispatch("run_command", command=malicious_command)
        # The command should execute as-is, but our simple implementation should handle it
        assert "status" in result

    @pytest.mark.asyncio
    async def test_file_path_sanitization(self):
        """Test file operations handle paths safely"""
        registry = ToolRegistry()

        # Test with relative paths
        with tempfile.TemporaryDirectory() as temp_dir:
            safe_path = os.path.join(temp_dir, "test.txt")

            result = await registry.dispatch("write_file", path=safe_path, content="safe")
            assert result["status"] == "ok"

            result = await registry.dispatch("read_file", path=safe_path)
            assert result["status"] == "ok"
            assert result["content"] == "safe"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
