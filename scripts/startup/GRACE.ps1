# Grace PowerShell Control Script
# Cross-platform management for Grace

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'watch', 'logs')]
    [string]$Command = 'help'
)

$GraceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $GraceDir

function Start-Grace {
    Write-Host ""
    Write-Host "Starting Grace Backend..." -ForegroundColor Green
    Write-Host ""
    
    # Clear manual shutdown flag
    @{
        manual_shutdown = $false
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        started_by = "powershell_script"
    } | ConvertTo-Json | Set-Content "grace_state.json"
    
    # Start serve.py
    Start-Process python -ArgumentList "serve.py" -NoNewWindow
    
    Write-Host "✅ Grace starting..." -ForegroundColor Green
    Write-Host "   Check status with: .\GRACE.ps1 status" -ForegroundColor Cyan
}

function Stop-Grace {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Yellow
    Write-Host "GRACE KILL SWITCH - Manual Stop" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Yellow
    Write-Host ""
    
    # Set manual shutdown flag
    @{
        manual_shutdown = $true
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        stopped_by = "kill_switch"
    } | ConvertTo-Json | Set-Content "grace_state.json"
    
    Write-Host "Stopping Grace process..." -ForegroundColor Yellow
    
    # Kill python processes running serve.py
    Get-Process python -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*serve.py*" } | 
        Stop-Process -Force
    
    Write-Host ""
    Write-Host "✅ Grace stopped (manual shutdown)" -ForegroundColor Green
    Write-Host "   Watchdog will NOT auto-restart" -ForegroundColor Cyan
    Write-Host ""
}

function Get-GraceStatus {
    Write-Host ""
    Write-Host "Grace Status" -ForegroundColor Cyan
    Write-Host "============" -ForegroundColor Cyan
    Write-Host ""
    
    # Check state file
    if (Test-Path "grace_state.json") {
        $state = Get-Content "grace_state.json" | ConvertFrom-Json
        Write-Host "State File:" -ForegroundColor White
        Write-Host "  Manual Shutdown: $($state.manual_shutdown)" -ForegroundColor $(if ($state.manual_shutdown) { "Yellow" } else { "Green" })
        Write-Host "  Last Update: $($state.timestamp)" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Check if backend is responding
    Write-Host "Backend Health:" -ForegroundColor White
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing
        Write-Host "  ✅ ALIVE on port 8000" -ForegroundColor Green
        Write-Host "  Response: $($response.Content)" -ForegroundColor Gray
    } catch {
        Write-Host "  ❌ Not responding" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Check process
    $graceProcess = Get-Process python -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*serve.py*" }
    
    if ($graceProcess) {
        Write-Host "Process:" -ForegroundColor White
        Write-Host "  PID: $($graceProcess.Id)" -ForegroundColor Green
        Write-Host "  CPU: $($graceProcess.CPU)s" -ForegroundColor Gray
        Write-Host "  Memory: $([math]::Round($graceProcess.WorkingSet64 / 1MB, 2)) MB" -ForegroundColor Gray
    } else {
        Write-Host "Process: Not running" -ForegroundColor Red
    }
    
    Write-Host ""
}

function Start-Watchdog {
    Write-Host ""
    Write-Host "Starting Grace with Watchdog Supervisor" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The watchdog will:" -ForegroundColor Cyan
    Write-Host "  ✅ Keep Grace running" -ForegroundColor White
    Write-Host "  ✅ Auto-restart on crashes" -ForegroundColor White
    Write-Host "  ✅ Respect kill switch (manual stops)" -ForegroundColor White
    Write-Host "  ✅ Log all restart events" -ForegroundColor White
    Write-Host "  ✅ Alert on failures" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    python grace_watchdog.py
}

function Show-Logs {
    Write-Host ""
    Write-Host "Recent Watchdog Logs:" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path "watchdog.log") {
        Get-Content "watchdog.log" -Tail 50
    } else {
        Write-Host "No watchdog.log found" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Execute command
switch ($Command) {
    'start'   { Start-Grace }
    'stop'    { Stop-Grace }
    'restart' { Stop-Grace; Start-Sleep -Seconds 3; Start-Grace }
    'status'  { Get-GraceStatus }
    'watch'   { Start-Watchdog }
    'logs'    { Show-Logs }
    default   { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        # Show help
        $Command = 'help'
        & $MyInvocation.MyCommand.Path 'help'
    }
}
