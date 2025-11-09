@echo off
echo Running Grace's New Systems Tests...
echo.

python -m pytest tests/test_new_systems_integration.py -v --tb=short

pause
