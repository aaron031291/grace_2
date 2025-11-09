# Simple Backend Start Script
# No tests, just start backend immediately

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "GRACE BACKEND - SIMPLE START" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check we're in right directory
if (-not (Test-Path "backend\main.py")) {
    Write-Host "ERROR: Can't find backend\main.py" -ForegroundColor Red
    Write-Host "Make sure you're in C:\Users\aaron\grace_2 directory" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run this first:" -ForegroundColor Yellow
    Write-Host "  cd C:\Users\aaron\grace_2" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✓ Found backend directory" -ForegroundColor Green

# Check Python
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Creating it now..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
}

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pipList = & .venv\Scripts\pip list 2>&1
if ($pipList -notmatch "fastapi") {
    Write-Host "Installing dependencies (this will take a few minutes)..." -ForegroundColor Yellow
    & .venv\Scripts\pip install -r backend\requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

# Check .env
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env created" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit .env and add your API keys!" -ForegroundColor Yellow
    Write-Host "Press any key to continue anyway..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "✓ .env file found" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "STARTING BACKEND" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host "  http://localhost:8000/docs (API Documentation)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start backend
& .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

Write-Host ""
Write-Host "Backend stopped." -ForegroundColor Yellow
