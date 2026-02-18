# OpenViking Python API Reference

## Initialization

```python
import openviking as ov

client = ov.SyncOpenViking(path="./openviking_data")
client.initialize()
```

Always call `client.close()` when done, or use try/finally.

## Core Operations

### Add resource

```python
result = client.add_resource(path="./file.md")
# result: {'status': 'success', 'root_uri': 'viking://resources/file', ...}

# Wait for embedding + summary generation
client.wait_processed()
```

Supports: local files, URLs. Directories are NOT supported directly — iterate over files.

### Semantic search

```python
results = client.find("query text", limit=5)
# Optional: target_uri="viking://resources/subdir" to scope search

for r in results.resources:
    print(r.uri, r.score)
```

### Browse (ls)

```python
entries = client.ls("viking://resources")
# Returns list of dicts: {'name', 'uri', 'isDir', 'size', ...}
```

### Read content (L2)

```python
content = client.read("viking://resources/doc/section.md")
```

### Abstract (L0 summary)

```python
abstract = client.abstract("viking://resources/doc")
```

### Overview (L1 detailed summary)

```python
overview = client.overview("viking://resources/doc")
```

## Batch indexing pattern

```python
import glob

client = ov.SyncOpenViking(path="./openviking_data")
client.initialize()

files = sorted(glob.glob("./docs/**/*.md", recursive=True))
for f in files:
    result = client.add_resource(path=f)
    print(f"{f}: {result.get('status')}")

client.wait_processed()
client.close()
```

## Known limitations

1. **File name collisions**: Files with identical names from different directories conflict (`/a/readme.md` and `/b/readme.md` both become `viking://resources/readme`). Rename files to be unique before indexing.
2. **No directory import**: `add_resource(path="./dir/")` fails. Iterate over files instead.
3. **VLM errors are non-fatal**: If summary generation fails, embedding/search still works.
