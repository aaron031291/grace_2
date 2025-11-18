"""
Action Executor - Unified execution system for Grace's actions

Handles execution of approved actions with:
- Tool access (repos, CI, infrastructure)
- Self-healing on failures
- Audit logging
- Rollback capabilities
"""

import os
import asyncio
import subprocess
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

from backend.action_gateway import action_gateway
from backend.event_bus import event_bus, Event, EventType


class ExecutionStatus(Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ActionExecutor:
    """
    Unified action executor with tool access and self-healing
    
    Executes approved actions from the Action Gateway with:
    - Repository access (git operations)
    - CI/CD triggers
    - Infrastructure commands
    - Code deployment
    - Self-healing on failures
    """
    
    def __init__(self):
        self.execution_history: list[Dict[str, Any]] = []
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.tool_registry: Dict[str, Callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tool handlers"""
        self.tool_registry = {
            "execute_code": self.execute_code,
            "git_operation": self.git_operation,
            "deploy_service": self.deploy_service,
            "run_ci": self.run_ci,
            "modify_file": self.modify_file,
            "write_memory": self.write_memory,
            "external_api_call": self.external_api_call,
        }
    
    async def execute_action(
        self,
        trace_id: str,
        action_type: str,
        params: Dict[str, Any],
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """
        Execute an approved action
        
        Args:
            trace_id: Trace ID from Action Gateway
            action_type: Type of action to execute
            params: Action parameters
            user_id: User who approved the action
        
        Returns:
            Execution result
        """
        execution_id = f"exec_{trace_id}"
        
        # Create execution record
        execution = {
            "execution_id": execution_id,
            "trace_id": trace_id,
            "action_type": action_type,
            "params": params,
            "user_id": user_id,
            "status": ExecutionStatus.PENDING.value,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "result": None,
            "error": None,
            "rollback_data": None
        }
        
        self.active_executions[execution_id] = execution
        
        # Log execution start
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="action_executor",
            data={
                "action": "execution_started",
                "execution_id": execution_id,
                "action_type": action_type
            },
            trace_id=trace_id
        ))
        
        try:
            # Update status to running
            execution["status"] = ExecutionStatus.RUNNING.value
            
            # Get handler for action type
            handler = self.tool_registry.get(action_type)
            
            if not handler:
                raise ValueError(f"No handler registered for action type: {action_type}")
            
            # Execute action
            result = await handler(params, trace_id)
            
            # Update execution record
            execution["status"] = ExecutionStatus.SUCCESS.value
            execution["result"] = result
            execution["completed_at"] = datetime.now().isoformat()
            
            # Record success in Action Gateway
            await action_gateway.record_outcome(
                trace_id=trace_id,
                success=True,
                result=result
            )
            
            # Log success
            await event_bus.publish(Event(
                event_type=EventType.LEARNING_OUTCOME,
                source="action_executor",
                data={
                    "action": "execution_succeeded",
                    "execution_id": execution_id,
                    "action_type": action_type,
                    "result": result
                },
                trace_id=trace_id
            ))
            
            return {
                "success": True,
                "execution_id": execution_id,
                "result": result,
                "execution": execution
            }
        
        except Exception as e:
            # Execution failed
            execution["status"] = ExecutionStatus.FAILED.value
            execution["error"] = str(e)
            execution["completed_at"] = datetime.now().isoformat()
            
            # Record failure in Action Gateway
            await action_gateway.record_outcome(
                trace_id=trace_id,
                success=False,
                result=None,
                error=str(e)
            )
            
            # Log failure
            await event_bus.publish(Event(
                event_type=EventType.LEARNING_OUTCOME,
                source="action_executor",
                data={
                    "action": "execution_failed",
                    "execution_id": execution_id,
                    "action_type": action_type,
                    "error": str(e)
                },
                trace_id=trace_id
            ))
            
            # Attempt self-healing
            if os.getenv("ENABLE_SELF_HEALING") == "true":
                healing_result = await self.attempt_self_healing(execution, e)
                if healing_result["healed"]:
                    return healing_result
            
            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e),
                "execution": execution
            }
        
        finally:
            # Move to history
            self.execution_history.append(execution)
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def execute_code(self, params: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment
        
        Args:
            params: {code: str, language: str, timeout: int}
            trace_id: Trace ID
        
        Returns:
            Execution result
        """
        code = params.get("code")
        language = params.get("language", "python")
        timeout = params.get("timeout", 30)
        
        if not code:
            raise ValueError("Code parameter is required")
        
        # Sandbox execution (placeholder - use Docker/VM in production)
        if language == "python":
            # Run in subprocess with timeout
            process = await asyncio.create_subprocess_exec(
                "python", "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return {
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "returncode": process.returncode,
                    "success": process.returncode == 0
                }
            except asyncio.TimeoutError:
                process.kill()
                raise TimeoutError(f"Code execution timed out after {timeout}s")
        
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    async def git_operation(self, params: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """
        Perform git operation
        
        Args:
            params: {operation: str, repo_path: str, args: list}
            trace_id: Trace ID
        
        Returns:
            Git operation result
        """
        operation = params.get("operation")  # clone, pull, push, commit, etc.
        repo_path = params.get("repo_path", ".")
        args = params.get("args", [])
        
        # Build git command
        git_cmd = ["git", operation] + args
        
        # Execute git command
        process = await asyncio.create_subprocess_exec(
            *git_cmd,
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "operation": operation,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": process.returncode,
            "success": process.returncode == 0
        }
    
    async def deploy_service(self, params: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """
        Deploy a service
        
        Args:
            params: {service_name: str, environment: str, config: dict}
            trace_id: Trace ID
        
        Returns:
            Deployment result
        """
        service_name = params.get("service_name")
        environment = params.get("environment", "staging")
        
        # Placeholder - integrate with actual deployment system
        # (Kubernetes, Docker, Terraform, etc.)
        
        return {
            "service_name": service_name,
            "environment": environment,
            "status": "deployed",
            "message": f"Service {service_name} deployed to {environment} (mock)"
        }
    
    async def run_ci(self, params: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """
        Trigger CI/CD pipeline
        
        Args:
            params: {pipeline: str, branch: str, params: dict}
            trace_id: Trace ID
        
        Returns:
            CI run result
        """
        pipeline = params.get("pipeline")
        branch = params.get("branch", "main")
        
        # Placeholder - integrate with CI system (GitHub Actions, GitLab CI, etc.)
        
        return {
            "pipeline": pipeline,
            "branch": branch,
            "status": "triggered",
            "message": f"CI pipeline {pipeline} triggered for branch {branch} (mock)"
        }
    
    async def modify_file(self, params: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """
        Modify a file
        
        Args:
            params: {file_path: str, content: str, operation: str}
            trace_id: Trace ID
        
        Returns:
            File modification result
        """
        file_path = params.get("file_path")
        content = params.get("content")
        operation = params.get("operation", "write")  # write, append, patch
        
        if not file_path:
            raise ValueError("file_path is required")
        
        # Store rollback data
        rollback_data = None
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                rollback_data = f.read()
        
        # Perform operation
        if operation == "write":
            with open(file_path, 'w') as f:
                f.write(content)
        elif operation == "append":
            with open(file_path, 'a') as f:
                f.write(content)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        return {
            "file_path": file_path,
            "operation": operation,
            "success": True,
            "rollback_data": rollback_data
        }
    
    async def write_memory(self, params: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Write to world model memory"""
        from backend.world_model.grace_world_model import grace_world_model
        
        category = params.get("category", "general")
        content = params.get("content")
        source = params.get("source", "action_executor")
        
        if not content:
            raise ValueError("content is required")
        
        await grace_world_model.add_knowledge(
            category=category,
            content=content,
            source=source,
            confidence=params.get("confidence", 0.9),
            tags=params.get("tags", []),
            metadata={"trace_id": trace_id}
        )
        
        return {
            "category": category,
            "content": content,
            "success": True
        }
    
    async def external_api_call(self, params: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Make external API call"""
        import aiohttp
        
        url = params.get("url")
        method = params.get("method", "GET")
        headers = params.get("headers", {})
        data = params.get("data")
        
        if not url:
            raise ValueError("url is required")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                result = await response.json() if response.content_type == "application/json" else await response.text()
                
                return {
                    "url": url,
                    "method": method,
                    "status_code": response.status,
                    "result": result,
                    "success": response.status < 400
                }
    
    async def attempt_self_healing(
        self,
        execution: Dict[str, Any],
        error: Exception
    ) -> Dict[str, Any]:
        """
        Attempt to self-heal from execution failure
        
        Args:
            execution: Failed execution record
            error: Exception that caused failure
        
        Returns:
            Healing result
        """
        # Log healing attempt
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="action_executor",
            data={
                "action": "self_healing_attempt",
                "execution_id": execution["execution_id"],
                "error": str(error)
            },
            trace_id=execution["trace_id"]
        ))
        
        # Placeholder - implement actual healing strategies
        # - Retry with backoff
        # - Rollback changes
        # - Alternative approach
        
        return {
            "healed": False,
            "message": "Self-healing not yet implemented for this action type"
        }


# Singleton instance
action_executor = ActionExecutor()
