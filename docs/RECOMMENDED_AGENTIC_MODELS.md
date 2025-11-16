# Recommended Agentic Open Source Models

## Currently Installed (14/15)
✅ Grace has these installed

## Additional Enterprise Agentic Models

### Tier 1: Best for Agents (Highly Recommended)

1. **llama3.1:70b** - Meta's flagship agentic model
   - Excellent tool calling
   - Strong reasoning
   - 128K context window
   - Command: `ollama pull llama3.1:70b`
   - Size: ~40GB

2. **llama3.1:405b** - Ultimate quality for agents
   - Best open source reasoning
   - Industry-leading tool use
   - 128K context
   - Command: `ollama pull llama3.1:405b`
   - Size: ~231GB (needs powerful GPU)

3. **qwen2.5-coder:32b** - Alibaba's coding specialist
   - Excellent code generation
   - Strong function calling
   - Good for coding agents
   - Command: `ollama pull qwen2.5-coder:32b`
   - Size: ~19GB

4. **nemotron:70b** - NVIDIA's enterprise agent model
   - Optimized for agentic workflows
   - Excellent instruction following
   - Strong reasoning
   - Command: `ollama pull nemotron:70b`
   - Size: ~40GB

5. **mixtral:8x22b** - Mistral's largest MoE
   - Excellent reasoning
   - 64K context
   - Strong tool use
   - Command: `ollama pull mixtral:8x22b`
   - Size: ~82GB

### Tier 2: Specialized Agentic Models

6. **yi:34b** - 01.AI's flagship
   - Underrated for agents
   - 200K context window
   - Strong reasoning
   - Command: `ollama pull yi:34b`
   - Size: ~20GB

7. **wizardlm2:8x22b** - WizardLM flagship
   - Designed for complex instructions
   - Multi-step reasoning
   - Excellent for autonomous tasks
   - Command: `ollama pull wizardlm2:8x22b`
   - Size: ~82GB

8. **aya:35b** - Cohere's multilingual agent
   - 101 languages
   - Strong instruction following
   - Good for global deployments
   - Command: `ollama pull aya:35b`
   - Size: ~20GB

9. **solar:10.7b** - Upstage's efficient model
   - Depth upscaling
   - Excellent performance/size ratio
   - Good for resource-constrained agents
   - Command: `ollama pull solar:10.7b`
   - Size: ~6.1GB

10. **openhermes:13b** - Teknium's instruction model
    - Fine-tuned for agents
    - Strong tool use
    - Based on Mistral
    - Command: `ollama pull openhermes:13b`
    - Size: ~7.4GB

### Tier 3: Specialized Use Cases

11. **starcoder2:15b** - BigCode's coding model
    - Excellent code completion
    - 16K context
    - Good for coding agents
    - Command: `ollama pull starcoder2:15b`
    - Size: ~9GB

12. **dolphin2.9:llama3.1-70b** - Uncensored Llama 3.1
    - No restrictions
    - Full agentic capabilities
    - Based on Llama 3.1 70b
    - Command: `ollama pull dolphin2.9-llama3.1:70b`
    - Size: ~40GB

13. **nous-hermes2:34b** - Nous Research's Yi-based
    - Excellent instruction following
    - 200K context
    - Strong multi-step reasoning
    - Command: `ollama pull nous-hermes2:34b`
    - Size: ~20GB

14. **openchat:7b** - Fine-tuned Mistral
    - Optimized for conversations
    - Good agentic behavior
    - Very efficient
    - Command: `ollama pull openchat:7b`
    - Size: ~4.1GB

15. **vicuna:33b** - LMSYS's instruction model
    - Strong conversation
    - Good tool use
    - Based on Llama
    - Command: `ollama pull vicuna:33b`
    - Size: ~19GB

## Recommended Addition Strategy

### For Maximum Agentic Power (Add These 5)
1. **llama3.1:70b** - Best overall agent model
2. **nemotron:70b** - Enterprise-grade agent
3. **qwen2.5-coder:32b** - Coding specialist
4. **mixtral:8x22b** - Strong reasoning
5. **yi:34b** - Long context specialist

**Total added size: ~201GB**

### For Balanced Performance (Add These 3)
1. **llama3.1:70b** - Best agent
2. **solar:10.7b** - Efficient
3. **openhermes:13b** - Tool specialist

**Total added size: ~53GB**

### Quick Install Commands

```bash
# Maximum power (5 models)
ollama pull llama3.1:70b
ollama pull nemotron:70b
ollama pull qwen2.5-coder:32b
ollama pull mixtral:8x22b
ollama pull yi:34b

# Balanced (3 models)
ollama pull llama3.1:70b
ollama pull solar:10.7b
ollama pull openhermes:13b
```

## Model Capabilities Comparison

### Best for:
- **Autonomous Reasoning**: llama3.1:405b, nemotron:70b, mixtral:8x22b
- **Tool Calling**: llama3.1:70b, qwen2.5-coder:32b
- **Code Generation**: deepseek-coder-v2:16b (installed), qwen2.5-coder:32b
- **Long Context**: yi:34b (200K), llama3.1:70b (128K)
- **Efficiency**: solar:10.7b, phi3.5 (installed), openchat:7b
- **Multi-step Planning**: wizardlm2:8x22b, nemotron:70b
- **Function Calling**: llama3.1:70b, qwen2.5-coder:32b
- **Uncensored**: dolphin-mixtral (installed), dolphin2.9-llama3.1:70b

## Current Grace Status

**Models Installed: 14**
- ✅ qwen2.5:32b, qwen2.5:72b
- ✅ deepseek-coder-v2:16b, deepseek-r1:70b
- ✅ llava:34b (vision)
- ✅ command-r-plus (RAG)
- ✅ phi3.5 (fast)
- ✅ codegemma:7b, granite-code:20b
- ✅ dolphin-mixtral, nous-hermes2-mixtral
- ✅ gemma2:9b, llama3.2, mistral-nemo

**Recommended Next Additions:**
1. llama3.1:70b (essential for agents)
2. qwen2.5-coder:32b (coding specialist)
3. nemotron:70b (enterprise agent)

**Total Storage Available: 1TB**
**Currently Used: ~213GB**
**Remaining: ~787GB** - Plenty for more models!
