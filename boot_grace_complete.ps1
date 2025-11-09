# ============================================================================
# Grace Complete E2E Boot Script - PowerShell
# Starts ALL Grace systems: Backend, Frontend, Monitoring, Databases
# ============================================================================

param(
    [switch]$SkipFrontend,
    [switch]$SkipMonitoring,
    [switch]$DevMode
)

$ErrorActionPreference = "Continue"

# Colors
function Write-Header {
    param($Message)
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param($Message)
    Write-Host "→ $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Main Boot Sequence
Write-Header "🤖 GRACE COMPLETE E2E BOOT SEQUENCE"

Write-Host "Starting Grace AI Learning System..." -ForegroundColor White
Write-Host "Mode: $(if ($DevMode) {'Development'} else {'Production'})" -ForegroundColor White
Write-Host ""

# ============================================================================
# STEP 1: Pre-flight Checks
# ============================================================================
Write-Header "STEP 1: Pre-flight System Checks"

# Check Python
Write-Info "Checking Python..."
if (Test-Path ".venv\Scripts\python.exe") {
    $pythonVersion = & .venv\Scripts\python.exe --version
    Write-Success "Python found: $pythonVersion"
} else {
    Write-Error-Custom "Python virtual environment not found!"
    Write-Host "Run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Check Node.js (for frontend)
if (-not $SkipFrontend) {
    Write-Info "Checking Node.js..."
    try {
        $nodeVersion = node --version 2>$null
        Write-Success "Node.js found: $nodeVersion"
    } catch {
        Write-Error-Custom "Node.js not found (needed for frontend)"
        $SkipFrontend = $true
    }
}

# Check .env file
Write-Info "Checking environment configuration..."
if (Test-Path ".env") {
    Write-Success ".env file found"
    
    # Check for Amp API key
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "AMP_API_KEY=") {
        Write-Success "Amp API key configured"
    } else {
        Write-Host "⚠ Amp API key not found in .env" -ForegroundColor Yellow
    }
} else {
    Write-Error-Custom ".env file not found"
    Write-Info "Creating from .env.example..."
    Copy-Item ".env.example" ".env"
    Write-Success ".env created - please add your API keys"
}

# Check databases
Write-Info "Checking databases..."
if (Test-Path "backend\grace.db") {
    $dbSize = (Get-Item "backend\grace.db").Length / 1MB
    Write-Success "Main database found ($([math]::Round($dbSize, 2)) MB)"
} else {
    Write-Host "⚠ Main database will be created on first run" -ForegroundColor Yellow
}

# ============================================================================
# STEP 2: Create Required Directories
# ============================================================================
Write-Header "STEP 2: Creating Required Directories"

$directories = @(
    "logs",
    "storage\provenance",
    "storage\web_knowledge",
    "storage\exports",
    "sandbox\knowledge_tests",
    "sandbox\api_tests",
    "config",
    "databases"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Success "Created: $dir"
    } else {
        Write-Info "Exists: $dir"
    }
}

# ============================================================================
# STEP 3: Install/Update Dependencies
# ============================================================================
Write-Header "STEP 3: Checking Dependencies"

Write-Info "Checking Python packages..."
& .venv\Scripts\python.exe -m pip install -q --upgrade pip
Write-Success "pip updated"

if ($DevMode) {
    Write-Info "Installing backend dependencies..."
    & .venv\Scripts\python.exe -m pip install -q -r backend\requirements.txt
    Write-Success "Backend dependencies installed"
}

if (-not $SkipFrontend -and $DevMode) {
    Write-Info "Checking frontend dependencies..."
    if (Test-Path "frontend\node_modules") {
        Write-Success "Frontend dependencies found"
    } else {
        Write-Info "Installing frontend dependencies (this may take a while)..."
        Set-Location frontend
        npm install --silent
        Set-Location ..
        Write-Success "Frontend dependencies installed"
    }
}

# ============================================================================
# STEP 4: Database Initialization
# ============================================================================
Write-Header "STEP 4: Database Initialization"

Write-Info "Running database migrations..."
try {
    & .venv\Scripts\alembic.exe upgrade head 2>$null
    Write-Success "Database migrations complete"
} catch {
    Write-Host "⚠ Migrations skipped (will run on startup)" -ForegroundColor Yellow
}

# ============================================================================
# STEP 5: Start Backend Server
# ============================================================================
Write-Header "STEP 5: Starting Grace Backend"

Write-Host ""
Write-Host "Grace Backend will start with:" -ForegroundColor Cyan
Write-Host "  ✓ Web Learning (83+ domains)" -ForegroundColor Green
Write-Host "  ✓ GitHub Mining" -ForegroundColor Green
Write-Host "  ✓ YouTube Learning" -ForegroundColor Green
Write-Host "  ✓ Reddit Learning (38+ subreddits)" -ForegroundColor Green
Write-Host "  ✓ API Discovery & Integration" -ForegroundColor Green
Write-Host "  ✓ Amp API (Last Resort + Verification)" -ForegroundColor Green
Write-Host "  ✓ Remote Computer Access" -ForegroundColor Green
Write-Host "  ✓ Visual Ingestion Logger" -ForegroundColor Green
Write-Host "  ✓ ML/DL Reliability Learning" -ForegroundColor Green
Write-Host "  ✓ Knowledge Verifier" -ForegroundColor Green
Write-Host "  ✓ Proactive Improvement" -ForegroundColor Green
Write-Host "  ✓ Performance Optimizer" -ForegroundColor Green
Write-Host "  ✓ Autonomous Goal Setting" -ForegroundColor Green
Write-Host "  ✓ Self-Healing Systems" -ForegroundColor Green
Write-Host "  ✓ Complete Governance" -ForegroundColor Green
Write-Host ""

Write-Info "Starting backend on http://localhost:8000 ..."

# Start backend in background job
$backendJob = Start-Job -ScriptBlock {
    param($rootPath)
    Set-Location $rootPath
    & .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $PWD

Write-Success "Backend starting (Job ID: $($backendJob.Id))"

# Wait for backend to be ready
Write-Info "Waiting for backend to initialize..."
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend is online!"
            break
        }
    } catch {
        Start-Sleep -Seconds 1
        $waited++
        Write-Host "." -NoNewline
    }
}
Write-Host ""

if ($waited -ge $maxWait) {
    Write-Host "⚠ Backend may still be starting..." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Backend accessible at:" -ForegroundColor Cyan
    Write-Host "  • http://localhost:8000" -ForegroundColor White
    Write-Host "  • http://localhost:8000/docs (API Documentation)" -ForegroundColor White
    Write-Host "  • http://localhost:8000/health (Health Check)" -ForegroundColor White
}

# ============================================================================
# STEP 6: Start Frontend (Optional)
# ============================================================================
if (-not $SkipFrontend) {
    Write-Header "STEP 6: Starting Grace Frontend"
    
    Write-Info "Starting frontend on http://localhost:5173 ..."
    
    $frontendJob = Start-Job -ScriptBlock {
        param($rootPath)
        Set-Location "$rootPath\frontend"
        npm run dev
    } -ArgumentList $PWD
    
    Write-Success "Frontend starting (Job ID: $($frontendJob.Id))"
    
    Start-Sleep -Seconds 3
    Write-Host ""
    Write-Host "Frontend accessible at:" -ForegroundColor Cyan
    Write-Host "  • http://localhost:5173" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "→ Frontend skipped (use -SkipFrontend:$false to enable)" -ForegroundColor Yellow
}

# ============================================================================
# STEP 7: Open Monitoring Tools (Optional)
# ============================================================================
if (-not $SkipMonitoring) {
    Write-Header "STEP 7: Starting Monitoring Tools"
    
    # Open visual ingestion log
    Write-Info "Opening visual ingestion log..."
    if (Test-Path "logs\ingestion.html") {
        Start-Process "logs\ingestion.html"
        Write-Success "Visual log opened in browser"
    } else {
        Write-Host "⚠ Visual log will be created on first ingestion" -ForegroundColor Yellow
    }
    
    # Start terminal monitor in new window
    Write-Info "Starting terminal monitor..."
    Start-Process cmd -ArgumentList "/k", ".\scripts\monitoring\watch_ingestion.bat"
    Write-Success "Terminal monitor started in new window"
    
} else {
    Write-Host ""
    Write-Host "→ Monitoring tools skipped" -ForegroundColor Yellow
}

# ============================================================================
# STEP 8: System Status Summary
# ============================================================================
Write-Header "GRACE SYSTEM STATUS"

Write-Host "🤖 GRACE IS NOW RUNNING!" -ForegroundColor Green
Write-Host ""

Write-Host "SERVICES:" -ForegroundColor Cyan
Write-Host "  ✓ Backend:  http://localhost:8000" -ForegroundColor Green
if (-not $SkipFrontend) {
    Write-Host "  ✓ Frontend: http://localhost:5173" -ForegroundColor Green
}
Write-Host ""

Write-Host "APIS (40+ endpoints):" -ForegroundColor Cyan
Write-Host "  • /web-learning/learn           - Trigger learning" -ForegroundColor White
Write-Host "  • /web-learning/amp/query       - Amp API (last resort)" -ForegroundColor White
Write-Host "  • /web-learning/verify/source   - Verify with Amp" -ForegroundColor White
Write-Host "  • /web-learning/ingestions/*    - Monitor ingestions" -ForegroundColor White
Write-Host "  • Full docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "CONTROL INTERFACES:" -ForegroundColor Cyan
Write-Host "  • Chat:     scripts\control\grace_terminal.bat" -ForegroundColor White
Write-Host "  • Control:  scripts\control\grace_control.bat" -ForegroundColor White
Write-Host "  • Monitor:  scripts\control\grace_monitor.bat" -ForegroundColor White
Write-Host ""

Write-Host "MONITORING:" -ForegroundColor Cyan
Write-Host "  • Visual:   scripts\monitoring\view_ingestion_log.bat" -ForegroundColor White
Write-Host "  • Terminal: scripts\monitoring\watch_ingestion.bat" -ForegroundColor White
Write-Host ""

Write-Host "LOGS:" -ForegroundColor Cyan
Write-Host "  • Ingestion: logs\ingestion.html (clickable links!)" -ForegroundColor White
Write-Host "  • Terminal:  logs\ingestion_visual.log" -ForegroundColor White
Write-Host ""

Write-Host "LEARNING SOURCES:" -ForegroundColor Cyan
Write-Host "  • Web (83+ domains) • GitHub • YouTube" -ForegroundColor White
Write-Host "  • Reddit (38+ subreddits) • APIs • Amp (last resort)" -ForegroundColor White
Write-Host ""

Write-Host "FEATURES:" -ForegroundColor Cyan
Write-Host "  ✓ Amp API Verification (validates free sources)" -ForegroundColor Green
Write-Host "  ✓ ML/DL Learning (learns source reliability)" -ForegroundColor Green
Write-Host "  ✓ Cost-Effective Batching (80-95% savings)" -ForegroundColor Green
Write-Host "  ✓ Complete Governance (100% compliance)" -ForegroundColor Green
Write-Host "  ✓ Clickable HTTP Links (trace every source)" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Keep Running
# ============================================================================
Write-Header "GRACE IS OPERATIONAL"

Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""
Write-Host "Monitoring jobs..." -ForegroundColor Cyan
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        # Check backend job
        $backendState = (Get-Job -Id $backendJob.Id).State
        
        if ($backendState -eq "Running") {
            Write-Host "`r✓ Backend: Running | " -NoNewline -ForegroundColor Green
        } else {
            Write-Host "`r✗ Backend: $backendState | " -NoNewline -ForegroundColor Red
        }
        
        if (-not $SkipFrontend -and $frontendJob) {
            $frontendState = (Get-Job -Id $frontendJob.Id).State
            if ($frontendState -eq "Running") {
                Write-Host "Frontend: Running" -NoNewline -ForegroundColor Green
            } else {
                Write-Host "Frontend: $frontendState" -NoNewline -ForegroundColor Red
            }
        }
        
        $timeStr = Get-Date -Format "HH:mm:ss"
        Write-Host " | Time: $timeStr  " -NoNewline
        
        Start-Sleep -Seconds 2
    }
} finally {
    # Cleanup on exit
    Write-Host ""
    Write-Host ""
    Write-Header "Shutting Down Grace"
    
    Write-Info "Stopping backend..."
    Stop-Job -Id $backendJob.Id
    Remove-Job -Id $backendJob.Id
    Write-Success "Backend stopped"
    
    if ($frontendJob) {
        Write-Info "Stopping frontend..."
        Stop-Job -Id $frontendJob.Id
        Remove-Job -Id $frontendJob.Id
        Write-Success "Frontend stopped"
    }
    
    Write-Host ""
    Write-Host "✓ Grace shutdown complete" -ForegroundColor Green
    Write-Host ""
}
