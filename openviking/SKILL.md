---
name: openviking
description: >
  Semantic search, context management, and document indexing via OpenViking.
  Use when the user asks to: index/import documents or files into a knowledge base,
  perform semantic search across indexed content, browse or explore indexed resources,
  get summaries/overviews of indexed documents, manage an OpenViking instance,
  or integrate structured context retrieval into workflows.
  Also use when sub-agents need to retrieve relevant context from a large document collection.
---

# OpenViking Skill

Manage an OpenViking context database: index documents, semantic search, browse, and retrieve summaries.

## Prerequisites

- Python 3.9+ with `openviking` package installed (`pip install openviking`)
- Config file at `~/.openviking/ov.conf` with valid embedding and VLM credentials
- Environment variable `OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf`

If prerequisites are not met, guide the user through setup. See `references/setup-guide.md`.

## Quick Reference

### Index a file

```bash
python3 scripts/viking.py add /path/to/file.md
```

### Index all files in a directory (recursive)

```bash
python3 scripts/viking.py add-dir /path/to/directory --pattern "*.md"
```

### Semantic search

```bash
python3 scripts/viking.py search "query text" --limit 5
```

### Browse resources

```bash
python3 scripts/viking.py ls [viking://resources/path]
```

### Get summary

```bash
python3 scripts/viking.py abstract viking://resources/my_doc
python3 scripts/viking.py overview viking://resources/my_doc
```

### Read full content

```bash
python3 scripts/viking.py read viking://resources/my_doc/section.md
```

## Usage Notes

- **Data directory**: Defaults to `./openviking_data` in the current working directory. Override with `--data-dir`.
- **File name collisions**: OpenViking uses file names (not full paths) as URIs. Avoid indexing files with identical names from different directories simultaneously.
- **VLM model**: Use non-reasoning models (e.g. `meta/llama-3.3-70b-instruct`) for the VLM. Reasoning models return content in the wrong field.
- **Embedding model**: `nvidia/nv-embed-v1` (symmetric, 4096-dim) works without extra parameters. Asymmetric models (e.g. `nv-embedqa-e5-v5`) require `input_type` which OpenViking doesn't pass.

## When to Use Python API vs CLI Script

- **CLI script** (`scripts/viking.py`): For quick one-off operations from the shell.
- **Python API**: For complex workflows, batch operations, or integration into other scripts. See `references/python-api.md`.
