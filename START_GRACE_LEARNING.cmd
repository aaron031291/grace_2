@echo off
echo.
echo ========================================
echo GRACE AUTONOMOUS LEARNING SYSTEM
echo ========================================
echo.
echo Grace will learn by building real projects:
echo.
echo Priority Projects:
echo   1. CRM System (business need)
echo   2. E-commerce Analytics SaaS (business need)  
echo   3. Cloud Infrastructure from Scratch
echo.
echo Learning Method:
echo   - Uses local open-source LLMs
echo   - Builds in sandbox (safe experimentation)
echo   - Discovers edge cases autonomously
echo   - Tracks KPIs and trust scores
echo   - Records all learnings
echo.
echo ========================================
echo.
pause
echo.
echo Starting Grace backend...
python serve.py
