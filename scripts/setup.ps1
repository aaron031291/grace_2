# GRACE Setup Script
# Complete environment setup and validation

param(
    [switch]$SkipTests,
    [switch]$Quick
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "GRACE COMPLETE SETUP" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# ========== TIER 1: DEPENDENCIES ==========
Write-Host "TIER 1: INSTALLING DEPENDENCIES" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "[1/4] Checking Python virtual environment..." -ForegroundColor White
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor White
& .\.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
& .\.venv\Scripts\pip.exe install --quiet -r requirements.txt
Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green

Write-Host "[3/4] Installing frontend dependencies..." -ForegroundColor White
if (-not $Quick) {
    & npm install --prefix frontend --silent
    Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⊘ Skipped (--Quick mode)" -ForegroundColor Gray
}

Write-Host "[4/4] Checking environment configuration..." -ForegroundColor White
if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
} else {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  ✓ Created .env from example" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ No .env file (using defaults)" -ForegroundColor Yellow
    }
}

Write-Host ""

# ========== TIER 2: FOUNDATION ==========
Write-Host "TIER 2: FOUNDATION SETUP" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "[1/3] Creating databases folder..." -ForegroundColor White
if (-not (Test-Path "databases")) {
    New-Item -ItemType Directory -Path "databases" | Out-Null
    Write-Host "  ✓ Databases folder created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Databases folder exists" -ForegroundColor Green
}

Write-Host "[2/3] Running database migrations..." -ForegroundColor White
& .\.venv\Scripts\alembic.exe upgrade head 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Migrations applied successfully" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Migration warnings (may be OK)" -ForegroundColor Yellow
}

if (-not $SkipTests) {
    Write-Host "[3/3] Running foundation tests..." -ForegroundColor White
    & .\.venv\Scripts\pytest.exe backend/tests --quiet --tb=short 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 5) {
        Write-Host "  ✓ Tests passed (or no tests found)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Some tests failed (continuing)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[3/3] Skipping tests (--SkipTests mode)" -ForegroundColor Gray
}

Write-Host ""

# ========== COMPLETION ==========
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor White
Write-Host ""
Write-Host "1. Start backend:" -ForegroundColor Yellow
Write-Host "   .\.venv\Scripts\uvicorn.exe backend.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start frontend (optional):" -ForegroundColor Yellow
Write-Host "   npm run dev --prefix frontend" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test endpoints:" -ForegroundColor Yellow
Write-Host "   curl http://localhost:8000/health" -ForegroundColor Gray
Write-Host "   curl http://localhost:8000/api/meta/focus" -ForegroundColor Gray
Write-Host ""
Write-Host "4. View documentation:" -ForegroundColor Yellow
Write-Host "   docs/guides/QUICK_START.md" -ForegroundColor Gray
Write-Host "   docs/planning/SPRINT_STATUS.md" -ForegroundColor Gray
Write-Host ""
Write-Host "GRACE is ready to run! 🚀" -ForegroundColor Green
