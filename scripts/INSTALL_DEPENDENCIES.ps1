# Install All Grace Dependencies
# Run this if you get "ModuleNotFoundError"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "INSTALLING GRACE DEPENDENCIES" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Write-Host "This may take 2-5 minutes..." -ForegroundColor Yellow
Write-Host ""

# Activate venv and install
& .venv\Scripts\pip install --upgrade pip
& .venv\Scripts\pip install -r backend\requirements.txt

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "DEPENDENCIES INSTALLED!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""

Write-Host "Now run:" -ForegroundColor Cyan
Write-Host "  .\START_BACKEND_SIMPLE.ps1" -ForegroundColor White
Write-Host ""
