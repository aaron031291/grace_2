# Start Grace Backend Server
Write-Host "Starting Grace API Server..." -ForegroundColor Green
Write-Host ""

# Check if port 8000 is already in use
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "ERROR: Port 8000 is already in use!" -ForegroundColor Red
    Write-Host "Run this to kill the process:" -ForegroundColor Yellow
    Write-Host "  taskkill /PID $($port8000.OwningProcess) /F"
    exit 1
}

# Start the server
python backend/unified_grace_orchestrator.py --serve
