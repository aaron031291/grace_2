#!/usr/bin/env pwsh
Set-Location 'C:\Users\aaron\grace_2'
if (Test-Path '.venv\Scripts\Activate.ps1') {
    & '.venv\Scripts\Activate.ps1'
}
python -m backend.unified_grace_orchestrator $args
