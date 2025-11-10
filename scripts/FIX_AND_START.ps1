# ============================================================================
# FIX ALL ISSUES AND START GRACE
# Run this to fix dependencies and start the full system
# ============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "FIXING GRACE DEPENDENCIES & STARTING SYSTEM" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop any running jobs
Write-Host "→ Stopping any running backend jobs..." -ForegroundColor Yellow
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
Write-Host "✓ Jobs cleared" -ForegroundColor Green
Write-Host ""

# Step 2: Install dependencies
Write-Host "→ Installing all dependencies (this takes 2-5 minutes)..." -ForegroundColor Yellow
Write-Host ""

& .venv\Scripts\python.exe -m pip install --upgrade pip --quiet

Write-Host "Installing core packages..." -ForegroundColor Cyan
& .venv\Scripts\pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings --quiet

Write-Host "Installing AI/ML packages..." -ForegroundColor Cyan
& .venv\Scripts\pip install openai anthropic --quiet

Write-Host "Installing web packages..." -ForegroundColor Cyan
& .venv\Scripts\pip install aiohttp httpx requests beautifulsoup4 lxml --quiet

Write-Host "Installing remaining packages..." -ForegroundColor Cyan
& .venv\Scripts\pip install -r backend\requirements.txt --quiet

Write-Host ""
Write-Host "✓ All dependencies installed!" -ForegroundColor Green
Write-Host ""

# Step 3: Start backend directly to see if it works
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "STARTING GRACE BACKEND" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend will be at: http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start backend
& .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
