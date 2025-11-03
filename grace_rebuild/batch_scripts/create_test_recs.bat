@echo off
echo Creating test recommendations...
curl -X POST http://localhost:8000/api/meta/test/create-samples -H "Content-Type: application/json"
echo.
echo Done! Check the Meta-Loop dashboard at http://localhost:5173
pause
