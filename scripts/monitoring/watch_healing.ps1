# GRACE Autonomous Healing Monitor (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GRACE Autonomous Healing Monitor" -ForegroundColor Cyan
Write-Host "  Real-time healing activity display" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

python scripts\watch_healing.py
