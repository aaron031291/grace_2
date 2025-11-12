# Restart Grace Backend Server
Write-Host "Restarting Grace Backend..." -ForegroundColor Yellow

# Find and kill process on port 8000
$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "Stopping existing server (PID: $($process.OwningProcess))..." -ForegroundColor Yellow
    Stop-Process -Id $process.OwningProcess -Force
    Start-Sleep -Seconds 2
}

# Start new server
Write-Host "Starting Grace API server..." -ForegroundColor Green
python serve.py
