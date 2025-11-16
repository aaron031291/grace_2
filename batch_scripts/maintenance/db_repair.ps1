<#
.SYNOPSIS
  Repairs (or rebuilds) the local development database and applies Alembic migrations.

.DESCRIPTION
  Windows-friendly helper to:
   - Optionally delete the dev SQLite database file (clean rebuild)
   - Ensure Python/Alembic are available
   - Set DATABASE_URL if provided
   - Run `alembic upgrade head`

.PARAMETER Clean
  When passed, deletes the SQLite file before migrating (default: false).

.PARAMETER DatabaseUrl
  Custom SQLAlchemy async DB URL. Defaults to sqlite+aiosqlite:///./databases/grace.db

.EXAMPLE
  .\batch_scripts\db_repair.ps1

.EXAMPLE
  .\batch_scripts\db_repair.ps1 -Clean -DatabaseUrl "sqlite+aiosqlite:///./databases/grace.db"

.NOTES
  Close any running backend/tests that may be holding a lock on the SQLite file.
#>
param(
  [switch]$Clean = $false,
  [string]$DatabaseUrl = ""
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host $msg -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host $msg -ForegroundColor Red }

# Determine project root (this script is under batch_scripts)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $RepoRoot

# Default DB URL if not provided
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
  $DatabaseUrl = "sqlite+aiosqlite:///./databases/grace.db"
}

Write-Info "DB Repair — Using DATABASE_URL: $DatabaseUrl"
$env:DATABASE_URL = $DatabaseUrl

# Ensure Alembic is installed
$pythonCmd = "py"
try { $null = & $pythonCmd -V 2>$null } catch { $pythonCmd = "python" }

Write-Info "Ensuring Alembic is installed..."
& $pythonCmd -m pip install --quiet --upgrade pip | Out-Null
& $pythonCmd -m pip install --quiet alembic | Out-Null

# Optionally delete the SQLite file when using the default URL
if ($Clean.IsPresent) {
  try {
    if ($DatabaseUrl.StartsWith("sqlite+aiosqlite")) {
      $path = $DatabaseUrl -replace "^sqlite\+aiosqlite:///", ""
      $path = $path -replace "/", "\"  # normalize
      $dbPath = Resolve-Path -ErrorAction SilentlyContinue $path
      if ($dbPath) {
        Write-Warn "Deleting DB file: $($dbPath.Path)"
        Remove-Item -Force $dbPath.Path
      } else {
        Write-Warn "DB file not found (ok): $path"
      }
    } else {
      Write-Warn "Clean option ignored for non-sqlite DATABASE_URL"
    }
  } catch {
    Write-Err "Failed to delete DB file: $($_.Exception.Message)"
  }
}

# Apply migrations
try {
  Write-Info "Running Alembic upgrade head..."
  & alembic upgrade head
  if ($LASTEXITCODE -ne 0) {
    throw "Alembic failed with exit code $LASTEXITCODE"
  }
  Write-Host "✓ Migrations applied successfully." -ForegroundColor Green
} catch {
  Write-Err "Alembic migration failed: $($_.Exception.Message)"
  exit 1
}

Write-Info "Next steps:"
Write-Host "  1) Start backend:  set SECRET_KEY=dev-secret-please-change; py -m uvicorn backend.main:app --reload" -ForegroundColor DarkGray
Write-Host "  2) (Optional) Run tests:  py -m pytest -q backend\tests\routes\test_approvals.py" -ForegroundColor DarkGray
exit 0
