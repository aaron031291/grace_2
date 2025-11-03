@echo off
echo ========================================
echo Alert Severity ML Prediction Demo
echo ========================================
echo.

echo Step 1: Installing ML dependencies...
py -m pip install -q scikit-learn numpy
echo.

echo Step 2: Generating synthetic training data...
py -m backend.seed_security_events
echo.

echo Step 3: Training the ML model...
py -m backend.train_alert_model
echo.

echo Step 4: Running integration tests...
py -m backend.test_alert_ml
echo.

echo ========================================
echo Demo Complete!
echo ========================================
echo.
echo Model saved to: backend\models\alert_severity_predictor.pkl
echo.
pause
