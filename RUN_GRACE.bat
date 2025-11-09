@echo off
echo.
echo ========================================
echo Starting Grace Backend in PowerShell
echo ========================================
echo.

REM Run PowerShell script with proper execution policy
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0start_grace.ps1"

pause
