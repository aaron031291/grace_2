@echo off
REM Upload a book and track it through the pipeline

echo ============================================================
echo GRACE - BOOK UPLOAD AND TRACKING
echo ============================================================
echo.

if "%~1"=="" (
    echo Usage: UPLOAD_AND_TRACK.bat path\to\book.txt "Book Title" "Author Name"
    echo.
    echo Example:
    echo   UPLOAD_AND_TRACK.bat frankenstein.txt "Frankenstein" "Mary Shelley"
    echo.
    echo First, download a sample book:
    echo   curl https://www.gutenberg.org/cache/epub/84/pg84.txt -o frankenstein.txt
    echo.
    pause
    exit /b 1
)

set FILEPATH=%~1
set TITLE=%~2
set AUTHOR=%~3

if not exist "%FILEPATH%" (
    echo ❌ File not found: %FILEPATH%
    pause
    exit /b 1
)

echo 📚 Uploading: %FILEPATH%
echo    Title: %TITLE%
echo    Author: %AUTHOR%
echo.

curl -X POST http://localhost:8000/api/books/upload ^
  -F "file=@%FILEPATH%" ^
  -F "title=%TITLE%" ^
  -F "author=%AUTHOR%" ^
  -F "trust_level=high"

echo.
echo.
echo ============================================================
echo TRACKING INGESTION PIPELINE
echo ============================================================
echo.

timeout /t 2

echo [1/5] Checking book stats...
curl -s http://localhost:8000/api/books/stats
echo.
echo.

timeout /t 2

echo [2/5] Checking recent books...
curl -s http://localhost:8000/api/books/recent
echo.
echo.

timeout /t 2

echo [3/5] Checking activity...
curl -s http://localhost:8000/api/books/activity
echo.
echo.

timeout /t 2

echo [4/5] Checking self-healing (rate limits)...
curl -s http://localhost:8000/api/self-healing/stats
echo.
echo.

timeout /t 2

echo [5/5] Checking database for document...
python -c "import sys, io, sqlite3; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); conn = sqlite3.connect('databases/memory_tables.db'); cursor = conn.execute('SELECT COUNT(*) FROM memory_documents'); print(f'Total documents in DB: {cursor.fetchone()[0]}'); cursor = conn.execute('SELECT title, summary FROM memory_documents ORDER BY ROWID DESC LIMIT 1'); doc = cursor.fetchone(); print(f'\nMost recent: {doc[0] if doc else \"None\"}')"

echo.
echo.
echo ============================================================
echo Need to see the content?
echo   python query_book.py "%TITLE%"
echo.
echo Monitor logs:
echo   powershell "Get-Content logs\orchestrator.log -Tail 50 -Wait"
echo ============================================================
pause
