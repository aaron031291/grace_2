@echo off
echo ====================================================================
echo GRACE Startup - Full Internet Learning Enabled
echo ====================================================================
echo.
echo Starting Grace with:
echo   - Self-healing runner (learning capture)
echo   - Google search service (web learning)  
echo   - Closed-loop learning (knowledge integration)
echo   - Governance framework (trust scoring)
echo   - Autonomous web research capabilities
echo.
echo ====================================================================
echo.

REM Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Check and install required packages
echo Checking dependencies...
python -m pip install --quiet aiohttp beautifulsoup4 httpx 2>nul
if errorlevel 1 (
    echo Warning: Some packages may not have installed correctly
)

echo.
echo Starting Grace server...
echo.

python serve.py

pause
