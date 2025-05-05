import logging
import json
import os
from typing import List, Tuple
import uuid
import tiktoken
from atlas.chunking.base_chunker import CodeChunk
from atlas.config import CHUNK_DIR, MAX_TOKENS

ENCODER = tiktoken.get_encoding("cl100k_base")
logger = logging.getLogger(__name__)


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
                logger.info(f"Failed to remove {chunk_file.name}: {e}")
        else:
            errors += 1

    logger.info(f"Removed {count} chunk files in total, leaving {errors} files with error")


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
            logger.info(f"Chunk {chunk_file.name} has these errors {data['errors']}")
            errors += 1

    logger.info(f"Found {count} correct chunk files, {errors} files have errors")


def classify_chunk_content(source: str) -> Tuple[str, int]:
    stripped = source.strip()

    if not stripped:
        return "empty", 0

    if stripped in {"}", "};", "{", "{;"}:
        return "brace", 1

    lines = [line.strip() for line in source.splitlines() if line.strip()]
    if all(line.startswith("//") or line.startswith("/*") for line in lines) and len(lines) <= 2:
        return "trivial_comment", len(lines)

    meaningful_lines = [line for line in lines if not line.startswith("//")]
    if len(meaningful_lines) < 3:
        return "tiny", len(meaningful_lines)

    return "normal", len(meaningful_lines)

def validate_chunks():
    ensure_chunk_dir()
    failed = []
    ok = 0

    trivial_counts = {
        "empty": 0,
        "brace": 0,
        "trivial_comment": 0,
        "tiny": 0,
        "normal": 0
    }

    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as r:
            data = json.load(r)

        source = data.get("source", "")
        token_count = len(ENCODER.encode(source))

        # Token limit check
        if token_count > MAX_TOKENS:
            logger.info(f"{chunk_file.name} too large: {token_count} tokens")
            if 'errors' not in data:
                data['errors'] = []
            data['errors'].append({
                'source': 'validation',
                'error': f"{chunk_file.name} too large: {token_count} tokens while maximum is {MAX_TOKENS}"
            })
            with open(chunk_file, "w", encoding="utf-8") as w:
                w.write(json.dumps(data, indent=2))
            failed.append((chunk_file, token_count))
        else:
            ok += 1

        # Chunk content classification
        chunk_type, count = classify_chunk_content(source)
        trivial_counts[chunk_type] += 1

    logger.info(f"Validation complete. Valid: {ok}, Over-limit: {len(failed)}")

    logger.info("Chunk content summary:")
    for key, value in trivial_counts.items():
        logger.info(f"{key}: {value}")

    return failed
