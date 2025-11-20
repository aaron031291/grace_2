@echo off
echo Switching Grace to mock search provider...
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    copy .env.example .env >nul 2>&1
)

REM Add or update SEARCH_PROVIDER
findstr /C:"SEARCH_PROVIDER" .env >nul 2>&1
if %errorlevel%==0 (
    echo Updating SEARCH_PROVIDER in .env...
    powershell -Command "(Get-Content .env) -replace '^SEARCH_PROVIDER=.*', 'SEARCH_PROVIDER=mock' | Set-Content .env"
) else (
    echo Adding SEARCH_PROVIDER to .env...
    echo SEARCH_PROVIDER=mock >> .env
)

echo.
echo ✅ Search provider set to mock
echo ✅ Grace will no longer hit DuckDuckGo or external APIs
echo.
echo Next steps:
echo 1. Restart Grace: python server.py
echo 2. Verify in logs: "Mock provider enabled"
echo.
echo To switch to real search later:
echo - Get Google API key from: https://console.cloud.google.com/apis/credentials
echo - Set: SEARCH_PROVIDER=google
echo - Set: GOOGLE_SEARCH_API_KEY=your-key
echo.
pause
