@echo off
REM One-Command Book Library Sync - Finds & Ingests Everything

echo ============================================================
echo GRACE - AUTO-SYNC COMPLETE BOOK LIBRARY
echo ============================================================
echo.
echo This will:
echo   1. Scan grace_training folder for ALL PDFs
echo   2. Detect duplicates automatically
echo   3. Ingest missing books instantly
echo   4. Extract full text + chunk + embed
echo   5. Sync to Memory Fusion
echo.
echo All automatic - just press Enter!
echo ============================================================
pause

python ingest_missing_books.py

echo.
echo ============================================================
echo LIBRARY STATUS
echo ============================================================

curl -s http://localhost:8000/api/books/stats | python -m json.tool

echo.
echo ============================================================
echo Try searching:
echo   python scripts\search_books.py "sales closing"
echo   python scripts\search_books.py "influence"  
echo   python scripts\search_books.py "Dotcom Secrets"
echo ============================================================
pause
