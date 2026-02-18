# OpenViking Skill for OpenClaw

An [OpenClaw](https://github.com/openclaw/openclaw) skill that integrates [OpenViking](https://github.com/volcengine/OpenViking) — a context database for AI agents — using NVIDIA NIM API for embeddings and VLM.

## Why OpenViking? — Upgrading from OpenClaw's Default Memory

OpenClaw's default `qmd` memory backend + manual `MEMORY.md` files work fine for lightweight use, but hit limits with large document collections:

| Capability | qmd (default) | OpenViking |
|------------|--------------|------------|
| Semantic search | Basic vector matching | Directory-recursive + semantic fusion |
| Auto summaries | ❌ | ✅ L0/L1/L2 three-tier |
| Structured browsing | ❌ | ✅ Virtual filesystem |
| Token savings | ❌ | ✅ Load only what's needed |

**Recommended setup**: Keep qmd for daily lightweight memory, use OpenViking for large document libraries (books, codebases, research papers). Sub-agents can search OpenViking for relevant context instead of stuffing entire documents into prompts.

## What It Does

- **Semantic search** across your indexed documents (books, code, notes, etc.)
- **Auto-generate summaries** (L0 abstract / L1 overview) for every indexed file
- **Browse & read** indexed content via a virtual filesystem (`viking://resources/...`)
- **Batch index** entire directories of files

All powered by free NVIDIA NIM API — no paid API keys required.

## Install

### 1. Clone the skill

```bash
# Option A: Clone directly into your skills directory
git clone https://github.com/swizardlv/openclaw_openviking_skill.git
cp -r openclaw_openviking_skill/openviking ~/.openclaw/workspace/skills/

# Option B: Or just copy the skill folder
cp -r openviking/ ~/.openclaw/workspace/skills/
```

### 2. Install Python dependencies

```bash
pip install openviking
```

### 3. Get a NVIDIA API key (free)

1. Visit https://build.nvidia.com/
2. Sign in → API Keys → Generate Key
3. Save the key (starts with `nvapi-`)

### 4. Create config file

```bash
mkdir -p ~/.openviking
cat > ~/.openviking/ov.conf << 'EOF'
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
EOF
```

### 5. Set environment variable

```bash
echo 'export OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### CLI Tool

The skill ships with `scripts/viking.py`, a CLI tool for all operations:

```bash
# Check configuration status
python3 scripts/viking.py info

# Index a single file
python3 scripts/viking.py add ./my-document.md

# Index all markdown files in a directory
python3 scripts/viking.py add-dir ./my-docs/ --pattern "*.md"

# Semantic search
python3 scripts/viking.py search "how to configure nginx" --limit 5

# Browse indexed resources
python3 scripts/viking.py ls
python3 scripts/viking.py ls viking://resources/my-document

# Get auto-generated summaries
python3 scripts/viking.py abstract viking://resources/my-document
python3 scripts/viking.py overview viking://resources/my-document

# Read full content
python3 scripts/viking.py read viking://resources/my-document/section.md
```

### In OpenClaw Chat

Once installed, your OpenClaw agent can use the skill directly. Examples:

> "Index all the markdown files in my books folder"
> "Search my documents for content about machine learning"
> "Give me a summary of the indexed project"

### Python API

For advanced usage in scripts or other skills:

```python
import openviking as ov

client = ov.SyncOpenViking(path="./openviking_data")
client.initialize()

# Add a file
client.add_resource(path="./doc.md")
client.wait_processed()

# Search
results = client.find("query", limit=5)
for r in results.resources:
    print(f"{r.uri} (score: {r.score:.4f})")

# Read content
content = client.read("viking://resources/doc/section.md")

client.close()
```

See `references/python-api.md` for the full API reference.

## Model Choices

### Embedding (for search)

| Model | Dim | Notes |
|-------|-----|-------|
| `nvidia/nv-embed-v1` | 4096 | ✅ Recommended — symmetric, no extra params |
| `nvidia/nv-embedcode-7b-v1` | 4096 | Better for code |
| `nvidia/nv-embedqa-e5-v5` | 1024 | ❌ Requires `input_type` param, incompatible |

### VLM (for summaries)

| Model | Notes |
|-------|-------|
| `meta/llama-3.3-70b-instruct` | ✅ Recommended |
| `meta/llama-3.1-8b-instruct` | Lighter, faster |

> ⚠️ **Avoid reasoning models** (kimi-k2.5, deepseek-r1, etc.) — they return content in a `reasoning` field instead of `content`, which OpenViking can't parse.

## Known Issues

- **File name collisions**: OpenViking uses file names (not full paths) as URIs. Files with the same name in different directories will conflict. Rename to unique names before indexing.
- **No directory import**: `add_resource(path="./dir/")` doesn't work. Use `add-dir` command or iterate over files.
- **VLM failures are non-fatal**: If summary generation fails, search still works fine.

## Project Structure

```
openviking/
├── SKILL.md                       # Skill definition (triggers + instructions)
├── scripts/
│   └── viking.py                  # CLI tool
└── references/
    ├── setup-guide.md             # Detailed setup instructions
    └── python-api.md              # Python API reference
```

## License

MIT
