# OpenViking Setup Guide

## Installation

```bash
pip install openviking
```

## Configuration

### 1. Create config file

```bash
mkdir -p ~/.openviking
```

Edit `~/.openviking/ov.conf`:

```json
{
  "embedding": {
    "dense": {
      "api_base": "https://integrate.api.nvidia.com/v1",
      "api_key": "YOUR_NVIDIA_API_KEY",
      "provider": "openai",
      "dimension": 4096,
      "model": "nvidia/nv-embed-v1"
    }
  },
  "vlm": {
    "api_base": "https://integrate.api.nvidia.com/v1",
    "api_key": "YOUR_NVIDIA_API_KEY",
    "provider": "openai",
    "model": "meta/llama-3.3-70b-instruct"
  }
}
```

### 2. Set environment variable

```bash
echo 'export OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf' >> ~/.bashrc
source ~/.bashrc
```

### 3. Get NVIDIA API Key

1. Visit https://build.nvidia.com/
2. Sign in → API Keys → Generate Key
3. Copy and paste into config

## Model Selection

### Embedding models

| Model | Dimension | Type | Notes |
|-------|-----------|------|-------|
| `nvidia/nv-embed-v1` | 4096 | symmetric | ✅ Recommended, no extra params needed |
| `nvidia/nv-embedqa-e5-v5` | 1024 | asymmetric | ❌ Requires `input_type`, incompatible |
| `nvidia/nv-embedcode-7b-v1` | 4096 | symmetric | Good for code |

### VLM models (for summaries)

| Model | Notes |
|-------|-------|
| `meta/llama-3.3-70b-instruct` | ✅ Recommended |
| `meta/llama-3.1-8b-instruct` | Lighter alternative |

> ⚠️ Do NOT use reasoning models (kimi-k2.5, deepseek-r1) — they return content in a non-standard field that OpenViking cannot parse.

## Verification

```bash
python3 scripts/viking.py info
```

Expected output shows config file location, models, and openviking version.
