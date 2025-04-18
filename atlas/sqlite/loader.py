import json
import sqlite3
import random
from typing import Dict, Tuple
from datetime import datetime
from atlas.config import CHUNK_DIR, DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    chunk_id TEXT UNIQUE,
    chunk_type TEXT,
    name TEXT,
    chunk_no INTEGER,
    start_line INTEGER,
    end_line INTEGER,
    file_path TEXT,
    source TEXT,
    tokens INTEGER,
    created_at TEXT
);
"""


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    with connect_db() as conn:
        conn.executescript(SCHEMA)


def insert_chunk_record(chunk: Dict) -> Tuple[bool, str]:
    with connect_db() as conn:
        try:
            cur = conn.cursor()
            chunk_id = chunk.get("chunk_id")
            if not chunk_id:
                return True, f'Cannot find chunk_id in this chunk {chunk}'
            cur.execute(
                """INSERT INTO chunks 
                   (chunk_id, 
                   chunk_type, 
                   name,
                   chunk_no,
                   start_line, 
                   end_line, 
                   file_path, 
                   source, 
                   tokens, 
                   created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    chunk["type"],
                    chunk["name"],
                    chunk["chunk_no"],
                    chunk["start_line"],
                    chunk["end_line"],
                    chunk["file_path"],
                    chunk["source"],
                    chunk.get("tokens", 0),
                    datetime.utcnow().isoformat()
                )
            )
            conn.commit()
            if random.randrange(0, 50) == 25:
                return True, 'This is random error'

            return False, ''
        except Exception as e:
            return True, str(e)


def load_chunks_to_sqlite():
    init_db()
    count = 0
    errors = 0
    for chunk_file in CHUNK_DIR.glob("*.json"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            count += 1
            is_error, error = insert_chunk_record(data)
            if is_error:
                errors += 1
                with open(chunk_file, "r+", encoding="utf-8") as w:
                    if 'errors' not in data:
                        data['errors'] = []
                    data['errors'].append({'source': 'sqlite', 'error': error})
                    json.dump(data, w, indent=2)

    print(f"✅ Inserted {count} chunks into SQLite. {errors} files finished with error")
