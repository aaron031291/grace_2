@echo off
cls
echo.
echo ====================================================================
echo INSTALL ALL 15 OPEN SOURCE MODELS FOR GRACE
echo ====================================================================
echo.
echo This will install ALL recommended models:
echo.
echo Tier 1 - Essential (69GB):
echo   1. qwen2.5:32b           - Main conversation
echo   2. deepseek-coder-v2:16b - Best coding
echo   3. qwen2.5:72b           - Ultimate quality
echo.
echo Tier 2 - Specialized (74GB):
echo   4. deepseek-r1:70b       - Complex reasoning (o1-level)
echo   5. kimi:latest           - 128K context
echo.
echo Tier 3 - Vision + Extras (137GB):
echo   6. llava:34b             - Vision + text
echo   7. command-r-plus        - RAG specialist
echo   8. dolphin-mixtral       - Uncensored
echo   9. nous-hermes2-mixtral  - Instructions
echo.
echo Tier 4 - Fast Models (33GB):
echo   10. phi3.5:latest        - Ultra fast
echo   11. codegemma:7b         - Code completion
echo   12. granite-code:20b     - Enterprise code
echo   13. gemma2:9b            - Fast general
echo   14. llama3.2:latest      - Lightweight
echo   15. mistral-nemo         - Efficient
echo.
echo Total: ~313GB (out of 1TB available)
echo.
echo This will take 2-3 hours depending on your internet speed.
echo.
echo ====================================================================
echo.
pause

echo.
echo [1/15] Installing Qwen 2.5 32B (conversation)...
ollama pull qwen2.5:32b

echo.
echo [2/15] Installing DeepSeek Coder V2 16B (coding)...
ollama pull deepseek-coder-v2:16b

echo.
echo [3/15] Installing Qwen 2.5 72B (ultimate quality)...
ollama pull qwen2.5:72b

echo.
echo [4/15] Installing DeepSeek R1 70B (reasoning)...
ollama pull deepseek-r1:70b

echo.
echo [5/15] Installing Kimi (128K context)...
ollama pull kimi:latest

echo.
echo [6/15] Installing LLaVA 34B (vision)...
ollama pull llava:34b

echo.
echo [7/15] Installing Command R+ (RAG)...
ollama pull command-r-plus:latest

echo.
echo [8/15] Installing Dolphin Mixtral (uncensored)...
ollama pull dolphin-mixtral:latest

echo.
echo [9/15] Installing Nous Hermes 2 Mixtral (instructions)...
ollama pull nous-hermes2-mixtral:latest

echo.
echo [10/15] Installing Phi 3.5 (ultra fast)...
ollama pull phi3.5:latest

echo.
echo [11/15] Installing CodeGemma 7B (code completion)...
ollama pull codegemma:7b

echo.
echo [12/15] Installing Granite Code 20B (enterprise)...
ollama pull granite-code:20b

echo.
echo [13/15] Installing Gemma 2 9B (fast general)...
ollama pull gemma2:9b

echo.
echo [14/15] Installing Llama 3.2 (lightweight)...
ollama pull llama3.2:latest

echo.
echo [15/15] Installing Mistral Nemo (efficient)...
ollama pull mistral-nemo:latest

echo.
echo ====================================================================
echo INSTALLATION COMPLETE!
echo ====================================================================
echo.
echo Grace now has 15 open source models installed:
echo.
echo   Conversation: qwen2.5:32b, qwen2.5:72b
echo   Coding: deepseek-coder-v2:16b, codegemma:7b, granite-code:20b
echo   Reasoning: deepseek-r1:70b
echo   Vision: llava:34b
echo   Long context: kimi:latest, command-r-plus
echo   Fast: phi3.5:latest, gemma2:9b, llama3.2, mistral-nemo
echo   Uncensored: dolphin-mixtral
echo   Instructions: nous-hermes2-mixtral
echo.
echo Total storage: ~313GB / 1TB available
echo.
echo Grace will automatically use the best model for each task!
echo.
echo ====================================================================
pause
