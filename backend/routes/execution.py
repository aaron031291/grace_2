"""
API routes for multi-language code execution
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
from ..auth import get_current_user
from ..execution_engine import execution_engine
from ..execution_config import LANGUAGE_CONFIGS, EXECUTION_PRESETS
=======
from ..schemas_extended import ExecutionLanguagesResponse, ExecutionPresetsResponse, ExecutionValidateResponse
>>>>>>> origin/main

router = APIRouter(prefix="/api/execute", tags=["execution"])


class ExecuteRequest(BaseModel):
    code: str = Field(..., description="Source code to execute")
    language: str = Field(..., description="Programming language (python, javascript, typescript, bash, sql, go, rust)")
    preset: str = Field(default="dev", description="Execution preset (safe, dev, production)")
    filename: Optional[str] = Field(None, description="Optional filename override")
    additional_files: Optional[Dict[str, str]] = Field(None, description="Additional files for multi-file execution")


@router.post("")
async def execute_code(
    request: ExecuteRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Execute code in a sandboxed environment
    
    Supports multiple languages with security controls:
    - Python: Standard Python 3 with timeout and resource limits
    - JavaScript: Node.js with memory limits
    - TypeScript: Compiled to JS then executed
    - Bash: Restricted shell with command whitelist
    - SQL: SQLite in read-only mode
    - Go: go run with isolated workspace
    - Rust: cargo run with isolated workspace
    
    Security features:
    - Governance policy checks before execution
    - Hunter security scanning for malicious code
    - Resource limits (CPU, memory, timeout)
    - Verification logging to immutable audit trail
    - Command whitelisting for shell execution
    
    Execution presets:
    - safe: Strict limits, no network, 15s timeout
    - dev: Relaxed limits, network allowed, 60s timeout
    - production: Medium limits, full logging, 30s timeout
    """
    try:
        result = await execution_engine.execute(
            code=request.code,
            language=request.language,
            user=current_user,
            preset=request.preset,
            filename=request.filename,
            additional_files=request.additional_files
        )
        
        return result.to_dict()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


<<<<<<< HEAD
@router.get("/languages")
async def get_supported_languages(
    current_user: str = Depends(get_current_user)
):
    """Get list of supported programming languages and their configurations"""
    languages = []
    for key, config in LANGUAGE_CONFIGS.items():
        languages.append({
            "id": key,
            "name": config.name,
            "file_extension": config.file_extension,
            "timeout": config.timeout,
            "memory_limit_mb": config.memory_limit_mb,
            "requires_compilation": config.requires_compilation,
            "allow_network": config.allow_network
        })
    
    return {"languages": languages, "count": len(languages)}


@router.get("/presets")
async def get_execution_presets(
    current_user: str = Depends(get_current_user)
):
    """Get list of execution presets and their configurations"""
    presets = []
    for key, preset in EXECUTION_PRESETS.items():
        presets.append({
            "id": key,
            "name": preset.name,
            "timeout_multiplier": preset.timeout_multiplier,
            "memory_multiplier": preset.memory_multiplier,
            "allow_network": preset.allow_network,
            "enable_logging": preset.enable_logging,
            "strict_limits": preset.strict_limits
        })
    
    return {"presets": presets, "count": len(presets)}


@router.post("/validate")
async def validate_code(
    request: ExecuteRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Validate code without executing it
    
    Performs security checks:
    - Shell command validation
    - Forbidden pattern detection
    - Governance policy checks
    """
    from ..execution_engine import ExecutionEngine
    
    engine = ExecutionEngine()
    
    if request.language == "bash":
        validation_error = engine._validate_shell_code(request.code)
        if validation_error:
            return {
                "valid": False,
                "error": validation_error,
                "language": request.language
            }
    
    from ..governance import governance_engine
    governance_result = await governance_engine.check(
        actor=current_user,
        action="code.validate",
        resource=f"{request.language}_code",
        payload={
            "language": request.language,
            "code_length": len(request.code)
        }
    )
    
    if governance_result["decision"] == "deny":
        return {
            "valid": False,
            "error": "Code denied by governance policy",
            "language": request.language,
            "governance_decision": governance_result["decision"]
        }
    
    return {
        "valid": True,
        "language": request.language,
        "governance_decision": governance_result["decision"]
    }
