Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\\.venv\\Scripts\\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 5
Invoke-Expression "python .\\frontend.py"
