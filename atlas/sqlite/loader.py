import json
from atlas.config import CHUNK_DIR
from atlas.sqlite.storage import init_db, insert_chunk_records


def load_chunks_to_sqlite():
    init_db()
    records = []
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        records.append(data)
    insert_chunk_records(records)
    print(f"✅ Inserted {len(records)} chunks into SQLite")
