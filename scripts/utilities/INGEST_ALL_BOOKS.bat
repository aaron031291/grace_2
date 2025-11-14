@echo off
REM Ingest all 13 business intelligence books

echo ============================================================
echo GRACE - BUSINESS INTELLIGENCE BOOK INGESTION
echo ============================================================
echo.
echo This will ingest 13 business/marketing books:
echo   - Dotcom Secrets
echo   - The Lean Startup
echo   - Traffic Secrets
echo   - 5 Dysfunctions
echo   - Corporate Finance
echo   - $100M Playbooks (x5)
echo   + more
echo.
echo Total: ~50MB of business knowledge
echo Time: ~20-30 minutes
echo.
echo ============================================================

pause

echo.
echo Starting batch ingestion...
echo.

python scripts\ingest_pdf_batch.py "business intelligence" --delay 5

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! All books ingested.
    echo ============================================================
    echo.
    echo Query your knowledge:
    echo   python query_book.py
    echo   python query_book.py "marketing"
    echo   python query_book.py "sales"
    echo.
) else (
    echo.
    echo ============================================================
    echo FAILED - Check errors above
    echo ============================================================
    echo.
)

pause
