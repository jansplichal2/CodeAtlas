import json
import shutil
from typing import List
import uuid
import tiktoken
from atlas.chunking.base_chunker import CodeChunk
from atlas.config import CHUNK_DIR, CHUNK_ERROR_DIR,  MAX_TOKENS

ENCODER = tiktoken.get_encoding("cl100k_base")


def ensure_chunk_dir():
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    CHUNK_ERROR_DIR.mkdir(parents=True, exist_ok=True)


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
            print(f"⚠️  Moving {chunk_file.name} to: {CHUNK_ERROR_DIR}")
            if 'errors' not in data:
                data['errors'] = []
            data['errors'].append({
                'error_type': 'validation_error',
                'error_message': f"{chunk_file.name} too large: {token_count} tokens while maximum in {MAX_TOKENS}"
            })
            with open(chunk_file, "w", encoding="utf-8") as w:
                w.write(json.dumps(data))
            failed.append((chunk_file, token_count))
            shutil.move(chunk_file, CHUNK_ERROR_DIR / chunk_file.name)
        else:
            ok += 1
    print(f"✅ Validation complete. Valid: {ok}, Over-limit: {len(failed)}")
    return failed
