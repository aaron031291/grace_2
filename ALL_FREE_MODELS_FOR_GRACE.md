# All Free Open-Source Models for Grace

With 1TB storage, you can install ALL the best models! Here's the complete list:

---

## Current Grace Setup

**Already Configured:**
1. Qwen 2.5 32B - Best reasoning (20GB) ⭐
2. DeepSeek Coder V2 16B - Best coding (9GB) ⭐
3. Kimi - Long context 128K (4GB) ⭐
4. Llama 3.2 - Fast fallback (2GB)

**Total: 35GB**

---

## Additional FREE Models to Enhance Grace

### 1. Reasoning & Math Specialist
**DeepSeek R1** (NEW - o1 competitor)
```bash
ollama pull deepseek-r1:latest
```
- Size: ~70GB (multiple variants available)
- Best for: Complex reasoning, math, logic
- Shows thinking process like o1
- **Beats o1 on some benchmarks!**

---

### 2. Multi-Modal (Vision + Text)
**LLaVA 34B** (See images + chat)
```bash
ollama pull llava:34b
```
- Size: ~20GB
- Best for: Image analysis, visual tasks
- Can see screenshots, diagrams, photos
- Integrates with Grace's librarian

---

### 3. Long Context Champion
**Command R+** (Cohere's model)
```bash
ollama pull command-r-plus:latest
```
- Size: ~24GB
- Context: 128K tokens
- Best for: Long documents, research
- Excellent retrieval-augmented generation (RAG)

---

### 4. Fast & Efficient
**Phi-3.5 Medium** (Microsoft)
```bash
ollama pull phi3.5:latest
```
- Size: ~8GB
- Speed: Ultra fast
- Quality: Excellent for size
- Best for: Quick responses, low latency

---

### 5. Coding Alternatives
**CodeGemma 7B** (Google)
```bash
ollama pull codegemma:7b
```
- Size: ~5GB
- Best for: Code completion, debugging
- Trained by Google on code

**Granite Code 20B** (IBM)
```bash
ollama pull granite-code:20b
```
- Size: ~12GB
- Enterprise-grade code model
- Multiple languages

---

### 6. Uncensored/Unrestricted
**Dolphin Mixtral** (No guardrails)
```bash
ollama pull dolphin-mixtral:latest
```
- Size: ~26GB
- Uncensored, no restrictions
- Best for: Technical tasks without limits

---

### 7. Chinese + English Bilingual
**Qwen 2.5 72B** (Ultimate version)
```bash
ollama pull qwen2.5:72b
```
- Size: ~40GB
- Best overall open-source model
- Beats GPT-4 Turbo on benchmarks
- Bilingual excellence

---

### 8. Scientific & Academic
**WizardLM 2** (Research specialist)
```bash
ollama pull wizardlm2:latest
```
- Size: ~40GB
- Best for: Academic writing, research
- Complex reasoning

---

### 9. Tiny but Mighty
**Gemma 2 9B** (Google)
```bash
ollama pull gemma2:9b
```
- Size: ~5GB
- Surprisingly good for size
- Very fast responses

---

### 10. Specialist Models

**Nous Hermes 2 Mixtral** (Instruction following)
```bash
ollama pull nous-hermes2-mixtral:latest
```
- Size: ~26GB
- Excellent at following complex instructions

**Mistral Nemo** (Latest Mistral)
```bash
ollama pull mistral-nemo:latest
```
- Size: ~7GB
- Fast, efficient, great quality

**Solar 10.7B** (High performance)
```bash
ollama pull solar:latest
```
- Size: ~6GB
- Excellent quality/size ratio

---

## Recommended Full Setup for Grace (1TB)

### Tier 1: Essential (69GB)
```bash
ollama pull qwen2.5:32b              # 20GB - Main conversation
ollama pull deepseek-coder-v2:16b   # 9GB - Coding
ollama pull qwen2.5:72b              # 40GB - Ultra mode
```

### Tier 2: Specialized (74GB)
```bash
ollama pull kimi:latest              # 4GB - Long context
ollama pull deepseek-r1:70b          # 70GB - Reasoning/math
```

### Tier 3: Vision & Extras (90GB)
```bash
ollama pull llava:34b                # 20GB - Vision
ollama pull command-r-plus:latest    # 24GB - RAG specialist
ollama pull dolphin-mixtral:latest   # 26GB - Uncensored
ollama pull nous-hermes2-mixtral     # 26GB - Instructions
```

**Total: ~233GB** (Still 767GB free!)

---

## Grace's Smart Routing

With all models installed, Grace will:

**Code Questions** → DeepSeek Coder V2
**Math/Reasoning** → DeepSeek R1 or Qwen 72B
**Long Conversations** → Kimi (128K context)
**Image Analysis** → LLaVA 34B
**General Chat** → Qwen 2.5 32B
**Fast Responses** → Phi-3.5 or Gemma 2
**Research Tasks** → Command R+
**Complex Instructions** → Nous Hermes 2

---

## Update Grace's Configuration

**Edit `.env`:**
```env
# Conversation models (priority order)
OLLAMA_MODEL=qwen2.5:32b
OLLAMA_REASONING_MODEL=deepseek-r1:70b
OLLAMA_CODING_MODEL=deepseek-coder-v2:16b
OLLAMA_VISION_MODEL=llava:34b
OLLAMA_LONG_CONTEXT_MODEL=kimi:latest
```

---

## Model Size Reference

| Model | Size | Use Case |
|-------|------|----------|
| Qwen 2.5 72B | 40GB | Ultimate quality |
| Qwen 2.5 32B | 20GB | Best conversation ⭐ |
| DeepSeek R1 70B | 70GB | Complex reasoning |
| DeepSeek Coder V2 16B | 9GB | Best coding ⭐ |
| LLaVA 34B | 20GB | Vision + text |
| Command R+ | 24GB | Long docs/RAG |
| Dolphin Mixtral | 26GB | Uncensored |
| Nous Hermes 2 | 26GB | Instructions |
| Kimi | 4GB | 128K context ⭐ |
| Phi-3.5 | 8GB | Ultra fast |
| CodeGemma | 5GB | Code completion |
| Granite Code 20B | 12GB | Enterprise code |
| Gemma 2 9B | 5GB | General fast |
| Llama 3.2 3B | 2GB | Lightweight ⭐ |

---

## Complete Install Script

Save as `install_all_models.cmd`:

```bash
@echo off
echo Installing ALL premium models for Grace...
echo This will take 1-2 hours and use ~270GB
echo.
pause

ollama pull qwen2.5:32b
ollama pull qwen2.5:72b
ollama pull deepseek-coder-v2:16b
ollama pull deepseek-r1:70b
ollama pull kimi:latest
ollama pull llava:34b
ollama pull command-r-plus:latest
ollama pull dolphin-mixtral:latest
ollama pull nous-hermes2-mixtral
ollama pull phi3.5:latest
ollama pull codegemma:7b
ollama pull granite-code:20b
ollama pull gemma2:9b
ollama pull llama3.2:latest
ollama pull mistral-nemo:latest

echo.
echo Complete! Grace now has 15 models installed!
echo Total size: ~270GB
echo Remaining: ~730GB
pause
```

---

## Benefits for Grace

**With all models, Grace gets:**

✅ **World-class coding** - DeepSeek Coder V2  
✅ **GPT-4 Turbo level reasoning** - Qwen 2.5 72B  
✅ **Complex math/logic** - DeepSeek R1  
✅ **Vision capabilities** - LLaVA (see images)  
✅ **128K context** - Kimi (long conversations)  
✅ **Fast responses** - Phi-3.5 (<1 second)  
✅ **Uncensored mode** - Dolphin (no limits)  
✅ **RAG specialist** - Command R+  
✅ **All 100% FREE!**  
✅ **All 100% private!**  
✅ **No API costs ever!**

---

## Recommended Quick Start

**Best 5 Models (99GB):**
```bash
ollama pull qwen2.5:32b          # Conversation
ollama pull deepseek-coder-v2:16b # Code
ollama pull deepseek-r1:70b       # Reasoning
ollama pull kimi:latest           # Long context
ollama pull llava:34b             # Vision
```

This gives you:
- ChatGPT-4 quality
- Best coding model available
- Complex reasoning (o1 level)
- Long conversation memory
- Image understanding

**All free, all local, better than most paid APIs!**

---

## Start Grace with All Models

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Grace Backend
cd C:\Users\aaron\grace_2
python serve.py

# Terminal 3: Frontend
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

Grace will automatically detect and use the best available model for each task!
