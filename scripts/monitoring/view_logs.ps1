# Grace Log Viewer (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GRACE System Logs Viewer" -ForegroundColor Cyan
Write-Host "  Last 50 Entries from All Systems" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

Write-Host "Running log viewer..." -ForegroundColor Green
Write-Host ""

# Run log viewer
python scripts\view_all_logs.py

Read-Host "`nPress Enter to exit"
