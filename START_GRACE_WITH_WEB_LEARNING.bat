@echo off
echo ====================================================================
echo GRACE - Starting with Full Internet Learning
echo ====================================================================
echo.

REM Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Quick dependency check
python -m pip install --quiet beautifulsoup4 2>nul

python serve.py

pause
