@echo off
echo ======================================
echo IDE WebSocket Integration Test
echo ======================================
echo.

echo Starting Backend Server...
echo Run this in a separate terminal:
echo   cd grace_rebuild
echo   python -m uvicorn backend.main:app --reload
echo.

echo Then run tests:
echo   pytest tests/test_ide_websocket.py -v
echo.

echo Or open browser test:
echo   http://localhost:8000/static/test_ide.html
echo.

pause
