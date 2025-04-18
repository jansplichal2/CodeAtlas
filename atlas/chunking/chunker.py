import json
import os
from typing import List
import uuid
import tiktoken
from atlas.chunking.base_chunker import CodeChunk
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


def cleanup_chunks():
    ensure_chunk_dir()
    count = 0
    errors = 0
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as r:
            data = json.load(r)
        if 'errors' not in data:
            try:
                os.remove(chunk_file)
                count += 1
            except Exception as e:
                print(f"⚠️ Failed to remove {chunk_file.name}: {e}")
        else:
            errors += 1

    print(f"Removed {count} chunk files in total, leaving {errors} files with error")


def display_error_chunks():
    ensure_chunk_dir()
    count = 0
    errors = 0
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as r:
            data = json.load(r)
        if 'errors' not in data:
            count += 1
        else:
            print(f"Chunk {chunk_file.name} has these errors {data['errors']}")
            errors += 1

    print(f"Found {count} correct chunk files, {errors} files have errors")


def validate_chunks():
    ensure_chunk_dir()
    failed = []
    ok = 0
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as r:
            data = json.load(r)
        source = data.get("source", "")
        token_count = len(ENCODER.encode(source))
        if token_count > MAX_TOKENS:
            print(f"⚠️  {chunk_file.name} too large: {token_count} tokens")
            if 'errors' not in data:
                data['errors'] = []
            data['errors'].append({
                'source': 'validation',
                'error': f"{chunk_file.name} too large: {token_count} tokens while maximum in {MAX_TOKENS}"
            })
            with open(chunk_file, "w", encoding="utf-8") as w:
                w.write(json.dumps(data))
            failed.append((chunk_file, token_count))
        else:
            ok += 1
    print(f"✅ Validation complete. Valid: {ok}, Over-limit: {len(failed)}")
    return failed
