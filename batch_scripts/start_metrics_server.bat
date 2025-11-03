@echo off
echo ================================================================================
echo Grace Metrics API Server
echo ================================================================================
echo.
echo Starting standalone metrics server...
echo This runs independently of the main Grace backend
echo.
echo API will be available at: http://localhost:8001
echo Documentation at: http://localhost:8001/docs
echo.
echo Press CTRL+C to stop
echo.
echo ================================================================================
echo.

uvicorn backend.metrics_server:app --host 0.0.0.0 --port 8001 --reload
