# Tail Grace logs with jq filtering
# Usage: .\scripts\tail_logs.ps1 [-Subsystem "agentic_spine"] [-RunId "run_abc123"]

param(
    [string]$Subsystem = "",
    [string]$RunId = "",
    [switch]$Errors
)

$logFile = "logs\backend.log"

if (-not (Test-Path $logFile)) {
    Write-Host "[ERROR] Log file not found: $logFile" -ForegroundColor Red
    exit 1
}

# Check if jq is available
try {
    $jqVersion = & jq --version 2>$null
} catch {
    Write-Host "[WARN] jq not installed. Install from: https://stedolan.github.io/jq/" -ForegroundColor Yellow
    Write-Host "[INFO] Showing raw logs instead..." -ForegroundColor Yellow
    Get-Content $logFile -Wait -Tail 20
    exit 0
}

# Build jq filter
$filter = ""

if ($Subsystem) {
    $filter += "select(.subsystem == \`"$Subsystem\`") | "
}

if ($RunId) {
    $filter += "select(.run_id == \`"$RunId\`") | "
}

if ($Errors) {
    $filter += "select(.level == \`"ERROR\`" or .level == \`"CRITICAL\`") | "
}

# Default output format
$filter += '"\(.[\"timestamp\"]) [\(.level)] \(.subsystem // \"system\") \(.event_type // \"log\") => \(.message)"'

Write-Host "Tailing logs with filter..." -ForegroundColor Cyan
if ($Subsystem) { Write-Host "  Subsystem: $Subsystem" -ForegroundColor Yellow }
if ($RunId) { Write-Host "  Run ID: $RunId" -ForegroundColor Yellow }
if ($Errors) { Write-Host "  Errors only: Yes" -ForegroundColor Yellow }
Write-Host ""

# Tail and pipe through jq
Get-Content $logFile -Wait -Tail 20 | ForEach-Object {
    $_ | jq -r $filter 2>$null
}
