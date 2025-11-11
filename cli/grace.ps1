$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$GraceRoot = Split-Path -Parent $ScriptDir

if (Test-Path "$GraceRoot\.venv\Scripts\Activate.ps1") {
    & "$GraceRoot\.venv\Scripts\Activate.ps1"
} elseif (Test-Path "$GraceRoot\venv\Scripts\Activate.ps1") {
    & "$GraceRoot\venv\Scripts\Activate.ps1"
}

python -m backend.unified_grace_orchestrator $args