"""
Terminal over WebSocket - Natural Language Controlled
User speaks naturally, Grace translates to commands
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
import subprocess
import logging

from ..grace_llm import get_grace_llm
from ..settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class NLPTerminal:
    """Natural language controlled terminal"""
    
    def __init__(self):
        self.llm = None
        self.allowed_commands = settings.TERMINAL_ALLOWED_COMMANDS
        self.blocked_commands = settings.TERMINAL_BLOCKED_COMMANDS
    
    async def initialize(self):
        """Initialize LLM for command translation"""
        self.llm = await get_grace_llm()
    
    async def translate_to_command(self, user_input: str) -> dict:
        """
        Translate natural language to terminal command
        
        User: "Show me the git status"
        → Command: "git status"
        
        User: "List files in the backend directory"
        → Command: "dir backend" (Windows) or "ls backend" (Unix)
        """
        
        # Simple pattern matching (would use LLM in production)
        user_lower = user_input.lower()
        
        # Git operations
        if "git status" in user_lower or "show git status" in user_lower:
            return {"command": "git status", "safe": True}
        
        if "git log" in user_lower:
            return {"command": "git log --oneline -10", "safe": True}
        
        # File operations
        if "list files" in user_lower or "show files" in user_lower:
            path = "." 
            if "backend" in user_lower:
                path = "backend"
            elif "frontend" in user_lower:
                path = "frontend"
            return {"command": f"dir {path}" if settings else "ls -la {path}", "safe": True}
        
        # Python operations
        if "run python" in user_lower or "execute python" in user_lower:
            return {"command": "python --version", "safe": True, "info": "Specify full command"}
        
        # System info
        if "system info" in user_lower or "hardware info" in user_lower:
            return {"command": "systeminfo", "safe": True}
        
        # Default: ask for clarification
        return {
            "command": None,
            "safe": False,
            "message": "I'm not sure what command to run. Can you be more specific?"
        }
    
    def is_command_safe(self, command: str) -> tuple[bool, Optional[str]]:
        """Check if command is safe to execute"""
        
        # Check blocked commands
        for blocked in self.blocked_commands:
            if blocked.lower() in command.lower():
                return False, f"Blocked: '{blocked}' is not allowed for safety"
        
        # Check if starts with allowed command
        cmd_start = command.split()[0].lower() if command.split() else ""
        if cmd_start not in [c.lower() for c in self.allowed_commands]:
            return False, f"Command '{cmd_start}' not in allowed list"
        
        return True, None
    
    async def execute_command(self, command: str) -> dict:
        """Execute command and return output"""
        
        safe, reason = self.is_command_safe(command)
        if not safe:
            return {
                "success": False,
                "error": reason,
                "output": ""
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd="c:/Users/aaron/grace_2"
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "exit_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 30 seconds",
                "output": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }


nlp_terminal = NLPTerminal()


@router.websocket("/ws/terminal")
async def terminal_websocket(websocket: WebSocket):
    """
    WebSocket terminal with natural language control
    
    User types naturally:
    - "Show me git status"
    - "List Python files in backend"
    - "Check system health"
    
    Grace translates to commands and executes safely.
    """
    await websocket.accept()
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "message": "Grace Terminal ready. Speak naturally - I'll translate to commands.",
            "examples": [
                "Show me git status",
                "List files in backend",
                "Check Python version"
            ]
        })
        
        while True:
            # Receive natural language input
            data = await websocket.receive_text()
            user_input = data
            
            # Translate to command
            translation = await nlp_terminal.translate_to_command(user_input)
            
            if not translation.get("command"):
                await websocket.send_json({
                    "type": "clarification",
                    "message": translation.get("message", "Could not understand request")
                })
                continue
            
            command = translation["command"]
            
            # Show what Grace understood
            await websocket.send_json({
                "type": "translation",
                "user_input": user_input,
                "command": command,
                "message": f"Executing: {command}"
            })
            
            # Execute command
            result = await nlp_terminal.execute_command(command)
            
            # Send result
            await websocket.send_json({
                "type": "result",
                "command": command,
                "success": result["success"],
                "output": result["output"],
                "error": result.get("error")
            })
    
    except WebSocketDisconnect:
        logger.info("[TERMINAL] WebSocket disconnected")
    except Exception as e:
        logger.error(f"[TERMINAL] Error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
