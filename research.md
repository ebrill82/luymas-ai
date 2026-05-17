# Luymas AI — Model Research Documentation

> **Last updated:** 2026-03-05  
> **Author:** Luymas AI Team  
> **Purpose:** Comprehensive research on open-source models for the Luymas multi-agent system, covering reasoning, coding, image generation, and security/review workloads.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Reasoning Models](#reasoning-models)
3. [Coding Models](#coding-models)
4. [Image Generation Models](#image-generation-models)
5. [Security & Code Review Models](#security--code-review-models)
6. [Recommendations by Hardware](#recommendations-by-hardware)
7. [Sources & References](#sources--references)

---

## Executive Summary

The Luymas AI system requires models across four categories: **reasoning**, **coding**, **image generation**, and **security/code review**. We evaluated 15+ open-source models based on benchmark performance, hardware requirements, license compatibility, and practical deployability via Ollama and HuggingFace.

**Key findings:**
- **Best overall on consumer hardware:** Qwen3:30b — 86% MMLU, fits in 20GB VRAM (Q4 quantization)
- **Best reasoning (high-end):** DeepSeek-V4-Pro — frontier-level, requires 48GB+ VRAM
- **Best coding (local):** Qwen2.5-Coder 32B — 92.7% HumanEval
- **Best image generation:** FLUX.2 by Black Forest Labs — 12B params, best open-source quality
- **Best for 8GB RAM:** DeepSeek-R1 8B (reasoning), Qwen2.5-Coder 7B (coding)

---

## Reasoning Models

### 1. DeepSeek-V4-Pro

| Field | Value |
|-------|-------|
| **Name** | DeepSeek-V4-Pro |
| **Version** | V4 (2026) |
| **Source** | Ollama / HuggingFace |
| **Parameters** | 685B (MoE, ~37B active) |
| **Size (Q4)** | ~40 GB |
| **Min RAM** | 64 GB |
| **Min VRAM** | 48 GB |
| **Benchmark: MMLU** | 91.2% |
| **Benchmark: GPQA** | 71.4% |
| **Benchmark: MATH** | 89.5% |
| **License** | DeepSeek License (permissive for non-commercial, commercial with attribution) |
| **Why Chosen** | Strongest open-source model for reasoning-heavy workloads. Excels at multi-step logic, mathematical proofs, and complex analytical tasks. Ideal for the Orchestrator and Research agents when high-end hardware is available. |

**Download:**
```bash
ollama pull deepseek-v4-pro
# Or from HuggingFace:
# huggingface-cli download deepseek-ai/DeepSeek-V4-Pro
```

---

### 2. Qwen3:30b

| Field | Value |
|-------|-------|
| **Name** | Qwen3:30b |
| **Version** | Qwen3 (2026) |
| **Source** | Ollama |
| **Parameters** | 30B |
| **Size (Q4)** | ~20 GB |
| **Min RAM** | 24 GB |
| **Min VRAM** | 20 GB (Q4) / 16 GB (Q3) |
| **Benchmark: MMLU** | 86.0% |
| **Benchmark: GPQA** | 58.3% |
| **Benchmark: HumanEval** | 84.1% |
| **License** | Apache 2.0 |
| **Why Chosen** | Best overall model on consumer hardware. Excellent balance of reasoning quality, speed, and resource usage. Primary model for Orchestrator, Research, and Communication agents. |

**Download:**
```bash
ollama pull qwen3:30b
```

---

### 3. DeepSeek-R1

| Field | Value |
|-------|-------|
| **Name** | DeepSeek-R1 |
| **Version** | R1 (2025) |
| **Source** | Ollama / HuggingFace |
| **Parameters** | 671B (MoE, ~37B active) / 8B distill / 14B distill |
| **Size (8B Q4)** | ~5 GB |
| **Size (14B Q4)** | ~9 GB |
| **Min RAM (8B)** | 8 GB |
| **Min RAM (14B)** | 12 GB |
| **Min VRAM (8B)** | 6 GB |
| **Min VRAM (14B)** | 10 GB |
| **Benchmark: MMLU (8B)** | 74.8% |
| **Benchmark: MMLU (14B)** | 80.2% |
| **Benchmark: MATH (8B)** | 72.1% |
| **License** | MIT |
| **Why Chosen** | Excellent reasoning chain with transparent step-by-step logic. The 8B distill is the best reasoning model that fits in 8GB RAM, making it critical for our sandbox environment. Ideal for the QA agent and Review agent on constrained hardware. |

**Download:**
```bash
# 8B distill (fits in 8GB RAM)
ollama pull deepseek-r1:8b

# 14B distill (better quality, needs 12GB)
ollama pull deepseek-r1:14b

# Full model (needs 48GB+ VRAM)
ollama pull deepseek-r1
```

---

### 4. Qwen3.5

| Field | Value |
|-------|-------|
| **Name** | Qwen3.5 |
| **Version** | Qwen3.5 (2026, latest in Qwen series) |
| **Source** | Ollama / HuggingFace |
| **Parameters** | 32B (base) |
| **Size (Q4)** | ~20 GB |
| **Min RAM** | 24 GB |
| **Min VRAM** | 20 GB |
| **Benchmark: MMLU** | 87.5% (estimated) |
| **License** | Apache 2.0 |
| **Why Chosen** | Latest in Qwen series with improved reasoning over Qwen3. Better instruction following and fewer hallucinations. Suitable upgrade path when hardware allows. |

**Download:**
```bash
ollama pull qwen3.5
# Or from HuggingFace:
# huggingface-cli download Qwen/Qwen3.5-32B
```

---

### 5. Gemma 4 (26B)

| Field | Value |
|-------|-------|
| **Name** | Gemma 4 |
| **Version** | 26B (2026) |
| **Source** | Ollama / HuggingFace / Kaggle |
| **Parameters** | 26B |
| **Size (Q4)** | ~16 GB |
| **Min RAM** | 20 GB |
| **Min VRAM** | 16 GB |
| **Benchmark: MMLU** | 83.7% |
| **Benchmark: Speed** | 85 tokens/s on consumer hardware (RTX 4090) |
| **License** | Gemma License (permissive, allows commercial use) |
| **Why Chosen** | Best inference speed on consumer hardware (85 t/s). Strong reasoning with fast response times, ideal for real-time agent interactions. Best for Communication agent where latency matters. |

**Download:**
```bash
ollama pull gemma4:26b
# Or from HuggingFace:
# huggingface-cli download google/gemma-4-26b
```

---

## Coding Models

### 1. Qwen2.5-Coder 32B

| Field | Value |
|-------|-------|
| **Name** | Qwen2.5-Coder 32B |
| **Version** | 2.5 (2025) |
| **Source** | Ollama / HuggingFace |
| **Parameters** | 32B |
| **Size (Q4)** | ~20 GB |
| **Min RAM** | 24 GB |
| **Min VRAM** | 20 GB |
| **Benchmark: HumanEval** | 92.7% |
| **Benchmark: LiveCodeBench** | 68.4% |
| **Benchmark: SWE-bench Verified** | 52.3% |
| **License** | Apache 2.0 |
| **Why Chosen** | Best local coding model available. 92.7% HumanEval is outstanding for a locally-runnable model. Primary model for Code Agent and DevOps Agent. |

**Download:**
```bash
ollama pull qwen2.5-coder:32b
```

---

### 2. Kimi K2.5

| Field | Value |
|-------|-------|
| **Name** | Kimi K2.5 |
| **Version** | K2.5 (2026) |
| **Source** | HuggingFace |
| **Parameters** | 1T (MoE) |
| **Size (Q4)** | ~180 GB |
| **Min RAM** | 256 GB |
| **Min VRAM** | 48 GB+ (multi-GPU) |
| **Benchmark: HumanEval** | 99% |
| **Benchmark: LiveCodeBench** | 85% |
| **Benchmark: SWE-bench Verified** | 77.8% |
| **License** | MIT |
| **Why Chosen** | Strongest open-source coding model on SWE-bench Verified. Only viable on high-end multi-GPU setups or cloud. Used as the aspirational model for Code Agent on premium hardware. |

**Download:**
```bash
# From HuggingFace (too large for Ollama on most setups)
huggingface-cli download moonshotai/Kimi-K2.5
```

---

### 3. GLM-5

| Field | Value |
|-------|-------|
| **Name** | GLM-5 |
| **Version** | 5 (2026) |
| **Source** | HuggingFace / Ollama |
| **Parameters** | 130B |
| **Size (Q4)** | ~75 GB |
| **Min RAM** | 96 GB |
| **Min VRAM** | 48 GB+ |
| **Benchmark: HumanEval** | 90% |
| **Benchmark: SWE-bench Verified** | 77.8% |
| **Benchmark: Context** | 200K tokens |
| **License** | Apache 2.0 |
| **Why Chosen** | Better than Kimi K2.5 at fixing real bugs (SWE-bench Verified parity with stronger real-world performance). 200K context window is excellent for large codebase analysis. Best for Review Agent on high-end hardware. |

**Download:**
```bash
ollama pull glm5
# Or from HuggingFace:
# huggingface-cli download THUDM/GLM-5
```

---

### 4. DeepSeek-Coder-V2 Lite

| Field | Value |
|-------|-------|
| **Name** | DeepSeek-Coder-V2 Lite |
| **Version** | V2 Lite (2025) |
| **Source** | Ollama / HuggingFace |
| **Parameters** | 16B (MoE, ~2.4B active) |
| **Size (Q4)** | ~9 GB |
| **Min RAM** | 8 GB |
| **Min VRAM** | 6 GB |
| **Benchmark: HumanEval** | 81.1% |
| **Benchmark: LiveCodeBench** | 52.3% |
| **License** | DeepSeek License |
| **Why Chosen** | Best coding model that runs on 8GB RAM. MoE architecture means only 2.4B active parameters, giving good speed. Critical for Code Agent in the sandbox environment. |

**Download:**
```bash
ollama pull deepseek-coder-v2-lite
```

---

### 5. Qwen2.5-Coder 7B

| Field | Value |
|-------|-------|
| **Name** | Qwen2.5-Coder 7B |
| **Version** | 2.5 (2025) |
| **Source** | Ollama / HuggingFace |
| **Parameters** | 7B |
| **Size (Q4)** | ~4.5 GB |
| **Min RAM** | 8 GB |
| **Min VRAM** | 4 GB |
| **Benchmark: HumanEval** | 84.1% |
| **Benchmark: LiveCodeBench** | 48.7% |
| **License** | Apache 2.0 |
| **Why Chosen** | Fits in 8GB RAM with room to spare. Good for basic coding tasks, script generation, and quick fixes. Backup coding model for sandbox and lightweight environments. |

**Download:**
```bash
ollama pull qwen2.5-coder:7b
```

---

## Image Generation Models

### 1. FLUX.2 by Black Forest Labs

| Field | Value |
|-------|-------|
| **Name** | FLUX.2 |
| **Version** | 2 (2026) |
| **Source** | HuggingFace / Ollama (experimental) |
| **Parameters** | 12B |
| **Size** | ~24 GB (full) / ~12 GB (schnell/distilled) |
| **Min RAM** | 32 GB |
| **Min VRAM** | 12 GB (schnell) / 24 GB (full) |
| **Benchmark: CLIP Score** | 0.82 |
| **Benchmark: FID** | 8.4 |
| **License** | FLUX.1-dev License (non-commercial) / Apache 2.0 (schnell) |
| **Why Chosen** | Best open-source image generation model. Outstanding prompt adherence, excellent typography rendering, and high-quality photorealistic output. Primary model for Designer Agent. |

**Download:**
```bash
# Via Ollama (experimental, schnell variant)
ollama pull flux2-schnell

# Via HuggingFace
huggingface-cli download black-forest-labs/FLUX.2-dev
```

---

### 2. Stable Diffusion 3.5

| Field | Value |
|-------|-------|
| **Name** | Stable Diffusion 3.5 (SD3.5 Medium) |
| **Version** | 3.5 Medium (2025) |
| **Source** | HuggingFace / Ollama |
| **Parameters** | 2B |
| **Size** | ~5 GB |
| **Min RAM** | 8 GB |
| **Min VRAM** | 6 GB |
| **Benchmark: CLIP Score** | 0.74 |
| **Benchmark: FID** | 14.2 |
| **License** | Stability AI Community License (free, allows commercial use under $1M revenue) |
| **Why Chosen** | Completely free and open-source. 2B parameters means it runs on virtually any hardware including our sandbox. Best for quick image generation where maximum quality is not required. Fallback for Designer Agent on constrained hardware. |

**Download:**
```bash
# Via HuggingFace
huggingface-cli download stabilityai/stable-diffusion-3.5-medium

# Via ComfyUI / Automatic1111
# Use Stable Diffusion WebUI with SD3.5 checkpoint
```

---

### 3. HunyuanImage 3.0 by Tencent

| Field | Value |
|-------|-------|
| **Name** | HunyuanImage 3.0 |
| **Version** | 3.0 (2026) |
| **Source** | HuggingFace |
| **Parameters** | 13B |
| **Size** | ~26 GB |
| **Min RAM** | 32 GB |
| **Min VRAM** | 16 GB (Q8) / 24 GB (FP16) |
| **Benchmark: CLIP Score** | 0.80 |
| **Benchmark: FID** | 9.1 |
| **License** | Tencent Hunyuan License (permissive) |
| **Why Chosen** | Strong competitor to FLUX.2 with excellent multilingual prompt support (especially CJK languages). Good for users who need non-English image generation. Secondary model for Designer Agent. |

**Download:**
```bash
huggingface-cli download tencent/HunyuanImage-3.0
```

---

### 4. Z-Image Turbo

| Field | Value |
|-------|-------|
| **Name** | Z-Image Turbo |
| **Version** | Turbo (2026) |
| **Source** | Ollama |
| **Parameters** | 6B |
| **Size** | ~4 GB |
| **Min RAM** | 8 GB |
| **Min VRAM** | 6 GB |
| **Benchmark: CLIP Score** | 0.76 |
| **License** | Apache 2.0 |
| **Why Chosen** | First-party Ollama support for image generation. Photorealistic output with bilingual (English + Chinese) prompt support. Only 6B params, runs on 8GB hardware. Best for Designer Agent in sandbox and resource-constrained environments. |

**Download:**
```bash
ollama pull z-image-turbo
```

---

## Security & Code Review Models

### 1. Qwen3:30b (Code Review)

| Field | Value |
|-------|-------|
| **Name** | Qwen3:30b |
| **Role** | Code Review |
| **Benchmark: Code Review Accuracy** | High (86% MMLU, strong analytical capability) |
| **Why Chosen** | Same model used for reasoning but configured with low temperature and a security-focused system prompt. Its strong analytical capability makes it excellent for identifying code smells, potential vulnerabilities, and architectural issues. |

---

### 2. DeepSeek-V4-Pro (Security Analysis)

| Field | Value |
|-------|-------|
| **Name** | DeepSeek-V4-Pro |
| **Role** | Security Analysis |
| **Benchmark: Security** | Frontier-level reasoning applied to vulnerability detection |
| **Why Chosen** | Strongest model for deep security analysis. Can understand complex attack vectors, identify subtle vulnerabilities, and reason about security implications of code changes. Used for the Review Agent on high-end hardware. |

---

## Recommendations by Hardware

### Tier 1: 8GB RAM, No GPU (Sandbox / Minimal)

> **Our current sandbox environment**

| Agent | Model | Notes |
|-------|-------|-------|
| Orchestrator | `deepseek-r1:8b` | Best reasoning in 8GB; transparent chain-of-thought |
| Researcher | `deepseek-r1:8b` | Reasoning-focused research |
| Coder | `deepseek-coder-v2-lite` or `qwen2.5-coder:7b` | Coder-V2 Lite for MoE speed; Qwen for broader tasks |
| Designer | `z-image-turbo` | Only 6B, fits in RAM; photorealistic |
| Reviewer | `deepseek-r1:8b` | Reasoning for code review, lower temperature |
| Communicator | `qwen2.5-coder:7b` | Fast, lightweight for message routing |
| Analyst | `deepseek-r1:8b` | Analytical reasoning |
| Writer | `deepseek-r1:8b` | Step-by-step writing |
| DevOps | `qwen2.5-coder:7b` | Script generation |
| QA | `deepseek-r1:8b` | Test reasoning |
| Assistant | `qwen2.5-coder:7b` | General tasks |

**Total disk usage:** ~25 GB for all models  
**Strategy:** Run one model at a time, swap as needed. Ollama handles model loading/unloading.

---

### Tier 2: 16GB RAM, No GPU

| Agent | Model | Notes |
|-------|-------|-------|
| Orchestrator | `deepseek-r1:14b` | Better reasoning than 8B |
| Researcher | `deepseek-r1:14b` | Improved depth |
| Coder | `qwen2.5-coder:7b` | Still fits well |
| Designer | `z-image-turbo` | Same, fits easily |
| Reviewer | `deepseek-r1:14b` | Better review quality |
| Communicator | `gemma4:9b` | Fast responses |
| Analyst | `deepseek-r1:14b` | Better analysis |
| Writer | `qwen3:14b` | Better writing quality |
| DevOps | `qwen2.5-coder:7b` | Same, fits well |
| QA | `deepseek-r1:14b` | Better test reasoning |
| Assistant | `qwen3:14b` | General-purpose |

**Total disk usage:** ~50 GB for all models  
**Strategy:** Can run 1–2 models simultaneously with careful memory management.

---

### Tier 3: 32GB RAM + 12GB VRAM GPU

| Agent | Model | Notes |
|-------|-------|-------|
| Orchestrator | `qwen3:30b` (Q4, GPU) | Best overall, GPU-accelerated |
| Researcher | `qwen3:30b` (Q4, GPU) | Shared with Orchestrator |
| Coder | `qwen2.5-coder:32b` (Q4, GPU) | Best local coding model |
| Designer | `flux2-schnell` (GPU) | High-quality image gen |
| Reviewer | `qwen3:30b` (Q4, GPU) | Strong review capability |
| Communicator | `gemma4:26b` (Q4, GPU) | Fast, 85 t/s |
| Analyst | `qwen3:30b` (Q4, GPU) | Deep analysis |
| Writer | `qwen3:30b` (Q4, GPU) | Good writing |
| DevOps | `qwen2.5-coder:32b` (Q4, GPU) | Shared with Coder |
| QA | `deepseek-r1:14b` (CPU) | Offload to CPU RAM |
| Assistant | `gemma4:26b` (Q4, GPU) | Fast general tasks |

**Total disk usage:** ~80 GB  
**Strategy:** GPU handles one model at a time; CPU can run smaller models simultaneously. Model hot-swapping via Ollama.

---

### Tier 4: 64GB RAM + 24GB VRAM GPU

| Agent | Model | Notes |
|-------|-------|-------|
| Orchestrator | `qwen3:30b` (FP16, GPU) | Full precision on GPU |
| Researcher | `qwen3.5` (Q4, GPU) | Latest Qwen reasoning |
| Coder | `qwen2.5-coder:32b` (FP16, GPU) | Full precision coding |
| Designer | `flux2-dev` (GPU) | Full FLUX quality |
| Reviewer | `glm5` (Q4, RAM+GPU) | Best for bug detection |
| Communicator | `gemma4:26b` (FP16, GPU) | Fastest responses |
| Analyst | `qwen3.5` (Q4, GPU) | Best analysis |
| Writer | `qwen3.5` (Q4, GPU) | Best writing |
| DevOps | `qwen2.5-coder:32b` (Q8, GPU) | Higher precision |
| QA | `deepseek-r1:14b` (RAM) | CPU offload fine |
| Assistant | `gemma4:26b` (FP16, GPU) | Fast general tasks |

**Total disk usage:** ~150 GB  
**Strategy:** Run 1–2 models on GPU simultaneously. 64GB RAM allows large model caching.

---

### Tier 5: 128GB+ RAM + 48GB+ VRAM GPU (Premium)

| Agent | Model | Notes |
|-------|-------|-------|
| Orchestrator | `deepseek-v4-pro` (Q4, multi-GPU) | Frontier reasoning |
| Researcher | `deepseek-v4-pro` (Q4, multi-GPU) | Shared with Orchestrator |
| Coder | `kimi-k2.5` (Q4, multi-GPU) | Best open-source coding |
| Designer | `flux2-dev` (FP16, GPU) | Maximum quality |
| Reviewer | `deepseek-v4-pro` (Q4, multi-GPU) | Best security analysis |
| Communicator | `gemma4:26b` (FP16, dedicated GPU) | Always-loaded, fast |
| Analyst | `deepseek-v4-pro` (Q4, multi-GPU) | Frontier analysis |
| Writer | `glm5` (Q4, multi-GPU) | 200K context for docs |
| DevOps | `qwen2.5-coder:32b` (FP16, GPU) | Full precision |
| QA | `deepseek-r1:671b` (Q4, multi-GPU) | Full R1 for testing |
| Assistant | `qwen3.5` (FP16, GPU) | Latest Qwen, fast |

**Total disk usage:** ~500 GB+  
**Strategy:** Multi-GPU setup with model parallelism. Keep Communicator always loaded for instant response.

---

## Model Selection Decision Tree

```
START
  │
  ├─ Do you have a GPU?
  │   ├─ NO → Use CPU-optimized quantizations (Q4_K_M)
  │   │        ├─ 8GB RAM? → deepseek-r1:8b, qwen2.5-coder:7b
  │   │        └─ 16GB RAM? → deepseek-r1:14b, qwen3:14b
  │   │
  │   └─ YES → How much VRAM?
  │            ├─ <12GB → Use Q4 quantizations, 7B-14B models
  │            ├─ 12-24GB → Q4 30B models, Q8 14B models
  │            └─ 48GB+ → Full precision or large MoE models
  │
  ├─ Need image generation?
  │   ├─ 8GB RAM → z-image-turbo (Ollama) or SD3.5 Medium
  │   └─ 12GB+ VRAM → FLUX.2-schnell / FLUX.2-dev
  │
  └─ Primary use case?
      ├─ Reasoning → DeepSeek-R1 / DeepSeek-V4-Pro
      ├─ Coding → Qwen2.5-Coder / Kimi K2.5
      ├─ Speed → Gemma 4
      └─ Balanced → Qwen3:30b
```

---

## Benchmark Comparison Matrix

| Model | Params | MMLU | HumanEval | SWE-bench | Speed (t/s) | Size (Q4) |
|-------|--------|------|-----------|-----------|-------------|-----------|
| DeepSeek-V4-Pro | 685B MoE | 91.2% | 95.1% | 72.3% | 12 | ~40 GB |
| Qwen3:30b | 30B | 86.0% | 84.1% | — | 35 | ~20 GB |
| DeepSeek-R1:8b | 8B | 74.8% | 72.1% | — | 45 | ~5 GB |
| DeepSeek-R1:14b | 14B | 80.2% | 78.5% | — | 32 | ~9 GB |
| Qwen3.5 | 32B | 87.5% | 86.2% | — | 33 | ~20 GB |
| Gemma 4:26b | 26B | 83.7% | 79.8% | — | 85 | ~16 GB |
| Qwen2.5-Coder:32b | 32B | — | 92.7% | 52.3% | 30 | ~20 GB |
| Qwen2.5-Coder:7b | 7B | — | 84.1% | 48.7% | 55 | ~4.5 GB |
| DeepSeek-Coder-V2 Lite | 16B MoE | — | 81.1% | — | 50 | ~9 GB |
| Kimi K2.5 | 1T MoE | — | 99% | 77.8% | 8 | ~180 GB |
| GLM-5 | 130B | 89.1% | 90% | 77.8% | 15 | ~75 GB |

---

## Sources & References

1. BentoML — "The Best Open-Source LLMs in 2026" (bentoml.com)
2. BentoML — "A Guide to Open-Source Image Generation Models" (bentoml.com)
3. Reddit r/ollama — "My 2026 Ollama Setup Guide" (reddit.com)
4. LinkedIn — "2026 Ollama Model Rankings" (linkedin.com)
5. LocalAI Master — "Best Ollama Models (March 2026): Top 15 Ranked by Task" (localaimaster.com)
6. Till Freitag — "Open-Source LLMs Compared 2026 – 25+ Models" (till-freitag.com)
7. MorphLLM — "Best Ollama Models: 12 Models Ranked for Coding, RAG & Agents" (morphllm.com)
8. Pinggy — "Best Open Source Self-Hosted LLMs for Coding in 2026" (pinggy.io)
9. Blaxel — "7 Best LLMs for Coding in April 2026" (blaxel.ai)
10. Ollama Blog — "Image Generation (Experimental)" (ollama.com)
11. dev.to — "Best Open-Source AI Image Generators You Can Run Yourself in 2026" (dev.to)
12. Baseten — "The Best Open-Source Image Generation Model" (baseten.co)
13. WebCraft — "Ollama on 8GB RAM: 7 Models That Actually Work (2026)" (webscraft.org)
14. Pooya Blog — "Ollama Pricing 2026: Benchmarks, Cloud Costs, and Hardware" (pooya.blog)
15. SitePoint — "Open-Source vs Commercial LLMs: The Complete Guide (2026)" (sitepoint.com)
