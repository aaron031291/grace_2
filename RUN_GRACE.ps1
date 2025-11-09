# ============================================================================
# GRACE ONE-COMMAND RUNNER
# Simple wrapper to test then boot Grace
# ============================================================================

param(
    [switch]$SkipTest,
    [switch]$SkipFrontend,
    [switch]$QuickStart,
    [switch]$Help
)

if ($Help) {
    Write-Host ""
    Write-Host "GRACE ONE-COMMAND RUNNER" -ForegroundColor Cyan
    Write-Host "=" * 60
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\RUN_GRACE.ps1                    # Test + Boot everything"
    Write-Host "  .\RUN_GRACE.ps1 -SkipTest          # Skip tests, just boot"
    Write-Host "  .\RUN_GRACE.ps1 -SkipFrontend      # Boot backend only"
    Write-Host "  .\RUN_GRACE.ps1 -QuickStart        # Fast boot (skip installs)"
    Write-Host ""
    Write-Host "What it does:" -ForegroundColor Yellow
    Write-Host "  1. Tests environment & kernels (unless -SkipTest)"
    Write-Host "  2. Boots complete Grace system"
    Write-Host "  3. Monitors until Ctrl+C"
    Write-Host ""
    Write-Host "Services started:" -ForegroundColor Yellow
    Write-Host "  • Backend:  http://localhost:8000"
    Write-Host "  • Frontend: http://localhost:5173 (unless -SkipFrontend)"
    Write-Host "  • API Docs: http://localhost:8000/docs"
    Write-Host ""
    Write-Host "Kernels:" -ForegroundColor Yellow
    Write-Host "  • POST /kernel/memory       (25 APIs)"
    Write-Host "  • POST /kernel/core         (47 APIs)"
    Write-Host "  • POST /kernel/code         (38 APIs)"
    Write-Host "  • POST /kernel/governance   (50 APIs)"
    Write-Host "  • POST /kernel/verification (35 APIs)"
    Write-Host "  • POST /kernel/intelligence (60 APIs)"
    Write-Host "  • POST /kernel/infrastructure (38 APIs)"
    Write-Host "  • POST /kernel/federation   (18 APIs)"
    Write-Host ""
    exit 0
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "  GRACE ONE-COMMAND RUNNER" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# STEP 1: TEST (unless skipped)
# ============================================================================
if (-not $SkipTest) {
    Write-Host "STEP 1: Running E2E Tests..." -ForegroundColor Yellow
    Write-Host ""
    
    & .\TEST_E2E_BOOT.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "=" * 80 -ForegroundColor Red
        Write-Host "TESTS FAILED - Aborting boot" -ForegroundColor Red
        Write-Host "=" * 80 -ForegroundColor Red
        Write-Host ""
        Write-Host "Fix the errors above and try again." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Or skip tests with:" -ForegroundColor Yellow
        Write-Host "  .\RUN_GRACE.ps1 -SkipTest" -ForegroundColor White
        Write-Host ""
        exit 1
    }
    
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to continue with boot..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
} else {
    Write-Host "STEP 1: Skipping tests (-SkipTest)" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================================================
# STEP 2: BOOT
# ============================================================================
Write-Host "STEP 2: Booting Grace Complete System..." -ForegroundColor Yellow
Write-Host ""

# Build arguments for boot script
$bootArgs = @()
if ($SkipFrontend) { $bootArgs += "-SkipFrontend" }
if ($QuickStart) { $bootArgs += "-QuickStart" }

# Call boot script
& .\BOOT_GRACE_COMPLETE_E2E.ps1 @bootArgs
