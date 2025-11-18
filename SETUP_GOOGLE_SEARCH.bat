@echo off
REM Google Search API Setup Helper
REM This script helps you complete the Google Search setup

echo ========================================
echo Google Search API Setup
echo ========================================
echo.
echo Step 1: ✅ You have the API key
echo   AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
echo.
echo Step 2: Create Search Engine ID
echo   1. Open: https://programmablesearchengine.google.com/
echo   2. Click "Add" or "Create"
echo   3. Configure:
echo      - Sites to search: Leave EMPTY (search entire web)
echo      - Name: Grace Web Learning
echo      - Language: English
echo   4. Click "Create"
echo   5. Copy your Search Engine ID (looks like: a1b2c3d4e5...)
echo.
echo Step 3: Enable the API
echo   Open: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
echo   Click "Enable" if not already enabled
echo.
echo ========================================
echo.
set /p SEARCH_ENGINE_ID="Paste your Search Engine ID here: "
echo.
echo Adding to .env file...
echo.

REM Add or update the API key and Search Engine ID in .env
(
echo.
echo # Google Search API
echo GOOGLE_SEARCH_API_KEY=AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
echo GOOGLE_SEARCH_ENGINE_ID=%SEARCH_ENGINE_ID%
) >> .env

echo ✅ Configuration added to .env
echo.
echo ========================================
echo Testing configuration...
echo ========================================
echo.

python -c "import os; os.environ['GOOGLE_SEARCH_API_KEY']='AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE'; os.environ['GOOGLE_SEARCH_ENGINE_ID']='%SEARCH_ENGINE_ID%'; from backend.services.google_search_service import GoogleSearchService; import asyncio; async def test(): s = GoogleSearchService(); await s.initialize(); print('\n✅ Google Search API configured successfully!'); print('   Using Google Custom Search API\n'); asyncio.run(test())"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Now restart Grace to use Google Search API:
echo   START_GRACE.bat
echo.
pause
