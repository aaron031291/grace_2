@echo off
REM Auto-install all Grace models without prompts

echo ============================================================
echo GRACE MODEL AUTO-INSTALLER
echo ============================================================
echo.

echo Installing all 13 missing models...
echo This will take a while (models are large)
echo.

echo [1/13] Installing deepseek-coder-v2:16b...
ollama pull deepseek-coder-v2:16b

echo [2/13] Installing deepseek-r1:70b...
ollama pull deepseek-r1:70b

echo [3/13] Installing kimi:latest...
ollama pull kimi:latest

echo [4/13] Installing llava:34b...
ollama pull llava:34b

echo [5/13] Installing command-r-plus:latest...
ollama pull command-r-plus:latest

echo [6/13] Installing phi3.5:latest...
ollama pull phi3.5:latest

echo [7/13] Installing codegemma:7b...
ollama pull codegemma:7b

echo [8/13] Installing granite-code:20b...
ollama pull granite-code:20b

echo [9/13] Installing dolphin-mixtral:latest...
ollama pull dolphin-mixtral:latest

echo [10/13] Installing nous-hermes2-mixtral:latest...
ollama pull nous-hermes2-mixtral:latest

echo [11/13] Installing gemma2:9b...
ollama pull gemma2:9b

echo [12/13] Installing llama3.2:latest...
ollama pull llama3.2:latest

echo [13/13] Installing mistral-nemo:latest...
ollama pull mistral-nemo:latest

echo.
echo ============================================================
echo INSTALLATION COMPLETE
echo ============================================================
echo.
echo All 15 Grace models are now installed!
echo You can restart Grace: python serve.py
echo.

pause
