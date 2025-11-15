# Open Source LLM Setup for Grace

Grace now supports **FREE, open-source LLMs** running locally!

---

## Option 1: Ollama (Recommended - Easiest)

### Install Ollama
```bash
# Download from https://ollama.ai
# Or with winget:
winget install Ollama.Ollama
```

### Start Ollama
```bash
ollama serve
```

### Pull a Model (Choose one)

**Llama 3.2 (Recommended - Conversational)**
```bash
ollama pull llama3.2:latest
```

**Mistral (Fast & Smart)**
```bash
ollama pull mistral:latest
```

**DeepSeek Coder (Best for Code)**
```bash
ollama pull deepseek-coder:latest
```

**CodeLlama (Code Specialist)**
```bash
ollama pull codellama:latest
```

**Phi-3 (Lightweight)**
```bash
ollama pull phi3:latest
```

### That's It!
Grace will automatically detect Ollama and use it.

**No API keys needed!**  
**100% free!**  
**Runs on your machine!**

---

## Option 2: LM Studio (GUI Alternative)

### Install
Download from: https://lmstudio.ai

### Setup
1. Open LM Studio
2. Download a model (Llama 3, Mistral, etc.)
3. Start local server (port 1234)
4. Grace will detect it automatically

---

## Option 3: Text-Generation-WebUI (Advanced)

### Install
```bash
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
pip install -r requirements.txt
```

### Run
```bash
python server.py --api
```

Grace will connect via OpenAI-compatible API.

---

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **Llama 3.2** | 3GB | Fast | Excellent | General conversation |
| **Mistral** | 4GB | Very Fast | Great | Quick responses |
| **DeepSeek Coder** | 6GB | Medium | Excellent | Code tasks |
| **CodeLlama** | 7GB | Medium | Great | Programming |
| **Phi-3** | 2GB | Very Fast | Good | Lightweight |

---

## Grace LLM Priority Order

Grace tries in this order:

1. **Ollama** (port 11434) - Open source, local, FREE ⭐
2. **OpenAI GPT-4** - If OPENAI_API_KEY set
3. **Claude 3.5** - If ANTHROPIC_API_KEY set
4. **Grace Built-in LLM** - Always available fallback

---

## Verify Ollama Works

### Test Command
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:latest",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}'
```

### Expected
```json
{
  "message": {
    "role": "assistant",
    "content": "Hello! How can I help you today?"
  }
}
```

---

## Start Grace with Ollama

### Terminal 1: Start Ollama
```bash
ollama serve
```

### Terminal 2: Start Grace Backend
```bash
cd C:\Users\aaron\grace_2
python serve.py
```

### Terminal 3: Start Frontend
```bash
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

### Test It
1. Go to http://localhost:5173
2. Click 💻 Coding Agent or 🎙️ Voice Loop
3. Chat with Grace
4. She'll use Llama 3.2 (100% open source!)

---

## Recommended Setup

**For Best Experience:**
```bash
# Install Ollama
winget install Ollama.Ollama

# Pull Llama 3.2 (conversational)
ollama pull llama3.2:latest

# Pull DeepSeek Coder (code tasks)
ollama pull deepseek-coder:6.7b

# Start Ollama
ollama serve
```

Now Grace has ChatGPT-quality conversations **completely free and private!**

---

## System Requirements

**For Ollama:**
- 8GB RAM minimum (16GB recommended)
- 4GB free disk space per model
- Windows, macOS, or Linux

**Models run on:**
- CPU (slower)
- GPU (much faster - NVIDIA, AMD, or Apple Silicon)

---

## Troubleshooting

### Ollama Not Detected
- Make sure `ollama serve` is running
- Check http://localhost:11434
- Verify model is pulled: `ollama list`

### Slow Responses
- Use smaller model (phi3, mistral)
- Enable GPU acceleration
- Reduce max_tokens

### Out of Memory
- Use phi3 (2GB) instead of llama3 (7GB)
- Close other applications
- Increase system RAM

---

## Summary

✅ **100% Free** - No API costs  
✅ **100% Private** - Runs on your machine  
✅ **ChatGPT Quality** - With Llama 3.2  
✅ **Easy Setup** - Install Ollama, pull model, done  
✅ **No API Keys** - Zero configuration needed  

**Grace prioritizes Ollama first, so you get free conversations by default!**
