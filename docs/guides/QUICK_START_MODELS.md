# Quick Start - Fast Models for Grace

If Grace is too slow, start with these lightweight, fast models:

---

## FASTEST Setup (5 minutes, 7GB total)

### Step 1: Install Ollama
```bash
winget install Ollama.Ollama
```

### Step 2: Pull FAST Models (Small & Quick)
```bash
# Start Ollama
ollama serve

# Pull fast models (in order of speed)
ollama pull llama3.2:latest      # 2GB - FASTEST ⚡
ollama pull gemma2:9b            # 5GB - Very fast
```

### Step 3: Start Grace
```bash
cd C:\Users\aaron\grace_2
python serve.py
```

**Result:** Responses in 1-3 seconds! ⚡

---

## Model Speed Comparison

| Model | Size | Speed | Quality | Response Time |
|-------|------|-------|---------|---------------|
| **Llama 3.2** | 2GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | 1-2 seconds |
| **Phi-3.5** | 8GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 2-3 seconds |
| **Gemma 2 9B** | 5GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 2-4 seconds |
| Mistral Nemo | 7GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | 3-5 seconds |
| Qwen 2.5 32B | 20GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | 5-10 seconds |
| Qwen 2.5 72B | 40GB | ⚡ | ⭐⭐⭐⭐⭐ | 15-30 seconds |
| DeepSeek R1 70B | 70GB | ⚡ | ⭐⭐⭐⭐⭐ | 20-40 seconds |

---

## Optimization Tips

### 1. Use GPU (Huge Speed Boost)
If you have NVIDIA/AMD GPU:
- Ollama auto-uses GPU
- 10-20x faster than CPU
- Check: `ollama ps` to see GPU usage

### 2. Reduce Token Length
Edit `.env`:
```env
MAX_TOKENS=300  # Shorter responses = faster
```

### 3. Use Fast Model Priority
Edit `.env`:
```env
OLLAMA_MODEL=llama3.2:latest  # Fast model first
```

Grace will try this first before slower models.

### 4. Increase Timeout Threshold
For slow systems, in `backend/main.py`:
```python
timeout=20.0  # Already set - good balance
```

---

## Recommended Progressive Setup

### Week 1: Fast Models (7GB)
```bash
ollama pull llama3.2:latest
ollama pull gemma2:9b
```
**Speed:** ⚡⚡⚡⚡⚡ Very fast  
**Quality:** Good for most tasks

### Week 2: Add Balanced Model (20GB)
```bash
ollama pull qwen2.5:32b
```
**Speed:** ⚡⚡⚡ Fast enough  
**Quality:** Excellent

### Week 3: Add Specialists (29GB)
```bash
ollama pull deepseek-coder-v2:16b  # For coding
ollama pull kimi:latest             # For long context
```

### Later: Add Premium (110GB+)
```bash
ollama pull qwen2.5:72b     # Ultimate quality
ollama pull deepseek-r1:70b  # Complex reasoning
```

---

## Current Grace Configuration

Grace tries models in this order:
1. Llama 3.2 (2GB) - FASTEST ⚡
2. Phi-3.5 (8GB) - Very fast
3. Gemma 2 (5GB) - Very fast
4. Qwen 2.5 32B (20GB) - Balanced
5. Larger models if installed

**First available = first used!**

---

## Speed Troubleshooting

### Still Slow?

**Check 1: Is Ollama running?**
```bash
curl http://localhost:11434/api/tags
```
Should return list of models.

**Check 2: Is model pulled?**
```bash
ollama list
```
Should show at least llama3.2.

**Check 3: CPU vs GPU**
- CPU: 5-15 seconds (normal)
- GPU: 1-3 seconds (fast)

**Check 4: RAM**
- 8GB RAM: Use llama3.2 only
- 16GB RAM: Can use gemma2, phi3.5
- 32GB+ RAM: Can use qwen2.5:32b

---

## Emergency Fast Mode

If you need INSTANT responses right now:

### Option 1: Use Built-in Grace LLM
Stop Ollama:
```bash
# Just don't run ollama serve
```

Grace will use built-in LLM (instant, but simpler responses).

### Option 2: Use Tiny Model
```bash
ollama pull tinyllama:latest  # 600MB only
```

Super fast but basic quality.

---

## Summary

**For Speed:**
- Start with Llama 3.2 (2GB)
- Use GPU if available
- Keep responses short (300 tokens)
- Add bigger models later

**Current Grace defaults prioritize speed!**

Restart backend and Grace will be much faster! ⚡
