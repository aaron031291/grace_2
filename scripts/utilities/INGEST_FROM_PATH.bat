@echo off
REM Ingest PDFs from a specific path

echo ============================================================
echo GRACE - PDF INGESTION FROM CUSTOM PATH
echo ============================================================
echo.

if "%~1"=="" (
    echo Please provide the folder path containing your PDFs
    echo.
    echo Usage:
    echo   INGEST_FROM_PATH.bat "C:\path\to\folder"
    echo.
    echo Example:
    echo   INGEST_FROM_PATH.bat "C:\Users\aaron\Documents\grace code\iCloudDrive\Downloads\16_10_25\grace\business intelligence"
    echo.
    pause
    exit /b 1
)

set FOLDER=%~1

echo Folder: %FOLDER%
echo.

if not exist "%FOLDER%" (
    echo ERROR: Folder not found!
    echo.
    echo Please check the path and try again.
    pause
    exit /b 1
)

echo Listing PDFs in folder...
dir "%FOLDER%\*.pdf"
echo.

echo Starting ingestion...
echo.

python scripts\ingest_pdf_batch.py "%FOLDER%" --delay 3

pause
