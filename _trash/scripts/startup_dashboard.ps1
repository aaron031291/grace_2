# Startup Dashboard - At-a-glance status
# Usage: .\scripts\startup_dashboard.ps1

$baseUrl = "http://localhost:8000"

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "GRACE STARTUP DASHBOARD" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Grace is running
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 2 -ErrorAction Stop
} catch {
    Write-Host "[ERROR] Grace is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Start with: .\GRACE.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Get dashboard data
try {
    $dashboard = Invoke-RestMethod -Uri "$baseUrl/api/startup/dashboard" -ErrorAction Stop
    
    # Boot Status
    Write-Host "BOOT STATUS" -ForegroundColor Yellow
    Write-Host "========================================================================" -ForegroundColor Gray
    
    $bootColor = switch ($dashboard.boot_status) {
        "success" { "Green" }
        "partial" { "Yellow" }
        "failed" { "Red" }
        default { "Gray" }
    }
    
    Write-Host "  Status: " -NoNewline
    Write-Host $dashboard.boot_status.ToUpper() -ForegroundColor $bootColor
    Write-Host "  Timestamp: $($dashboard.boot_timestamp)"
    
    if ($dashboard.boot_duration_ms) {
        Write-Host "  Duration: $($dashboard.boot_duration_ms)ms"
    }
    
    Write-Host ""
    
    # Active Systems
    Write-Host "ACTIVE SYSTEMS" -ForegroundColor Yellow
    Write-Host "========================================================================" -ForegroundColor Gray
    Write-Host "  Active Runs: $($dashboard.active_runs)"
    Write-Host "  Pending Approvals: $($dashboard.pending_approvals)"
    Write-Host "  Playbooks Available: $($dashboard.playbooks_available)"
    Write-Host "  Playbooks Executed Today: $($dashboard.playbooks_executed_today)"
    Write-Host ""
    
    # Metrics Health
    Write-Host "METRICS HEALTH" -ForegroundColor Yellow
    Write-Host "========================================================================" -ForegroundColor Gray
    
    $metricsColor = switch ($dashboard.metrics_health) {
        "healthy" { "Green" }
        "warning" { "Yellow" }
        "critical" { "Red" }
        default { "Gray" }
    }
    
    Write-Host "  Status: " -NoNewline
    Write-Host $dashboard.metrics_health.ToUpper() -ForegroundColor $metricsColor
    
    if ($dashboard.critical_metrics.Count -gt 0) {
        Write-Host "  Critical Metrics:"
        foreach ($metric in $dashboard.critical_metrics) {
            Write-Host "    - $metric" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    
    # Last Verification
    if ($dashboard.last_verification) {
        Write-Host "LAST VERIFICATION" -ForegroundColor Yellow
        Write-Host "========================================================================" -ForegroundColor Gray
        
        $verif = $dashboard.last_verification
        $verifColor = if ($verif.passed) { "Green" } else { "Red" }
        
        Write-Host "  Type: $($verif.type)"
        Write-Host "  Result: $($verif.result)"
        Write-Host "  Passed: " -NoNewline
        Write-Host $verif.passed -ForegroundColor $verifColor
        Write-Host "  Timestamp: $($verif.timestamp)"
        Write-Host ""
    }
    
    # Issues
    if ($dashboard.issues.Count -gt 0) {
        Write-Host "ISSUES" -ForegroundColor Red
        Write-Host "========================================================================" -ForegroundColor Gray
        foreach ($issue in $dashboard.issues) {
            Write-Host "  [!] $issue" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    # Recommendations
    if ($dashboard.recommendations.Count -gt 0) {
        Write-Host "RECOMMENDATIONS" -ForegroundColor Yellow
        Write-Host "========================================================================" -ForegroundColor Gray
        foreach ($rec in $dashboard.recommendations) {
            Write-Host "  [>] $rec" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    # Quick Links
    Write-Host "QUICK LINKS" -ForegroundColor Cyan
    Write-Host "========================================================================" -ForegroundColor Gray
    Write-Host "  API Docs:       $baseUrl/docs"
    Write-Host "  Health:         $baseUrl/health"
    Write-Host "  Active Runs:    $baseUrl/api/agent/runs/active"
    Write-Host "  Approvals:      $baseUrl/api/governance/approvals"
    Write-Host "  Metrics:        $baseUrl/api/metrics/summary"
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Could not fetch dashboard: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "API may not be fully started yet. Try again in a few seconds." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
