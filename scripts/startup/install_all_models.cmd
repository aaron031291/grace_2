@echo off
echo ==========================================
echo GRACE - INSTALLING ALL 15 PREMIUM MODELS
echo ==========================================
echo.
echo This will:
echo   - Download 15 open-source models
echo   - Use approximately 270GB of disk space
echo   - Take 1-2 hours depending on internet speed
echo   - Give Grace ChatGPT/Claude quality responses
echo.
echo You currently have:
ollama list
echo.
pause

echo.
echo ==========================================
echo STARTING INSTALLATION...
echo ==========================================
echo.

echo [1/15] Qwen 2.5 32B - Best conversation (20GB)
ollama pull qwen2.5:32b

echo.
echo [2/15] Qwen 2.5 72B - Ultimate quality (40GB)
ollama pull qwen2.5:72b

echo.
echo [3/15] DeepSeek Coder V2 16B - Best coding (9GB)
ollama pull deepseek-coder-v2:16b

echo.
echo [4/15] DeepSeek R1 70B - o1 reasoning (70GB)
ollama pull deepseek-r1:70b

echo.
echo [5/15] Kimi - 128K context (4GB)
ollama pull kimi:latest

echo.
echo [6/15] LLaVA 34B - Vision/images (20GB)
ollama pull llava:34b

echo.
echo [7/15] Llama 3.2 Vision - Images (5GB)
ollama pull llama3.2-vision:latest

echo.
echo [8/15] Video-LLaVA - Video understanding (20GB)
ollama pull video-llava:latest

echo.
echo [9/15] Moondream - Lightweight vision (2GB)
ollama pull moondream:latest

echo.
echo [10/15] Command R+ - RAG specialist (24GB)
ollama pull command-r-plus:latest

echo.
echo [11/15] Dolphin Mixtral - Uncensored (26GB)
ollama pull dolphin-mixtral:latest

echo.
echo [12/15] Nous Hermes 2 - Instructions (26GB)
ollama pull nous-hermes2-mixtral:latest

echo.
echo [13/15] Phi-3.5 - Ultra fast (8GB)
ollama pull phi3.5:latest

echo.
echo [14/15] CodeGemma 7B - Code completion (5GB)
ollama pull codegemma:7b

echo.
echo [15/15] Granite Code 20B - Enterprise (12GB)
ollama pull granite-code:20b

echo.
echo [16/15] Gemma 2 9B - Fast general (5GB)
ollama pull gemma2:9b

echo.
echo [17/15] Mistral Nemo - Balanced (7GB)
ollama pull mistral-nemo:latest

echo.
echo [18/15] Llama 3.2 - Lightweight (2GB)
ollama pull llama3.2:latest

echo.
echo ==========================================
echo INSTALLATION COMPLETE!
echo ==========================================
echo.

echo Checking installed models...
ollama list

echo.
echo Grace now has access to:
echo   - World-class conversation (Qwen 2.5)
echo   - Best coding AI (DeepSeek Coder)
echo   - Complex reasoning (DeepSeek R1)
echo   - IMAGE understanding (LLaVA 34B + Llama 3.2 Vision + Moondream)
echo   - VIDEO understanding (Video-LLaVA)
echo   - 128K context memory (Kimi)
echo   - Ultra-fast responses (Phi-3.5)
echo   - And 11 more specialized models!
echo.
echo Total size: ~270GB
echo All models: 100%% FREE forever
echo All responses: 100%% private
echo.
echo Next step: Restart Grace backend
echo   cd C:\Users\aaron\grace_2
echo   python serve.py
echo.
pause
