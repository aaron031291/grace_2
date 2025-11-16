<#!
.SYNOPSIS
  Starts the full Grace backend (uvicorn) with sensible dev defaults.

.DESCRIPTION
  Sets a development SECRET_KEY if not present and launches uvicorn on localhost:8000.
  Accepts optional DATABASE_URL and reload flag.

.PARAMETER DatabaseUrl
  Set a custom SQLAlchemy async DB URL (default uses local sqlite aiosqlite in project root).

.PARAMETER Reload
  When passed, enables --reload for automatic code reload on changes (default: true).

.EXAMPLE
  .\batch_scripts\start_full_backend.ps1
  .\batch_scripts\start_full_backend.ps1 -DatabaseUrl "sqlite+aiosqlite:///./databases/grace.db" -Reload:$false
#>
param(
  [string]$DatabaseUrl = "",
  [bool]$Reload = $true
)

if (-not $env:SECRET_KEY -or [string]::IsNullOrWhiteSpace($env:SECRET_KEY)) {
  $env:SECRET_KEY = "dev-secret-please-change"
}

if ($DatabaseUrl -and -not [string]::IsNullOrWhiteSpace($DatabaseUrl)) {
  $env:DATABASE_URL = $DatabaseUrl
}

Write-Host "Starting Grace backend..." -ForegroundColor Cyan
Write-Host " SECRET_KEY set? " ($env:SECRET_KEY -ne $null) -ForegroundColor DarkGray
if ($env:DATABASE_URL) { Write-Host " DATABASE_URL: $env:DATABASE_URL" -ForegroundColor DarkGray }

$pythonCmd = "py"
try { $null = & $pythonCmd -V 2>$null } catch { $pythonCmd = "python" }

$reloadArg = $Reload ? "--reload" : ""
& $pythonCmd -m uvicorn backend.main:app $reloadArg
