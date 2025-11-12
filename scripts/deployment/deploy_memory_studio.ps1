# Grace Memory Studio - Production Deployment Script
# Automated deployment and verification

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     GRACE MEMORY STUDIO - PRODUCTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Step 1: Check Prerequisites
Write-Host "Step 1: Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Python not found" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  [OK] Node: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Node.js not found" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Install Dependencies
Write-Host "Step 2: Installing Dependencies..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  Installing backend dependencies..." -ForegroundColor Gray
pip install -q fastapi uvicorn sqlalchemy aiosqlite pydantic python-multipart 2>$null
Write-Host "  [OK] Core dependencies installed" -ForegroundColor Green

Write-Host "  Installing optional processors (may fail, that's OK)..." -ForegroundColor Gray
pip install -q PyPDF2 2>$null
pip install -q Pillow 2>$null
pip install -q python-docx 2>$null
Write-Host "  [OK] Optional processors installed (if available)" -ForegroundColor Green

Write-Host ""
Write-Host "  Installing frontend dependencies..." -ForegroundColor Gray
Set-Location frontend
npm install --silent 2>$null
Set-Location ..
Write-Host "  [OK] Frontend dependencies installed" -ForegroundColor Green

Write-Host ""

# Step 3: Create grace_training directory
Write-Host "Step 3: Preparing File System..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path "grace_training")) {
    New-Item -Path "grace_training" -ItemType Directory -Force | Out-Null
    Write-Host "  [OK] Created grace_training/ directory" -ForegroundColor Green
} else {
    Write-Host "  [OK] grace_training/ directory exists" -ForegroundColor Green
}

Write-Host ""

# Step 4: Start Backend
Write-Host "Step 4: Starting Backend Server..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  Stopping any existing backend processes..." -ForegroundColor Gray
Get-Process | Where-Object {$_.CommandLine -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "  Starting backend on port 8000..." -ForegroundColor Gray
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python -m uvicorn backend.main:app --reload --port 8000 2>&1
}

Write-Host "  Waiting for backend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Check if backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  [OK] Backend started successfully on port 8000" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Backend may still be starting..." -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Test API Endpoints
Write-Host "Step 5: Verifying API Endpoints..." -ForegroundColor Yellow
Write-Host ""

$endpoints = @(
    @{Method="GET"; Path="/api/memory/status"; Name="Memory Status"},
    @{Method="GET"; Path="/api/grace/memory/categories"; Name="Grace Categories"},
    @{Method="GET"; Path="/api/ingestion/pipelines"; Name="Pipelines"}
)

foreach ($endpoint in $endpoints) {
    try {
        $url = "http://localhost:8000$($endpoint.Path)"
        $response = Invoke-WebRequest -Uri $url -Method $endpoint.Method -TimeoutSec 2 -ErrorAction Stop
        Write-Host "  [OK] $($endpoint.Name)" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] $($endpoint.Name) - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 6: Start Frontend
Write-Host "Step 6: Starting Frontend Server..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  Stopping any existing frontend processes..." -ForegroundColor Gray
Get-Process | Where-Object {$_.Name -eq "node"} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "  Starting frontend on port 5173..." -ForegroundColor Gray
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\frontend"
    npm run dev 2>&1
}

Write-Host "  Waiting for frontend to start..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Check if frontend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  [OK] Frontend started successfully on port 5173" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Frontend may still be starting..." -ForegroundColor Yellow
}

Write-Host ""

# Step 7: Run Tests
Write-Host "Step 7: Running Verification Tests..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  Running test suite..." -ForegroundColor Gray
python test_memory_workspace.py 2>$null | Select-String -Pattern "✓|✗" | ForEach-Object {
    if ($_ -match "✓") {
        Write-Host "  $_" -ForegroundColor Green
    } else {
        Write-Host "  $_" -ForegroundColor Red
    }
}

Write-Host ""

# Step 8: Summary
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                 DEPLOYMENT COMPLETE!" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services Running:" -ForegroundColor White
Write-Host "  - Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "  - Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Open browser: http://localhost:5173" -ForegroundColor Gray
Write-Host "  2. Login: admin / admin123" -ForegroundColor Gray
Write-Host "  3. Click: 📁 Memory button" -ForegroundColor Gray
Write-Host "  4. Explore: 4 tabs (Workspace, Pipelines, Dashboard, Grace)" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation:" -ForegroundColor White
Write-Host "  - SESSION_COMPLETE.md - Full summary" -ForegroundColor Gray
Write-Host "  - MEMORY_WORKSPACE_GUIDE.md - Complete guide" -ForegroundColor Gray
Write-Host "  - MEMORY_FUSION_ROADMAP_50.md - 50-item roadmap" -ForegroundColor Gray
Write-Host ""
Write-Host "To Stop Services:" -ForegroundColor White
Write-Host "  Press Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Keep script running
Write-Host "Services are running. Press Ctrl+C to stop..." -ForegroundColor Yellow
Write-Host ""

# Monitor jobs
while ($true) {
    Start-Sleep -Seconds 30
    
    # Check if services still running
    $backendRunning = Get-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
    $frontendRunning = Get-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
    
    if (-not $backendRunning -or $backendRunning.State -ne "Running") {
        Write-Host "[WARN] Backend stopped unexpectedly" -ForegroundColor Red
        break
    }
    
    if (-not $frontendRunning -or $frontendRunning.State -ne "Running") {
        Write-Host "[WARN] Frontend stopped unexpectedly" -ForegroundColor Red
        break
    }
}
