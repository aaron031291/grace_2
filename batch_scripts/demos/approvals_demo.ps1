<#!
.SYNOPSIS
  Runs the Approvals walkthrough against a running backend.

.DESCRIPTION
  Wraps scripts/approvals_walkthrough.py for Windows. Requires GRACE_TOKEN env var to be set.

.PARAMETER BackendUrl
  Backend base URL (default http://localhost:8000)

.EXAMPLE
  .\batch_scripts\approvals_demo.ps1
  .\batch_scripts\approvals_demo.ps1 -BackendUrl http://127.0.0.1:8000

.NOTES
  Ensure the backend is running and GRACE_TOKEN is set to a valid JWT.
#>
param(
  [string]$BackendUrl = "http://localhost:8000"
)

Write-Host "Approvals Demo -- Backend: $BackendUrl" -ForegroundColor Cyan

# Verify token is present
if (-not $env:GRACE_TOKEN -or [string]::IsNullOrWhiteSpace($env:GRACE_TOKEN)) {
  Write-Host "ERROR: GRACE_TOKEN not set. Obtain a JWT via login and set GRACE_TOKEN." -ForegroundColor Red
  Write-Host "Example (PowerShell):`n  $env:GRACE_TOKEN = '<your-jwt-token>'" -ForegroundColor Yellow
  exit 1
}

# Pass backend URL to the Python script via env
$env:GRACE_BACKEND_URL = $BackendUrl

# Prefer 'py' launcher, fallback to 'python'
$pythonCmd = "py"
try {
  $pyVersion = & $pythonCmd -V 2>$null
} catch {
  $pythonCmd = "python"
}

# Run the walkthrough
$scriptPath = Join-Path $PSScriptRoot "..\scripts\approvals_walkthrough.py"
$scriptPath = (Resolve-Path $scriptPath).Path

Write-Host "Running approvals walkthrough script..." -ForegroundColor Green
& $pythonCmd $scriptPath

if ($LASTEXITCODE -ne 0) {
  Write-Host "Walkthrough exited with code $LASTEXITCODE" -ForegroundColor Yellow
  exit $LASTEXITCODE
}

Write-Host "Approvals walkthrough complete." -ForegroundColor Green
exit 0
