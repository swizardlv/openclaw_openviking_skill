# OpenViking Skill for OpenClaw

An OpenClaw skill that integrates [OpenViking](https://github.com/volcengine/OpenViking) for semantic search and context management, using NVIDIA NIM API for embeddings and VLM.

## Install into OpenClaw

Add this skill to your OpenClaw workspace:

```bash
# Clone to your skills directory
git clone https://github.com/swizardlv/openclaw_openviking_skill.git /path/to/skills/

# Or copy the openviking/ folder into your workspace skills directory
cp -r openviking/ ~/.openclaw/workspace/skills/
```

## Prerequisites

1. Python 3.9+ with `openviking` package: `pip install openviking`
2. NVIDIA NIM API key from https://build.nvidia.com/
3. Config file at `~/.openviking/ov.conf` (see skill references for setup guide)

## Structure

```
openviking/
├── SKILL.md                    # Skill definition
├── scripts/
│   └── viking.py               # CLI tool for all operations
└── references/
    ├── setup-guide.md           # Installation and configuration
    └── python-api.md            # Python API reference
```

## Quick Test

```bash
export OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf
python3 openviking/scripts/viking.py info
python3 openviking/scripts/viking.py search "test query" --limit 3
```

## License

MIT
