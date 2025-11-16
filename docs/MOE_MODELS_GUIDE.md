# Mixture of Experts (MoE) Models for Grace

## What is MoE?
Mixture of Experts uses multiple specialized "expert" neural networks, activating only relevant experts per token. This gives **huge model capacity** with **lower compute cost**.

## Best Open Source MoE Models

### Tier 1: Production-Ready MoE (Highly Recommended)

1. **mixtral:8x7b** - Mistral's flagship MoE
   - 8 experts, 2 active per token
   - 46.7B total params, only 12.9B active
   - **Excellent quality/efficiency ratio**
   - Strong reasoning, coding, and agents
   - Command: `ollama pull mixtral:8x7b`
   - Size: ~26GB
   - **Best bang for buck**

2. **mixtral:8x22b** - Mistral's largest MoE
   - 8 experts, 2 active per token
   - 141B total params, 39B active
   - **Top-tier performance**
   - Excellent for complex agentic tasks
   - 64K context window
   - Command: `ollama pull mixtral:8x22b`
   - Size: ~82GB
   - **Best overall MoE**

3. **deepseek-v2.5:236b** - DeepSeek's MoE flagship
   - 236B total params
   - Excellent reasoning
   - Strong coding capabilities
   - Command: `ollama pull deepseek-v2.5:236b`
   - Size: ~133GB
   - **Best for reasoning**

4. **qwen2.5:72b-instruct-moe** - Alibaba's latest
   - Multi-expert architecture
   - Excellent multilingual
   - Strong instruction following
   - Command: `ollama pull qwen2.5:72b` (MoE variant)
   - Size: ~40GB

### Tier 2: Specialized MoE Models

5. **wizardlm2:8x22b** - Microsoft's WizardLM MoE
   - Based on Mixtral 8x22b
   - Fine-tuned for complex instructions
   - **Excellent for multi-step agents**
   - Command: `ollama pull wizardlm2:8x22b`
   - Size: ~82GB

6. **dolphin-mixtral:8x22b** - Uncensored Mixtral
   - No restrictions
   - Full agentic capabilities
   - Based on Mixtral 8x22b
   - Command: `ollama pull dolphin-mixtral:8x22b`
   - Size: ~82GB

7. **nous-hermes2-mixtral:8x7b** - Already installed! ✅
   - Nous Research fine-tune
   - Excellent instruction following
   - Strong for agents
   - Size: ~26GB

8. **dolphin-mixtral:8x7b** - Already installed! ✅
   - Uncensored Mixtral 8x7b
   - Good for unrestricted agents
   - Size: ~26GB

### Tier 3: Experimental/Emerging

9. **arctic:70b** - Snowflake's MoE
   - Dense-Sparse architecture
   - Enterprise-focused
   - Command: `ollama pull snowflake-arctic`
   - Size: ~40GB

10. **jamba:12b** - AI21's hybrid MoE
    - Combines Transformer + Mamba (SSM)
    - Novel architecture
    - 256K context window
    - Command: `ollama pull jamba`
    - Size: ~7GB

## MoE Models Already Installed

Grace already has these MoE models:
- ✅ **dolphin-mixtral:latest** (8x7b variant)
- ✅ **nous-hermes2-mixtral:latest** (8x7b variant)

## Recommended Additions

### For Maximum MoE Power (Add These 3)
1. **mixtral:8x22b** - Best overall MoE
2. **deepseek-v2.5:236b** - Best reasoning
3. **wizardlm2:8x22b** - Best for agents

**Total: ~297GB**

### For Balanced MoE (Add These 2)
1. **mixtral:8x7b** - Best efficiency
2. **mixtral:8x22b** - Best quality

**Total: ~108GB**

### Quick Win (Add Just 1)
**mixtral:8x22b** - The best all-around MoE model

**Total: ~82GB**

## Install Commands

```bash
# Maximum MoE power
ollama pull mixtral:8x22b
ollama pull deepseek-v2.5:236b
ollama pull wizardlm2:8x22b

# Balanced
ollama pull mixtral:8x7b
ollama pull mixtral:8x22b

# Quick win
ollama pull mixtral:8x22b
```

## MoE Benefits for Grace

### Why MoE for Agents?
1. **Efficiency**: Only activate needed experts
2. **Specialization**: Different experts for different tasks
3. **Scalability**: Huge capacity without huge compute
4. **Quality**: Matches or beats dense models 3x their active size

### Best MoE for Different Tasks

**Coding Agents:**
- mixtral:8x22b
- deepseek-v2.5:236b

**General Agents:**
- mixtral:8x22b
- wizardlm2:8x22b

**Conversational Agents:**
- mixtral:8x7b (fast)
- dolphin-mixtral:8x22b (uncensored)

**Multi-step Reasoning:**
- deepseek-v2.5:236b
- wizardlm2:8x22b

**Resource Efficient:**
- mixtral:8x7b (best quality per GB)
- jamba:12b (256K context!)

## Current Status

**MoE Models Installed: 2/10**
- ✅ dolphin-mixtral (8x7b)
- ✅ nous-hermes2-mixtral (8x7b)

**Recommended Next:**
1. **mixtral:8x22b** - Essential upgrade
2. **mixtral:8x7b** - Efficient baseline
3. **deepseek-v2.5:236b** - Reasoning powerhouse

**Storage:**
- Used: ~213GB
- Available: ~787GB
- Top 3 MoE: ~297GB (still 490GB free!)

## Comparison: MoE vs Dense

| Model Type | Params | Active | Quality | Speed | Memory |
|------------|--------|--------|---------|-------|--------|
| Dense 70B | 70B | 70B | ★★★★☆ | Slow | 40GB |
| Mixtral 8x22B | 141B | 39B | ★★★★★ | Fast | 82GB |
| DeepSeek 236B | 236B | ~37B | ★★★★★ | Fast | 133GB |

**MoE wins on quality AND speed!**

## Advanced: Combining MoE Models

Grace can use **multiple MoE models** for different tasks:
- **mixtral:8x7b** - Quick responses, general queries
- **mixtral:8x22b** - Complex reasoning, planning
- **deepseek-v2.5:236b** - Hard coding, math, logic
- **wizardlm2:8x22b** - Multi-step agent workflows

Route tasks to the right expert MoE model!
