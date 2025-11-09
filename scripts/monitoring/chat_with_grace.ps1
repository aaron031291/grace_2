# Grace Terminal Chat Launcher (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Grace Terminal Chat" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure backend is running first!" -ForegroundColor Yellow
Write-Host "Backend should be at: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "Warning: Virtual environment not found" -ForegroundColor Yellow
    Write-Host "Using system Python..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting Grace chat interface..." -ForegroundColor Green
Write-Host ""

# Run terminal chat
python backend\terminal_chat.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error starting Grace chat" -ForegroundColor Red
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. Backend is running (.\start_both.bat)" -ForegroundColor Yellow
    Write-Host "  2. Virtual environment is set up" -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"
