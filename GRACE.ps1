#!/usr/bin/env pwsh
# PowerShell wrapper for universal grace command

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Set UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    if (-not $pythonVersion) {
        Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Run the Python grace launcher
if ($Arguments) {
    python grace $Arguments
} else {
    python grace
}

