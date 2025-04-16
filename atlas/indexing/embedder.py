import json
from typing import List
import uuid
import tiktoken
from atlas.indexing.base_chunker import CodeChunk
from atlas.config import CHUNK_DIR, MAX_TOKENS

ENCODER = tiktoken.get_encoding("cl100k_base")


def ensure_chunk_dir():
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)


def save_chunks_to_files(chunks: List[CodeChunk]):
    ensure_chunk_dir()
    for chunk in chunks:
        chunk_id = str(uuid.uuid4())
        data = chunk.to_dict()
        data["chunk_id"] = chunk_id
        filename = f"chunk_{chunk_id}.json"
        path = CHUNK_DIR / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


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
