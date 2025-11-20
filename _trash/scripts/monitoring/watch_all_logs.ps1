# GRACE Auto-Refresh Log Viewer (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GRACE Auto-Refresh Log Viewer" -ForegroundColor Cyan
Write-Host "  Updates every 5 minutes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

python scripts\watch_all_logs.py
