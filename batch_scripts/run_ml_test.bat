@echo off
echo ========================================
echo ML Deployment & Auto-Retrain Test
echo ========================================
echo.
cd grace_rebuild\backend
python3 -m pytest test_ml_deployment.py -v -s
pause
