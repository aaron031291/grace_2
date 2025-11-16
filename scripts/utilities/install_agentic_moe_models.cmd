@echo off
REM Install Top Agentic + MoE Models for Grace

echo ============================================================
echo GRACE AGENTIC + MOE MODEL INSTALLER
echo ============================================================
echo.
echo Installing 7 additional models (~340GB total)
echo This will take a while...
echo.

echo [1/7] Installing llama3.1:70b (40GB) - Best agentic model...
ollama pull llama3.1:70b

echo.
echo [2/7] Installing nemotron:70b (40GB) - NVIDIA enterprise agent...
ollama pull nemotron:70b

echo.
echo [3/7] Installing qwen2.5-coder:32b (19GB) - Coding specialist...
ollama pull qwen2.5-coder:32b

echo.
echo [4/7] Installing mixtral:8x22b (82GB) - Best MoE reasoning...
ollama pull mixtral:8x22b

echo.
echo [5/7] Installing yi:34b (20GB) - 200K context specialist...
ollama pull yi:34b

echo.
echo [6/7] Installing mixtral:8x7b (26GB) - Efficient MoE...
ollama pull mixtral:8x7b

echo.
echo [7/7] Installing deepseek-v2.5:236b (133GB) - MoE reasoning powerhouse...
ollama pull deepseek-v2.5:236b

echo.
echo ============================================================
echo INSTALLATION COMPLETE
echo ============================================================
echo.
echo Added 7 new models:
echo   [OK] llama3.1:70b - Best agent
echo   [OK] nemotron:70b - Enterprise agent
echo   [OK] qwen2.5-coder:32b - Coding specialist
echo   [OK] mixtral:8x22b - MoE reasoning
echo   [OK] yi:34b - Long context
echo   [OK] mixtral:8x7b - Efficient MoE
echo   [OK] deepseek-v2.5:236b - MoE powerhouse
echo.
echo Grace now has 21 models total!
echo Restart Grace: python serve.py
echo.

pause
