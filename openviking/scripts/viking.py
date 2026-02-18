#!/usr/bin/env python3
"""OpenViking CLI wrapper for OpenClaw skill integration.

Usage:
    viking.py add <file_path> [--data-dir DIR]
    viking.py add-dir <dir_path> [--pattern GLOB] [--data-dir DIR]
    viking.py search <query> [--limit N] [--data-dir DIR]
    viking.py ls [uri] [--data-dir DIR]
    viking.py abstract <uri> [--data-dir DIR]
    viking.py overview <uri> [--data-dir DIR]
    viking.py read <uri> [--data-dir DIR]
    viking.py info [--data-dir DIR]
"""

import argparse
import glob as globmod
import json
import os
import sys

def get_client(data_dir):
    """Initialize and return an OpenViking client."""
    try:
        import openviking as ov
    except ImportError:
        print("ERROR: openviking not installed. Run: pip install openviking", file=sys.stderr)
        sys.exit(1)

    config_file = os.environ.get("OPENVIKING_CONFIG_FILE", os.path.expanduser("~/.openviking/ov.conf"))
    if not os.path.exists(config_file):
        print(f"ERROR: Config not found at {config_file}", file=sys.stderr)
        print("Create ~/.openviking/ov.conf or set OPENVIKING_CONFIG_FILE", file=sys.stderr)
        sys.exit(1)

    client = ov.SyncOpenViking(path=data_dir)
    client.initialize()
    return client


def cmd_add(args):
    """Add a single file to the index."""
    client = get_client(args.data_dir)
    try:
        result = client.add_resource(path=args.file_path)
        status = result.get("status", "unknown")
        errors = result.get("errors", [])
        root_uri = result.get("root_uri", "")

        if status == "success":
            print(f"✅ Added: {args.file_path}")
            print(f"   URI: {root_uri}")
            print("⏳ Processing embeddings and summaries...")
            client.wait_processed()
            print("✅ Processing complete.")
        else:
            print(f"❌ Failed: {args.file_path}")
            for e in errors:
                print(f"   Error: {e}")
    finally:
        client.close()


def cmd_add_dir(args):
    """Add all matching files from a directory."""
    pattern = args.pattern or "*.md"
    search_path = os.path.join(args.dir_path, "**", pattern)
    files = sorted(globmod.glob(search_path, recursive=True))

    if not files:
        print(f"No files matching '{pattern}' found in {args.dir_path}")
        return

    client = get_client(args.data_dir)
    try:
        success_count = 0
        fail_count = 0

        for f in files:
            result = client.add_resource(path=f)
            status = result.get("status", "unknown")
            errors = result.get("errors", [])

            if status == "success":
                print(f"  ✅ {f}")
                success_count += 1
            else:
                err_msg = errors[0] if errors else "unknown error"
                print(f"  ❌ {f}: {err_msg}")
                fail_count += 1

        print(f"\n⏳ Processing {success_count} files...")
        client.wait_processed()
        print(f"✅ Done. Success: {success_count}, Failed: {fail_count}")
    finally:
        client.close()


def cmd_search(args):
    """Semantic search across indexed content."""
    client = get_client(args.data_dir)
    try:
        results = client.find(args.query, limit=args.limit)

        if not results.resources:
            print(f"No results for '{args.query}'")
            return

        print(f"🔍 Results for '{args.query}':\n")
        for i, r in enumerate(results.resources, 1):
            print(f"  {i}. {r.uri}")
            print(f"     Score: {r.score:.4f}")
            # Try to read a preview
            try:
                content = client.read(r.uri)
                if content:
                    preview = content[:150].replace("\n", " ").strip()
                    print(f"     Preview: {preview}...")
            except Exception:
                pass
            print()
    finally:
        client.close()


def cmd_ls(args):
    """List resources at a URI."""
    uri = args.uri or "viking://resources"
    client = get_client(args.data_dir)
    try:
        entries = client.ls(uri)

        if not entries:
            print(f"Empty: {uri}")
            return

        print(f"📁 {uri}\n")
        for entry in entries:
            name = entry.get("name", "?")
            is_dir = entry.get("isDir", False)
            size = entry.get("size", 0)
            entry_uri = entry.get("uri", "")

            if name.startswith("."):
                continue  # skip hidden files

            icon = "📁" if is_dir else "📄"
            size_str = f" ({size}B)" if not is_dir else ""
            print(f"  {icon} {name}{size_str}")
            print(f"     {entry_uri}")
    finally:
        client.close()


def cmd_abstract(args):
    """Get L0 abstract (one-line summary) for a URI."""
    client = get_client(args.data_dir)
    try:
        result = client.abstract(args.uri)
        if result:
            print(f"📝 Abstract for {args.uri}:\n")
            print(result)
        else:
            print(f"No abstract available for {args.uri}")
    finally:
        client.close()


def cmd_overview(args):
    """Get L1 overview for a URI."""
    client = get_client(args.data_dir)
    try:
        result = client.overview(args.uri)
        if result:
            print(f"📖 Overview for {args.uri}:\n")
            print(result)
        else:
            print(f"No overview available for {args.uri}")
    finally:
        client.close()


def cmd_read(args):
    """Read full L2 content for a URI."""
    client = get_client(args.data_dir)
    try:
        result = client.read(args.uri)
        if result:
            print(result)
        else:
            print(f"No content at {args.uri}")
    finally:
        client.close()


def cmd_info(args):
    """Show OpenViking status and configuration."""
    config_file = os.environ.get("OPENVIKING_CONFIG_FILE", os.path.expanduser("~/.openviking/ov.conf"))

    print("OpenViking Status\n")
    print(f"  Config: {config_file}")
    print(f"  Config exists: {os.path.exists(config_file)}")
    print(f"  Data dir: {os.path.abspath(args.data_dir)}")
    print(f"  Data exists: {os.path.exists(args.data_dir)}")

    if os.path.exists(config_file):
        try:
            with open(config_file) as f:
                cfg = json.load(f)
            emb = cfg.get("embedding", {}).get("dense", {})
            vlm = cfg.get("vlm", {})
            print(f"\n  Embedding model: {emb.get('model', 'not set')}")
            print(f"  Embedding dim: {emb.get('dimension', 'auto')}")
            print(f"  VLM model: {vlm.get('model', 'not set')}")
            print(f"  API base: {emb.get('api_base', 'not set')}")
        except Exception as e:
            print(f"\n  Config parse error: {e}")

    # Quick connectivity test
    try:
        import openviking as ov
        print(f"\n  openviking version: {ov.__version__}")
    except ImportError:
        print("\n  ❌ openviking not installed")
    except AttributeError:
        print("\n  openviking installed (version unknown)")


def main():
    parser = argparse.ArgumentParser(description="OpenViking CLI for OpenClaw")
    parser.add_argument("--data-dir", default="./openviking_data", help="Data storage directory")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # add
    p_add = subparsers.add_parser("add", help="Add a file to index")
    p_add.add_argument("file_path", help="Path to file")

    # add-dir
    p_adddir = subparsers.add_parser("add-dir", help="Add all files from directory")
    p_adddir.add_argument("dir_path", help="Directory path")
    p_adddir.add_argument("--pattern", default="*.md", help="Glob pattern (default: *.md)")

    # search
    p_search = subparsers.add_parser("search", help="Semantic search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")

    # ls
    p_ls = subparsers.add_parser("ls", help="List resources")
    p_ls.add_argument("uri", nargs="?", default="viking://resources", help="URI to list")

    # abstract
    p_abs = subparsers.add_parser("abstract", help="Get L0 abstract")
    p_abs.add_argument("uri", help="Resource URI")

    # overview
    p_ov = subparsers.add_parser("overview", help="Get L1 overview")
    p_ov.add_argument("uri", help="Resource URI")

    # read
    p_read = subparsers.add_parser("read", help="Read full content")
    p_read.add_argument("uri", help="Resource URI")

    # info
    subparsers.add_parser("info", help="Show status and config")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "add": cmd_add,
        "add-dir": cmd_add_dir,
        "search": cmd_search,
        "ls": cmd_ls,
        "abstract": cmd_abstract,
        "overview": cmd_overview,
        "read": cmd_read,
        "info": cmd_info,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
