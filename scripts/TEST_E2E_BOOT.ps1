# ============================================================================
# GRACE E2E BOOT TEST SCRIPT
# Tests that all systems boot correctly and are responsive
# ============================================================================

param(
    [int]$Timeout = 120,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

# Colors
function Write-TestHeader {
    param($Message)
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host ""
}

function Write-TestSuccess {
    param($Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-TestFail {
    param($Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

function Write-TestInfo {
    param($Message)
    Write-Host "  → $Message" -ForegroundColor Yellow
}

# Test results
$script:PassCount = 0
$script:FailCount = 0
$script:TestResults = @()

function Test-Item {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    Write-TestInfo "Testing: $Name"
    try {
        $result = & $Test
        if ($result) {
            Write-TestSuccess "$Name - PASS"
            $script:PassCount++
            $script:TestResults += [PSCustomObject]@{
                Test = $Name
                Result = "PASS"
                Error = $null
            }
            return $true
        } else {
            Write-TestFail "$Name - FAIL"
            $script:FailCount++
            $script:TestResults += [PSCustomObject]@{
                Test = $Name
                Result = "FAIL"
                Error = "Test returned false"
            }
            return $false
        }
    } catch {
        Write-TestFail "$Name - ERROR: $_"
        $script:FailCount++
        $script:TestResults += [PSCustomObject]@{
            Test = $Name
            Result = "FAIL"
            Error = $_.Exception.Message
        }
        return $false
    }
}

# ============================================================================
# STEP 1: PRE-BOOT CHECKS
# ============================================================================
Write-TestHeader "STEP 1: Pre-Boot Environment Checks"

Test-Item "Python virtual environment exists" {
    Test-Path ".venv\Scripts\python.exe"
}

Test-Item "Backend directory exists" {
    Test-Path "backend"
}

Test-Item "Frontend directory exists" {
    Test-Path "frontend"
}

Test-Item ".env file exists" {
    Test-Path ".env"
}

Test-Item "Database directory exists" {
    Test-Path "databases" -PathType Container
}

Test-Item "Logs directory exists" {
    Test-Path "logs" -PathType Container
}

# ============================================================================
# STEP 2: PYTHON IMPORTS
# ============================================================================
Write-TestHeader "STEP 2: Python Module Import Tests"

Test-Item "Import backend.kernels" {
    $output = & .venv\Scripts\python.exe -c "from backend.kernels import *; print('OK')" 2>&1
    $output -match "OK"
}

Test-Item "Import backend.main" {
    $output = & .venv\Scripts\python.exe -c "from backend.main import app; print('OK')" 2>&1
    $output -match "OK"
}

Test-Item "Import backend.routes" {
    $output = & .venv\Scripts\python.exe -c "from backend.routes import kernel_gateway; print('OK')" 2>&1
    $output -match "OK"
}

Test-Item "All 9 kernels import" {
    $output = & .venv\Scripts\python.exe -c @"
from backend.kernels import (
    memory_kernel, core_kernel, code_kernel,
    governance_kernel, verification_kernel,
    intelligence_kernel, infrastructure_kernel,
    federation_kernel
)
print('OK')
"@ 2>&1
    $output -match "OK"
}

# ============================================================================
# STEP 3: START BACKEND
# ============================================================================
Write-TestHeader "STEP 3: Starting Backend Server"

Write-TestInfo "Starting backend on http://localhost:8000..."

$backendJob = Start-Job -ScriptBlock {
    param($rootPath)
    Set-Location $rootPath
    & .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
} -ArgumentList $PWD

Write-TestSuccess "Backend job started (ID: $($backendJob.Id))"

# Wait for backend
Write-TestInfo "Waiting for backend to initialize (max $Timeout seconds)..."
$waited = 0
$backendReady = $false

while ($waited -lt $Timeout) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-TestSuccess "Backend is online! (took $waited seconds)"
            break
        }
    } catch {
        Start-Sleep -Seconds 2
        $waited += 2
        if ($Verbose) {
            Write-Host "." -NoNewline
        }
    }
}

if ($Verbose) {
    Write-Host ""
}

if (-not $backendReady) {
    Write-TestFail "Backend failed to start within $Timeout seconds"
    Stop-Job -Id $backendJob.Id
    Remove-Job -Id $backendJob.Id -Force
    exit 1
}

# ============================================================================
# STEP 4: API ENDPOINT TESTS
# ============================================================================
Write-TestHeader "STEP 4: Testing API Endpoints"

Test-Item "GET /health" {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    $response.status -eq "healthy"
}

Test-Item "GET /docs (API documentation)" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET
    $response.StatusCode -eq 200
}

# ============================================================================
# STEP 5: KERNEL ENDPOINT TESTS
# ============================================================================
Write-TestHeader "STEP 5: Testing Domain Kernel Endpoints"

Test-Item "POST /kernel/memory" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/memory" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "memory"
    } catch {
        $false
    }
}

Test-Item "POST /kernel/core" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/core" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "core"
    } catch {
        $false
    }
}

Test-Item "POST /kernel/code" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/code" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "code"
    } catch {
        $false
    }
}

Test-Item "POST /kernel/governance" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/governance" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "governance"
    } catch {
        $false
    }
}

Test-Item "POST /kernel/verification" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/verification" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "verification"
    } catch {
        $false
    }
}

Test-Item "POST /kernel/intelligence" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/intelligence" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "intelligence"
    } catch {
        $false
    }
}

Test-Item "POST /kernel/infrastructure" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/infrastructure" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "infrastructure"
    } catch {
        $false
    }
}

Test-Item "POST /kernel/federation" {
    try {
        $body = @{
            intent = "Test kernel"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/kernel/federation" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        $response.kernel_name -eq "federation"
    } catch {
        $false
    }
}

# ============================================================================
# STEP 6: SUBSYSTEM STATUS CHECKS
# ============================================================================
Write-TestHeader "STEP 6: Checking Subsystem Status"

Test-Item "Health endpoint returns all systems" {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    $health.systems -ne $null
}

# ============================================================================
# CLEANUP
# ============================================================================
Write-TestHeader "CLEANUP: Stopping Backend"

Write-TestInfo "Stopping backend job..."
Stop-Job -Id $backendJob.Id
Remove-Job -Id $backendJob.Id -Force
Write-TestSuccess "Backend stopped"

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
Write-TestHeader "TEST RESULTS SUMMARY"

$totalTests = $script:PassCount + $script:FailCount
$passRate = if ($totalTests -gt 0) { [math]::Round(($script:PassCount / $totalTests) * 100, 1) } else { 0 }

Write-Host ""
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed:      $($script:PassCount)" -ForegroundColor Green
Write-Host "Failed:      $($script:FailCount)" -ForegroundColor Red
Write-Host "Pass Rate:   $passRate%" -ForegroundColor $(if ($passRate -ge 90) { 'Green' } elseif ($passRate -ge 70) { 'Yellow' } else { 'Red' })
Write-Host ""

# Show failed tests
if ($script:FailCount -gt 0) {
    Write-Host "FAILED TESTS:" -ForegroundColor Red
    $script:TestResults | Where-Object { $_.Result -eq "FAIL" } | ForEach-Object {
        Write-Host "  ✗ $($_.Test)" -ForegroundColor Red
        if ($_.Error) {
            Write-Host "    Error: $($_.Error)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

# Final verdict
if ($script:FailCount -eq 0) {
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "✅ ALL TESTS PASSED - GRACE E2E BOOT: SUCCESS" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Host "Grace is ready for production!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run the full system with:" -ForegroundColor Cyan
    Write-Host "  .\BOOT_GRACE_COMPLETE_E2E.ps1" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "=" * 80 -ForegroundColor Red
    Write-Host "❌ SOME TESTS FAILED - GRACE E2E BOOT: PARTIAL SUCCESS" -ForegroundColor Red
    Write-Host "=" * 80 -ForegroundColor Red
    Write-Host ""
    Write-Host "Review failed tests above and fix before production deployment." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
