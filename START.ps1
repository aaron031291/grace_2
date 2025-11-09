# START GRACE - All import errors fixed!

Write-Host "🚀 GRACE STARTING (All fixes applied)..." -ForegroundColor Green
Write-Host ""

.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
