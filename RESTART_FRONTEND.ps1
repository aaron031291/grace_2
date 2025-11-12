# Restart Frontend Server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Grace Frontend Restart Script" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop all node processes (frontend dev servers)
Write-Host "Stopping existing frontend servers..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.Name -like '*node*'} | ForEach-Object {
    Write-Host "  Stopping process: $($_.Id) - $($_.Name)" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Starting frontend dev server..." -ForegroundColor Green
Write-Host ""

# Change to frontend directory and start dev server
Set-Location "c:/Users/aaron/grace_2/frontend"

# Start npm dev server
Write-Host "Running: npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "Once you see 'ready in Xms', open your browser to:" -ForegroundColor Yellow
Write-Host "  http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Then:" -ForegroundColor Yellow
Write-Host "  1. Press Ctrl+Shift+R to hard refresh" -ForegroundColor White
Write-Host "  2. Click '📁 Memory' button" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

npm run dev
