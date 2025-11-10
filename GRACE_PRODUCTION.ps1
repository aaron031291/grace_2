# ============================================================================
# GRACE PRODUCTION BOOT - Hardened & Optimized
# Production-ready startup with health checks, validation, and monitoring
# ============================================================================

param(
    [switch]$Stop,
    [switch]$Status,
    [switch]$Audit,
    [switch]$SkipChecks
)

# Set UTF-8 encoding
chcp 65001 > $null
$env:PYTHONIOENCODING = "utf-8"
$ErrorActionPreference = "Continue"

# ============================================================================
# CONFIGURATION
# ============================================================================
$GRACE_ROOT = $PSScriptRoot
$VENV_PATH = Join-Path $GRACE_ROOT ".venv"
$PYTHON_EXE = Join-Path $VENV_PATH "Scripts\python.exe"
$BACKEND_PORT = 8000
$FRONTEND_PORT = 5173

# ============================================================================
# STOP MODE
# ============================================================================
if ($Stop) {
    Write-Host ""
    Write-Host "Stopping Grace..." -ForegroundColor Yellow
    Get-Job | Stop-Job -ErrorAction SilentlyContinue
    Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
    
    # Kill any orphaned processes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -like "*grace_2*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "[OK] Grace stopped" -ForegroundColor Green
    Write-Host ""
    exit 0
}

# ============================================================================
# STATUS MODE
# ============================================================================
if ($Status) {
    Write-Host ""
    Write-Host "Grace Production Status:" -ForegroundColor Cyan
    Write-Host "=" * 80
    
    $jobs = Get-Job
    if ($jobs.Count -eq 0) {
        Write-Host "[FAIL] Grace is not running" -ForegroundColor Red
    } else {
        Write-Host "[OK] Grace is running ($($jobs.Count) job(s))" -ForegroundColor Green
        $jobs | Format-Table Id, Name, State
    }
    
    # Check backend health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$BACKEND_PORT/health" -TimeoutSec 2
        Write-Host "[OK] Backend healthy" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Backend not responding" -ForegroundColor Red
    }
    
    Write-Host ""
    exit 0
}

# ============================================================================
# AUDIT MODE
# ============================================================================
if ($Audit) {
    Write-Host ""
    Write-Host "Running Production Readiness Audit..." -ForegroundColor Cyan
    Write-Host "=" * 80
    Write-Host ""
    
    & $PYTHON_EXE scripts/production_readiness_audit.py
    exit $LASTEXITCODE
}

# ============================================================================
# PRODUCTION STARTUP
# ============================================================================

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "GRACE PRODUCTION BOOT" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Step 1: Pre-flight checks
if (-not $SkipChecks) {
    Write-Host "[1/7] Pre-flight Checks" -ForegroundColor Yellow
    Write-Host "-" * 80
    
    # Check virtual environment
    if (-not (Test-Path $PYTHON_EXE)) {
        Write-Host "[FAIL] Virtual environment not found" -ForegroundColor Red
        Write-Host "Run: python -m venv .venv" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  ✓ Virtual environment" -ForegroundColor Green
    
    # Check .env
    if (-not (Test-Path ".env")) {
        Write-Host "  ⚠ .env not found, using defaults" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ Environment configured" -ForegroundColor Green
    }
    
    # Check critical directories
    $dirs = @("logs", "databases", "storage", "ml_artifacts")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    Write-Host "  ✓ Directories ready" -ForegroundColor Green
    
    Write-Host ""
}

# Step 2: Syntax validation
if (-not $SkipChecks) {
    Write-Host "[2/7] Syntax Validation" -ForegroundColor Yellow
    Write-Host "-" * 80
    
    # Check for merge conflicts
    $conflicts = Get-ChildItem backend -Recurse -Include *.py | Select-String -Pattern "^<<<<<<< |^=======$|^>>>>>>>" -ErrorAction SilentlyContinue
    if ($conflicts) {
        Write-Host "  [FAIL] Merge conflicts found!" -ForegroundColor Red
        Write-Host "  Run: python scripts/fix_merge_conflicts.py" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  ✓ No merge conflicts" -ForegroundColor Green
    
    Write-Host ""
}

# Step 3: Database initialization
Write-Host "[3/7] Database Initialization" -ForegroundColor Yellow
Write-Host "-" * 80

& $PYTHON_EXE scripts/create_missing_tables.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Database initialization failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Database ready" -ForegroundColor Green
Write-Host ""

# Step 4: Dependency check
if (-not $SkipChecks) {
    Write-Host "[4/7] Dependency Check" -ForegroundColor Yellow
    Write-Host "-" * 80
    
    $required = @("fastapi", "uvicorn", "sqlalchemy", "pydantic")
    $missing = @()
    
    foreach ($pkg in $required) {
        & $PYTHON_EXE -c "import $pkg" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $missing += $pkg
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "  [FAIL] Missing packages: $($missing -join ', ')" -ForegroundColor Red
        Write-Host "  Run: pip install -r backend/requirements.txt" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "  ✓ All dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Step 5: Start Backend
Write-Host "[5/7] Starting Backend" -ForegroundColor Yellow
Write-Host "-" * 80

$backendJob = Start-Job -ScriptBlock {
    param($root, $python)
    Set-Location $root
    & $python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
} -ArgumentList $GRACE_ROOT, $PYTHON_EXE -Name "Grace-Backend"

Write-Host "  ✓ Backend starting (Job ID: $($backendJob.Id))" -ForegroundColor Green
Write-Host ""

# Step 6: Health check
Write-Host "[6/7] Health Check" -ForegroundColor Yellow
Write-Host "-" * 80

$maxRetries = 30
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries -and -not $healthy) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$BACKEND_PORT/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $healthy = $true
        }
    } catch {
        $retryCount++
        Write-Host "  Waiting for backend... ($retryCount/$maxRetries)" -ForegroundColor Gray
    }
}

if (-not $healthy) {
    Write-Host "  [FAIL] Backend failed to start" -ForegroundColor Red
    Write-Host "  Check logs: Get-Job -Id $($backendJob.Id) | Receive-Job" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✓ Backend healthy" -ForegroundColor Green
Write-Host ""

# Step 7: Summary
Write-Host "[7/7] Startup Complete" -ForegroundColor Yellow
Write-Host "-" * 80
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "GRACE IS OPERATIONAL" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:$BACKEND_PORT" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:$BACKEND_PORT/docs" -ForegroundColor Cyan
Write-Host "Health:   http://localhost:$BACKEND_PORT/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  Status:  .\GRACE_PRODUCTION.ps1 -Status" -ForegroundColor Gray
Write-Host "  Audit:   .\GRACE_PRODUCTION.ps1 -Audit" -ForegroundColor Gray
Write-Host "  Stop:    .\GRACE_PRODUCTION.ps1 -Stop" -ForegroundColor Gray
Write-Host ""
Write-Host "Logs:" -ForegroundColor Yellow
Write-Host "  Get-Job | Receive-Job" -ForegroundColor Gray
Write-Host ""

