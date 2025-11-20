# Check correlation IDs in logs and timeline
# Usage: .\scripts\check_correlations.ps1 -RunId "run_abc123"

param(
    [Parameter(Mandatory=$true)]
    [string]$RunId
)

$baseUrl = "http://localhost:8000"

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "CORRELATION CHECK: $RunId" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Get timeline from API
Write-Host "[1/3] Fetching timeline from API..." -ForegroundColor Yellow

try {
    $timeline = Invoke-RestMethod -Uri "$baseUrl/api/agent/runs/$RunId/timeline" -Method GET
    
    Write-Host "  Run Status: $($timeline.run.status)" -ForegroundColor Green
    Write-Host "  Steps: $($timeline.steps.Count)" -ForegroundColor Green
    Write-Host "  Correlated Logs: $($timeline.log_entries)" -ForegroundColor Green
    
} catch {
    Write-Host "  [FAIL] Could not fetch timeline: $_" -ForegroundColor Red
    exit 1
}

# 2. Check logs for run_id
Write-Host ""
Write-Host "[2/3] Searching logs for run_id=$RunId..." -ForegroundColor Yellow

$logFile = "logs\backend.log"

if (-not (Test-Path $logFile)) {
    Write-Host "  [FAIL] Log file not found" -ForegroundColor Red
    exit 1
}

$logEntries = Get-Content $logFile | Where-Object { $_ -match $RunId }

Write-Host "  Found: $($logEntries.Count) log entries" -ForegroundColor Green

# 3. Show timeline steps
Write-Host ""
Write-Host "[3/3] Timeline Steps:" -ForegroundColor Yellow

foreach ($step in $timeline.steps) {
    $status = switch ($step.status) {
        "success" { "[OK]" }
        "failed" { "[FAIL]" }
        "running" { "[RUN]" }
        default { "[$($step.status)]" }
    }
    
    $duration = if ($step.duration_ms) { "$($step.duration_ms)ms" } else { "-" }
    
    Write-Host "  $status $($step.step_type) - $($step.description) ($duration)" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "Use: .\scripts\tail_logs.ps1 -RunId $RunId" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
