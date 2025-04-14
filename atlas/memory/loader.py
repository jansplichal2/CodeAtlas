import json
import tiktoken
from atlas.config import CHUNK_DIR, MAX_TOKENS
from atlas.memory.storage import init_db, insert_chunk_records

ENCODER = tiktoken.get_encoding("cl100k_base")


def load_chunks_to_sqlite():
    init_db()
    records = []
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        source = data.get("source", "")
        tokens = len(ENCODER.encode(source))
        if tokens <= MAX_TOKENS:
            data["tokens"] = tokens
            data["status"] = "ready"
            records.append(data)
        else:
            print(f"⚠️ Skipping {chunk_file.name}: {tokens} tokens (too large)")
    insert_chunk_records(records)
    print(f"✅ Inserted {len(records)} chunks into SQLite")
