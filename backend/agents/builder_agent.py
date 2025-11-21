"""
Builder Agent - Full-Stack Software Engineer
The Architect and Constructor.

Capabilities:
- Build complete applications from natural language
- Support multiple languages (Python, JavaScript, TypeScript, HTML/CSS)
- Auto-scaffold projects using templates
- Install dependencies (pip, npm)
- Run tests and iterate on errors
- Start dev servers in sandbox
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from backend.core.message_bus import message_bus
from backend.core.agent_protocol import AgentProtocol, AgentRequest, AgentResponse
from backend.model_orchestrator import model_orchestrator
from backend.misc.sandbox_manager import sandbox_manager
from backend.agents.full_stack_templates import get_template, list_templates

logger = logging.getLogger(__name__)

class BuilderAgent:
    """
    Builder Agent - Autonomous Software Construction
    
    Capabilities:
    - Plan: Break down complex tasks.
    - Build: Generate code.
    - Test: Run code in sandbox.
    - Iterate: Fix errors based on stderr.
    """
    
    def __init__(self):
        self.running = False
        self.active_projects = {}
        
    async def start(self):
        """Start the builder agent"""
        self.running = True
        asyncio.create_task(self._listen_for_requests())
        logger.info("[BUILDER] Agent ready to build")
        
    async def stop(self):
        self.running = False
        
    async def _listen_for_requests(self):
        """Listen for build requests"""
        queue = await message_bus.subscribe("builder_agent", AgentProtocol.TOPIC_REQUEST)
        
        while self.running:
            try:
                message = await queue.get()
                payload = message.payload
                
                if payload.get('target_capability') == 'build':
                    request = AgentRequest(**payload)
                    logger.info(f"[BUILDER] Received build request: {request.query}")
                    asyncio.create_task(self._handle_build_request(request))
                    
            except Exception as e:
                logger.error(f"[BUILDER] Error in listener: {e}")
                await asyncio.sleep(1)
                
    async def _handle_build_request(self, request: AgentRequest):
        """Execute the build process with template scaffolding"""
        try:
            # 1. Detect project type and scaffold if applicable
            await self._send_update(request, "Analyzing request...")
            template_name = await self._detect_template(request.query)
            
            project_name = self._extract_project_name(request.query)
            project_path = f"{project_name}"
            
            if template_name:
                # Use template scaffolding
                await self._send_update(request, f"Scaffolding {template_name} project...")
                await self._scaffold_project(template_name, project_path)
                
                # Install dependencies
                await self._send_update(request, "Installing dependencies...")
                await self._install_dependencies(template_name, project_path)
                
                # Success response
                template = get_template(template_name)
                run_cmd = template.get_run_command()
                
                response = AgentProtocol.create_response(
                    request_id=request.request_id,
                    source="builder_agent",
                    content=f"""✅ **Build Complete!**

**Project**: `{project_name}`
**Type**: {template_name}
**Location**: `sandbox/{project_path}/`

**To run:**
```bash
cd sandbox/{project_path}
{run_cmd}
```

All files have been created and dependencies installed.""",
                    artifacts=[{"type": "project", "path": f"sandbox/{project_path}"}]
                )
                
                await message_bus.publish(
                    source="builder_agent",
                    topic=AgentProtocol.TOPIC_RESPONSE,
                    payload=response.to_dict(),
                    correlation_id=request.request_id
                )
                return
            
            # 2. Fallback: Custom build (original flow)
            await self._send_update(request, "Planning custom build...")
            plan = await self._create_plan(request.query)
            
            await self._send_update(request, f"Plan created: {len(plan['steps'])} steps. Starting build...")
            
            # Execute Steps
            results = []
            for i, step in enumerate(plan['steps']):
                step_num = i + 1
                await self._send_update(request, f"Step {step_num}/{len(plan['steps'])}: {step['description']}")
                
                # Generate Code
                code_files = await self._generate_code(step, request.query)
                
                # Write to Sandbox
                for file_path, content in code_files.items():
                    full_path = f"{project_path}/{file_path}"
                    await sandbox_manager.write_file("builder", full_path, content)
                
                # Run & Verify (if applicable)
                if step.get('test_command'):
                    await self._send_update(request, f"Testing step {step_num}...")
                    test_cmd = f"cd {project_path} && {step['test_command']}"
                    stdout, stderr, exit_code, _ = await sandbox_manager.run_command("builder", test_cmd)
                    
                    if exit_code != 0:
                        # Attempt self-correction
                        await self._send_update(request, f"Step {step_num} failed. Attempting fix...")
                        fixed_code = await self._fix_code(code_files, stderr, step)
                        
                        # Write fixed code
                        for file_path, content in fixed_code.items():
                            full_path = f"{project_path}/{file_path}"
                            await sandbox_manager.write_file("builder", full_path, content)
                            
                        # Retry test
                        stdout, stderr, exit_code, _ = await sandbox_manager.run_command("builder", test_cmd)
                        if exit_code != 0:
                            raise Exception(f"Build failed at step {step_num}: {stderr}")
                
                results.append(f"Completed: {step['description']}")
            
            # Finalize
            await self._send_update(request, "Build complete!")
            
            response = AgentProtocol.create_response(
                request_id=request.request_id,
                source="builder_agent",
                content=f"✅ **Build Successful!**\n\n" + "\n".join(results) + f"\n\n**Location**: `sandbox/{project_path}/`",
                artifacts=[{"type": "sandbox_files", "path": f"./sandbox/{project_path}"}]
            )
            
            await message_bus.publish(
                source="builder_agent",
                topic=AgentProtocol.TOPIC_RESPONSE,
                payload=response.to_dict(),
                correlation_id=request.request_id
            )
            
        except Exception as e:
            logger.error(f"[BUILDER] Build failed: {e}")
            error_response = AgentProtocol.create_response(
                request_id=request.request_id,
                source="builder_agent",
                content=f"❌ **Build Failed**\n\n{str(e)}",
                status="failure"
            )
            await message_bus.publish(
                source="builder_agent",
                topic=AgentProtocol.TOPIC_RESPONSE,
                payload=error_response.to_dict(),
                correlation_id=request.request_id
            )

    async def _detect_template(self, query: str) -> Optional[str]:
        """Detect if query matches a known template"""
        query_lower = query.lower()
        
        # Keyword matching for templates
        if "blockchain" in query_lower:
            return "blockchain"
        elif ("react" in query_lower and "fastapi" in query_lower) or \
             ("frontend" in query_lower and "backend" in query_lower) or \
             ("full stack" in query_lower or "fullstack" in query_lower):
            return "react-fastapi"
        elif "flask" in query_lower and ("api" in query_lower or "rest" in query_lower):
            return "flask-api"
        elif "python" in query_lower and ("cli" in query_lower or "script" in query_lower or "command" in query_lower):
            return "python-cli"
        
        return None
    
    def _extract_project_name(self, query: str) -> str:
        """Extract project name from query"""
        # Try to find "build a <name>" pattern
        match = re.search(r'build (?:a |an )?([a-zA-Z0-9_-]+)', query.lower())
        if match:
            name = match.group(1).replace(' ', '_')
            return name
        
        # Fallback: generate name from timestamp
        return f"project_{int(datetime.now().timestamp())}"
    
    async def _scaffold_project(self, template_name: str, project_path: str):
        """Scaffold a project from a template"""
        template = get_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        structure = template.get_structure()
        
        # Write all files
        for file_path, content in structure.items():
            full_path = f"{project_path}/{file_path}"
            await sandbox_manager.write_file("builder", full_path, content)
            logger.info(f"[BUILDER] Created {full_path}")
    
    async def _install_dependencies(self, template_name: str, project_path: str):
        """Install project dependencies"""
        template = get_template(template_name)
        if not template:
            return
        
        deps = template.get_dependencies()
        
        # Install pip dependencies
        if "pip" in deps and deps["pip"]:
            pip_cmd = f"cd {project_path} && pip install " + " ".join(deps["pip"])
            logger.info(f"[BUILDER] Running: {pip_cmd}")
            await sandbox_manager.run_command("builder", pip_cmd)
        
        # Install npm dependencies
        if "npm" in deps and deps["npm"]:
            # Check if package.json exists (it should from template)
            npm_cmd = f"cd {project_path}/frontend && npm install"
            logger.info(f"[BUILDER] Running: {npm_cmd}")
            await sandbox_manager.run_command("builder", npm_cmd)

    async def _create_plan(self, query: str) -> Dict[str, Any]:
        """Use LLM to create a build plan"""
        prompt = f"""
        You are an expert software architect.
        User Request: "{query}"
        
        Create a step-by-step implementation plan to build this in a sandbox environment.
        Output JSON format:
        {{
            "steps": [
                {{
                    "description": "Create main.py with basic logic",
                    "files_needed": ["main.py"],
                    "test_command": "python main.py --test"
                }}
            ]
        }}
        """
        # Use MoE reasoning model for faster planning
        response = await model_orchestrator.chat_with_learning(prompt, user_preference="mixtral:8x22b")
        # Extract JSON from response (naive implementation)
        try:
            text = response['text']
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except:
            # Fallback plan
            return {"steps": [{"description": "Implement logic", "files_needed": ["main.py"], "test_command": "python main.py"}]}

    async def _generate_code(self, step: Dict, context: str) -> Dict[str, str]:
        """Generate code for a step"""
        prompt = f"""
        Write the code for: {step['description']}
        Context: {context}
        Files: {step['files_needed']}
        
        Output JSON: {{ "filename": "code_content" }}
        """
        # Use coding specialist with better function calling
        response = await model_orchestrator.chat_with_learning(prompt, user_preference="qwen2.5-coder:32b")
        try:
            text = response['text']
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except:
            return {}

    async def _fix_code(self, files: Dict[str, str], error: str, step: Dict) -> Dict[str, str]:
        """Fix broken code"""
        prompt = f"""
        The code failed with error: {error}
        
        Files:
        {json.dumps(files, indent=2)}
        
        Fix the code. Output JSON: {{ "filename": "fixed_content" }}
        """
        # Use ultra-fast model for quick fixes
        response = await model_orchestrator.chat_with_learning(prompt, user_preference="codegemma:7b")
        try:
            text = response['text']
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except:
            return files

    async def _send_update(self, request: AgentRequest, status: str):
        """Send progress update"""
        await message_bus.publish(
            source="builder_agent",
            topic="agent.progress", # New topic for UI updates
            payload={
                "request_id": request.request_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Global instance
builder_agent = BuilderAgent()
