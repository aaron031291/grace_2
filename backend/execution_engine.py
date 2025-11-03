"""
Multi-language code execution engine with security controls
"""
import os
import re
import asyncio
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from .execution_config import (
    get_language_config,
    get_execution_preset,
    apply_preset_to_config,
    SHELL_WHITELIST,
    SHELL_BLACKLIST,
    LanguageConfig
)
from .governance import governance_engine
from .hunter import hunter
from .verification import verification_engine
from .immutable_log import immutable_log
import uuid


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: str
    error: str
    exit_code: int
    duration_ms: int
    language: str
    governance_decision: str = "allow"
    security_alerts: list = None
    verification_passed: bool = True
    
    def __post_init__(self):
        if self.security_alerts is None:
            self.security_alerts = []
    
    def to_dict(self) -> dict:
        return asdict(self)


class ExecutionEngine:
    """Multi-language code execution engine"""
    
    def __init__(self):
        self.temp_base = Path(tempfile.gettempdir()) / "grace_execution"
        self.temp_base.mkdir(exist_ok=True)
    
    async def execute(
        self,
        code: str,
        language: str,
        user: str,
        preset: str = "dev",
        filename: Optional[str] = None,
        additional_files: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute code in specified language with security checks
        
        Args:
            code: Source code to execute
            language: Programming language (python, javascript, etc.)
            user: Username executing the code
            preset: Execution preset (safe, dev, production)
            filename: Optional filename override
            additional_files: Optional dict of filename -> content for supporting files
        """
        start_time = time.time()
        
        try:
            config = get_language_config(language)
            preset_obj = get_execution_preset(preset)
            config = apply_preset_to_config(config, preset_obj)
            
            governance_result = await governance_engine.check(
                actor=user,
                action="code.execute",
                resource=f"{language}_code",
                payload={
                    "language": language,
                    "code_length": len(code),
                    "preset": preset
                }
            )
            
            if governance_result["decision"] == "deny":
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Execution denied by governance policy",
                    exit_code=-1,
                    duration_ms=0,
                    language=language,
                    governance_decision="deny"
                )
            
            security_alerts = await hunter.inspect(
                actor=user,
                action="code.execute",
                resource=f"{language}_code",
                payload={
                    "language": language,
                    "code_snippet": code[:500],
                    "preset": preset
                }
            )
            
            if language == "bash":
                validation_error = self._validate_shell_code(code)
                if validation_error:
                    return ExecutionResult(
                        success=False,
                        output="",
                        error=validation_error,
                        exit_code=-1,
                        duration_ms=0,
                        language=language,
                        security_alerts=[("shell_validation_failed", 0)]
                    )
            
            result = await self._execute_by_language(
                code, language, config, filename, additional_files
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            action_id = str(uuid.uuid4())
            await verification_engine.log_verified_action(
                action_id=action_id,
                actor=user,
                action_type="code_execution",
                resource=f"{language}_execution",
                input_data={
                    "language": language,
                    "code_length": len(code),
                    "preset": preset
                },
                output_data={
                    "success": result["success"],
                    "exit_code": result["exit_code"],
                    "duration_ms": duration_ms
                },
                criteria_met=result["success"]
            )
            
            immutable_record_id = await immutable_log.append(
                actor=user,
                action="code_execution",
                resource=f"{language}_code",
                subsystem="execution_engine",
                payload={
                    "language": language,
                    "preset": preset,
                    "code_length": len(code)
                },
                result="success" if result["success"] else "failed"
            )
            
            return ExecutionResult(
                success=result["success"],
                output=result["output"],
                error=result["error"],
                exit_code=result["exit_code"],
                duration_ms=duration_ms,
                language=language,
                governance_decision=governance_result["decision"],
                security_alerts=security_alerts,
                verification_passed=immutable_record_id is not None
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution engine error: {str(e)}",
                exit_code=-1,
                duration_ms=duration_ms,
                language=language
            )
    
    async def _execute_by_language(
        self,
        code: str,
        language: str,
        config: LanguageConfig,
        filename: Optional[str],
        additional_files: Optional[Dict[str, str]]
    ) -> dict:
        """Route execution to appropriate language handler"""
        if language == "python":
            return await self._execute_python(code, config, filename)
        elif language == "javascript":
            return await self._execute_javascript(code, config, filename)
        elif language == "typescript":
            return await self._execute_typescript(code, config, filename)
        elif language == "bash":
            return await self._execute_bash(code, config, filename)
        elif language == "sql":
            return await self._execute_sql(code, config)
        elif language == "go":
            return await self._execute_go(code, config, additional_files)
        elif language == "rust":
            return await self._execute_rust(code, config)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    async def _execute_python(self, code: str, config: LanguageConfig, filename: Optional[str]) -> dict:
        """Execute Python code"""
        with tempfile.TemporaryDirectory(prefix="grace_py_") as temp_dir:
            script_path = Path(temp_dir) / (filename or "script.py")
            script_path.write_text(code, encoding='utf-8')
            
            env = os.environ.copy()
            env.update(config.env_vars)
            env["PYTHONPATH"] = temp_dir
            
            return await self._run_process(
                [config.command.split()[0], str(script_path)],
                config.timeout,
                env,
                cwd=temp_dir
            )
    
    async def _execute_javascript(self, code: str, config: LanguageConfig, filename: Optional[str]) -> dict:
        """Execute JavaScript with Node.js"""
        with tempfile.TemporaryDirectory(prefix="grace_js_") as temp_dir:
            script_path = Path(temp_dir) / (filename or "script.js")
            script_path.write_text(code, encoding='utf-8')
            
            env = os.environ.copy()
            env.update(config.env_vars)
            
            cmd_parts = config.command.split()
            cmd_parts.append(str(script_path))
            
            return await self._run_process(
                cmd_parts,
                config.timeout,
                env,
                cwd=temp_dir
            )
    
    async def _execute_typescript(self, code: str, config: LanguageConfig, filename: Optional[str]) -> dict:
        """Execute TypeScript (compile then run)"""
        with tempfile.TemporaryDirectory(prefix="grace_ts_") as temp_dir:
            src_path = Path(temp_dir) / "src"
            out_path = Path(temp_dir) / "dist"
            src_path.mkdir()
            out_path.mkdir()
            
            script_path = src_path / (filename or "script.ts")
            script_path.write_text(code, encoding='utf-8')
            
            env = os.environ.copy()
            env.update({k: v.replace("{output_dir}", str(out_path)) for k, v in config.env_vars.items()})
            
            compile_cmd = config.compile_command.replace("{output_dir}", str(out_path))
            compile_result = await self._run_process(
                compile_cmd.split() + [str(script_path)],
                config.timeout // 2,
                env,
                cwd=temp_dir
            )
            
            if compile_result["exit_code"] != 0:
                return {
                    "success": False,
                    "output": compile_result["output"],
                    "error": f"TypeScript compilation failed: {compile_result['error']}",
                    "exit_code": compile_result["exit_code"]
                }
            
            compiled_js = out_path / "script.js"
            if not compiled_js.exists():
                return {
                    "success": False,
                    "output": "",
                    "error": "Compilation succeeded but output file not found",
                    "exit_code": -1
                }
            
            return await self._run_process(
                [config.command, str(compiled_js)],
                config.timeout // 2,
                env,
                cwd=temp_dir
            )
    
    async def _execute_bash(self, code: str, config: LanguageConfig, filename: Optional[str]) -> dict:
        """Execute Bash script with restrictions"""
        with tempfile.TemporaryDirectory(prefix="grace_sh_") as temp_dir:
            script_path = Path(temp_dir) / (filename or "script.sh")
            script_path.write_text(code, encoding='utf-8')
            script_path.chmod(0o755)
            
            env = os.environ.copy()
            env["PATH"] = "/usr/bin:/bin"
            
            return await self._run_process(
                ["bash", str(script_path)],
                config.timeout,
                env,
                cwd=temp_dir
            )
    
    async def _execute_sql(self, code: str, config: LanguageConfig) -> dict:
        """Execute SQL in SQLite (read-only mode)"""
        with tempfile.TemporaryDirectory(prefix="grace_sql_") as temp_dir:
            db_path = Path(temp_dir) / "sandbox.db"
            sql_path = Path(temp_dir) / "query.sql"
            sql_path.write_text(code, encoding='utf-8')
            
            commands = [
                "sqlite3",
                str(db_path),
                "-readonly",
                "-batch",
                f".read {sql_path}"
            ]
            
            return await self._run_process(
                commands,
                config.timeout,
                cwd=temp_dir
            )
    
    async def _execute_go(self, code: str, config: LanguageConfig, additional_files: Optional[Dict[str, str]]) -> dict:
        """Execute Go code"""
        with tempfile.TemporaryDirectory(prefix="grace_go_") as temp_dir:
            go_path = Path(temp_dir) / "go"
            go_path.mkdir()
            
            main_path = go_path / "main.go"
            main_path.write_text(code, encoding='utf-8')
            
            if additional_files:
                for name, content in additional_files.items():
                    file_path = go_path / name
                    file_path.write_text(content, encoding='utf-8')
            
            env = os.environ.copy()
            for k, v in config.env_vars.items():
                env[k] = v.replace("{temp_dir}", temp_dir)
            
            return await self._run_process(
                ["go", "run", str(main_path)],
                config.timeout,
                env,
                cwd=go_path
            )
    
    async def _execute_rust(self, code: str, config: LanguageConfig) -> dict:
        """Execute Rust code"""
        with tempfile.TemporaryDirectory(prefix="grace_rust_") as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()
            
            cargo_toml = project_path / "Cargo.toml"
            cargo_toml.write_text("""[package]
name = "grace_sandbox"
version = "0.1.0"
edition = "2021"

[dependencies]
""", encoding='utf-8')
            
            src_path = project_path / "src"
            src_path.mkdir()
            
            main_rs = src_path / "main.rs"
            main_rs.write_text(code, encoding='utf-8')
            
            env = os.environ.copy()
            for k, v in config.env_vars.items():
                env[k] = v.replace("{temp_dir}", temp_dir)
            
            manifest_path = project_path / "Cargo.toml"
            
            return await self._run_process(
                ["cargo", "run", "--manifest-path", str(manifest_path), "--quiet"],
                config.timeout,
                env,
                cwd=project_path
            )
    
    async def _run_process(
        self,
        command: list,
        timeout: int,
        env: dict = None,
        cwd: str = None
    ) -> dict:
        """Run subprocess with timeout and resource limits"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=cwd
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                exit_code = process.returncode or 0
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "output": "",
                    "error": f"Execution timeout ({timeout}s limit exceeded)",
                    "exit_code": -1
                }
            
            output = stdout.decode('utf-8', errors='replace')[:100000]
            error = stderr.decode('utf-8', errors='replace')[:100000]
            
            return {
                "success": exit_code == 0,
                "output": output,
                "error": error,
                "exit_code": exit_code
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Process execution error: {str(e)}",
                "exit_code": -1
            }
    
    def _validate_shell_code(self, code: str) -> Optional[str]:
        """Validate shell script for dangerous commands"""
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            tokens = re.split(r'[\s|&;]+', line)
            command = tokens[0] if tokens else ""
            
            if command in SHELL_BLACKLIST:
                return f"Forbidden command '{command}' at line {line_num}"
            
            if '>' in line and '/dev/' in line:
                return f"Device file access forbidden at line {line_num}"
            
            if re.search(r'\$\(.*\)', line) or re.search(r'`.*`', line):
                for token in tokens:
                    if any(cmd in token for cmd in SHELL_BLACKLIST):
                        return f"Command substitution contains forbidden command at line {line_num}"
        
        return None


execution_engine = ExecutionEngine()
