@echo off
echo Starting Grace Metrics Server...
echo Server will run on http://localhost:8001
echo Press CTRL+C to stop
echo.
uvicorn backend.simple_metrics_server:app --host 127.0.0.1 --port 8001 --reload
