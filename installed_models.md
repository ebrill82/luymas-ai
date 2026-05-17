# Luymas AI - Installed Models

This file tracks which AI models have been installed on this system.

## System Information

- **OS**: Linux (sandbox)
- **RAM**: 8GB
- **GPU**: None (CPU-only mode)
- **Ollama**: Not installed in sandbox (requires dedicated server)

## Recommended Hardware Tiers

### Tier 1: 8GB RAM, No GPU (Current Sandbox)
| Model | Size | Role | Ollama Tag |
|-------|------|------|------------|
| DeepSeek R1 8B | ~4.7GB | Reasoning | `deepseek-r1:8b` |
| Qwen2.5 Coder 7B | ~4.5GB | Code Generation | `qwen2.5-coder:7b` |
| Gemma 3 4B | ~2.6GB | Lightweight Tasks | `gemma3:4b` |
| Z-Image Turbo | ~3.8GB | Image Generation | `z-image-turbo` |
| Llama 3.2 3B | ~2.0GB | Quick Tasks | `llama3.2:3b` |

### Tier 2: 16GB RAM, No GPU
| Model | Size | Role | Ollama Tag |
|-------|------|------|------------|
| Qwen3 14B | ~8GB | Reasoning | `qwen3:14b` |
| Qwen2.5 Coder 14B | ~8GB | Code Generation | `qwen2.5-coder:14b` |
| DeepSeek R1 14B | ~8GB | Reasoning | `deepseek-r1:14b` |

### Tier 3: 32GB RAM + 12GB VRAM GPU
| Model | Size | Role | Ollama Tag |
|-------|------|------|------------|
| Qwen3 30B (Q4) | ~18GB | Reasoning/Code | `qwen3:30b` |
| Qwen2.5 Coder 32B (Q4) | ~20GB | Code Generation | `qwen2.5-coder:32b` |
| DeepSeek V4 Pro | ~24GB | Advanced Reasoning | (HuggingFace) |

### Tier 4: 64GB RAM + 24GB VRAM GPU
| Model | Size | Role | Ollama Tag |
|-------|------|------|------------|
| Llama 3.3 70B (Q4) | ~40GB | All-purpose | `llama3.3:70b` |
| Qwen3 30B (Q8) | ~32GB | High Quality | `qwen3:30b` |

### Tier 5: 128GB+ RAM + 48GB+ VRAM GPU
| Model | Size | Role | Ollama Tag |
|-------|------|------|------------|
| Kimi K2.5 (1T, 4-bit) | ~60GB | Best SWE-bench | (HuggingFace) |
| DeepSeek V4 Pro (full) | ~80GB+ | Frontier Reasoning | (HuggingFace) |

## Installation Commands

```bash
# Install a model via Ollama
ollama pull <model-tag>

# Example:
ollama pull deepseek-r1:8b
ollama pull qwen2.5-coder:7b

# List installed models
ollama list

# Install via HuggingFace (for models not on Ollama)
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download('model-id')"
```

## Image Generation Models

Image generation models require special setup:

### Z-Image Turbo (via Ollama - Experimental)
```bash
ollama pull z-image-turbo
```

### FLUX.1 Pro / FLUX.2 (via HuggingFace)
```bash
pip install diffusers transformers accelerate
python -c "
from diffusers import FluxPipeline
pipe = FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-dev')
pipe.save_pretrained('./models/flux-1-pro')
"
```

### Stable Diffusion 3 Medium (via HuggingFace)
```bash
pip install diffusers transformers
python -c "
from diffusers import StableDiffusion3Pipeline
pipe = StableDiffusion3Pipeline.from_pretrained('stabilityai/stable-diffusion-3-medium-diffusers')
pipe.save_pretrained('./models/sd3-medium')
"
```

## Notes

- Models with `(Q4)` are 4-bit quantized versions (smaller, faster, slight quality loss)
- Models with `(Q8)` are 8-bit quantized (better quality, larger size)
- Full precision models require significantly more RAM/VRAM
- Always check `ollama list` to verify installed models
- Image generation via Ollama is experimental - use HuggingFace for production quality
