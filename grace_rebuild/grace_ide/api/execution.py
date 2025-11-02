"""Multi-language execution engine"""

import asyncio
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ExecutionConfig:
    language: str
    file_path: str
    command: Optional[str] = None
    timeout: int = 10
    memory_limit_mb: int = 512
    env_vars: Dict[str, str] = None

class ExecutorEngine:
    """Execute code in multiple languages safely"""
    
    LANGUAGE_RUNNERS = {
        "python": "python",
        "python3": "python3",
        "javascript": "node",
        "typescript": "ts-node",
        "bash": "bash",
        "sh": "sh",
    }
    
    async def execute(self, config: ExecutionConfig, sandbox_dir: Path) -> Tuple[str, str, int, float]:
        """Execute code with language-specific runner"""
        
        runner = self.LANGUAGE_RUNNERS.get(config.language)
        if not runner:
            return "", f"Unsupported language: {config.language}", -1, 0.0
        
        if config.command:
            command = config.command
        else:
            command = f"{runner} {config.file_path}"
        
        start_time = time.time()
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(sandbox_dir),
                env=config.env_vars
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout
                )
                exit_code = process.returncode or 0
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                stdout = b''
                stderr = f'Execution timeout ({config.timeout}s limit)'.encode()
                exit_code = -1
            
            duration = time.time() - start_time
            
            return (
                stdout.decode('utf-8', errors='replace')[:50000],
                stderr.decode('utf-8', errors='replace')[:50000],
                exit_code,
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return '', str(e), -1, duration
    
    def detect_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.sh': 'bash',
            '.bash': 'bash',
        }
        
        return ext_map.get(ext, 'unknown')

executor_engine = ExecutorEngine()
