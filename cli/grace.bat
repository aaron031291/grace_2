@echo off
REM Grace CLI wrapper for Windows

REM Find Grace root directory
set GRACE_ROOT=%~dp0

REM Activate virtual environment if it exists
if exist "%GRACE_ROOT%.venv\Scripts\activate.bat" (
    call "%GRACE_ROOT%.venv\Scripts\activate.bat"
) else if exist "%GRACE_ROOT%venv\Scripts\activate.bat" (
    call "%GRACE_ROOT%venv\Scripts\activate.bat"
)

REM Run the orchestrator
python -m backend.unified_grace_orchestrator %*


