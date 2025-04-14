# Stub for embedding logic

import os
import json
from pathlib import Path
from typing import List
import tiktoken
from atlas.indexing.base_chunker import CodeChunk

CHUNK_DIR = Path(".chunks")
MAX_TOKENS = 8192
ENCODER = tiktoken.get_encoding("cl100k_base")


def ensure_chunk_dir():
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)


def save_chunks_to_files(chunks: List[CodeChunk]):
    ensure_chunk_dir()
    for chunk in chunks:
        name_hash = f"{chunk.chunk_type}_{chunk.name or 'anon'}_{chunk.start_line}_{chunk.end_line}".replace("/", "_")
        path = CHUNK_DIR / f"{name_hash}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chunk.to_dict(), f, indent=2)


def dry_run_validate_chunks():
    ensure_chunk_dir()
    failed = []
    ok = 0
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        source = data.get("source", "")
        token_count = len(ENCODER.encode(source))
        if token_count > MAX_TOKENS:
            print(f"⚠️  {chunk_file.name} too large: {token_count} tokens")
            failed.append((chunk_file, token_count))
        else:
            ok += 1
    print(f"✅ Dry run complete. Valid: {ok}, Over-limit: {len(failed)}")
    return failed
