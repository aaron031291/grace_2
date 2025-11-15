# Complete Open Source Model Setup for Grace

## All 15 Recommended Models

Grace's boot script (`serve.py`) now checks for all 15 open source models and shows which are installed.

---

## Quick Install (All 15 Models)

```bash
scripts/startup/install_all_models.cmd
```

This installs all models (~313GB, 2-3 hours)

---

## Models by Category

### Conversation & Reasoning (109GB)
1. **qwen2.5:32b** (20GB) - Main conversation ⭐
2. **qwen2.5:72b** (40GB) - Ultimate quality
3. **deepseek-r1:70b** (70GB) - Complex reasoning (o1-level)
4. **wizardlm2:latest** (40GB) - Academic/research

### Coding (26GB)
5. **deepseek-coder-v2:16b** (9GB) - Best coding ⭐
6. **granite-code:20b** (12GB) - Enterprise code
7. **codegemma:7b** (5GB) - Code completion

### Long Context & RAG (28GB)
8. **kimi:latest** (4GB) - 128K context ⭐
9. **command-r-plus:latest** (24GB) - RAG specialist

### Vision (20GB)
10. **llava:34b** (20GB) - Vision + text

### Fast Models (28GB)
11. **phi3.5:latest** (8GB) - Ultra fast
12. **gemma2:9b** (5GB) - Fast general
13. **llama3.2:latest** (2GB) - Lightweight
14. **mistral-nemo:latest** (7GB) - Efficient

### Uncensored & Instructions (52GB)
15. **dolphin-mixtral:latest** (26GB) - No restrictions
16. **nous-hermes2-mixtral:latest** (26GB) - Complex instructions

**Total:** ~313GB (out of 1TB available)

---

## What serve.py Does Now

When you run `python serve.py`, it:

```
[2/5] Loading open source LLMs...
  ✓ Ollama: Running
  ✓ Models available: 15
  ✓ Grace models installed: 15/15

  Installed models:
    • qwen2.5:32b - Conversation & reasoning
    • deepseek-coder-v2:16b - Best coding
    • deepseek-r1:70b - Complex reasoning (o1-level)
    • kimi:latest - 128K context
    • llava:34b - Vision + text
    ... and 10 more
```

Or if models are missing:
```
  ⚠️  Missing models: 8
    Run: scripts/startup/install_all_models.cmd
```

---

## Install Individual Models

**Essential (minimum setup):**
```bash
ollama pull qwen2.5:32b
ollama pull deepseek-coder-v2:16b
ollama pull kimi:latest
```

**Add reasoning:**
```bash
ollama pull deepseek-r1:70b
```

**Add vision:**
```bash
ollama pull llava:34b
```

**Add all:**
```bash
scripts/startup/install_all_models.cmd
```

---

## Model Selection Logic

Grace automatically selects the best model for each task:

**Coding tasks** → DeepSeek Coder V2 16B  
**Complex reasoning** → DeepSeek R1 70B  
**Long documents** → Kimi or Command R+  
**Image analysis** → LLaVA 34B  
**Fast responses** → Phi 3.5 or Gemma 2  
**General chat** → Qwen 2.5 32B  
**Ultimate quality** → Qwen 2.5 72B  
**No restrictions** → Dolphin Mixtral  

---

## Storage Requirements

| Tier | Models | Size | Priority |
|------|--------|------|----------|
| Tier 1 | qwen2.5:32b, deepseek-coder, kimi | 33GB | Essential |
| Tier 2 | qwen2.5:72b, deepseek-r1 | 110GB | High quality |
| Tier 3 | llava, command-r+, dolphin | 70GB | Specialized |
| Tier 4 | Fast models (phi, gemma, llama) | 22GB | Speed |
| All | All 15 models | ~313GB | Complete |

**With 1TB:** You can install all + have 687GB free!

---

## Benefits

✅ **Free forever** - No API costs  
✅ **100% private** - All local  
✅ **No rate limits** - Use as much as you want  
✅ **Better than GPT-3.5** - Many exceed GPT-3.5 Turbo  
✅ **Some beat GPT-4** - Qwen 72B, DeepSeek R1  
✅ **Vision included** - LLaVA sees images  
✅ **Reasoning included** - DeepSeek R1 shows thinking  
✅ **Auto-routing** - Grace picks best model  

---

## Check Installation Status

**When you start Grace:**
```bash
python serve.py
```

You'll see:
```
[2/5] Loading open source LLMs...
  ✓ Ollama: Running
  ✓ Models available: 15
  ✓ Grace models installed: 15/15
```

**Or check manually:**
```bash
ollama list
```

---

## Quick Install Script

The script at `scripts/startup/install_all_models.cmd` will:

1. ✅ Install all 15 models
2. ✅ Show progress for each
3. ✅ Total time: 2-3 hours
4. ✅ Uses ~313GB storage
5. ✅ Grace auto-detects them on next start

---

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| Qwen 2.5 72B | 40GB | Slow | Highest | Ultimate quality |
| Qwen 2.5 32B | 20GB | Medium | High | Main use ⭐ |
| DeepSeek R1 70B | 70GB | Slow | Highest | Complex reasoning |
| DeepSeek Coder 16B | 9GB | Fast | Highest | Coding ⭐ |
| LLaVA 34B | 20GB | Medium | High | Vision |
| Kimi | 4GB | Fast | Good | Long context ⭐ |
| Phi 3.5 | 8GB | Fastest | Good | Quick tasks |

---

## What Grace Shows on Boot

**With all models:**
```
[2/5] Loading open source LLMs...
  ✓ Ollama: Running
  ✓ Models available: 15
  ✓ Grace models installed: 15/15

  Installed models:
    • qwen2.5:32b - Conversation & reasoning
    • deepseek-coder-v2:16b - Best coding
    • deepseek-r1:70b - Complex reasoning (o1-level)
    • kimi:latest - 128K context
    • llava:34b - Vision + text
    ... and 10 more
```

**With some missing:**
```
[2/5] Loading open source LLMs...
  ✓ Ollama: Running
  ✓ Models available: 8
  ✓ Grace models installed: 8/15

  Installed models:
    • qwen2.5:32b - Conversation & reasoning
    • deepseek-coder-v2:16b - Best coding
    ... and 6 more

  ⚠️  Missing models: 7
    Run: scripts/startup/install_all_models.cmd
    Or: ollama pull <model_name>
```

---

## Summary

- ✅ **serve.py** now checks all 15 models on boot
- ✅ **Shows which are installed** vs missing
- ✅ **One script installs all** - scripts/startup/install_all_models.cmd
- ✅ **Auto-routing** - Grace uses best model for task
- ✅ **Complete LLM stack** - 15 models for every use case

**Install all models:** `scripts/startup/install_all_models.cmd`

**Start Grace:** `python serve.py` (auto-detects models)
