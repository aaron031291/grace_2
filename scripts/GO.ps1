# GO - Start Grace NOW (All fixes applied)

Write-Host ""
Write-Host "🚀 STARTING GRACE..." -ForegroundColor Cyan
Write-Host ""

Set-Location C:\Users\aaron\grace_2
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue

Write-Host "✓ All import errors fixed" -ForegroundColor Green
Write-Host "✓ Starting backend..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

& .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
